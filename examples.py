"""
示例脚本 - 演示如何使用 SELABS Agent

这个脚本展示了如何以程序方式调用 Agent，而不是使用交互式 CLI。
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.agent import LabAgent


def example_1_single_query():
    """示例 1: 单个查询"""
    print("\n" + "="*60)
    print("示例 1: 单个查询")
    print("="*60)
    
    try:
        agent = LabAgent()
        
        queries = [
            "查询有哪些实验设备?",
            "帮我创建一个新的实验",
            "查看今天的预约情况",
        ]
        
        for query in queries:
            print(f"\n用户: {query}")
            response = agent.run(query)
            print(f"Agent: {response}\n")
            
    except ValueError as e:
        print(f"配置错误: {e}")
        print("请检查 .env 文件中的 DEEPSEEK_API_KEY")
    except Exception as e:
        print(f"错误: {e}")


def example_2_multi_turn_conversation():
    """示例 2: 多轮对话"""
    print("\n" + "="*60)
    print("示例 2: 多轮对话（保持上下文）")
    print("="*60)
    
    try:
        agent = LabAgent()
        
        # 模拟多轮对话
        conversation = [
            "查询一下有哪些设备",
            "其中哪个是显微镜?",
            "显微镜今天下午有时间预约吗?",
        ]
        
        messages = []
        for user_input in conversation:
            print(f"\n用户: {user_input}")
            
            # 累积消息列表
            messages.append(user_input)
            
            # 调用 Agent（自动处理历史）
            response = agent.run_with_history(messages)
            print(f"Agent: {response}")
            
            # 添加 Agent 的响应到消息（用于下一轮）
            messages.append(response)
            
    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"错误: {e}")


def example_3_programmatic_use():
    """示例 3: 程序方式使用 Agent（集成到你的系统）"""
    print("\n" + "="*60)
    print("示例 3: 程序方式集成到系统")
    print("="*60)
    
    try:
        # 初始化一次，可多次使用
        agent = LabAgent()
        print("✓ Agent 初始化成功")
        
        # 假设这是来自你系统的用户请求
        user_request = {
            "user_id": "user_001",
            "query": "查询设备编号SD-001的状态",
            "timestamp": "2024-05-13 10:30:00"
        }
        
        print(f"\n处理请求: {user_request}")
        
        # 调用 Agent
        response = agent.run(user_request["query"])
        
        # 处理响应
        result = {
            "user_id": user_request["user_id"],
            "query": user_request["query"],
            "response": response,
            "timestamp": "2024-05-13 10:30:15"
        }
        
        print(f"\n响应: {result}")
        
        return result
        
    except Exception as e:
        print(f"错误: {e}")
        return None


def example_4_batch_processing():
    """示例 4: 批量处理多个查询"""
    print("\n" + "="*60)
    print("示例 4: 批量处理查询")
    print("="*60)
    
    try:
        agent = LabAgent()
        
        # 需要处理的查询列表
        queries = [
            "有多少台显微镜?",
            "实验工作台今天的预约情况如何?",
            "最新的实验报告有吗?",
        ]
        
        results = []
        for i, query in enumerate(queries, 1):
            print(f"\n处理查询 {i}/{len(queries)}: {query}")
            
            response = agent.run(query)
            results.append({
                "query": query,
                "response": response
            })
            
            print(f"✓ 完成")
        
        print(f"\n批处理完成，共处理 {len(results)} 个查询")
        
        return results
        
    except Exception as e:
        print(f"错误: {e}")
        return []


def example_5_error_handling():
    """示例 5: 错误处理"""
    print("\n" + "="*60)
    print("示例 5: 错误处理演示")
    print("="*60)
    
    try:
        agent = LabAgent()
        
        # 演示各种输入
        test_cases = [
            "",  # 空输入
            "这是一个很长的查询" * 100,  # 很长的输入
            "查询@#$%^&*设备",  # 特殊字符
            "123456789",  # 纯数字
        ]
        
        for i, query in enumerate(test_cases, 1):
            query_display = query[:50] + "..." if len(query) > 50 else query
            print(f"\n测试用例 {i}: {query_display}")
            
            try:
                response = agent.run(query)
                print(f"✓ 成功: {response[:80]}...")
            except Exception as e:
                print(f"✗ 异常: {type(e).__name__}: {str(e)[:80]}")
        
    except ValueError as e:
        print(f"配置错误: {e}")
    except Exception as e:
        print(f"其他错误: {e}")


def main():
    """主程序"""
    examples = {
        "1": ("单个查询", example_1_single_query),
        "2": ("多轮对话", example_2_multi_turn_conversation),
        "3": ("程序集成", example_3_programmatic_use),
        "4": ("批量处理", example_4_batch_processing),
        "5": ("错误处理", example_5_error_handling),
    }
    
    print("\n")
    print("="*60)
    print("SELABS Agent 使用示例")
    print("="*60)
    print("\n选择要运行的示例:")
    print()
    
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print(f"  0. 运行所有示例")
    print(f"  q. 退出")
    print()
    
    choice = input("请输入选择 (0-5, q): ").strip()
    
    if choice == "q":
        print("退出")
        return
    elif choice == "0":
        for name, func in examples.values():
            try:
                func()
            except KeyboardInterrupt:
                print("\n\n用户中断")
                break
            except Exception as e:
                print(f"\n示例执行失败: {e}")
    elif choice in examples:
        name, func = examples[choice]
        print(f"\n运行示例 {choice}: {name}\n")
        try:
            func()
        except KeyboardInterrupt:
            print("\n\n用户中断")
        except Exception as e:
            print(f"\n示例执行失败: {e}")
    else:
        print("无效选择")
    
    print("\n完成")


if __name__ == "__main__":
    main()
