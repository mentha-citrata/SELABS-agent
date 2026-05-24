"""会话认证测试 - 测试登录工具和会话上下文管理"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Any

# 项目路径（指向项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_session_context_management():
    """测试会话上下文（contextvars）管理"""
    print("\n" + "="*60)
    print("会话认证测试 1: 会话上下文管理")
    print("="*60)
    
    try:
        from src.tools.tool_definitions import (
            set_session_context,
            get_session_context,
            _get_session_auth_info
        )
        
        # 测试1: 设置和获取会话上下文
        session_id = "test-session-123"
        auth_info = {
            "is_authenticated": True,
            "user_id": 1,
            "user_number": "2024001",
            "auth_token": "test-token-abc"
        }
        
        set_session_context(session_id, auth_info)
        context = get_session_context()
        
        assert context["session_id"] == session_id, f"期望 session_id={session_id}，实际={context.get('session_id')}"
        assert context["auth_info"]["is_authenticated"] == True, "期望 is_authenticated=True"
        assert context["auth_info"]["auth_token"] == "test-token-abc", "期望正确的 auth_token"
        print("✓ 会话上下文设置和获取成功")
        
        # 测试2: 获取认证信息
        auth = _get_session_auth_info()
        assert auth["auth_token"] == "test-token-abc", "期望从 auth_info 获取 auth_token"
        print("✓ 认证信息获取成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 会话上下文管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_login_tool_response_parsing():
    """测试登录工具对异常响应的处理"""
    print("\n" + "="*60)
    print("会话认证测试 2: 登录工具响应处理")
    print("="*60)
    
    try:
        from src.tools.tool_definitions import login_user
        from unittest.mock import patch
        
        # Mock _post_json 来模拟登录成功的响应
        with patch('src.tools.tool_definitions._post_json') as mock_post:
            # 模拟成功登录响应
            mock_post.return_value = {
                "status": "success",
                "message": "请求成功",
                "response": {
                    "code": 0,
                    "data": {
                        "id": 123,
                        "userNumber": "2024001",
                        "name": "Test User",
                        "token": "Bearer-token-xyz",
                    }
                }
            }
            
            # login_user 是 StructuredTool，通过 invoke 调用
            result = login_user.invoke({"user_number": "2024001", "password": "password123"})
            
            assert result.get("status") == "success", "期望登录成功状态"
            assert result.get("authenticated") == True, "期望 authenticated=True"
            assert result.get("user_info", {}).get("user_id") == 123, "期望正确的 user_id"
            assert result.get("user_info", {}).get("user_number") == "2024001", "期望正确的 user_number"
            print("✓ 成功登录响应处理成功")
        
        # Mock _post_json 来模拟登录失败的响应
        with patch('src.tools.tool_definitions._post_json') as mock_post:
            mock_post.return_value = {
                "status": "error",
                "message": "用户名或密码错误",
                "response": {
                    "code": 400,
                    "msg": "用户名或密码错误"
                }
            }
            
            result = login_user.invoke({"user_number": "2024001", "password": "wrongpassword"})
            
            assert result.get("status") == "error", "期望登录失败状态"
            assert result.get("authenticated") != True, "期望登录失败不设置认证"
            print("✓ 失败登录响应处理成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 登录工具响应处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_with_session():
    """测试 Agent 接收和使用会话信息"""
    print("\n" + "="*60)
    print("会话认证测试 3: Agent 会话集成")
    print("="*60)
    
    try:
        # 设置环境变量
        os.environ['DEEPSEEK_API_KEY'] = 'test-key'
        
        from src.agent.agent import LabAgent
        from src.agent.state import AgentState
        
        # 模拟 LLM
        mock_llm = MagicMock()
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)
        
        # 模拟 LLM 响应（只回复，不调用工具）
        from langchain_core.messages import AIMessage
        mock_response = AIMessage(content="你好，我已准备就绪")
        mock_llm.invoke = MagicMock(return_value=mock_response)
        
        with patch('src.agent.agent.get_llm', return_value=mock_llm):
            agent = LabAgent()
            
            # 测试1: 无会话信息运行
            response = agent.run("hello")
            assert isinstance(response, str), "期望返回字符串响应"
            print("✓ Agent 无会话运行成功")
            
            # 测试2: 带会话信息运行
            session_id = "test-session-456"
            auth_info = {
                "is_authenticated": True,
                "user_id": 42,
                "user_number": "2024001",
                "auth_token": "test-token-xyz"
            }
            
            response = agent.run("hello", session_id=session_id, auth_info=auth_info)
            assert isinstance(response, str), "期望返回字符串响应"
            print("✓ Agent 带会话运行成功")
            
            # 测试3: 流式运行
            chunks = list(agent.run_stream(
                "hello",
                session_id=session_id,
                auth_info=auth_info,
                chunk_size=5
            ))
            assert len(chunks) > 0, "期望获得响应数据块"
            print(f"✓ Agent 流式运行成功（{len(chunks)} 块数据）")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent 会话集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'DEEPSEEK_API_KEY' in os.environ:
            del os.environ['DEEPSEEK_API_KEY']


def test_request_headers_with_auth():
    """测试认证令牌在请求头中的正确传递"""
    print("\n" + "="*60)
    print("会话认证测试 4: 请求头认证传递")
    print("="*60)
    
    try:
        from src.tools.tool_definitions import (
            set_session_context,
            _get_session_auth_info,
            _request_json
        )
        from unittest.mock import patch
        
        # 设置会话认证信息
        session_id = "test-session-789"
        auth_info = {
            "is_authenticated": True,
            "user_id": 99,
            "user_number": "2024099",
            "auth_token": "Bearer-special-token-789"
        }
        set_session_context(session_id, auth_info)
        
        # Mock urlopen 来捕获请求头
        with patch('src.tools.tool_definitions.urlopen') as mock_urlopen:
            # 设置模拟响应
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"code": 0, "msg": "success", "data": {}}'
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response
            
            # 执行请求
            result = _request_json("GET", "/v1/reservation/get-seats", params={"roomName": "Lab1"})
            
            # 验证结果
            assert result.get("status") == "success", "期望成功状态"
            
            # 验证请求头包含认证信息
            call_args = mock_urlopen.call_args
            request_obj = call_args[0][0]  # 第一个位置参数是 Request 对象
            
            auth_header = request_obj.headers.get('Authorization')
            assert auth_header == "Bearer Bearer-special-token-789", f"期望正确的 Authorization 头，实际={auth_header}"
            print("✓ 认证令牌正确传递到请求头")
        
        return True
        
    except Exception as e:
        print(f"✗ 请求头认证传递测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有认证测试"""
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║         会话认证功能集成测试套件                               ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    tests = [
        test_session_context_management,
        test_login_tool_response_parsing,
        test_agent_with_session,
        test_request_headers_with_auth,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "="*60)
    print(f"测试结果: {sum(results)}/{len(results)} 通过")
    print("="*60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
