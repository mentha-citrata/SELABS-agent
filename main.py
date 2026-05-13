"""
主程序入口 - 启动实验室管理 Agent
支持多轮对话的交互式命令行界面
"""

import sys
from agent.agent import LabAgent


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "="*60)
    print("欢迎使用实验室管理助手 Agent")
    print("="*60)
    print("\n功能说明:")
    print("  • 查询设备、实验、预约等信息")
    print("  • 创建和修改实验、预约等")
    print("  • 支持自然语言交互")
    print("\n输入说明:")
    print("  • 输入 'quit' 或 'exit' 退出")
    print("  • 输入 'clear' 清空对话历史")
    print("  • 输入 'help' 获取帮助信息")
    print("\n" + "="*60 + "\n")


def print_help():
    """打印帮助信息"""
    print("\n帮助信息:")
    print("-" * 60)
    print("支持的操作示例:")
    print("  • '查询所有设备' - 查询实验室设备")
    print("  • '查看正在进行的实验' - 查看当前实验状态")
    print("  • '预约显微镜明天上午10点' - 预约设备")
    print("  • '创建一个新实验' - 创建新实验")
    print("-" * 60 + "\n")


def run_interactive_mode():
    """运行交互式对话模式"""
    try:
        # 初始化 Agent
        print("正在初始化 Agent...")
        agent = LabAgent()
        print("✓ Agent 初始化成功\n")
        
    except ValueError as e:
        print(f"✗ 配置错误: {e}")
        print("请检查 .env 文件中的配置，特别是 DEEPSEEK_API_KEY")
        return
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return
    
    print_welcome()
    
    conversation_history = []
    
    while True:
        try:
            # 获取用户输入
            user_input = input("你: ").strip()
            
            if not user_input:
                continue
            
            # 处理特殊命令
            if user_input.lower() in ["quit", "exit"]:
                print("\n再见! 👋")
                break
            
            if user_input.lower() == "clear":
                conversation_history = []
                print("✓ 对话历史已清空\n")
                continue
            
            if user_input.lower() == "help":
                print_help()
                continue
            
            # 添加用户消息到历史
            conversation_history.append(user_input)
            
            print("\nAgent 正在处理...", end=" ", flush=True)
            
            # 调用 Agent
            try:
                if len(conversation_history) == 1:
                    # 单轮对话
                    response = agent.run(user_input)
                else:
                    # 多轮对话
                    response = agent.run_with_history(conversation_history)
                
                # 添加 Agent 响应到历史
                conversation_history.append(response)
                
                print(f"\n\nAgent: {response}\n")
                
            except Exception as e:
                print(f"\n✗ 处理请求失败: {e}\n")
        
        except KeyboardInterrupt:
            print("\n\n用户中断 (Ctrl+C)，退出...")
            break
        except Exception as e:
            print(f"\n✗ 发生错误: {e}\n")


def run_single_query(query: str) -> str:
    """运行单个查询
    
    Args:
        query: 用户查询
        
    Returns:
        str: Agent 响应
    """
    try:
        agent = LabAgent()
        response = agent.run(query)
        return response
    except Exception as e:
        return f"错误: {e}"


def main():
    """主程序入口"""
    if len(sys.argv) > 1:
        # 命令行参数模式
        query = " ".join(sys.argv[1:])
        response = run_single_query(query)
        print(response)
    else:
        # 交互式模式
        run_interactive_mode()


if __name__ == "__main__":
    main()
