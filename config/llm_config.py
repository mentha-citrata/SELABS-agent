"""LLM 配置模块 - 配置 DeepSeek LLM 连接"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 加载环境变量
load_dotenv()


def get_llm():
    """获取配置好的 DeepSeek LLM 实例
    
    Returns:
        ChatOpenAI: 配置好的 LLM 实例
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    temperature = float(os.getenv("AGENT_TEMPERATURE", "0.7"))
    max_tokens = int(os.getenv("AGENT_MAX_TOKENS", "2048"))
    
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
    
    # 使用 OpenAI 兼容接口连接 DeepSeek
    llm = ChatOpenAI(
        api_key=api_key,
        model=model,
        base_url="https://api.deepseek.com",
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return llm
