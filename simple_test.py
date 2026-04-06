#!/usr/bin/env python
"""
简单测试登录功能
"""
import requests

# 测试登录API
base_url = 'http://localhost:5000'


def test_login(username, password, login_type='user', remember=False):
    """测试登录"""
    data = {
        'username': username,
        'password': password,
        'loginType': login_type,
        'remember': remember
    }
    response = requests.post(f'{base_url}/api/login', json=data)
    try:
        result = response.json()
        print(f"Login attempt: {username}/{password} -> {response.status_code}: {result}")
    except:
        print(f"Login attempt: {username}/{password} -> {response.status_code}: {response.text}")
    return response


if __name__ == '__main__':
    # 测试正常登录
    print("Testing normal login...")
    test_login('admin', 'admin', 'admin')
