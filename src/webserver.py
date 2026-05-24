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
from typing import Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, StreamingResponse

from .agent.agent import LabAgent

app = FastAPI(title="SELABS Agent Web Prototype")

WEB_DIR = Path(__file__).resolve().parents[1] / "web"


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/chat.js")
async def chat_js():
    return FileResponse(WEB_DIR / "chat.js")

# 简易内存会话存储：session_id -> asyncio.Queue
SESSIONS: Dict[str, asyncio.Queue] = {}

# 单例 Agent
AGENT = LabAgent()


@app.post("/api/agent/session")
async def create_session():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = asyncio.Queue()
    return JSONResponse({"session_id": session_id})


@app.post("/api/agent/send")
async def send_message(payload: Request):
    body = await payload.json()
    session_id = body.get("session_id")
    message = body.get("message")

    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=400, detail="invalid session_id")

    if not message:
        raise HTTPException(status_code=400, detail="message required")

    queue = SESSIONS[session_id]

    # 在后台任务中运行 Agent 的流式生成器并将片段放入队列
    async def _run_and_push():
        loop = asyncio.get_running_loop()

        def gen():
            for chunk in AGENT.run_stream(message):
                yield chunk

        for piece in await loop.run_in_executor(None, lambda: list(gen())):
            await queue.put({"data": piece})

        # 标记结束
        await queue.put({"done": True})

    asyncio.create_task(_run_and_push())

    return JSONResponse({"status": "processing"}, status_code=202)


@app.get("/api/agent/stream")
async def stream(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=400, detail="invalid session_id")

    queue = SESSIONS[session_id]

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
