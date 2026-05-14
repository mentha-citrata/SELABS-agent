"""工具定义模块 - 定义 Agent 可用的工具（预留接口）"""

import json
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from langchain_core.tools import tool

from ..config.api_config import APIConfig
from ..utils.error_handler import handle_api_error


def _post_json(path: str, payload: dict[str, Any]) -> dict:
    """向后端发送 JSON POST 请求。"""
    url = f"{APIConfig.BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=APIConfig.TIMEOUT) as response:
            raw_body = response.read().decode("utf-8")
            if not raw_body:
                return {
                    "status": "success",
                    "message": "请求成功，但未返回内容",
                    "request": payload,
                }

            try:
                response_body = json.loads(raw_body)
            except json.JSONDecodeError:
                response_body = raw_body

            return {
                "status": "success",
                "message": "请求成功",
                "request": payload,
                "response": response_body,
            }
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        return {
            "status": "error",
            "message": handle_api_error(error),
            "http_status": error.code,
            "details": error_body or str(error),
            "request": payload,
        }
    except URLError as error:
        return {
            "status": "error",
            "message": handle_api_error(error),
            "details": str(error),
            "request": payload,
        }
    except Exception as error:
        return {
            "status": "error",
            "message": handle_api_error(error),
            "details": str(error),
            "request": payload,
        }


@tool
def reserve_seat(seat_id: int, user_id: int, start_time: str, end_time: str) -> dict:
    """预约座位

    对应接口: POST /v1/reservation/reserve-seat

    Args:
        seat_id: 座位 ID
        user_id: 用户 ID
        start_time: 开始时间，建议格式 YYYY-MM-DD HH:MM:SS
        end_time: 结束时间，建议格式 YYYY-MM-DD HH:MM:SS

    Returns:
        dict: 座位预约结果
    """
    payload = {
        "seatId": seat_id,
        "userId": user_id,
        "startTime": start_time,
        "endTime": end_time,
    }
    return _post_json("/v1/reservation/reserve-seat", payload)

# 导出所有工具供 Agent 使用
TOOLS = [
    reserve_seat,
]
