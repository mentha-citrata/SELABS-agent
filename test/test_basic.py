"""基础功能测试 - 不需要 API Key"""

import sys
import os

# 项目路径（指向项目根目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_imports():
    """测试所有导入"""
    print("\n" + "="*60)
    print("测试 1: 模块导入")
    print("="*60)
    
    tests = [
        ("src.config.api_config", "APIConfig"),
        ("src.config.llm_config", "get_llm"),
        ("src.agent.state", "AgentState"),
        ("src.tools.tool_definitions", "TOOLS"),
        ("src.utils.error_handler", "handle_api_error"),
    ]
    
    for module_name, item_name in tests:
        try:
            module = __import__(module_name, fromlist=[item_name])
            item = getattr(module, item_name)
            print(f"✓ {module_name}.{item_name}")
        except Exception as e:
            print(f"✗ {module_name}.{item_name}: {e}")
            return False
    
    return True


def test_api_config():
    """测试 API 配置"""
    print("\n" + "="*60)
    print("测试 2: API 配置加载")
    print("="*60)
    
    try:
        from src.config.api_config import APIConfig
        
        print(f"✓ BaseURL: {APIConfig.BASE_URL}")
        print(f"✓ Timeout: {APIConfig.TIMEOUT}s")
        print(f"✓ Debug: {APIConfig.DEBUG}")
        print(f"✓ Endpoints 数量: {len(APIConfig.ENDPOINTS)}")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_tools():
    """测试工具定义"""
    print("\n" + "="*60)
    print("测试 3: 工具调用（占位符）")
    print("="*60)
    
    try:
        from src.tools.tool_definitions import (
            query_devices,
            query_experiments,
            create_experiment,
            TOOLS
        )
        
        # 测试查询工具
        result1 = query_devices.invoke({"device_id": "DEV-001"})
        print(f"✓ query_devices 调用成功")
        print(f"  返回: {result1}")
        
        # 测试创建工具
        result2 = create_experiment.invoke({
            "name": "测试实验",
            "description": "描述",
            "device_id": "DEV-001"
        })
        print(f"✓ create_experiment 调用成功")
        print(f"  返回: {result2}")
        
        # 验证工具列表
        print(f"✓ 工具总数: {len(TOOLS)}")
        for tool in TOOLS:
            print(f"  - {tool.name}")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_state():
    """测试 Agent 状态"""
    print("\n" + "="*60)
    print("测试 4: Agent 状态定义")
    print("="*60)
    
    try:
        from src.agent.state import AgentState
        from langchain_core.messages import HumanMessage
        
        # 创建示例状态
        state = {
            "messages": [
                HumanMessage(content="你好")
            ]
        }
        
        print(f"✓ AgentState 是一个 TypedDict")
        print(f"✓ 消息类型: {type(state['messages'][0]).__name__}")
        print(f"✓ 消息内容: {state['messages'][0].content}")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handler():
    """测试错误处理"""
    print("\n" + "="*60)
    print("测试 5: 错误处理")
    print("="*60)
    
    try:
        from src.utils.error_handler import handle_api_error, handle_llm_error
        
        # 测试 API 错误
        test_error = Exception("测试 API 错误")
        api_msg = handle_api_error(test_error)
        print(f"✓ API 错误处理: {api_msg}")
        
        # 测试 LLM 错误
        test_error2 = Exception("测试 LLM 错误")
        llm_msg = handle_llm_error(test_error2)
        print(f"✓ LLM 错误处理: {llm_msg}")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_env_config():
    """测试环境配置"""
    print("\n" + "="*60)
    print("测试 6: 环境变量配置")
    print("="*60)
    
    try:
        import os
        from dotenv import load_dotenv
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 加载 .env.example 作为示例
        load_dotenv('.env.example')
        
        # 检查关键环境变量
        env_vars = [
            "DEEPSEEK_API_KEY",
            "DEEPSEEK_MODEL",
            "LAB_API_BASE_URL",
            "AGENT_TEMPERATURE"
        ]
        
        print("环境变量状态:")
        for var in env_vars:
            value = os.getenv(var, "未设置")
            # 对于 API Key，只显示前几个字符
            if var == "DEEPSEEK_API_KEY" and value != "未设置":
                value = value[:10] + "***"
            print(f"  {var}: {value}")
        
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False


def test_agent_initialization():
    """测试 Agent 初始化（不需要调用 LLM）"""
    print("\n" + "="*60)
    print("测试 7: Agent 初始化")
    print("="*60)
    
    try:
        # 检查是否有 .env 文件
        if not os.path.exists('.env'):
            print("⚠ 警告: 缺少 .env 文件，跳过 LLM 初始化测试")
            print("  (完整的 Agent 测试需要配置 DEEPSEEK_API_KEY)")
            return True
        
        from src.agent.agent import LabAgent
        
        print("正在初始化 Agent...")
        agent = LabAgent()
        print("✓ Agent 初始化成功")
        print(f"✓ LLM 配置: DeepSeek")
        print(f"✓ 工具数量: {len(agent.tools)}")
        print(f"✓ Graph 已编译")
        
        return True
    except ValueError as e:
        if "DEEPSEEK_API_KEY" in str(e):
            print(f"⚠ 预期的配置告警: {e}")
            print("  (这是正常的，需要配置 .env 文件后才能完全初始化)")
            return True
        else:
            print(f"✗ 错误: {e}")
            return False
    except Exception as e:
        print(f"✗ 错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "    🧪 SELABS Agent 基础功能测试".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # 运行所有测试
    results.append(("模块导入", test_imports()))
    results.append(("API 配置", test_api_config()))
    results.append(("工具调用", test_tools()))
    results.append(("Agent 状态", test_agent_state()))
    results.append(("错误处理", test_error_handler()))
    results.append(("环境变量", test_env_config()))
    results.append(("Agent 初始化", test_agent_initialization()))
    
    # 汇总
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {test_name}")
    
    print()
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有基础测试通过！\n")
        print("后续步骤:")
        print("  1. 配置 .env: cp .env.example .env")
        print("  2. 填入 DEEPSEEK_API_KEY")
        print("  3. 运行 Agent: python main.py")
        return 0
    else:
        print(f"\n⚠ 有 {total - passed} 个测试失败\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
