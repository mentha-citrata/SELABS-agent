"""
验证脚本 - 检查项目结构和导入的正确性
不需要 DeepSeek API Key，只验证代码结构
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_imports():
    """检查所有必要的导入"""
    print("=" * 60)
    print("检查项目导入...")
    print("=" * 60)
    
    checks = [
        ("config.api_config", "API 配置", ["APIConfig"]),
        ("tools.tool_definitions", "工具定义", ["query_devices", "create_experiment", "TOOLS"]),
        ("agent.state", "Agent 状态", ["AgentState"]),
        ("utils.error_handler", "错误处理", ["handle_api_error", "handle_llm_error"]),
    ]
    
    all_passed = True
    
    for module_name, description, expected_items in checks:
        try:
            module = __import__(module_name, fromlist=expected_items)
            
            # 检查模块中的期望项
            missing = []
            for item in expected_items:
                if not hasattr(module, item):
                    missing.append(item)
            
            if missing:
                print(f"✗ {description} ({module_name})")
                print(f"  缺失项: {', '.join(missing)}")
                all_passed = False
            else:
                print(f"✓ {description} ({module_name})")
                
        except ImportError as e:
            print(f"✗ {description} ({module_name})")
            print(f"  导入错误: {e}")
            all_passed = False
        except Exception as e:
            print(f"✗ {description} ({module_name})")
            print(f"  错误: {e}")
            all_passed = False
    
    print()
    return all_passed


def check_file_structure():
    """检查文件结构"""
    print("=" * 60)
    print("检查文件结构...")
    print("=" * 60)
    
    required_files = [
        "requirements.txt",
        ".env.example",
        "README.md",
        "config/__init__.py",
        "config/llm_config.py",
        "config/api_config.py",
        "tools/__init__.py",
        "tools/tool_definitions.py",
        "agent/__init__.py",
        "agent/state.py",
        "agent/agent.py",
        "utils/__init__.py",
        "utils/error_handler.py",
        "main.py",
    ]
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    all_exist = True
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"✓ {file_path} ({file_size} bytes)")
        else:
            print(f"✗ {file_path} - 文件不存在")
            all_exist = False
    
    print()
    return all_exist


def check_tools():
    """检查工具定义"""
    print("=" * 60)
    print("检查工具定义...")
    print("=" * 60)
    
    try:
        from tools.tool_definitions import TOOLS
        
        print(f"✓ 工具总数: {len(TOOLS)}")
        
        for i, tool in enumerate(TOOLS, 1):
            tool_name = getattr(tool, "name", "未知")
            tool_desc = getattr(tool, "description", "")
            print(f"  {i}. {tool_name}")
            if tool_desc:
                # 只显示前 50 个字符
                desc_preview = tool_desc[:50] + "..." if len(tool_desc) > 50 else tool_desc
                print(f"     {desc_preview}")
        
        print()
        return True
        
    except Exception as e:
        print(f"✗ 工具检查失败: {e}")
        print()
        return False


def main():
    """运行所有检查"""
    print("\n")
    print("🔍 SELABS Agent 项目验证\n")
    
    results = []
    
    # 运行所有检查
    results.append(("文件结构", check_file_structure()))
    results.append(("导入检查", check_imports()))
    results.append(("工具检查", check_tools()))
    
    # 总结
    print("=" * 60)
    print("验证总结")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 所有检查通过！项目结构正确。\n")
        print("后续步骤:")
        print("  1. 复制 .env.example 为 .env")
        print("  2. 在 .env 中填入 DEEPSEEK_API_KEY")
        print("  3. 安装依赖: pip install -r requirements.txt")
        print("  4. 运行 Agent: python main.py\n")
        return 0
    else:
        print("⚠️  某些检查失败，请修复上述问题。\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
