"""示例脚本 - 演示如何使用 SELABS Agent。"""

from .agent.agent import LabAgent


def example_1_single_query():
    """示例 1: 单个查询"""
    print("\n" + "=" * 60)
    print("示例 1: 单个查询")
    print("=" * 60)

    try:
        agent = LabAgent()
        response = agent.run("查询有哪些实验设备？")
        print(f"Agent: {response}")
    except Exception as e:
        print(f"错误: {e}")


def example_2_multi_turn_conversation():
    """示例 2: 多轮对话"""
    print("\n" + "=" * 60)
    print("示例 2: 多轮对话")
    print("=" * 60)

    try:
        agent = LabAgent()
        first_response = agent.run("你好，请介绍一下你自己。")
        print(f"第 1 轮: {first_response}")
        second_response = agent.run_with_history([
            "你好，请介绍一下你自己。",
            first_response,
            "请补充一句你能做什么。",
        ])
        print(f"第 2 轮: {second_response}")
    except Exception as e:
        print(f"错误: {e}")


def main():
    """主程序"""
    print("SELABS Agent 示例")
    example_1_single_query()
    example_2_multi_turn_conversation()


if __name__ == "__main__":
    main()
