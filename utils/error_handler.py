"""错误处理模块 - 统一的错误处理和响应格式"""

from typing import Any, Dict


class LabAgentError(Exception):
    """实验室 Agent 通用异常"""
    pass


def handle_api_error(error: Exception) -> str:
    """处理 API 调用错误，返回通用错误消息
    
    Args:
        error: 异常对象
        
    Returns:
        str: 用户友好的错误消息
    """
    # 所有 API 错误统一返回通用消息
    return "抱歉，操作失败。请稍后重试或联系管理员。"


def handle_llm_error(error: Exception) -> str:
    """处理 LLM 调用错误
    
    Args:
        error: 异常对象
        
    Returns:
        str: 用户友好的错误消息
    """
    return "抱歉，处理您的请求时出现错误。请重新表述您的问题试试。"


def format_tool_result(result: Any) -> Dict[str, Any]:
    """格式化工具执行结果
    
    Args:
        result: 工具返回的原始结果
        
    Returns:
        Dict: 格式化后的结果字典
    """
    if isinstance(result, dict):
        return result
    
    return {
        "status": "success",
        "result": result
    }
