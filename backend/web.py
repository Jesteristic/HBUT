from flask import Flask, request, jsonify, send_from_directory
import json
from flask_login import login_user, logout_user, login_required, current_user
from .sql.sql_tools import RedisUtils, MysqlUtils
from .configs import MysqlConfig, CrawlerConfig
from .spiders.wanfangtools import WanfangPatentProducer, WanfangPatentComsumer
from .auth import login_manager, init_user_table, User
from .nlp_tools import extract_technical_elements, create_patent_map_image, analyze_technology_opportunities
from threading import Lock

# 将静态目录指向可能的构建输出
app = Flask(__name__, static_folder='../static/dist', static_url_path='')

redis = RedisUtils()
mysql = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                  user=MysqlConfig.user, password=MysqlConfig.password,
                  database=MysqlConfig.database, charset=MysqlConfig.charset)

# 简单的爬虫线程管理

# 初始化用户表并登录管理器
init_user_table()
login_manager.init_app(app)

def init_database_tables():
    """初始化数据库表"""
    # 读取createTables.sql文件
    import os
    sql_path = os.path.join(os.path.dirname(__file__), 'sql', 'createTables.sql')
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 分割SQL语句并执行
    statements = sql_content.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement:
            try:
                mysql.execute_update(statement)
            except Exception as e:
                print(f"Error creating table: {e}")

# 初始化数据库表
init_database_tables()

@app.before_request
def protect_frontend():
    # allow API, static, and favicon without change
    path = request.path
    if path.startswith('/api') or path.startswith('/static') or path.startswith('/favicon'):
        return
    # if not logged in, serve SPA anyway; router will redirect to /login
    # this prevents browsing index without backend auth
    if not current_user.is_authenticated:
        return send_from_directory('static/dist', 'index.html')
crawler_lock = Lock()
producers = []
consumers = []


def start_crawlers(prod=1, cons=1):
    with crawler_lock:
        if producers or consumers:
            return False  # 已经启动
        cfg = CrawlerConfig()
        for i in range(prod):
            p = WanfangPatentProducer(cfg, producerID=i + 1)
            p.daemon = True
            p.start()
            producers.append(p)
        for j in range(cons):
            c = WanfangPatentComsumer(cfg, comsumerID=j + 1)
            c.daemon = True
            c.start()
            consumers.append(c)
        return True


def stop_crawlers():
    with crawler_lock:
        for t in producers + consumers:
            try:
                t.stop()
            except Exception:
                pass
        producers.clear()
        consumers.clear()


@app.route('/')
def index():
    # 优先返回构建后前端的 index.html
    import os
    dist_idx = os.path.join(app.static_folder, 'index.html')
    if os.path.exists(dist_idx):
        return send_from_directory(app.static_folder, 'index.html')
    # 否则返回旧版静态页面（保留教程时）
    return send_from_directory('../static', 'index.html')

@app.route('/<path:path>')
def catch_all(path):
    # 对于前端路由，返回 index.html，让 Vue 路由器处理
    if path.startswith('api/') or path.startswith('static/'):
        return jsonify({'error': 'Not Found'}), 404
    return index()


@app.route('/api/task', methods=['POST'])
@login_required
def add_task():
    data = request.get_json()
    if not data or 'keyword' not in data:
        return jsonify({"error": "keyword required"}), 400
    # persist to history
    mysql.insert('producer_tasks', {
        'keyword': data.get('keyword'),
        'page_size': data.get('page_size',1),
        'pages': data.get('pages',1),
        'status': 'pending'
    })
    redis.rpush('wanfang:producer_tasks', json.dumps(data))
    return jsonify({"ok": True})


@app.route('/api/logs')
@login_required
def get_logs():
    # support filtering
    page = int(request.args.get('page', 1))
    per = int(request.args.get('per', 20))
    keyword = request.args.get('keyword')
    action = request.args.get('action')
    start = request.args.get('start')
    end = request.args.get('end')
    conditions = []
    params = []
    if keyword:
        conditions.append("keyword LIKE %s")
        params.append(f"%{keyword}%")
    if action:
        conditions.append("action=%s")
        params.append(action)
    if start:
        conditions.append("created_at>=%s")
        params.append(start)
    if end:
        conditions.append("created_at<=%s")
        params.append(end)
    condition = " AND ".join(conditions) if conditions else None
    offset = (page - 1) * per
    rows = mysql.select('spider_logs', '*', condition=condition, params=params or None,
                        order_by='created_at DESC', limit=per, offset=offset)
    total = mysql.count('spider_logs', condition=condition, params=params or None)
    return jsonify({'rows': rows, 'total': total})


@app.route('/api/status')
@login_required
def status():
    user_info = {'username': current_user.username} if current_user.is_authenticated else None
    return jsonify({
        "producer_tasks": redis.llen('wanfang:producer_tasks'),
        "task_queue": redis.llen('wanfang:task_queue'),
        "producers_running": len(producers),
        "consumers_running": len(consumers),
        "user": user_info
    })


@app.route('/api/start', methods=['POST'])
@login_required
def api_start():
    content = request.get_json() or {}
    prod = content.get('producers', 1)
    cons = content.get('consumers', 1)
    started = start_crawlers(prod, cons)
    return jsonify({"started": started})


@app.route('/api/stop', methods=['POST'])
@login_required
def api_stop():
    stop_crawlers()
    return jsonify({"stopped": True})


@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    # lookup user
    row = mysql.select('users', '*', condition='username=%s', params=(username,), fetch_one=True)
    if not row:
        return jsonify({'error': 'invalid credential'}), 401
    user = User(row['id'], row['username'], row['password'])
    if not user.check_password(password):
        return jsonify({'error': 'invalid credential'}), 401
    login_user(user)
    return jsonify({'ok': True})

@app.route('/api/logout')
@login_required
def api_logout():
    logout_user()
    return jsonify({'ok': True})

# task history endpoints
def _update_task_status(task_id, status):
    mysql.update('producer_tasks', {'status': status}, condition='id=%s', condition_params=(task_id,))

@app.route('/api/tasks')
@login_required
def get_tasks():
    page = int(request.args.get('page', 1))
    per = int(request.args.get('per', 20))
    offset = (page - 1) * per
    rows = mysql.select('producer_tasks', '*', order_by='created_at DESC', limit=per, offset=offset)
    total = mysql.count('producer_tasks')
    return jsonify({'rows': rows, 'total': total})

@app.route('/api/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    mysql.delete('producer_tasks', condition='id=%s', params=(task_id,))
    return jsonify({'ok': True})

@app.route('/api/tasks/<int:task_id>/rerun', methods=['POST'])
@login_required
def rerun_task(task_id):
    row = mysql.get_by_id('producer_tasks', task_id)
    if not row:
        return jsonify({'error': 'not found'}), 404
    payload = {'keyword': row['keyword'], 'page_size': row['page_size'], 'pages': row['pages']}
    redis.rpush('wanfang:producer_tasks', json.dumps(payload))
    _update_task_status(task_id, 'pending')
    return jsonify({'ok': True})

# Patent APIs
@app.route('/api/patents', methods=['GET'])
@login_required
def get_patents():
    page = int(request.args.get('page', 1))
    per = int(request.args.get('per', 20))
    keyword = request.args.get('keyword')
    applicant = request.args.get('applicant')
    conditions = []
    params = []
    if keyword:
        conditions.append("title LIKE %s")
        params.append(f"%{keyword}%")
    if applicant:
        conditions.append("applicant LIKE %s")
        params.append(f"%{applicant}%")
    condition = " AND ".join(conditions) if conditions else None
    offset = (page - 1) * per
    rows = mysql.select('patent_basic', '*', condition=condition, params=params or None,
                        order_by='publication_date DESC', limit=per, offset=offset)
    total = mysql.count('patent_basic', condition=condition, params=params or None)
    return jsonify({'rows': rows, 'total': total})

@app.route('/api/patents/<int:patent_id>', methods=['GET'])
@login_required
def get_patent_detail(patent_id):
    patent = mysql.get_by_id('patent_basic', patent_id)
    if not patent:
        return jsonify({'error': 'not found'}), 404
    # Get full text if available
    full_text = mysql.select('patent_full_text', '*', condition='patent_id=%s', params=(patent_id,), fetch_one=True)
    patent['full_text'] = full_text
    return jsonify(patent)

@app.route('/api/patents/analyze', methods=['POST'])
@login_required
def analyze_patents():
    data = request.get_json() or {}
    patent_ids = data.get('patent_ids', [])
    analysis_type = data.get('type', 'elements')  # elements, map, opportunities

    patents = []
    for pid in patent_ids:
        patent = mysql.get_by_id('patent_basic', pid)
        if patent:
            patents.append(patent)

    if analysis_type == 'elements':
        results = []
        for patent in patents:
            text = patent.get('title', '') + ' ' + (patent.get('abstract', '') or '')
            elements = extract_technical_elements(text)
            results.append({'patent_id': patent['id'], 'elements': elements})
        return jsonify({'results': results})
    elif analysis_type == 'map':
        image_b64 = create_patent_map_image(patents)
        return jsonify({'image': image_b64})
    elif analysis_type == 'opportunities':
        opportunities = analyze_technology_opportunities(patents)
        return jsonify({'opportunities': opportunities})
    else:
        return jsonify({'error': 'invalid analysis type'}), 400

if __name__ == '__main__':
    # 在启动服务时不自动启动爬虫线程，需手动调用 /api/start
    app.run(debug=True, host='0.0.0.0', port=5000)
