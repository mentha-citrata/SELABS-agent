"""Agent 状态定义模块"""

from typing import Any, Annotated, TypedDict, Optional
from langchain_core.messages import BaseMessage


class AgentState(TypedDict, total=False):
    """Agent 的状态定义"""
    
    # 消息列表，维护对话历史
    messages: Annotated[list[BaseMessage], "对话消息列表"]
    
    # 会话 ID，用于绑定登录态和权限上下文
    session_id: Annotated[str, "Web 会话 ID"]
    
    # 认证信息：是否已登录
    is_authenticated: Annotated[bool, "是否已登录"]
    
    # 当前登录用户 ID（仅在已登录时有效）
    user_id: Annotated[Optional[int], "当前登录用户 ID，None 表示未登录"]
    
    # 当前登录用户的学工号（便于工具层查询）
    user_number: Annotated[Optional[str], "当前登录用户的学工号"]
    
    # 用户权限 token 或其它凭证信息（可扩展）
    auth_token: Annotated[Optional[str], "认证 token 或凭证"]
