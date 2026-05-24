"""轻量 Web 原型：FastAPI + SSE（session-based）

提供三个接口：
- POST /api/agent/session -> 创建会话，返回 session_id
- POST /api/agent/send -> 发送用户消息（将触发 Agent 处理并把分片放入会话队列）
- GET  /api/agent/stream -> 以 SSE 方式消费会话队列

此模块为原型实现，使用内存会话队列，不适合生产环境（无持久化）。
"""

import asyncio
import json
from pathlib import Path
import uuid
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse

from .agent.agent import LabAgent
from .tools.tool_definitions import get_session_context

app = FastAPI(title="SELABS Agent Web Prototype")

WEB_DIR = Path(__file__).resolve().parents[1] / "web"


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/chat.js")
async def chat_js():
    return FileResponse(WEB_DIR / "chat.js")

# 会话结构：session_id -> {queue: asyncio.Queue, auth: {...}}
SESSIONS: Dict[str, Dict[str, Any]] = {}

# 单例 Agent
AGENT = LabAgent()


@app.post("/api/agent/session")
async def create_session():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "queue": asyncio.Queue(),
        "auth": {
            "is_authenticated": False,
            "user_id": None,
            "user_number": None,
            "auth_token": None,
        }
    }
    return JSONResponse({"session_id": session_id})


def _sync_session_auth(session_id: str):
    """从 contextvars 上下文同步会话认证信息回 SESSIONS 存储
    
    这用于同步工具执行中对认证信息的更新（例如登录工具更新的令牌信息）
    """
    if session_id not in SESSIONS:
        return
    
    session_context = get_session_context()
    if session_context and session_context.get("session_id") == session_id:
        auth_info = session_context.get("auth_info", {})
        if auth_info:
            SESSIONS[session_id]["auth"].update(auth_info)


@app.post("/api/agent/send")
async def send_message(payload: Request):
    body = await payload.json()
    session_id = body.get("session_id")
    message = body.get("message")

    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=400, detail="invalid session_id")

    if not message:
        raise HTTPException(status_code=400, detail="message required")

    session_data = SESSIONS[session_id]
    queue = session_data["queue"]
    auth_info = session_data["auth"]

    # 在后台任务中运行 Agent 的流式生成器并将片段放入队列
    async def _run_and_push():
        loop = asyncio.get_running_loop()

        def gen():
            for chunk in AGENT.run_stream(message, session_id=session_id, auth_info=auth_info):
                yield chunk

        for piece in await loop.run_in_executor(None, lambda: list(gen())):
            await queue.put({"data": piece})

        # 同步认证信息回 SESSIONS（在 Agent 执行完成后）
        _sync_session_auth(session_id)

        # 标记结束
        await queue.put({"done": True})

    asyncio.create_task(_run_and_push())

    return JSONResponse({"status": "processing"}, status_code=202)


@app.get("/api/agent/stream")
async def stream(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=400, detail="invalid session_id")

    session_data = SESSIONS[session_id]
    queue = session_data["queue"]

    async def event_generator():
        try:
            while True:
                item = await queue.get()
                if item is None:
                    continue
                if item.get("done"):
                    # 发送 done 事件并结束
                    yield "event: done\n\n"
                    break
                # 发送数据片段为 SSE data
                data = json.dumps({"data": item.get("data")})
                yield f"data: {data}\n\n"
        finally:
            # 清理会话队列
            SESSIONS.pop(session_id, None)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
