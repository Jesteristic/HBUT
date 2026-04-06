#!/usr/bin/env python
"""
测试修复后的登录和状态检查
"""
import requests

base_url = 'http://localhost:5000'


def test_status_without_auth():
    """测试未登录时的状态检查"""
    response = requests.get(f'{base_url}/api/status')
    print(f"Status without auth -> {response.status_code}: {response.text}")
    return response


def test_login():
    """测试登录"""
    data = {
        'username': 'admin',
        'password': 'admin',
        'loginType': 'admin'
    }
    response = requests.post(f'{base_url}/api/login', json=data)
    try:
        result = response.json()
        print(f"Login -> {response.status_code}: {result}")
    except:
        print(f"Login -> {response.status_code}: {response.text}")
    return response


def test_status_with_session():
    """测试登录后的状态检查"""
    # 使用session保持cookies
    session = requests.Session()

    # 先登录
    login_data = {
        'username': 'admin',
        'password': 'admin',
        'loginType': 'admin'
    }
    login_resp = session.post(f'{base_url}/api/login', json=login_data)
    print(
        f"Login with session -> {login_resp.status_code}: {login_resp.json() if login_resp.status_code == 200 else login_resp.text}")

    # 然后检查状态
    status_resp = session.get(f'{base_url}/api/status')
    print(
        f"Status with session -> {status_resp.status_code}: {status_resp.json() if status_resp.status_code == 200 else status_resp.text}")

    return status_resp


if __name__ == '__main__':
    print("Testing status without authentication...")
    test_status_without_auth()

    print("\nTesting login...")
    test_login()

    print("\nTesting status with session...")
    test_status_with_session()
