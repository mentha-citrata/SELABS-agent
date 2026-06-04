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
import re
import uuid
from typing import Dict, Any, Optional

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

# 单例 Agent，按需懒加载，避免导入 webserver 时强制要求 LLM 配置。
AGENT: Optional[LabAgent] = None


def _get_agent() -> LabAgent:
    """获取单例 Agent，仅在实际处理用户消息时初始化。"""
    global AGENT

    if AGENT is None:
        AGENT = LabAgent()

    return AGENT


A2UI_BLOCK_RE = re.compile(r"```a2ui\s*(\{.*?\})\s*```", re.DOTALL)


def _format_sse_event(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def _format_done_sse_event() -> str:
    """Serialize a dispatchable custom SSE done event."""
    return "event: done\ndata: {}\n\n"


def _extract_a2ui_blocks(text: str) -> tuple[str, list[dict[str, Any]]]:
    blocks: list[dict[str, Any]] = []

    def replace(match: re.Match[str]) -> str:
        raw = match.group(1)
        try:
            block = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)

        if isinstance(block, dict) and block.get("kind") == "form":
            blocks.append(block)
            return ""

        return match.group(0)

    markdown = A2UI_BLOCK_RE.sub(replace, text).strip()
    return markdown, blocks


def _message_events_from_agent_text(text: str, message_id: Optional[str] = None):
    resolved_id = message_id or str(uuid.uuid4())
    markdown, blocks = _extract_a2ui_blocks(text)
    yield {"type": "message_start", "message_id": resolved_id}
    if markdown:
        yield {"type": "markdown_delta", "message_id": resolved_id, "content": markdown}
    for block in blocks:
        yield {"type": "ui_block", "message_id": resolved_id, "block": block}
    yield {"type": "message_done", "message_id": resolved_id}


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
        try:
            response = await loop.run_in_executor(
                None,
                lambda: _get_agent().run(message, session_id=session_id, auth_info=auth_info),
            )
            for event in _message_events_from_agent_text(response):
                await queue.put(event)
        except Exception as error:
            await queue.put({"type": "error", "message": str(error)})
        finally:
            # 同步认证信息回 SESSIONS（在 Agent 执行完成后）
            _sync_session_auth(session_id)
            await queue.put({"type": "stream_done"})

    asyncio.create_task(_run_and_push())

    return JSONResponse({"status": "processing"}, status_code=202)


@app.get("/api/agent/stream")
async def stream(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=400, detail="invalid session_id")

    session_data = SESSIONS[session_id]
    queue = session_data["queue"]

    async def event_generator():
        while True:
            item = await queue.get()
            if item is None:
                continue
            if item.get("type") == "stream_done":
                # 发送 done 事件并结束；会话保存登录态，不随单次 stream 清理。
                yield _format_done_sse_event()
                break
            yield _format_sse_event(item)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
