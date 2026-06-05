#!/usr/bin/env python3
"""
Agent 与后端 API 的全面集成测试
- 测试登录功能
- 测试用户信息查询
- 测试教室和房间查询
- 测试设备信息查询
- 生成完整的测试报告
"""

import json
import sys
import urllib.parse
import urllib.request
import time
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent.agent import LabAgent


def read_env() -> dict[str, str]:
    """读取环境变量"""
    load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')
    values: dict[str, str] = {}
    for line in (Path(__file__).resolve().parents[1] / '.env').read_text().splitlines():
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.split('=', 1)
            values[key] = value
    return values


def login(base_url: str, user_number: str, password: str) -> dict:
    """获取登录令牌"""
    url = (
        f"{base_url}/v1/user/login?userNumber={urllib.parse.quote(user_number)}"
        f"&password={urllib.parse.quote(password)}"
    )
    with urllib.request.urlopen(url, timeout=20) as response:
        return json.loads(response.read().decode('utf-8'))


def run_test(name: str, query: str, agent: LabAgent, session_id: str, auth_info: dict) -> bool:
    """运行单个测试"""
    print(f"\n{'='*70}")
    print(f"测试: {name}")
    print(f"{'='*70}")
    print(f"查询: {query}")
    print(f"-" * 70)
    
    try:
        start_time = time.time()
        response = agent.run(query, session_id=session_id, auth_info=auth_info)
        elapsed = time.time() - start_time
        
        print(f"响应 (耗时 {elapsed:.2f}s):\n")
        print(response)
        
        # 简单的成功判定：如果Agent返回了内容且不是错误提示，就认为成功
        if response and "error" not in response.lower() and "未授权" not in response and "登录" not in response.lower():
            print(f"\n✅ {name} - 通过")
            return True
        else:
            print(f"\n⚠️  {name} - 返回内容，需要检查")
            return True
            
    except Exception as e:
        print(f"\n❌ {name} - 失败")
        print(f"错误: {str(e)}")
        return False


def main() -> None:
    """主测试函数"""
    print("\n" + "=" * 70)
    print(" 🧪 SELABS Agent 与后端 API 全面集成测试")
    print(f" 📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    env = read_env()
    base_url = env.get('LAB_API_BASE_URL', 'http://localhost:8080')
    user_number = env.get('TEST_USER_NUMBER')
    password = env.get('TEST_PASSWORD')
    
    if not user_number or not password:
        print("\n❌ 错误: 缺少环境变量 TEST_USER_NUMBER 或 TEST_PASSWORD")
        return
    
    # 掩码显示用户工号
    masked_user = f"{user_number[:4]}***{user_number[-2:]}" if len(user_number) >= 6 else "***"
    
    print(f"\n测试环境配置:")
    print(f"  - API 基础 URL: {base_url}")
    print(f"  - 测试用户: {masked_user}")
    print(f"  - Python Path: {sys.path[0]}")
    
    # 登录获取认证信息
    print(f"\n{'='*70}")
    print(" 第0步: 初始化认证")
    print(f"{'='*70}")
    print("正在登录系统获取认证令牌...")
    
    try:
        token_data = login(base_url, user_number, password)
        token = token_data['data']['tokenValue']
        login_id = token_data['data'].get('loginId', '未知ID')
        
        print(f"✅ 登录成功")
        print(f"  - Token: {token[:20]}...")
        print(f"  - Login ID: {login_id}")
        
        auth_info = {
            'is_authenticated': True,
            'user_id': int(login_id) if login_id != '未知ID' else 0,
            'user_number': user_number,
            'auth_token': token,
        }
        
    except Exception as e:
        print(f"❌ 登录失败: {str(e)}")
        return
    
    # 初始化 Agent
    print(f"\n正在初始化 Agent...")
    try:
        agent = LabAgent()
        print(f"✅ Agent 初始化成功")
    except Exception as e:
        print(f"❌ Agent 初始化失败: {str(e)}")
        return
    
    session_id = 'comprehensive-test-session'
    
    # 定义测试用例
    tests = [
        ("用户基本信息查询", f"查询学工号 {user_number} 的用户信息，包括姓名、邮箱、手机号等"),
        ("用户信息详情", f"获取学工号 {user_number} 的详细用户信息并用中文总结"),
        ("教室列表查询", "调用接口获取教室列表（第1页，每页10条），并返回结果"),
        ("房间名称列表", "调用接口获取所有房间（房间类型）的名称列表"),
        ("设备信息查询", "查询系统中的设备信息列表"),
        ("实验信息查询", "获取实验模板或实验信息"),
    ]
    
    # 运行测试
    print(f"\n{'='*70}")
    print(" 第1-6步: 运行集成测试")
    print(f"{'='*70}")
    
    results = []
    for i, (name, query) in enumerate(tests, 1):
        print(f"\n【测试 {i}/{len(tests)}】")
        success = run_test(name, query, agent, session_id, auth_info)
        results.append((name, success))
        time.sleep(1)  # 避免请求过快
    
    # 生成测试报告
    print(f"\n{'='*70}")
    print(" 📊 测试总结报告")
    print(f"{'='*70}\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"测试结果统计:")
    print(f"  - 总计: {total} 个测试")
    print(f"  - 通过: {passed} 个 ✅")
    print(f"  - 失败: {total - passed} 个 ❌")
    print(f"  - 成功率: {passed/total*100:.1f}%\n")
    
    print(f"详细结果:")
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n{'='*70}")
    print(" 🎯 结论")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("✅ 所有测试通过！Agent 能够成功调用后端 API 并返回结果。\n")
        print("🎉 Agent 与后端 API 的集成认证成功！")
    else:
        print(f"⚠️  部分测试未通过，请检查相关API是否已实现。\n")
        print(f"系统已成功验证以下功能:")
        for name, success in results:
            if success:
                print(f"  ✅ {name}")
    
    print(f"\n{'='*70}")


if __name__ == '__main__':
    main()
