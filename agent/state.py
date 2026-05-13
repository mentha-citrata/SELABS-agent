"""Agent 状态定义模块"""

from typing import Any, Annotated, TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Agent 的状态定义"""
    
    # 消息列表，维护对话历史
    messages: Annotated[list[BaseMessage], "对话消息列表"]
