"""工具定义模块 - 定义 Agent 可用的工具（预留接口）"""

import contextvars
import json
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from langchain_core.tools import tool

from ..config.api_config import APIConfig
from ..utils.error_handler import handle_api_error

# 使用 contextvars 来存储会话上下文，确保线程安全且支持异步
_session_context_var: contextvars.ContextVar[dict] = contextvars.ContextVar(
    '_session_context', default={}
)


def set_session_context(session_id: str, auth_info: dict = None):
    """设置当前请求的会话上下文"""
    _session_context_var.set({
        "session_id": session_id,
        "auth_info": auth_info or {},
    })


def get_session_context() -> dict:
    """获取当前请求的会话上下文"""
    return _session_context_var.get()


def _get_session_auth_info() -> dict:
    """获取当前会话的认证信息"""
    context = get_session_context()
    return context.get("auth_info", {})



def _clean_params(params: Optional[dict[str, Any]]) -> dict[str, Any]:
    """移除空值参数，避免把 None 发送到查询串里。"""
    if not params:
        return {}

    return {key: value for key, value in params.items() if value is not None}


def _request_json(
    method: str,
    path: str,
    params: Optional[dict[str, Any]] = None,
    payload: Optional[dict[str, Any]] = None,
) -> dict:
    """向后端发送 JSON 请求，并支持会话认证。"""
    # 未登录时默认禁止调用系统查询/操作接口（除白名单外），以实现“登录解锁查询功能”策略
    WHITELIST_PATHS = [
        "/v1/user/login",
    ]

    session_auth = _get_session_auth_info()
    is_auth = bool(session_auth.get("is_authenticated"))
    # 如果未认证且不是白名单接口，直接返回提示，避免对后端发起请求
    if not is_auth and path not in WHITELIST_PATHS:
        return {
            "status": "error",
            "message": "未登录：请先调用 login_user(login 工具) 登录以访问系统接口",
            "http_status": 401,
            "request": payload if payload is not None else (_clean_params(params) if params else {}),
        }
    url = f"{APIConfig.BASE_URL.rstrip('/')}/{path.lstrip('/')}"

    clean_params = _clean_params(params)
    if clean_params:
        query_string = urlencode(clean_params, doseq=True)
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{query_string}"

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    # 构建请求头，包含认证信息
    headers = {"Content-Type": "application/json"}
    
    # 从会话上下文获取认证令牌（如果有的话）
    auth_info = _get_session_auth_info()
    if auth_info.get("auth_token"):
        headers["satoken"] = auth_info['auth_token']

    request = Request(
        url,
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urlopen(request, timeout=APIConfig.TIMEOUT) as response:
            raw_body = response.read().decode("utf-8")
            if not raw_body:
                return {
                    "status": "success",
                    "message": "请求成功，但未返回内容",
                    "request": payload if payload is not None else clean_params,
                }

            try:
                response_body = json.loads(raw_body)
            except json.JSONDecodeError:
                response_body = raw_body

            if isinstance(response_body, dict) and response_body.get("code") not in (None, 0, "0"):
                return {
                    "status": "error",
                    "message": response_body.get("msg") or "请求失败",
                    "request": payload if payload is not None else clean_params,
                    "response": response_body,
                }

            return {
                "status": "success",
                "message": "请求成功",
                "request": payload if payload is not None else clean_params,
                "response": response_body,
            }
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="ignore")
        # 检查认证错误
        if error.code in (401, 403):
            error_msg = "会话已过期或权限不足，请重新登录"
        else:
            error_msg = handle_api_error(error)
        
        return {
            "status": "error",
            "message": error_msg,
            "http_status": error.code,
            "details": error_body or str(error),
            "request": payload if payload is not None else clean_params,
        }
    except URLError as error:
        return {
            "status": "error",
            "message": handle_api_error(error),
            "details": str(error),
            "request": payload if payload is not None else clean_params,
        }
    except Exception as error:
        return {
            "status": "error",
            "message": handle_api_error(error),
            "details": str(error),
            "request": payload if payload is not None else clean_params,
        }


def _post_json(path: str, payload: dict[str, Any]) -> dict:
    """向后端发送 JSON POST 请求。"""
    return _request_json("POST", path, payload=payload)


def _get_json(path: str, params: Optional[dict[str, Any]] = None) -> dict:
    """向后端发送 JSON GET 请求。"""
    return _request_json("GET", path, params=params)


def _delete_json(path: str, params: Optional[dict[str, Any]] = None) -> dict:
    """向后端发送 JSON DELETE 请求。"""
    return _request_json("DELETE", path, params=params)


@tool
def login_user(user_number: str, password: str) -> dict:
    """用户登录
    
    对应接口: POST /v1/user/login
    
    Args:
        user_number: 用户工号或学号
        password: 登录密码
    
    Returns:
        dict: 登录结果，包含用户信息和认证令牌
    """
    payload = {
        "userNumber": user_number,
        "password": password,
    }
    result = _post_json("/v1/user/login", payload)
    
    # 如果登录成功，更新会话上下文中的认证信息
    if result.get("status") == "success" and result.get("response", {}).get("data"):
        try:
            user_data = result["response"]["data"]
            
            # 获取当前会话上下文
            session_context = get_session_context()
            auth_info = session_context.get("auth_info", {})
            
            # 更新认证信息
            auth_info["is_authenticated"] = True
            auth_info["user_id"] = user_data.get("id")
            auth_info["user_number"] = user_data.get("userNumber")
            auth_info["auth_token"] = user_data.get("tokenValue") or user_data.get("token") or user_data.get("accessToken")
            
            # 更新会话上下文
            session_context["auth_info"] = auth_info
            set_session_context(session_context.get("session_id"), auth_info)
            
            result["authenticated"] = True
            result["user_info"] = {
                "user_id": auth_info["user_id"],
                "user_number": auth_info["user_number"],
            }
        except Exception as e:
            result["error_detail"] = f"无法更新会话信息: {str(e)}"
    
    return result


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


@tool
def get_seats_by_room_name(room_name: str, user_id: int) -> dict:
    """获取指定房间内机位状态

    对应接口: GET /v1/reservation/get-seats-by-room-name

    Args:
        room_name: 房间名称
        user_id: 用户 ID

    Returns:
        dict: 房间内机位状态列表
    """
    params = {
        "roomName": room_name,
        "userId": user_id,
    }
    return _get_json("/v1/reservation/get-seats-by-room-name", params)


@tool
def get_available_seats_by_time(
    start_time: str,
    end_time: str,
    room_name: Optional[str] = None,
) -> dict:
    """获取时间段内可用机位

    对应接口: GET /v1/reservation/get-available-seats-by-time

    Args:
        start_time: 开始时间，建议格式 YYYY-MM-DD HH:MM:SS
        end_time: 结束时间，建议格式 YYYY-MM-DD HH:MM:SS
        room_name: 房间名称，可选

    Returns:
        dict: 可用机位列表
    """
    params = {
        "startTime": start_time,
        "endTime": end_time,
        "roomName": room_name,
    }
    return _get_json("/v1/reservation/get-available-seats-by-time", params)


@tool
def get_room_names() -> dict:
    """获取所有房间名称

    对应接口: GET /v1/reservation/get-room-names

    Returns:
        dict: 房间名称列表
    """
    return _get_json("/v1/reservation/get-room-names")


@tool
def get_user_reservations(user_id: int, page_no: Optional[int] = None, page_size: Optional[int] = None) -> dict:
    """获取用户预约信息

    对应接口: GET /v1/reservation/get-user-reservations

    Args:
        user_id: 用户 ID
        page_no: 页码，可选
        page_size: 每页条数，可选

    Returns:
        dict: 用户预约列表
    """
    params = {
        "userId": user_id,
        "pageNo": page_no,
        "pageSize": page_size,
    }
    return _get_json("/v1/reservation/get-user-reservations", params)


@tool
def get_user_reservation_count(user_id: int) -> dict:
    """获取用户预约数量

    对应接口: GET /v1/reservation/get-user-reservation-count

    Args:
        user_id: 用户 ID

    Returns:
        dict: 预约数量
    """
    return _get_json("/v1/reservation/get-user-reservation-count", {"userId": user_id})


@tool
def cancel_seat_reservation(reservation_id: int, user_id: int) -> dict:
    """取消机位预约

    对应接口: DELETE /v1/reservation/cancel-reservation

    Args:
        reservation_id: 预约 ID
        user_id: 用户 ID

    Returns:
        dict: 取消结果
    """
    params = {
        "reservationId": reservation_id,
        "userId": user_id,
    }
    return _delete_json("/v1/reservation/cancel-reservation", params)


@tool
def get_reservation_status(reservation_id: Optional[int] = None) -> dict:
    """获取预约状态

    对应接口: GET /v1/reservation/get-reservation-status

    Args:
        reservation_id: 预约 ID，可选

    Returns:
        dict: 预约状态信息
    """
    params = {"reservationId": reservation_id}
    return _get_json("/v1/reservation/get-reservation-status", params)


@tool
def reserve_room(classroom_reservation_form: dict[str, Any]) -> dict:
    """预约教室

    对应接口: POST /v1/classroom-reservation/reserve-room

    Args:
        classroom_reservation_form: ClassroomReservationFromVO 对象

    Returns:
        dict: 教室预约结果
    """
    return _post_json("/v1/classroom-reservation/reserve-room", classroom_reservation_form)


@tool
def get_room_status(room_id: int, start_date: Optional[str] = None, days: Optional[int] = None) -> dict:
    """获取教室状态

    对应接口: GET /v1/classroom-reservation/get-room-status

    Args:
        room_id: 教室 ID
        start_date: 起始日期，可选
        days: 天数，可选

    Returns:
        dict: 教室状态列表
    """
    params = {
        "roomId": room_id,
        "startDate": start_date,
        "days": days,
    }
    return _get_json("/v1/classroom-reservation/get-room-status", params)


@tool
def cancel_classroom_reservation(reservation_id: int, user_id: int) -> dict:
    """取消教室预约

    对应接口: DELETE /v1/classroom-reservation/cancel-reservation

    Args:
        reservation_id: 预约 ID
        user_id: 用户 ID

    Returns:
        dict: 取消结果
    """
    params = {
        "reservationId": reservation_id,
        "userId": user_id,
    }
    return _delete_json("/v1/classroom-reservation/cancel-reservation", params)


@tool
def get_classroom_reservations(user_id: int, page_no: Optional[int] = None, page_size: Optional[int] = None) -> dict:
    """获取教室预约记录

    对应接口: GET /v1/classroom-reservation/get-room-reservation

    Args:
        user_id: 用户 ID
        page_no: 页码，可选
        page_size: 每页条数，可选

    Returns:
        dict: 教室预约记录列表
    """
    params = {
        "userId": user_id,
        "pageNo": page_no,
        "pageSize": page_size,
    }
    return _get_json("/v1/classroom-reservation/get-room-reservation", params)


@tool
def get_classroom_reservation_count(user_id: int) -> dict:
    """获取教室预约记录总数

    对应接口: GET /v1/classroom-reservation/get-room-reservation-count

    Args:
        user_id: 用户 ID

    Returns:
        dict: 教室预约记录数量
    """
    return _get_json("/v1/classroom-reservation/get-room-reservation-count", {"userId": user_id})


@tool
def get_classroom_reservation_by_id(reservation_id: int) -> dict:
    """按预约 ID 获取教室预约记录

    对应接口: GET /v1/classroom-reservation/get-room-reservation-by-id

    Args:
        reservation_id: 预约 ID

    Returns:
        dict: 单条教室预约记录
    """
    return _get_json("/v1/classroom-reservation/get-room-reservation-by-id", {"reservationId": reservation_id})


@tool
def get_classroom_list(page_no: int = 1, page_size: int = 20) -> dict:
    """获取教室列表

    对应接口: GET /v1/classroom/get-classroom-list

    Args:
        page_no: 页码
        page_size: 每页条数

    Returns:
        dict: 教室列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
    }
    return _get_json("/v1/classroom/get-classroom-list", params)


@tool
def get_classroom_count() -> dict:
    """获取教室数量

    对应接口: GET /v1/classroom/get-classroom-count

    Returns:
        dict: 教室数量
    """
    return _get_json("/v1/classroom/get-classroom-count")


@tool
def get_equipments(
    page_no: int = 1,
    page_size: int = 20,
    query: Optional[str] = None,
    min_count: Optional[int] = None,
    max_count: Optional[int] = None,
) -> dict:
    """获取设备列表

    对应接口: GET /v1/config/equipment/get-equipments

    Args:
        page_no: 页码
        page_size: 每页条数
        query: 搜索关键词，可选
        min_count: 最小数量，可选
        max_count: 最大数量，可选

    Returns:
        dict: 设备列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "query": query,
        "minCount": min_count,
        "maxCount": max_count,
    }
    return _get_json("/v1/config/equipment/get-equipments", params)


@tool
def get_equipments_count(
    query: Optional[str] = None,
    min_count: Optional[int] = None,
    max_count: Optional[int] = None,
) -> dict:
    """获取设备数量

    对应接口: GET /v1/config/equipment/get-equipments-count

    Args:
        query: 搜索关键词，可选
        min_count: 最小数量，可选
        max_count: 最大数量，可选

    Returns:
        dict: 设备数量
    """
    params = {
        "query": query,
        "minCount": min_count,
        "maxCount": max_count,
    }
    return _get_json("/v1/config/equipment/get-equipments-count", params)


@tool
def get_consumables(
    page_no: int = 1,
    page_size: int = 20,
    query: Optional[str] = None,
    min_count: Optional[int] = None,
    max_count: Optional[int] = None,
) -> dict:
    """获取耗材列表

    对应接口: GET /v1/config/consumable/get-consumables

    Args:
        page_no: 页码
        page_size: 每页条数
        query: 搜索关键词，可选
        min_count: 最小数量，可选
        max_count: 最大数量，可选

    Returns:
        dict: 耗材列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "query": query,
        "minCount": min_count,
        "maxCount": max_count,
    }
    return _get_json("/v1/config/consumable/get-consumables", params)


@tool
def get_consumables_count(
    query: Optional[str] = None,
    min_count: Optional[int] = None,
    max_count: Optional[int] = None,
) -> dict:
    """获取耗材数量

    对应接口: GET /v1/config/consumable/get-consumables-count

    Args:
        query: 搜索关键词，可选
        min_count: 最小数量，可选
        max_count: 最大数量，可选

    Returns:
        dict: 耗材数量
    """
    params = {
        "query": query,
        "minCount": min_count,
        "maxCount": max_count,
    }
    return _get_json("/v1/config/consumable/get-consumables-count", params)


@tool
def get_consumable(consumable_id: int) -> dict:
    """获取单个耗材

    对应接口: GET /v1/config/consumable/get-consumable

    Args:
        consumable_id: 耗材 ID

    Returns:
        dict: 耗材详情
    """
    return _get_json("/v1/config/consumable/get-consumable", {"id": consumable_id})


@tool
def get_user_device(user_id: int) -> dict:
    """获取用户设备

    对应接口: GET /v1/data_center/get_user_device

    Args:
        user_id: 用户 ID

    Returns:
        dict: 用户设备列表
    """
    return _get_json("/v1/data_center/get_user_device", {"user_id": user_id})


@tool
def get_device_info(device_id: int) -> dict:
    """获取设备详情

    对应接口: GET /v1/data_center/get_device_info

    Args:
        device_id: 设备 ID

    Returns:
        dict: 设备详情
    """
    return _get_json("/v1/data_center/get_device_info", {"device_id": device_id})


@tool
def get_devices(
    case_id: Optional[int] = None,
    device_types: Optional[list[str]] = None,
    user_id: Optional[int] = None,
) -> dict:
    """获取设备列表

    对应接口: GET /v1/data_center/get_devices

    Args:
        case_id: 案例 ID，可选
        device_types: 设备类型列表，可选
        user_id: 用户 ID，可选

    Returns:
        dict: 设备列表
    """
    params = {
        "caseId": case_id,
        "type": device_types,
        "userId": user_id,
    }
    return _get_json("/v1/data_center/get_devices", params)


@tool
def get_unreturned_records(user_id: int, page_no: int = 1, page_size: int = 20) -> dict:
    """获取未归还记录

    对应接口: GET /v1/equipment-borrowing/unreturned

    Args:
        page_no: 页码
        page_size: 每页条数
        user_id: 用户 ID

    Returns:
        dict: 未归还记录列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "userId": user_id,
    }
    return _get_json("/v1/equipment-borrowing/unreturned", params)


@tool
def get_processing_records(user_id: int, page_no: int = 1, page_size: int = 20) -> dict:
    """获取进行中记录

    对应接口: GET /v1/equipment-borrowing/processing

    Args:
        page_no: 页码
        page_size: 每页条数
        user_id: 用户 ID

    Returns:
        dict: 进行中记录列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "userId": user_id,
    }
    return _get_json("/v1/equipment-borrowing/processing", params)


@tool
def get_finished_records(user_id: int, page_no: int = 1, page_size: int = 20) -> dict:
    """获取已完成记录

    对应接口: GET /v1/equipment-borrowing/finished

    Args:
        page_no: 页码
        page_size: 每页条数
        user_id: 用户 ID

    Returns:
        dict: 已完成记录列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "userId": user_id,
    }
    return _get_json("/v1/equipment-borrowing/finished", params)


@tool
def get_borrowing_detail(record_id: int) -> dict:
    """获取借用详情

    对应接口: GET /v1/equipment-borrowing/detail/{id}

    Args:
        record_id: 记录 ID

    Returns:
        dict: 借用详情
    """
    return _get_json(f"/v1/equipment-borrowing/detail/{record_id}")


@tool
def get_unreturned_count(user_id: int) -> dict:
    """获取未归还数量

    对应接口: GET /v1/equipment-borrowing/count/unreturned/{userId}

    Args:
        user_id: 用户 ID

    Returns:
        dict: 未归还数量
    """
    return _get_json(f"/v1/equipment-borrowing/count/unreturned/{user_id}")


@tool
def get_processing_count(user_id: int) -> dict:
    """获取进行中数量

    对应接口: GET /v1/equipment-borrowing/count/processing/{userId}

    Args:
        user_id: 用户 ID

    Returns:
        dict: 进行中数量
    """
    return _get_json(f"/v1/equipment-borrowing/count/processing/{user_id}")


@tool
def get_finished_count(user_id: int) -> dict:
    """获取已完成数量

    对应接口: GET /v1/equipment-borrowing/count/finished/{userId}

    Args:
        user_id: 用户 ID

    Returns:
        dict: 已完成数量
    """
    return _get_json(f"/v1/equipment-borrowing/count/finished/{user_id}")


@tool
def get_borrowing_records(
    page_no: Optional[int] = None,
    page_size: Optional[int] = None,
    status: Optional[list[str]] = None,
) -> dict:
    """按状态获取记录

    对应接口: GET /v1/equipment-borrowing/record

    Args:
        page_no: 页码，可选
        page_size: 每页条数，可选
        status: 状态列表，可选

    Returns:
        dict: 借用记录列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "status": status,
    }
    return _get_json("/v1/equipment-borrowing/record", params)


@tool
def get_borrowing_record_count(status: Optional[list[str]] = None) -> dict:
    """按状态获取记录数

    对应接口: GET /v1/equipment-borrowing/count/record

    Args:
        status: 状态列表，可选

    Returns:
        dict: 借用记录数量
    """
    return _get_json("/v1/equipment-borrowing/count/record", {"status": status})


@tool
def get_borrowable_equipment() -> dict:
    """获取可借用设备

    对应接口: GET /v1/equipment-borrowing/borrowable-equipment

    Returns:
        dict: 可借用设备列表
    """
    return _get_json("/v1/equipment-borrowing/borrowable-equipment")


@tool
def get_user_info_by_user_number(user_number: str) -> dict:
    """按学工号获取用户信息

    对应接口: GET /v1/user/info/user-number/{userNumber}

    Args:
        user_number: 学工号

    Returns:
        dict: 用户信息
    """
    return _get_json(f"/v1/user/info/user-number/{user_number}")


@tool
def get_user_info_by_id(user_id: int) -> dict:
    """按用户 ID 获取用户信息

    对应接口: GET /v1/user/info/id/{userId}

    Args:
        user_id: 用户 ID

    Returns:
        dict: 用户信息
    """
    return _get_json(f"/v1/user/info/id/{user_id}")


@tool
def search_user(query: str) -> dict:
    """模糊搜索用户

    对应接口: GET /v1/user/search-user

    Args:
        query: 搜索关键词

    Returns:
        dict: 用户搜索结果
    """
    return _get_json("/v1/user/search-user", {"query": query})


@tool
def get_user_mentor(user_id: int) -> dict:
    """获取用户导师信息

    对应接口: GET /v1/user/get-user-mentor

    Args:
        user_id: 用户 ID

    Returns:
        dict: 导师信息
    """
    return _get_json("/v1/user/get-user-mentor", {"userId": user_id})


@tool
def get_user_recent_excels(user_id: int) -> dict:
    """获取用户最近导出文件

    对应接口: GET /v1/workstation/get-user-recent-excels

    Args:
        user_id: 用户 ID

    Returns:
        dict: 最近导出文件列表
    """
    return _get_json("/v1/workstation/get-user-recent-excels", {"userId": user_id})


@tool
def get_personal_repair_records(
    page_no: int = 1,
    page_size: int = 20,
    status: Optional[list[str]] = None,
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    """分页获取个人报修记录

    对应接口: GET /v1/repair/get-record-paged

    Args:
        page_no: 页码
        page_size: 每页条数
        status: 状态列表，可选
        begin_time: 起始时间，可选
        end_time: 结束时间，可选

    Returns:
        dict: 个人报修记录列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "status": status,
        "beginTime": begin_time,
        "endTime": end_time,
    }
    return _get_json("/v1/repair/get-record-paged", params)


@tool
def get_personal_repair_record_count(
    status: Optional[list[str]] = None,
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    """获取个人报修记录数

    对应接口: GET /v1/repair/record/count

    Args:
        status: 状态列表，可选
        begin_time: 起始时间，可选
        end_time: 结束时间，可选

    Returns:
        dict: 个人报修记录数量
    """
    params = {
        "status": status,
        "beginTime": begin_time,
        "endTime": end_time,
    }
    return _get_json("/v1/repair/record/count", params)


@tool
def get_all_repair_record_count(
    status: Optional[list[str]] = None,
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    """获取全部报修记录数

    对应接口: GET /v1/repair/record/all-count

    Args:
        status: 状态列表，可选
        begin_time: 起始时间，可选
        end_time: 结束时间，可选

    Returns:
        dict: 全部报修记录数量
    """
    params = {
        "status": status,
        "beginTime": begin_time,
        "endTime": end_time,
    }
    return _get_json("/v1/repair/record/all-count", params)


@tool
def get_all_repair_records(
    page_no: int = 1,
    page_size: int = 20,
    status: Optional[list[str]] = None,
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> dict:
    """分页获取全部报修记录

    对应接口: GET /v1/repair/get-all-record-paged

    Args:
        page_no: 页码
        page_size: 每页条数
        status: 状态列表，可选
        begin_time: 起始时间，可选
        end_time: 结束时间，可选

    Returns:
        dict: 全部报修记录列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "status": status,
        "beginTime": begin_time,
        "endTime": end_time,
    }
    return _get_json("/v1/repair/get-all-record-paged", params)


@tool
def get_record_imgs(record_id: int) -> dict:
    """获取报修记录图片

    对应接口: GET /v1/repair/record-imgs/{recordId}

    Args:
        record_id: 记录 ID

    Returns:
        dict: 图片地址列表
    """
    return _get_json(f"/v1/repair/record-imgs/{record_id}")


@tool
def get_result_imgs(result_id: int) -> dict:
    """获取报修结果图片

    对应接口: GET /v1/repair/result-imgs/{resultId}

    Args:
        result_id: 结果 ID

    Returns:
        dict: 图片地址列表
    """
    return _get_json(f"/v1/repair/result-imgs/{result_id}")


@tool
def get_repair_result(record_id: int) -> dict:
    """获取报修结果

    对应接口: GET /v1/repair/result/{recordId}

    Args:
        record_id: 记录 ID

    Returns:
        dict: 报修结果列表
    """
    return _get_json(f"/v1/repair/result/{record_id}")


@tool
def get_repair_record(record_id: int) -> dict:
    """获取报修记录详情

    对应接口: GET /v1/repair/record/{recordId}

    Args:
        record_id: 记录 ID

    Returns:
        dict: 报修记录详情
    """
    return _get_json(f"/v1/repair/record/{record_id}")


@tool
def get_repair_feedback(record_id: int) -> dict:
    """获取报修反馈

    对应接口: GET /v1/repair/feedback/{recordId}

    Args:
        record_id: 记录 ID

    Returns:
        dict: 报修反馈列表
    """
    return _get_json(f"/v1/repair/feedback/{record_id}")


@tool
def get_feedback_imgs(feedback_id: int) -> dict:
    """获取反馈图片

    对应接口: GET /v1/repair/feedback-imgs/{feedbackId}

    Args:
        feedback_id: 反馈 ID

    Returns:
        dict: 图片地址列表
    """
    return _get_json(f"/v1/repair/feedback-imgs/{feedback_id}")


@tool
def get_all_workstations_count() -> dict:
    """获取工位总数

    对应接口: GET /v1/statistics/workstation/get-all-workstations-count

    Returns:
        dict: 工位总数
    """
    return _get_json("/v1/statistics/workstation/get-all-workstations-count")


@tool
def get_finished_collections() -> dict:
    """获取已完成耗材领用数

    对应接口: GET /v1/statistics/consumable/get-finished-collections

    Returns:
        dict: 已完成耗材领用数
    """
    return _get_json("/v1/statistics/consumable/get-finished-collections")


@tool
def get_statistics_consumables() -> dict:
    """获取耗材列表

    对应接口: GET /v1/statistics/consumable/get-consumables

    Returns:
        dict: 耗材列表
    """
    return _get_json("/v1/statistics/consumable/get-consumables")


@tool
def get_all_available_seat_count() -> dict:
    """获取可预约机位总数

    对应接口: GET /v1/statistics/reservation/get-all-available-seat-count

    Returns:
        dict: 可预约机位总数
    """
    return _get_json("/v1/statistics/reservation/get-all-available-seat-count")


@tool
def get_equipment_borrowed_count() -> dict:
    """获取已借用设备数

    对应接口: GET /v1/statistics/equipment-borrowing/get-equipment-borrowed-count

    Returns:
        dict: 已借用设备数
    """
    return _get_json("/v1/statistics/equipment-borrowing/get-equipment-borrowed-count")


@tool
def get_statistics_equipments() -> dict:
    """获取设备列表

    对应接口: GET /v1/statistics/equipment-borrowing/get-equipments

    Returns:
        dict: 设备列表
    """
    return _get_json("/v1/statistics/equipment-borrowing/get-equipments")


@tool
def get_role_count() -> dict:
    """获取各角色用户数

    对应接口: GET /v1/statistics/user/get-role-count

    Returns:
        dict: 角色统计
    """
    return _get_json("/v1/statistics/user/get-role-count")


@tool
def get_unrepaired_record_count() -> dict:
    """获取未维修报修数

    对应接口: GET /v1/statistics/repair/get-unrepaired-record-count

    Returns:
        dict: 未维修报修数
    """
    return _get_json("/v1/statistics/repair/get-unrepaired-record-count")


@tool
def get_occupied_classroom() -> dict:
    """获取被占用教室

    对应接口: GET /v1/statistics/classroom/get-occupied-classroom

    Returns:
        dict: 被占用教室列表
    """
    return _get_json("/v1/statistics/classroom/get-occupied-classroom")


@tool
def get_free_classroom() -> dict:
    """获取空闲教室

    对应接口: GET /v1/statistics/classroom/get-free-classroom

    Returns:
        dict: 空闲教室列表
    """
    return _get_json("/v1/statistics/classroom/get-free-classroom")


@tool
def get_classroom_usage() -> dict:
    """获取教室使用情况

    对应接口: GET /v1/statistics/classroom/get-classroom-usage

    Returns:
        dict: 教室使用情况
    """
    return _get_json("/v1/statistics/classroom/get-classroom-usage")


@tool
def get_device_count() -> dict:
    """获取数据中心设备数

    对应接口: GET /v1/statistics/data-center/get-device-count

    Returns:
        dict: 数据中心设备数
    """
    return _get_json("/v1/statistics/data-center/get-device-count")


@tool
def get_application_count() -> dict:
    """获取模块申请数量

    对应接口: GET /v1/statistics/data-center/get-application-count

    Returns:
        dict: 模块申请统计
    """
    return _get_json("/v1/statistics/data-center/get-application-count")


@tool
def get_unhandled_inspect_count() -> dict:
    """获取未处理巡查问题数

    对应接口: GET /v1/statistics/inspect/unhandled

    Returns:
        dict: 未处理巡查问题数
    """
    return _get_json("/v1/statistics/inspect/unhandled")


@tool
def get_inspect_records() -> dict:
    """获取巡查记录列表

    对应接口: GET /v1/inspect/records

    Returns:
        dict: 巡查记录列表
    """
    return _get_json("/v1/inspect/records")


@tool
def get_inspect_records_by_page(page_size: int = 20, page_no: int = 1) -> dict:
    """分页获取巡查记录

    对应接口: GET /v1/inspect/getRecordsByPage

    Args:
        page_size: 每页条数
        page_no: 页码

    Returns:
        dict: 巡查记录列表
    """
    params = {
        "pageSize": page_size,
        "pageNo": page_no,
    }
    return _get_json("/v1/inspect/getRecordsByPage", params)


@tool
def get_inspect_records_count() -> dict:
    """获取巡查记录统计

    对应接口: GET /v1/inspect/recordsCount

    Returns:
        dict: 巡查记录统计
    """
    return _get_json("/v1/inspect/recordsCount")


@tool
def get_inspect_records_by_date(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """按日期获取巡查记录

    对应接口: GET /v1/inspect/getRecordsByDate

    Args:
        start_date: 开始日期，可选
        end_date: 结束日期，可选

    Returns:
        dict: 巡查记录列表
    """
    params = {
        "startDate": start_date,
        "endDate": end_date,
    }
    return _get_json("/v1/inspect/getRecordsByDate", params)


@tool
def get_inspect_record_by_id(record_id: int) -> dict:
    """按 ID 获取巡查记录

    对应接口: GET /v1/inspect/getRecordById

    Args:
        record_id: 记录 ID

    Returns:
        dict: 巡查记录详情
    """
    return _get_json("/v1/inspect/getRecordById", {"id": record_id})


@tool
def get_update_by_id(update_id: int) -> dict:
    """获取单条更新记录

    对应接口: GET /v1/inspect/update/getUpdate

    Args:
        update_id: 更新记录 ID

    Returns:
        dict: 更新记录详情
    """
    return _get_json("/v1/inspect/update/getUpdate", {"id": update_id})


@tool
def get_updates() -> dict:
    """获取更新记录列表

    对应接口: GET /v1/inspect/update/getUpdates

    Returns:
        dict: 更新记录列表
    """
    return _get_json("/v1/inspect/update/getUpdates")


@tool
def get_updates_by_page(page_size: int = 20, page_no: int = 1) -> dict:
    """分页获取更新记录

    对应接口: GET /v1/inspect/update/getUpdatesByPage

    Args:
        page_size: 每页条数
        page_no: 页码

    Returns:
        dict: 更新记录列表
    """
    params = {
        "pageSize": page_size,
        "pageNo": page_no,
    }
    return _get_json("/v1/inspect/update/getUpdatesByPage", params)


@tool
def get_update_history(update_id: int) -> dict:
    """获取记录更新历史

    对应接口: GET /v1/inspect/update/history

    Args:
        update_id: 更新记录 ID

    Returns:
        dict: 更新历史列表
    """
    return _get_json("/v1/inspect/update/history", {"id": update_id})


@tool
def get_authorize_url(user_id: int, front_end_url: str) -> dict:
    """获取授权 URL

    对应接口: GET /v1/consumable/get-authorize-url

    Args:
        user_id: 用户 ID
        front_end_url: 前端 URL

    Returns:
        dict: 授权 URL
    """
    params = {
        "userId": user_id,
        "frontEndUrl": front_end_url,
    }
    return _get_json("/v1/consumable/get-authorize-url", params)


@tool
def get_user_pending_requests(user_id: int) -> dict:
    """获取用户待处理领用申请

    对应接口: GET /v1/consumable/get-user-pending-requests

    Args:
        user_id: 用户 ID

    Returns:
        dict: 待处理领用申请列表
    """
    return _get_json("/v1/consumable/get-user-pending-requests", {"userId": user_id})


@tool
def get_collect_records(
    page_no: int = 1,
    page_size: int = 20,
    user_id: Optional[int] = None,
    transactor_id: Optional[int] = None,
    min_collect_time: Optional[str] = None,
    max_collect_time: Optional[str] = None,
    item_name: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """获取领用记录

    对应接口: GET /v1/consumable/get-collect-records

    Args:
        page_no: 页码
        page_size: 每页条数
        user_id: 用户 ID，可选
        transactor_id: 经办人 ID，可选
        min_collect_time: 起始领用时间，可选
        max_collect_time: 结束领用时间，可选
        item_name: 物品名称，可选
        status: 状态，可选

    Returns:
        dict: 领用记录列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "userId": user_id,
        "transactorId": transactor_id,
        "minCollectTime": min_collect_time,
        "maxCollectTime": max_collect_time,
        "itemName": item_name,
        "status": status,
    }
    return _get_json("/v1/consumable/get-collect-records", params)


@tool
def get_collect_records_count(
    user_id: Optional[int] = None,
    transactor_id: Optional[int] = None,
    min_collect_time: Optional[str] = None,
    max_collect_time: Optional[str] = None,
    item_name: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    """获取领用记录数

    对应接口: GET /v1/consumable/get-collect-records-count

    Args:
        user_id: 用户 ID，可选
        transactor_id: 经办人 ID，可选
        min_collect_time: 起始领用时间，可选
        max_collect_time: 结束领用时间，可选
        item_name: 物品名称，可选
        status: 状态，可选

    Returns:
        dict: 领用记录数量
    """
    params = {
        "userId": user_id,
        "transactorId": transactor_id,
        "minCollectTime": min_collect_time,
        "maxCollectTime": max_collect_time,
        "itemName": item_name,
        "status": status,
    }
    return _get_json("/v1/consumable/get-collect-records-count", params)


@tool
def get_workstations(
    page_no: Optional[int] = None,
    page_size: Optional[int] = None,
    student_name: Optional[str] = None,
    student_number: Optional[str] = None,
    student_grade: Optional[int] = None,
    student_degree: Optional[str] = None,
    student_major: Optional[str] = None,
    mentor_name: Optional[str] = None,
    office: Optional[str] = None,
    workstation_number: Optional[str] = None,
) -> dict:
    """获取工位信息

    对应接口: GET /v1/workstation/get-workstations

    Args:
        page_no: 页码，可选
        page_size: 每页条数，可选
        student_name: 学生姓名，可选
        student_number: 学工号，可选
        student_grade: 年级，可选
        student_degree: 学位，可选
        student_major: 专业，可选
        mentor_name: 导师姓名，可选
        office: 办公室，可选
        workstation_number: 工位号，可选

    Returns:
        dict: 工位列表
    """
    params = {
        "pageNo": page_no,
        "pageSize": page_size,
        "studentName": student_name,
        "studentNumber": student_number,
        "studentGrade": student_grade,
        "studentDegree": student_degree,
        "studentMajor": student_major,
        "mentorName": mentor_name,
        "office": office,
        "workstationNumber": workstation_number,
    }
    return _get_json("/v1/workstation/get-workstations", params)


@tool
def get_workstations_count(
    student_name: Optional[str] = None,
    student_number: Optional[str] = None,
    student_grade: Optional[int] = None,
    student_degree: Optional[str] = None,
    student_major: Optional[str] = None,
    mentor_name: Optional[str] = None,
    office: Optional[str] = None,
    workstation_number: Optional[str] = None,
) -> dict:
    """获取工位数量

    对应接口: GET /v1/workstation/get-workstations-count

    Returns:
        dict: 工位数量
    """
    params = {
        "studentName": student_name,
        "studentNumber": student_number,
        "studentGrade": student_grade,
        "studentDegree": student_degree,
        "studentMajor": student_major,
        "mentorName": mentor_name,
        "office": office,
        "workstationNumber": workstation_number,
    }
    return _get_json("/v1/workstation/get-workstations-count", params)


@tool
def get_workstation_by_user_id(user_id: int) -> dict:
    """按学生 ID 获取工位

    对应接口: GET /v1/workstation/getWorkstationByUserId

    Args:
        user_id: 用户 ID

    Returns:
        dict: 工位信息
    """
    return _get_json("/v1/workstation/getWorkstationByUserId", {"userId": user_id})


@tool
def get_workstation_excel_template() -> dict:
    """获取 Excel 模板链接

    对应接口: GET /v1/workstation/get-excel-template

    Returns:
        dict: 模板链接
    """
    return _get_json("/v1/workstation/get-excel-template")


@tool
def get_application_by_id(application_id: int) -> dict:
    """获取申请详情（数据中心进入申请）

    对应接口: GET /v1/application/data-center/get-application

    Args:
        application_id: 申请 ID

    Returns:
        dict: 申请详情
    """
    return _get_json("/v1/application/data-center/get-application", {"applicationId": application_id})


@tool
def get_server_modification_application_by_id(application_id: int) -> dict:
    """获取服务器修改申请详情

    对应接口: GET /v1/application/server-modification/get-application

    Args:
        application_id: 申请 ID

    Returns:
        dict: 申请详情
    """
    return _get_json("/v1/application/server-modification/get-application", {"applicationId": application_id})


@tool
def get_server_registry_application_by_id(application_id: int) -> dict:
    """获取服务器注册申请详情

    对应接口: GET /v1/application/server-registry/get-application

    Args:
        application_id: 申请 ID

    Returns:
        dict: 申请详情
    """
    return _get_json("/v1/application/server-registry/get-application", {"applicationId": application_id})


@tool
def get_approval_by_application_id(application_id: int) -> dict:
    """获取数据中心审批信息

    对应接口: GET /v1/approval/data-center/get-approval-by-application-id

    Args:
        application_id: 申请 ID

    Returns:
        dict: 审批信息
    """
    return _get_json("/v1/approval/data-center/get-approval-by-application-id", {"applicationId": application_id})


@tool
def get_server_modification_approval_by_application_id(application_id: int) -> dict:
    """获取服务器修改审批信息

    对应接口: GET /v1/approval/data-center/server-modification/get-approval-by-application-id

    Args:
        application_id: 申请 ID

    Returns:
        dict: 审批信息
    """
    return _get_json("/v1/approval/data-center/server-modification/get-approval-by-application-id", {"applicationId": application_id})


@tool
def get_server_registry_approval_by_application_id(application_id: int) -> dict:
    """获取服务器注册审批信息

    对应接口: GET /v1/approval/data-center/server-registry/get-approval-by-application-id

    Args:
        application_id: 申请 ID

    Returns:
        dict: 审批信息
    """
    return _get_json("/v1/approval/data-center/server-registry/get-approval-by-application-id", {"applicationId": application_id})

# 导出所有工具供 Agent 使用
TOOLS = [
    login_user,
    reserve_seat,
    get_seats_by_room_name,
    get_available_seats_by_time,
    get_room_names,
    get_user_reservations,
    get_user_reservation_count,
    cancel_seat_reservation,
    get_reservation_status,
    reserve_room,
    get_room_status,
    cancel_classroom_reservation,
    get_classroom_reservations,
    get_classroom_reservation_count,
    get_classroom_reservation_by_id,
    get_classroom_list,
    get_classroom_count,
    get_equipments,
    get_equipments_count,
    get_consumables,
    get_consumables_count,
    get_consumable,
    get_user_device,
    get_device_info,
    get_devices,
    get_unreturned_records,
    get_processing_records,
    get_finished_records,
    get_borrowing_detail,
    get_unreturned_count,
    get_processing_count,
    get_finished_count,
    get_borrowing_records,
    get_borrowing_record_count,
    get_borrowable_equipment,
    get_user_info_by_user_number,
    get_user_info_by_id,
    search_user,
    get_user_mentor,
    get_user_recent_excels,
    get_personal_repair_records,
    get_personal_repair_record_count,
    get_all_repair_record_count,
    get_all_repair_records,
    get_record_imgs,
    get_result_imgs,
    get_repair_result,
    get_repair_record,
    get_repair_feedback,
    get_feedback_imgs,
    get_all_workstations_count,
    get_finished_collections,
    get_statistics_consumables,
    get_all_available_seat_count,
    get_equipment_borrowed_count,
    get_statistics_equipments,
    get_role_count,
    get_unrepaired_record_count,
    get_occupied_classroom,
    get_free_classroom,
    get_classroom_usage,
    get_device_count,
    get_application_count,
    get_unhandled_inspect_count,
    get_inspect_records,
    get_inspect_records_by_page,
    get_inspect_records_count,
    get_inspect_records_by_date,
    get_inspect_record_by_id,
    get_update_by_id,
    get_updates,
    get_updates_by_page,
    get_update_history,
    get_authorize_url,
    get_user_pending_requests,
    get_collect_records,
    get_collect_records_count,
    get_workstations,
    get_workstations_count,
    get_workstation_by_user_id,
    get_workstation_excel_template,
    get_application_by_id,
    get_server_modification_application_by_id,
    get_server_registry_application_by_id,
    get_approval_by_application_id,
    get_server_modification_approval_by_application_id,
    get_server_registry_approval_by_application_id,
]
