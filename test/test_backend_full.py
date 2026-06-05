#!/usr/bin/env python3
"""
SELABS 后端接口完整测试 - 使用有效凭证
"""

import asyncio
import aiohttp
import json
import os
import time
from typing import Optional

from dotenv import load_dotenv

BASE_URL = "http://localhost:8080"
TIMEOUT = aiohttp.ClientTimeout(total=30, connect=10)

load_dotenv()

TEST_USER_NUMBER = os.getenv("TEST_USER_NUMBER")
TEST_PASSWORD = os.getenv("TEST_PASSWORD")


class FullAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.auth_token = None
        self.user_info = None
    
    async def login(self) -> bool:
        """登录获取token"""
        print("\n" + "="*60)
        print("第1步: 用户登录")
        print("="*60)

        if not TEST_USER_NUMBER or not TEST_PASSWORD:
            print("❌ 缺少测试凭证，请先在 .env 中设置 TEST_USER_NUMBER 和 TEST_PASSWORD")
            return False

        masked_user = f"{TEST_USER_NUMBER[:4]}***{TEST_USER_NUMBER[-2:]}" if len(TEST_USER_NUMBER) >= 6 else "***"
        print(f"登录用户: {masked_user}")
        
        try:
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                url = f"{self.base_url}/v1/user/login"
                params = {"userNumber": TEST_USER_NUMBER, "password": TEST_PASSWORD}
                
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
                    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    if data.get("code") == 0 and data.get("data"):
                        self.auth_token = data["data"].get("tokenValue") or data["data"].get("token")
                        self.user_info = data["data"]
                        print(f"\n✅ 登录成功!")
                        print(f"Token: {self.auth_token[:30]}...")
                        return True
                    else:
                        print(f"❌ 登录失败: {data.get('msg')}")
                        return False
        except Exception as e:
            print(f"❌ 错误: {e}")
            return False
    
    async def test_api(self, method: str, path: str, description: str) -> tuple[bool, dict]:
        """测试单个API接口"""
        print(f"\n  {description}")
        print(f"  {method} {path}")
        
        try:
            headers = {"satoken": self.auth_token}
            
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                url = f"{self.base_url}{path}"
                
                if method == "GET":
                    async with session.get(url, headers=headers) as resp:
                        data = await resp.json()
                elif method == "POST":
                    async with session.post(url, headers=headers, json={}) as resp:
                        data = await resp.json()
                else:
                    return False, {}
                
                code = data.get("code")
                msg = data.get("msg")
                
                if code == 0:
                    print(f"  ✅ 成功 (code=0)")
                    return True, data
                elif code == 100004:
                    print(f"  ⚠️ 权限不足: {msg}")
                    return False, data
                elif code == 100003:
                    print(f"  ❌ 未认证: {msg}")
                    return False, data
                else:
                    print(f"  ⚠️ 响应码 {code}: {msg}")
                    return False, data
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            return False, {}
    
    async def run_full_test(self):
        """运行完整测试"""
        print("\n" + "🔍 " * 20)
        print("SELABS 后端接口完整测试")
        print("🔍 " * 20)
        print(f"基础URL: {self.base_url}")
        print(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not await self.login():
            print("\n❌ 测试中止: 登录失败")
            return
        
        print("\n" + "="*60)
        print("第2步: 测试Core API接口")
        print("="*60)
        
        api_tests = [
            ("GET", f"/v1/user/info/user-number/{TEST_USER_NUMBER}", "获取用户信息"),
            ("GET", "/v1/user/search-user?query=lyh", "搜索用户"),
            ("GET", "/v1/classroom/get-classroom-list?pageNo=1&pageSize=10", "获取教室列表"),
            ("GET", "/v1/classroom/get-classroom-count", "获取教室数量"),
            ("GET", "/v1/classroom-reservation/get-room-list", "获取预约房间列表"),
            ("GET", "/v1/reservation/get-room-names", "获取机位房间名称"),
            ("GET", "/v1/config/equipment/get-equipments?pageNo=1&pageSize=5", "获取设备列表 (可能无权限)"),
            ("GET", "/v1/equipment-borrowing/unreturned?pageNo=1&pageSize=10&userId=1", "获取未归还设备 (可能无权限)"),
            ("GET", "/v1/repair/record/count", "获取报修记录数 (可能无权限)"),
            ("GET", "/v1/consumable/get-user-pending-requests?userId=1", "获取待处理领用申请 (可能无权限)"),
            ("GET", "/v1/statistics/workstation/get-all-workstations-count", "获取工位总数"),
            ("GET", "/v1/statistics/reservation/get-all-available-seat-count", "获取可预约机位数"),
        ]
        
        success_count = 0
        total_count = len(api_tests)
        
        for method, path, description in api_tests:
            success, result = await self.test_api(method, path, description)
            if success:
                success_count += 1
        
        print("\n" + "="*60)
        print("第3步: 测试Agent接口")
        print("="*60)
        
        agent_success = await self.test_agent_api()
        
        print("\n" + "="*60)
        print("🎯 测试汇总报告")
        print("="*60)
        print(f"\n✅ 登录状态: 成功")
        print(f"✅ 用户: {self.user_info.get('loginId')} (token有效期: {self.user_info.get('tokenTimeout')} 秒)")
        print(f"\n✅ Core API 接口测试:")
        print(f"   总数: {total_count}")
        print(f"   成功: {success_count}")
        print(f"   成功率: {success_count*100/total_count:.1f}%")
        print(f"\n✅ Agent API: {'可用' if agent_success else '需要认证'}")
        
        if success_count >= total_count * 0.8:
            print("\n🎉 后端接口工作正常！")
            print("\n后端信息总结:")
            print("  ✅ 认证系统: 正常")
            print("  ✅ Core API: 正常")
            print(f"  ✅ 权限系统: 部分接口受权限限制 (预期行为)")
        else:
            print("\n⚠️ 部分接口可能存在问题")
    
    async def test_agent_api(self) -> bool:
        """测试Agent消息接口"""
        print("\n  创建Agent会话")
        print("  POST /api/agent/session")
        
        try:
            headers = {"satoken": self.auth_token}
            
            async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
                url = f"{self.base_url}/api/agent/session"
                
                async with session.post(url, headers=headers) as resp:
                    print(f"  状态码: {resp.status}")
                    
                    if resp.status in [200, 202]:
                        data = await resp.json()
                        if "session_id" in data or data.get("code") == 0:
                            print(f"  ✅ 会话创建成功")
                            return True
                    else:
                        print(f"  ⚠️ 状态码: {resp.status}")
                        return False
        except Exception as e:
            print(f"  ⚠️ 错误: {e}")
            return False
        
        return False

async def main():
    tester = FullAPITester()
    await tester.run_full_test()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ 测试被中断")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
