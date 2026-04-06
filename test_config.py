#!/usr/bin/env python
"""
测试配置API
"""
import requests

base_url = 'http://localhost:5000'


def test_config_api():
    """测试配置API"""
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

    # 测试获取配置
    config_resp = session.get(f'{base_url}/api/config')
    print(
        f"Get config -> {config_resp.status_code}: {config_resp.json() if config_resp.status_code == 200 else config_resp.text}")

    # 测试更新配置
    update_data = {
        'max_pages': 15,
        'page_size': 25,
        'timeout': 45,
        'retry_times': 5
    }
    update_resp = session.post(f'{base_url}/api/config', json=update_data)
    print(
        f"Update config -> {update_resp.status_code}: {update_resp.json() if update_resp.status_code == 200 else update_resp.text}")

    # 再次获取配置验证更新
    config_resp2 = session.get(f'{base_url}/api/config')
    print(
        f"Get config after update -> {config_resp2.status_code}: {config_resp2.json() if config_resp2.status_code == 200 else config_resp2.text}")


if __name__ == '__main__':
    test_config_api()
