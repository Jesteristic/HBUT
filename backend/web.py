import json
import os
from datetime import datetime, timedelta
from functools import wraps
from threading import Lock

import loguru
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user

from auth import login_manager, init_user_table, User
from configs import MysqlConfig, CrawlerConfig
from nlp_tools import extract_technical_elements, create_patent_map_image, analyze_technology_opportunities
from spiders.wanfangtools import WanfangPatentProducer, WanfangPatentComsumer
from sql.sql_tools import RedisUtils, MysqlUtils

# 将静态目录优先指向前端构建输出 static/dist，fallback 到 static
static_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'dist')
if not os.path.exists(static_dir):
    static_dir = os.path.join(os.path.dirname(__file__), '..', 'static')
    loguru.logger.warning(f"static/dist not found, fallback to {static_dir}")
else:
    loguru.logger.info(f"Serving frontend from {static_dir}")
app = Flask(__name__, static_folder=static_dir, static_url_path='')
app.secret_key = 'your_secret_key_here'  # 设置Flask secret key
CORS(app, supports_credentials=True,
     origins=['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://localhost:3003',
              'http://localhost:3004', 'http://localhost:3005', 'http://localhost:5173', 'http://localhost:5174',
              'http://localhost:5175', 'http://localhost:5176', 'http://localhost:3006', 'http://localhost:3007'])

# Session配置 for 跨域
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = False

redis = RedisUtils()
mysql = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                  user=MysqlConfig.user, password=MysqlConfig.password,
                  database=MysqlConfig.database, charset=MysqlConfig.charset)

# 简单的爬虫线程管理

# 初始化用户表并登录管理器
init_user_table()
login_manager.init_app(app)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({'error': 'authentication required'}), 401
        if getattr(current_user, 'role', 'user') != 'admin':
            return jsonify({'error': 'admin access required'}), 403
        return f(*args, **kwargs)

    return decorated_function

def init_database_tables():
    """初始化数据库表"""
    # 读取createTables.sql文件
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

# 同步 queue_order 列，历史任务如果缺失 queue_order 列也会被补齐
try:
    columns = mysql.get_table_info('producer_tasks')
    if not any(col['Field'] == 'queue_order' for col in columns):
        mysql.execute_update('ALTER TABLE producer_tasks ADD COLUMN queue_order INT DEFAULT 0')
        mysql.execute_update('UPDATE producer_tasks SET queue_order = id WHERE queue_order = 0')
except Exception as e:
    print(f'Error ensuring producer_tasks queue_order: {e}')


def _build_producer_payload(task_id, keyword, page_size, pages):
    return json.dumps({'id': task_id, 'keyword': keyword, 'page_size': page_size, 'pages': pages})


def _normalize_pending_queue():
    rows = mysql.select('producer_tasks', '*', condition='status=%s', params=('pending',),
                        order_by='queue_order ASC, created_at ASC')
    current_order = 1
    for row in rows:
        if (row.get('queue_order') or 0) != current_order:
            mysql.update('producer_tasks', {'queue_order': current_order}, condition='id=%s',
                         condition_params=(row['id'],))
        current_order += 1
    return rows


def _sync_pending_queue():
    rows = _normalize_pending_queue()
    redis.delete('wanfang:producer_tasks')
    if rows:
        items = [_build_producer_payload(row['id'], row['keyword'], row['page_size'], row['pages']) for row in rows]
        redis.rpush('wanfang:producer_tasks', *items)
    return rows


def _queue_producer_task(keyword, page_size, pages):
    max_order = mysql.select('producer_tasks', 'MAX(queue_order) as max_order', fetch_one=True)
    next_order = (max_order.get('max_order') or 0) + 1 if max_order else 1
    task_id = mysql.insert('producer_tasks', {
        'keyword': keyword,
        'page_size': page_size,
        'pages': pages,
        'status': 'pending',
        'queue_order': next_order
    })
    if not task_id:
        raise RuntimeError('Failed to insert task')
    redis.rpush('wanfang:producer_tasks', _build_producer_payload(task_id, keyword, page_size, pages))
    return task_id


def _remove_pending_task_from_redis(task_id, keyword, page_size, pages):
    payload = _build_producer_payload(task_id, keyword, page_size, pages)
    removed = redis.lrem('wanfang:producer_tasks', 0, payload)
    if removed == 0:
        fallback = json.dumps({'keyword': keyword, 'page_size': page_size, 'pages': pages})
        removed = redis.lrem('wanfang:producer_tasks', 0, fallback)
    return removed


@app.before_request
def protect_frontend():
    # allow API, static, and favicon without change
    path = request.path
    if path.startswith('/api') or path.startswith('/static') or path.startswith('/favicon'):
        return
    # if not logged in, serve SPA anyway; router will redirect to /login
    # this prevents browsing index without backend auth
    if not current_user.is_authenticated:
        return send_from_directory(app.static_folder, 'index.html')
crawler_lock = Lock()
producers = []
consumers = []


def start_crawlers(prod=1, cons=1):
    with crawler_lock:
        cfg = CrawlerConfig()
        started = False
        if not producers:
            for i in range(prod):
                p = WanfangPatentProducer(cfg, producerID=len(producers) + 1)
                p.daemon = True
                p.start()
                producers.append(p)
                started = True
        if not consumers:
            for j in range(cons):
                c = WanfangPatentComsumer(cfg, comsumerID=len(consumers) + 1)
                c.daemon = True
                c.start()
                consumers.append(c)
                started = True
        return started


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
    # 返回前端的 index.html
    return send_from_directory(app.static_folder, 'index.html')

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
    if not data or not data.get('keyword'):
        return jsonify({"error": "keyword required"}), 400

    keyword = data.get('keyword').strip()
    page_size = max(1, int(data.get('page_size', 1)))
    pages = max(1, int(data.get('pages', 1)))

    try:
        _queue_producer_task(keyword, page_size, pages)
    except Exception as e:
        print(f"Error queuing task: {e}")
        return jsonify({'error': 'failed to queue task'}), 500

    # 自动启动爬虫线程，避免需要手动启动采集
    if not producers and not consumers:
        start_crawlers()

    return jsonify({"ok": True})


@app.route('/api/tasks/batch', methods=['POST'])
@login_required
def add_batch_tasks():
    data = request.get_json() or {}
    tasks = data.get('tasks') or []
    if not isinstance(tasks, list) or not tasks:
        keywords = (data.get('keywords') or '').splitlines()
        tasks = [
            {'keyword': k.strip(), 'page_size': int(data.get('page_size', 1)), 'pages': int(data.get('pages', 1))}
            for k in keywords if k.strip()
        ]

    if not tasks:
        return jsonify({'error': 'no tasks provided'}), 400

    queued = 0
    for item in tasks:
        if not item.get('keyword'):
            continue
        keyword = item.get('keyword').strip()
        page_size = max(1, int(item.get('page_size', 1)))
        pages = max(1, int(item.get('pages', 1)))
        try:
            _queue_producer_task(keyword, page_size, pages)
            queued += 1
        except Exception as e:
            print(f"Error queuing task {keyword}: {e}")

    if queued == 0:
        return jsonify({'error': 'no valid tasks queued'}), 400

    if not producers and not consumers:
        start_crawlers()

    return jsonify({'ok': True, 'queued': queued})


@app.route('/api/tasks/<int:task_id>/move', methods=['POST'])
@login_required
def move_task(task_id):
    data = request.get_json() or {}
    direction = data.get('direction')
    if direction not in ('up', 'down'):
        return jsonify({'error': 'direction required'}), 400

    task = mysql.get_by_id('producer_tasks', task_id)
    if not task:
        return jsonify({'error': 'task not found'}), 404
    if task.get('status') != 'pending':
        return jsonify({'error': 'only pending tasks can be reordered'}), 400

    pending = mysql.select('producer_tasks', '*', condition='status=%s', params=('pending',),
                           order_by='queue_order ASC, created_at ASC')
    if not pending:
        return jsonify({'error': 'no pending tasks found'}), 400

    index = next((i for i, row in enumerate(pending) if row['id'] == task_id), None)
    if index is None:
        return jsonify({'error': 'task not in queue'}), 404

    swap_index = index - 1 if direction == 'up' else index + 1
    if swap_index < 0 or swap_index >= len(pending):
        return jsonify({'error': 'cannot move task further'}), 400

    first = pending[index]
    second = pending[swap_index]
    mysql.update('producer_tasks', {'queue_order': second['queue_order']}, condition='id=%s',
                 condition_params=(first['id'],))
    mysql.update('producer_tasks', {'queue_order': first['queue_order']}, condition='id=%s',
                 condition_params=(second['id'],))
    _sync_pending_queue()
    return jsonify({'ok': True})


@app.route('/api/tasks/<int:task_id>/cancel', methods=['POST'])
@login_required
def cancel_task(task_id):
    task = mysql.get_by_id('producer_tasks', task_id)
    if not task:
        return jsonify({'error': 'task not found'}), 404

    status = task.get('status')
    if status in ('done', 'failed', 'canceled'):
        return jsonify({'ok': True, 'status': status})

    if status == 'pending':
        _remove_pending_task_from_redis(task_id, task.get('keyword'), task.get('page_size'), task.get('pages'))
        mysql.update('producer_tasks', {'status': 'canceled'}, condition='id=%s', condition_params=(task_id,))
        _sync_pending_queue()
        return jsonify({'ok': True, 'status': 'canceled'})

    if status == 'running':
        redis.sadd('wanfang:cancelled_producer_tasks', str(task_id))
        mysql.update('producer_tasks', {'status': 'canceled'}, condition='id=%s', condition_params=(task_id,))
        return jsonify({'ok': True, 'status': 'canceled'})

    mysql.update('producer_tasks', {'status': 'canceled'}, condition='id=%s', condition_params=(task_id,))
    return jsonify({'ok': True, 'status': 'canceled'})


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


@app.route('/api/check-auth')
def check_auth():
    """公开的认证状态检查端点"""
    user_info = {
        'username': current_user.username,
        'role': getattr(current_user, 'role', 'user')
    } if current_user.is_authenticated else None
    login_type = 'admin' if user_info and user_info.get('role') == 'admin' else 'user'

    return jsonify({
        "authenticated": current_user.is_authenticated,
        "user": user_info,
        "login_type": login_type
    })


@app.route('/api/status')
@login_required
def status():
    user_info = {
        'username': current_user.username,
        'role': getattr(current_user, 'role', 'user')
    } if current_user.is_authenticated else None
    login_type = 'admin' if user_info and user_info.get('role') == 'admin' else 'user'

    # 获取队列状态
    producer_tasks_count = redis.llen('wanfang:producer_tasks')
    task_queue_count = redis.llen('wanfang:task_queue')

    # 获取系统运行统计
    success_count = 0
    error_count = 0
    success_rate = 0
    memory_percent = 0
    cpu_percent = 0
    total_operations = 0

    try:
        # 获取最近1小时的日志统计
        one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        recent_logs = mysql.select('spider_logs', 'COUNT(*) as total, action',
                                   condition='created_at >= %s', params=(one_hour_ago,),
                                   group_by='action')

        for log in recent_logs:
            if log['action'] in ['task_completed', 'page_crawled']:
                success_count += log['total']
            elif log['action'] in ['task_failed', 'error']:
                error_count += log['total']

        # 计算成功率
        total_operations = success_count + error_count
        success_rate = (success_count / total_operations * 100) if total_operations > 0 else 0

        # 获取内存使用情况（简化版）
        import psutil
        memory_percent = psutil.virtual_memory().percent
        cpu_percent = psutil.cpu_percent(interval=1)

    except Exception as e:
        print(f"Error getting system stats: {e}")
        # 变量已在上面初始化，这里不需要重新赋值

    # 获取队列详情（最近的任务）
    try:
        recent_producer_tasks = redis.lrange('wanfang:producer_tasks', 0, 4)  # 获取前5个任务
        recent_task_queue = redis.lrange('wanfang:task_queue', 0, 4)  # 获取前5个任务ID
    except:
        recent_producer_tasks = []
        recent_task_queue = []

    print(f"Status: user={user_info}, login_type={login_type}")
    return jsonify({
        "producer_tasks": producer_tasks_count,
        "task_queue": task_queue_count,
        "producers_running": len(producers),
        "consumers_running": len(consumers),
        "user": user_info,
        "login_type": login_type,
        # 新增的监控指标
        "system_stats": {
            "success_rate": round(success_rate, 2),
            "memory_usage": round(memory_percent, 2),
            "cpu_usage": round(cpu_percent, 2),
            "recent_success": success_count,
            "recent_errors": error_count
        },
        "queue_details": {
            "recent_producer_tasks": [task.decode('utf-8') if isinstance(task, bytes) else task for task in
                                      recent_producer_tasks],
            "recent_task_ids": [task.decode('utf-8') if isinstance(task, bytes) else task for task in recent_task_queue]
        },
        "performance_metrics": {
            "avg_processing_time": 0,  # 可以后续实现
            "queue_growth_rate": 0,  # 可以后续实现
            "error_rate": round((error_count / max(total_operations, 1)) * 100, 2)
        }
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
    login_type = data.get('loginType') or data.get('login_type') or 'user'

    # 检查登录失败次数
    fail_key = f"login_fail_{username}"
    fail_count = int(redis.get(fail_key) or 0)
    if fail_count >= 5:
        return jsonify({'error': '登录失败次数过多，请稍后再试'}), 429

    print(f"Login attempt: username={username}, password={password}, login_type={login_type}")
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    # lookup user
    row = mysql.select('users', '*', condition='username=%s', params=(username,), fetch_one=True)
    if not row:
        print(f"User {username} not found")
        redis.set(fail_key, fail_count + 1, ex=300)  # 5分钟内失败+1
        return jsonify({'error': '用户名或密码错误'}), 401

    user = User(row['id'], row['username'], row['password'], row.get('role', 'user'))
    if not user.check_password(password):
        print(f"Password check failed for {username}")
        redis.set(fail_key, fail_count + 1, ex=300)
        return jsonify({'error': '用户名或密码错误'}), 401

    # 登录成功，重置失败计数
    redis.delete(fail_key)
    
    login_user(user)
    session['login_type'] = 'admin' if str(login_type).lower() == 'admin' else 'user'
    session.permanent = data.get('remember', False)  # 记住我设置session持久化

    print(f"Login successful for {username}, type={session['login_type']}")
    return jsonify({'ok': True})


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    # check if user exists
    existing = mysql.select('users', '*', condition='username=%s', params=(username,), fetch_one=True)
    if existing:
        return jsonify({'error': '用户名已存在'}), 400
    # create user
    from werkzeug.security import generate_password_hash
    pwd_hash = generate_password_hash(password)
    mysql.insert('users', {'username': username, 'password': pwd_hash})
    return jsonify({'ok': True, 'message': '注册成功'})


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    session.pop('login_type', None)
    logout_user()
    return jsonify({'ok': True})


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if getattr(current_user, 'role', 'user') != 'admin':
            return jsonify({'error': 'admin required'}), 403
        return f(*args, **kwargs)

    return wrapper


@app.route('/api/users')
@admin_required
def api_users():
    print(f"api_users called by {current_user.username if current_user.is_authenticated else 'anonymous'}")
    try:
        rows = mysql.select('users', 'id, username, role', order_by='id ASC')
        print(f"Users found: {len(rows)}")
        return jsonify({'users': rows})
    except Exception as e:
        print(f"Error in api_users: {e}")
        return jsonify({'error': 'database error'}), 500


@app.route('/api/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def api_user_delete(user_id):
    if current_user.id == user_id:
        return jsonify({'error': '不能删除当前登录用户'}), 400
    mysql.delete('users', condition='id=%s', params=(user_id,))
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
    rows = mysql.select(
        'producer_tasks', '*',
        order_by="FIELD(status, 'pending', 'running', 'done', 'failed', 'canceled'), queue_order ASC, created_at DESC",
        limit=per,
        offset=offset
    )
    total = mysql.count('producer_tasks')
    return jsonify({'rows': rows, 'total': total})

@app.route('/api/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    row = mysql.get_by_id('producer_tasks', task_id)
    if row and row.get('status') == 'pending':
        _remove_pending_task_from_redis(task_id, row.get('keyword'), row.get('page_size'), row.get('pages'))
        _sync_pending_queue()
    mysql.delete('producer_tasks', condition='id=%s', params=(task_id,))
    return jsonify({'ok': True})


@app.route('/api/config', methods=['GET'])
@admin_required
def get_config():
    # 从数据库或其他存储中获取配置，如果没有则使用默认值
    try:
        # 尝试从数据库获取配置
        config_row = mysql.select('system_config', '*', fetch_one=True)
        if config_row:
            return jsonify({
                'max_pages': config_row.get('max_pages', 10),
                'page_size': config_row.get('page_size', 20),
                'timeout': config_row.get('timeout', 30),
                'retry_times': config_row.get('retry_times', 3)
            })
        else:
            # 使用默认配置
            cfg = CrawlerConfig()
            return jsonify({
                'max_pages': cfg.max_pages,
                'page_size': cfg.page_size,
                'timeout': cfg.timeout,
                'retry_times': cfg.retry_times
            })
    except Exception as e:
        print(f"Error fetching config: {e}")
        # 返回默认配置
        cfg = CrawlerConfig()
        return jsonify({
            'max_pages': cfg.max_pages,
            'page_size': cfg.page_size,
            'timeout': cfg.timeout,
            'retry_times': cfg.retry_times
        })


@app.route('/api/config', methods=['POST'])
@admin_required
def update_config():
    data = request.get_json() or {}

    try:
        # 确保system_config表存在
        mysql.execute_update("""
                             CREATE TABLE IF NOT EXISTS system_config
                             (
                                 id
                                 INT
                                 PRIMARY
                                 KEY
                                 DEFAULT
                                 1,
                                 max_pages
                                 INT
                                 DEFAULT
                                 10,
                                 page_size
                                 INT
                                 DEFAULT
                                 20,
                                 timeout
                                 INT
                                 DEFAULT
                                 30,
                                 retry_times
                                 INT
                                 DEFAULT
                                 3,
                                 updated_at
                                 TIMESTAMP
                                 DEFAULT
                                 CURRENT_TIMESTAMP
                                 ON
                                 UPDATE
                                 CURRENT_TIMESTAMP
                             )
                             """)

        # 更新或插入配置
        config_data = {
            'max_pages': data.get('max_pages', 10),
            'page_size': data.get('page_size', 20),
            'timeout': data.get('timeout', 30),
            'retry_times': data.get('retry_times', 3)
        }

        # 使用REPLACE INTO来插入或更新
        mysql.execute_update("""
                             REPLACE
                             INTO system_config (id, max_pages, page_size, timeout, retry_times)
            VALUES (1,
                             %s,
                             %s,
                             %s,
                             %s
                             )
                             """, (config_data['max_pages'], config_data['page_size'], config_data['timeout'],
                                   config_data['retry_times']))

        return jsonify({'ok': True})
    except Exception as e:
        print(f"Error updating config: {e}")
        return jsonify({'error': '配置更新失败'}), 500


@app.route('/api/tasks/<int:task_id>/rerun', methods=['POST'])
@login_required
def rerun_task(task_id):
    row = mysql.get_by_id('producer_tasks', task_id)
    if not row:
        return jsonify({'error': 'not found'}), 404

    if row.get('status') == 'running':
        return jsonify({'error': 'task is already running'}), 400

    task_id = _queue_producer_task(row['keyword'], row['page_size'], row['pages'])
    return jsonify({'ok': True, 'queued_id': task_id})


@app.route('/api/patents', methods=['POST'])
@admin_required
def add_patent():
    data = request.get_json() or {}
    required_fields = ['title', 'applicant']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    # Insert patent
    patent_data = {
        'title': data['title'],
        'applicant': data['applicant'],
        'inventors': data.get('inventors', ''),
        'application_number': data.get('application_number', ''),
        'publication_number': data.get('publication_number', ''),
        'publication_date': data.get('publication_date', ''),
        'country_code': data.get('country_code', 'CN'),
        'abstract_text': data.get('abstract_text', '')
    }
    patent_id = mysql.insert('patent_basic', patent_data)
    return jsonify({'id': patent_id, 'ok': True})


@app.route('/api/patents/<int:patent_id>', methods=['DELETE'])
@admin_required
def delete_patent(patent_id):
    # Check if patent exists
    patent = mysql.get_by_id('patent_basic', patent_id)
    if not patent:
        return jsonify({'error': 'not found'}), 404
    # Delete full text first
    mysql.delete('patent_full_text', condition='patent_id=%s', params=(patent_id,))
    # Delete patent
    mysql.delete('patent_basic', condition='id=%s', params=(patent_id,))
    return jsonify({'ok': True})

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


@app.route('/api/patents/export', methods=['POST'])
@login_required
def export_patents():
    data = request.get_json() or {}
    export_data = data.get('data', [])
    export_type = data.get('type', 'opportunities')

    if export_type == 'opportunities':
        # 导出技术机会报告
        import pandas as pd
        from io import BytesIO

        df = pd.DataFrame(export_data)
        df = df[['title', 'score', 'level', 'recommendations']]
        df.columns = ['专利标题', '机会评分', '机会等级', '建议']

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='技术机会报告', index=False)
        output.seek(0)

        from flask import send_file
        return send_file(output, as_attachment=True, download_name='技术机会报告.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    return jsonify({'error': 'invalid export type'}), 400

if __name__ == '__main__':
    # 在启动服务时不自动启动爬虫线程，需手动调用 /api/start
    app.run(debug=True, host='0.0.0.0', port=5000)
