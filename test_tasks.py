#!/usr/bin/env python
"""
测试任务API
"""
import requests

base_url = 'http://localhost:5000'


def test_tasks_api():
    """测试任务API"""
    session = requests.Session()

    # 先登录管理员
    login_data = {
        'username': 'admin',
        'password': 'admin',
        'loginType': 'admin'
    }
    login_resp = session.post(f'{base_url}/api/login', json=login_data)
    print(
        f"Admin login -> {login_resp.status_code}: {login_resp.json() if login_resp.status_code == 200 else login_resp.text}")

    if login_resp.status_code != 200:
        return

    # 测试获取任务
    tasks_resp = session.get(f'{base_url}/api/tasks', params={'page': 1, 'per': 20})
    print(
        f"Get tasks -> {tasks_resp.status_code}: {tasks_resp.json() if tasks_resp.status_code == 200 else tasks_resp.text}")


if __name__ == '__main__':
    test_tasks_api()
