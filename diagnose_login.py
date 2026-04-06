import requests
import time

print("🔍 详细诊断登录问题")
print("=" * 60)

base_url = 'http://localhost:5000'

# 创建一个session来保持cookie
session = requests.Session()

print("1️⃣ 检查初始认证状态...")
try:
    check_response = session.get(f'{base_url}/api/check-auth')
    print(f"   状态码: {check_response.status_code}")
    print(f"   响应: {check_response.json()}")
    print(f"   Cookies: {dict(check_response.cookies)}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n2️⃣ 尝试登录...")
try:
    login_data = {
        'username': 'admin',
        'password': 'admin',
        'loginType': 'admin'
    }
    print(f"   发送数据: {login_data}")

    login_response = session.post(f'{base_url}/api/login', json=login_data)
    print(f"   登录状态码: {login_response.status_code}")
    print(f"   登录响应: {login_response.json()}")
    print(f"   登录后Cookies: {dict(login_response.cookies)}")

    # 检查session cookie
    session_cookie = login_response.cookies.get('session')
    if session_cookie:
        print(f"   ✅ Session cookie已设置: {session_cookie[:50]}...")
    else:
        print("   ❌ Session cookie未设置")

except Exception as e:
    print(f"   ❌ 登录错误: {e}")

print("\n3️⃣ 检查登录后的认证状态...")
try:
    # 等待一下确保session生效
    time.sleep(0.5)

    check_response = session.get(f'{base_url}/api/check-auth')
    print(f"   状态码: {check_response.status_code}")
    print(f"   响应: {check_response.json()}")
    print(f"   Cookies: {dict(check_response.cookies)}")

    data = check_response.json()
    if data.get('authenticated'):
        print("   ✅ 认证成功")
    else:
        print("   ❌ 认证失败")

except Exception as e:
    print(f"   ❌ 认证检查错误: {e}")

print("\n4️⃣ 测试访问受保护资源...")
try:
    status_response = session.get(f'{base_url}/api/status')
    print(f"   状态码: {status_response.status_code}")
    if status_response.status_code == 200:
        print("   ✅ 成功访问受保护资源")
        data = status_response.json()
        print(f"   系统状态: 生产者任务 {data.get('producer_tasks', 0)}")
    else:
        print(f"   ❌ 访问失败: {status_response.json()}")

except Exception as e:
    print(f"   ❌ 访问错误: {e}")

print("\n🔧 诊断完成")
print("💡 如果仍有问题，可能的原因:")
print("   - Session配置问题")
print("   - CORS阻止了cookie传递")
print("   - 前端请求配置问题")
print("   - 后端Session存储问题")
