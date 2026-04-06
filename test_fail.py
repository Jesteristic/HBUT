#!/usr/bin/env python
"""
测试登录失败计数
"""
import requests
import time

base_url = 'http://localhost:5000'


def test_failed_login():
    """测试失败登录"""
    response = requests.post(f'{base_url}/api/login', json={
        'username': 'nonexistent',
        'password': 'wrongpass',
        'loginType': 'user'
    })
    try:
        result = response.json()
        print(f"Failed login -> {response.status_code}: {result}")
    except:
        print(f"Failed login -> {response.status_code}: {response.text}")
    return response


if __name__ == '__main__':
    print("Testing failed login...")
    test_failed_login()
