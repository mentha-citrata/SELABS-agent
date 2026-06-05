# SELABS Agent

SELABS Agent 是一个面向实验室管理系统的对话式助手原型。当前后端基于 LangGraph + LangChain 构建 ReAct 风格 Agent，使用 DeepSeek 的 OpenAI 兼容接口作为 LLM，并通过 LangChain tools 封装实验室管理系统的 HTTP API。

## 项目现状

当前仓库已经不再是早期的“6 个占位工具”版本，运行时代码已扩展为更完整的 API 工具层：

- Agent 核心：`src/agent/agent.py` 使用 `StateGraph` 组织 LLM 节点、工具执行节点和结束节点。
- LLM 配置：`src/config/llm_config.py` 通过 `ChatOpenAI` 连接 DeepSeek，读取 `.env` 中的模型、温度和 token 配置。
- API 工具：`src/tools/tool_definitions.py` 定义了 87 个 `@tool`，覆盖登录、机位预约、教室预约、设备/耗材、借用记录、用户、报修、统计、巡查、数据中心申请与审批等接口。
- 会话认证：工具层使用 `contextvars` 保存会话上下文；除登录接口外，默认要求已认证后才调用后端业务接口。
- 交互入口：支持 CLI 单轮/多轮对话、编程调用，以及一个 FastAPI Agent API + SSE Web 服务。
- Vue 工作台：`web/vue/` 是当前推荐前端入口，支持结构化 SSE、Markdown 渲染、嵌入式 A2UI 表单和实验室管理中控布局；`web/` 保留早期静态页面。

需要注意：部分历史文档和测试仍引用早期的 `query_devices`、`create_experiment` 等旧工具名，已经落后于当前工具层。本文档按当前代码现状更新。

## 目录结构

```text
SELABS-agent/
├── src/
│   ├── __main__.py              # 支持 python3 -m src
│   ├── main.py                  # CLI 入口
│   ├── webserver.py             # FastAPI + SSE Web 原型
│   ├── agent/
│   │   ├── agent.py             # LabAgent / LangGraph 工作流
│   │   └── state.py             # AgentState，会话和认证字段
│   ├── config/
│   │   ├── api_config.py        # 后端 API 地址、超时、DEBUG
│   │   └── llm_config.py        # DeepSeek / ChatOpenAI 配置
│   ├── tools/
│   │   └── tool_definitions.py  # 87 个 LangChain tool + HTTP 请求封装
│   └── utils/
│       └── error_handler.py
├── web/                         # 早期最小 HTML/SSE 前端
├── web/vue/                     # Vue/Vite 实验室管理中控前端
├── test/                        # 测试与验证脚本，部分脚本需同步更新
├── doc/                         # 补充文档
├── examples.py                  # 编程调用示例
├── requirements.txt
├── .env.example
└── README.md
```

## 快速开始

更详细的步骤见 [doc/QUICKSTART.md](doc/QUICKSTART.md)。

```bash
cd SELABS-agent

python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，至少填入：

```env
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_MODEL=deepseek-chat
LAB_API_BASE_URL=http://localhost:8000/api
LAB_API_TIMEOUT=30
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2048
DEBUG=False
```

启动 CLI：

```bash
python3 -m src
```

单次查询：

```bash
python3 -m src "查询可用机位"
```

启动 Agent API + Vue 前端：

```bash
python3 -m uvicorn src.webserver:app --reload --host 127.0.0.1 --port 8000
```

另开一个终端：

```bash
cd web/vue
npm install
npm run dev
```

然后访问 Vite 输出的地址，默认是 `http://127.0.0.1:5173`。

## 运行模式

### CLI

`src/main.py` 提供两种模式：

- 不带参数：进入交互模式，支持 `help`、`clear`、`quit` / `exit`。
- 带参数：把命令行参数拼成一次用户查询，返回 Agent 响应。

推荐使用模块方式运行：

```bash
python3 -m src
python3 -m src "帮我查看我的预约"
```

### 编程调用

```python
from src.agent.agent import LabAgent

agent = LabAgent()

response = agent.run("查询教室列表")
print(response)

response = agent.run_with_history([
    "查询教室列表",
    "这里是上一轮回复",
    "帮我看一下哪个教室今天下午可用",
])
print(response)
```

### Agent API + Vue 前端

`src/webserver.py` 提供：

- `POST /api/agent/session`：创建内存会话。
- `POST /api/agent/send`：发送用户消息，后台运行 Agent。
- `GET /api/agent/stream`：通过 SSE 返回结构化事件。
- `/` 和 `/chat.js`：提供 `web/index.html` 对应的最小聊天页面。

当前推荐使用 `web/vue/` 作为前端入口。Vue 端通过 Vite 将 `/api` 代理到 Agent API，按 `message_start`、`markdown_delta`、`ui_block`、`message_done` 等事件渲染对话、Markdown 和 A2UI 表单。会话仍保存在内存中；当前 structured SSE 是完整 Agent 响应后的结构化派发，不是 LLM 原生 token 流。

## 工具与后端接口

工具层集中在 `src/tools/tool_definitions.py`，公共请求函数包括：

- `_request_json(method, path, params=None, payload=None)`
- `_get_json(path, params=None)`
- `_post_json(path, payload)`
- `_delete_json(path, params=None)`

当前工具覆盖的主要领域：

- 登录与用户信息：`login_user`、`get_user_info_by_id`、`search_user` 等。
- 机位预约：查询房间、可用机位、用户预约、取消预约等。
- 教室预约：预约教室、查询教室状态、预约记录、教室列表等。
- 设备/耗材：设备列表、设备详情、耗材列表、耗材详情等。
- 设备借用：未归还/处理中/已完成记录、可借用设备、记录统计等。
- 报修：个人/全部报修记录、图片、结果、反馈等。
- 统计与巡查：工位、耗材、设备、教室、用户、报修、巡查记录等统计接口。
- 数据中心申请与审批：申请详情、服务器注册/修改申请、审批信息等。

认证策略：

- `/v1/user/login` 是白名单。
- 其他工具请求默认要求会话已登录，否则直接返回 401 风格错误，不向后端发请求。
- Web 模式会把登录工具写入的认证信息同步回内存会话。

## 配置

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | 必填 |
| `DEEPSEEK_MODEL` | DeepSeek 模型名 | `deepseek-chat` |
| `LAB_API_BASE_URL` | 实验室管理系统 API 基础地址 | `http://localhost:8000/api` |
| `LAB_API_TIMEOUT` | 后端 API 超时秒数 | `30` |
| `AGENT_TEMPERATURE` | LLM 温度 | `0.7` |
| `AGENT_MAX_TOKENS` | LLM 最大输出 token | `2048` |
| `DEBUG` | 本地调试开关 | `False` |

## 验证与已知问题

建议先安装依赖后再验证：

```bash
python3 -m pip install -r requirements.txt
python3 test/verify_project.py
python3 test/test_auth.py
```

当前观察到的风险：

- 未安装依赖时，验证会因 `python-dotenv`、`langchain_core`、`langgraph` 缺失失败。
- `test/verify_project.py`、`test/test_basic.py`、`test/test_integration.py` 仍包含旧工具名断言，需要同步到当前 87 个工具的实现。
- `src/config/api_config.py` 中的 `ENDPOINTS` 字段仍是早期分类占位，不代表当前完整接口清单。
- `doc/ARCHITECTURE.md`、`doc/INDEX.md`、`test/README.md` 仍可能保留早期描述，阅读时以当前源码和本 README 为准。

## 后续建议

1. 同步测试：把旧工具名测试改为当前工具，例如 `login_user`、`reserve_seat`、`get_room_names`，并对认证门禁做明确断言。
2. 增加真实后端契约测试：用 mock HTTP 层校验 path、method、query/body 和 Authorization header。
3. 梳理工具分组：将 87 个工具按业务域拆分文件，降低 `tool_definitions.py` 的维护成本。
4. 改造真实流式：如果 DeepSeek/LangChain 配置支持 streaming，可在现有结构化 SSE 协议上接入 LLM 原生 token 流和工具状态事件。
5. 明确 Python 版本与包管理：补充 `pyproject.toml` 或锁定依赖版本，减少本地环境差异。

## 许可证

待定。
