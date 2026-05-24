# 会话认证实现总结

## 概述

已成功实现了 SELABS Agent 的会话级认证基础设施。系统现在支持：

1. **会话管理** - 基于 session_id 的用户会话隔离
2. **会话上下文** - 使用 Python 的 `contextvars` 实现线程安全的会话认证上下文
3. **登录工具** - Agent 可以调用 `login_user` 工具进行用户认证  
4. **会话感知请求** - 所有 API 请求自动包含认证令牌（如果已登录）
5. **会话持久化** - 认证信息在用户会话期间持久存储

## 实现细节

### 1. 会话上下文管理 (`src/tools/tool_definitions.py`)

使用 Python 的 `contextvars` 模块，而非全局变量，实现线程安全的会话上下文：

```python
_session_context_var: contextvars.ContextVar[dict] = contextvars.ContextVar(
    '_session_context', default={}
)

def set_session_context(session_id: str, auth_info: dict = None):
    """设置当前请求的会话上下文"""
    
def get_session_context() -> dict:
    """获取当前请求的会话上下文"""
```

**优点：**
- 线程安全，支持并发请求
- 工具函数可以访问当前请求的会话信息，无需通过参数传递
- 自动隔离不同会话间的认证信息

### 2. Agent 会话感知 (`src/agent/agent.py`)

Agent 的 `run()` 和 `run_stream()` 方法现在接受可选的 `session_id` 和 `auth_info` 参数：

```python
def run(self, user_message: str, session_id: str = None, auth_info: dict = None) -> str:
    """运行 Agent，支持会话认证"""
    # 设置会话上下文供工具使用
    if session_id:
        set_session_context(session_id, auth_info or {})
    
    # 将认证信息注入 AgentState
    initial_state: AgentState = {
        "messages": [...],
        "session_id": session_id or "",
        "is_authenticated": auth_info.get("is_authenticated", False) if auth_info else False,
        "user_id": auth_info.get("user_id") if auth_info else None,
        "user_number": auth_info.get("user_number") if auth_info else None,
        "auth_token": auth_info.get("auth_token") if auth_info else None,
    }
```

### 3. 登录工具 (`src/tools/tool_definitions.py`)

实现了 `login_user` 工具，允许 Agent 进行用户认证：

```python
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
```

**工作流程：**
1. 调用后端 `/v1/user/login` 接口
2. 提取响应中的用户信息和认证令牌
3. 更新当前会话上下文中的认证信息
4. 返回登录结果，包括 authenticated 标志和 user_info

### 4. 会话感知请求 (`src/tools/tool_definitions.py`)

修改了 `_request_json()` 函数，自动在所有 API 请求中包含认证令牌：

```python
def _request_json(method: str, path: str, params: dict = None, payload: dict = None) -> dict:
    """向后端发送 JSON 请求，并支持会话认证"""
    
    # 构建请求头，包含认证信息
    headers = {"Content-Type": "application/json"}
    
    # 从会话上下文获取认证令牌
    auth_info = _get_session_auth_info()
    if auth_info.get("auth_token"):
        headers["Authorization"] = f"Bearer {auth_info['auth_token']}"
    
    # 发送请求
    ...
    
    # 处理 401/403 认证错误
    if error.code in (401, 403):
        error_msg = "会话已过期或权限不足，请重新登录"
```

### 5. Web 层集成 (`src/webserver.py`)

FastAPI 服务器现在：

1. **为每个用户会话存储认证信息**：
```python
SESSIONS: Dict[str, Dict[str, Any]] = {}
# 会话结构: session_id -> {queue: asyncio.Queue, auth: {...}}
```

2. **在 Agent 执行前传递认证信息**：
```python
async def _run_and_push():
    # 将当前会话的认证信息传递给 Agent
    for chunk in AGENT.run_stream(message, session_id=session_id, auth_info=auth_info):
        ...
```

3. **同步登录后的认证信息**：
```python
def _sync_session_auth(session_id: str):
    """从 contextvars 上下文同步会话认证信息回 SESSIONS"""
    session_context = get_session_context()
    SESSIONS[session_id]["auth"].update(auth_info)
```

## 认证流程示例

### 1. 创建会话
```http
POST /api/agent/session
Response: {"session_id": "uuid-xxx"}
```

### 2. 发送登录请求
```http
POST /api/agent/send
{
  "session_id": "uuid-xxx",
  "message": "我需要登录，用户号是 2024001，密码是 mypassword"
}
```

Agent 将自动识别登录意图并调用 `login_user` 工具：
- 后端进行认证
- 提取认证令牌
- 更新会话认证信息
- 返回登录确认

### 3. 发送数据查询请求
```http
POST /api/agent/send
{
  "session_id": "uuid-xxx",
  "message": "帮我查询实验室 Lab1 有哪些可用座位"
}
```

所有后续 API 请求自动包含认证令牌：
```
Authorization: Bearer <token>
```

后端基于会话验证用户权限，返回相应数据。

## 完成的功能

✅ **contextvars 会话上下文管理**
- 线程安全
- 支持并发请求
- 自动请求隔离

✅ **Agent 会话感知**
- run() / run_stream() 支持 session_id 和 auth_info 参数
- AgentState 包含认证信息字段

✅ **登录工具**
- 实现 `login_user` 工具函数
- 处理登录成功和失败场景
- 自动更新会话认证信息

✅ **会话感知 API 请求**
- _request_json() 自动添加 Authorization 头
- 处理 401/403 认证错误
- 工具函数无需显式传递认证信息

✅ **Web 层集成**
- SESSIONS 存储结构支持认证信息
- send_message() 正确传递认证信息给 Agent
- _sync_session_auth() 同步登录后的新认证信息

✅ **测试覆盖**
- contextvars 上下文管理测试
- 登录工具响应处理测试
- Agent 会话集成测试
- 请求头认证传递测试
- 所有测试 4/4 通过

## 待完成项目

### 1. 会话持久化
- 当前实现使用内存存储，服务器重启会丢失会话
- 建议添加 Redis 或数据库支持

### 2. 会话过期
- 实现会话超时机制
- 自动清理过期会话

### 3. Cookie 支持
- 当前使用 Bearer Token
- 后续可添加 HTTP-only Cookie 支持

### 4. 刷新令牌
- 实现令牌刷新机制
- 支持长会话

### 5. 权限控制
- 基于用户角色的权限检查
- API 级别的权限验证

## 脚本

### 运行认证测试
```bash
python test/test_auth.py
```

### 启动 Web 服务器进行集成测试
```bash
python -m src.webserver
# 或使用 main.py
python src/main.py
```

## 相关文件

- `/src/agent/agent.py` - Agent 核心逻辑，现在支持会话参数
- `/src/agent/state.py` - AgentState TypedDict，包含认证字段
- `/src/tools/tool_definitions.py` - 工具定义，包含登录工具和会话感知请求
- `/src/webserver.py` - FastAPI 服务器，集成会话管理
- `/test/test_auth.py` - 认证功能测试套件

## 下一步建议

1. **持久化测试** - 添加数据库或 Redis 后端，测试会话持久化
2. **性能测试** - 测试并发会话数量和认证性能
3. **安全审计** - 评估会话安全性（CSRF 防护、会话固定等）
4. **用户体验** - 优化错误消息，提供更好的反馈
5. **日志记录** - 添加认证事件日志，便于调试和审计

