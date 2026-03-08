from flask import Flask, request, jsonify, send_from_directory
import json
from .sql.sql_tools import RedisUtils, MysqlUtils
from .configs import MysqlConfig, CrawlerConfig
from .spiders.wanfangtools import WanfangPatentProducer, WanfangPatentComsumer
from threading import Lock

# 将静态目录指向可能的构建输出
app = Flask(__name__, static_folder='../static/dist', static_url_path='')

redis = RedisUtils()
mysql = MysqlUtils(host=MysqlConfig.host, port=MysqlConfig.port,
                  user=MysqlConfig.user, password=MysqlConfig.password,
                  database=MysqlConfig.database, charset=MysqlConfig.charset)

# 简单的爬虫线程管理
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


@app.route('/api/task', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'keyword' not in data:
        return jsonify({"error": "keyword required"}), 400
    redis.rpush('wanfang:producer_tasks', json.dumps(data))
    return jsonify({"ok": True})


@app.route('/api/logs')
def get_logs():
    page = int(request.args.get('page', 1))
    per = int(request.args.get('per', 20))
    offset = (page - 1) * per
    rows = mysql.select('spider_logs', '*', order_by='created_at DESC', limit=per, offset=offset)
    return jsonify(rows)


@app.route('/api/status')
def status():
    return jsonify({
        "producer_tasks": redis.llen('wanfang:producer_tasks'),
        "task_queue": redis.llen('wanfang:task_queue'),
        "producers_running": len(producers),
        "consumers_running": len(consumers)
    })


@app.route('/api/start', methods=['POST'])
def api_start():
    content = request.get_json() or {}
    prod = content.get('producers', 1)
    cons = content.get('consumers', 1)
    started = start_crawlers(prod, cons)
    return jsonify({"started": started})


@app.route('/api/stop', methods=['POST'])
def api_stop():
    stop_crawlers()
    return jsonify({"stopped": True})


if __name__ == '__main__':
    # 在启动服务时不自动启动爬虫线程，需手动调用 /api/start
    app.run(debug=True, host='0.0.0.0', port=5000)
