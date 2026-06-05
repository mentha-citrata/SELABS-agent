#!/usr/bin/env python3
"""
SELABS 后端诊断工具
用于发现公开接口和调试认证问题
"""

import subprocess
import json
import os

from dotenv import load_dotenv

BASE_URL = "http://localhost:8080"

load_dotenv()

TEST_USER_NUMBER = os.getenv("TEST_USER_NUMBER")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")


def test_endpoint(method, path, headers=None, data=None):
    """使用curl测试一个端点"""
    cmd = ["curl", "-s", "-w", "\n%{http_code}", "-X", method, f"{BASE_URL}{path}"]
    
    if headers:
        for key, value in headers.items():
            cmd.extend(["-H", f"{key}: {value}"])
    
    if data:
        cmd.extend(["-H", "Content-Type: application/json", "-d", json.dumps(data)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        output = result.stdout
        lines = output.strip().split('\n')
        http_code = lines[-1] if lines else "000"
        body = '\n'.join(lines[:-1]) if len(lines) > 1 else ""
        return int(http_code), body
    except Exception as e:
        return None, str(e)


print("\n" + "="*60)
print("SELABS 后端诊断 - 寻找公开接口")
print("="*60)

public_endpoints = [
    ("GET", "/", "根路径"),
    ("GET", "/health", "健康检查"),
    ("GET", "/v1/statistics/workstation/get-all-workstations-count", "工位统计"),
    ("GET", "/v1/statistics/consumable/get-consumables", "耗材统计"),
    ("GET", "/v1/statistics/equipment-borrowing/get-equipment-borrowed-count", "设备统计"),
    ("OPTIONS", "/v1/user/login", "登录选项"),
]

print("\n测试公开接口...")
for method, path, description in public_endpoints:
    code, body = test_endpoint(method, path)
    if code:
        print(f"\n{description}")
        print(f"  {method} {path}")
        print(f"  状态码: {code}")
        if code == 200:
            print(f"  ✅ 可访问")
            try:
                data = json.loads(body)
                print(f"  响应: {json.dumps(data, ensure_ascii=False)[:100]}...")
            except:
                print(f"  响应长度: {len(body)} bytes")
        elif code in [401, 403]:
            print(f"  ❌ 需要认证 ({code})")
        elif code >= 500:
            print(f"  ❌ 服务器错误 ({code})")
        else:
            print(f"  ⚠️ 其他状态 ({code})")
    else:
        print(f"\n{description}")
        print(f"  {method} {path}")
        print(f"  ❌ 连接失败: {body}")

print("\n" + "="*60)
print("尝试默认账户登录")
print("="*60)

default_accounts = [
    ("admin", "admin"),
    ("admin", "123456"),
    ("admin", "password"),
    ("test", "test"),
    ("guest", "guest"),
]

for username, password in default_accounts:
    url = f"/v1/user/login?userNumber={username}&password={password}"
    code, body = test_endpoint("GET", url)
    print(f"\n尝试: {username}/{password}")
    print(f"  状态码: {code}")
    
    if code == 200:
        try:
            data = json.loads(body)
            if data.get("code") == 0:
                print(f"  ✅ 登录成功！")
                print(f"  用户信息: {json.dumps(data.get('data', {}), ensure_ascii=False)}")
                break
            else:
                print(f"  ❌ 响应: {data.get('msg', 'Unknown error')}")
        except:
            print(f"  ⚠️ 无法解析响应")
    elif code == 500:
        print(f"  ❌ 服务器错误 (500)")
    else:
        print(f"  ⚠️ 状态码: {code}")

print("\n" + "="*60)
print("尝试 .env 中的测试凭证")
print("="*60)

masked_user = f"{TEST_USER_NUMBER[:4]}***{TEST_USER_NUMBER[-2:]}" if TEST_USER_NUMBER and len(TEST_USER_NUMBER) >= 6 else "***"
if not TEST_USER_NUMBER or not TEST_PASSWORD:
    print("  ⚠️ .env 中未配置 TEST_USER_NUMBER 或 TEST_PASSWORD")
else:
    code, body = test_endpoint("GET", f"/v1/user/login?userNumber={TEST_USER_NUMBER}&password={TEST_PASSWORD}")
    print(f"\n尝试: {masked_user}")
    print(f"  状态码: {code}")
    if code == 200:
        try:
            data = json.loads(body)
            if data.get("code") == 0:
                print(f"  ✅ 登录成功！")
                print(f"  用户信息: {json.dumps(data.get('data', {}), ensure_ascii=False)}")
            else:
                print(f"  ❌ 响应: {data.get('msg', 'Unknown error')}")
        except:
            print(f"  ⚠️ 无法解析响应")
    else:
        print(f"  ⚠️ 状态码: {code}")

print("\n" + "="*60)
print("诊断完成")
print("="*60)
print("\n建议:")
print("1. 如果所有登录都失败，检查数据库是否有用户数据")
print("2. 可以尝试在后端创建测试用户")
print("3. 或者在SecurityConfig中添加公开接口白名单")
print("4. 查看后端日志了解具体错误信息")
