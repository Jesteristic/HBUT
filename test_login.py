#!/usr/bin/env python
"""
测试登录功能
"""
import requests
import time

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


def test_failed_logins():
    """测试登录失败计数"""
    print("Testing failed login attempts...")

    # 多次失败登录
    for i in range(6):
        print(f"Attempt {i + 1}:")
        test_login('testuser', 'wrongpass')
        time.sleep(1)

    # 第6次应该被限制
    print("Attempt 6 (should be blocked):")
    test_login('testuser', 'wrongpass')

    # 等待5分钟后重试
    print("Waiting 5 minutes for cooldown...")
    time.sleep(310)

    print("Attempt after cooldown:")
    test_login('testuser', 'wrongpass')


if __name__ == '__main__':
    # 测试正常登录
    print("Testing normal login...")
    test_login('admin', 'admin', 'admin')

    # 测试记住我功能
    print("\nTesting remember me...")
    test_login('admin', 'admin', 'admin', remember=True)

    # 测试失败计数
    print("\nTesting failed login protection...")
    test_failed_logins()
