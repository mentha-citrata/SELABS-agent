# 快速开始

这份指南按当前源码整理，适合从零启动 SELABS Agent。仓库里的部分历史测试和旧文档仍保留早期工具名，本文以当前 `src/` 代码为准。

## 1. 准备环境

进入项目根目录：

```bash
cd SELABS-agent
```

创建并激活虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
python3 -m pip install -r requirements.txt
```

如果你的系统里 `python` 不存在，统一使用 `python3`。当前项目依赖包括 LangChain、LangGraph、DeepSeek 的 OpenAI 兼容客户端、FastAPI、Uvicorn 和 python-dotenv。

## 2. 配置 `.env`

复制模板：

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_MODEL=deepseek-chat

LAB_API_BASE_URL=http://localhost:8000/api
LAB_API_TIMEOUT=30

AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2048

DEBUG=False
```

说明：

- `DEEPSEEK_API_KEY` 必填，否则 `LabAgent()` 初始化会失败。
- `LAB_API_BASE_URL` 指向实验室管理系统后端，不是本 Agent Web 原型地址。
- 当前 Vue 前端默认把 `/api` 代理到 Agent API 的 `8000` 端口；如果实验室管理系统后端也在本机运行，请把 `LAB_API_BASE_URL` 改成该后端真实端口，例如 `http://127.0.0.1:8080/api`。

## 3. 启动 CLI

交互模式：

```bash
python3 -m src
```

单次查询：

```bash
python3 -m src "查询可用机位"
```

交互模式支持：

| 命令 | 作用 |
| --- | --- |
| `help` | 显示示例问题 |
| `clear` | 清空当前对话历史 |
| `quit` / `exit` | 退出 |

## 4. 启动 Agent API + Vue 前端

当前推荐的本地 Web 组合是：

- Agent API 服务：`src.webserver:app`，提供 `/api/agent/session`、`/api/agent/send`、`/api/agent/stream`。
- Vue 前端：`web/vue`，由 Vite 启动，并把 `/api` 代理到 Agent API 服务。

先在项目根目录启动 Agent API 服务。当前 [web/vue/vite.config.js](../web/vue/vite.config.js) 默认代理到 `http://localhost:8000`，所以 API 服务也要监听 `8000`：

```bash
source .venv/bin/activate
python3 -m uvicorn src.webserver:app --reload --host 127.0.0.1 --port 8000
```

再开一个终端启动 Vue 前端：

```bash
cd web/vue
npm install
npm run dev
```

访问 Vite 输出的地址，默认是：

```text
http://127.0.0.1:5173
```

请求链路是：

```text
浏览器 -> Vite dev server :5173 -> /api 代理 -> Agent API :8000
```

Agent API 接口包括：

| 接口 | 方法 | 说明 |
| --- | --- | --- |
| `/api/agent/session` | `POST` | 创建内存会话 |
| `/api/agent/send` | `POST` | 发送用户消息 |
| `/api/agent/stream` | `GET` | SSE 消费响应片段 |
| `/` | `GET` | 返回 `web/index.html` |

如果你改用 `8001` 启动 Agent API，需要同步修改 `web/vue/vite.config.js`：

```js
proxy: {
  '/api': 'http://127.0.0.1:8001'
}
```

否则 Vue 控制台会出现类似错误：

```text
[vite] http proxy error: /api/agent/session
AggregateError [ECONNREFUSED]
```

这表示 Vite 代理连接不到目标 Agent API 端口。当前 SSE 会返回结构化事件：`message_start`、`markdown_delta`、`ui_block`、`message_done`，前端据此渲染 Markdown 和嵌入式 A2UI 表单。

验证 A2UI 表单：

1. 启动 Agent API 和 Vue 前端。
2. 在输入框发送 `预约机位表单`。
3. 确认回复中出现可填写表单。
4. 先直接提交，确认必填字段错误会显示在字段下方。
5. 填写后提交表单，确认表单变成只读摘要，右侧上下文面板出现最近表单信息，并继续把结构化提交发回 Agent。

## 5. 验证项目

安装 Python 依赖后，运行：

```bash
python3 test/verify_project.py
python3 test/test_auth.py
```

如果未安装依赖，常见失败是：

```text
ModuleNotFoundError: No module named 'dotenv'
ModuleNotFoundError: No module named 'langchain_core'
ModuleNotFoundError: No module named 'langgraph'
```

当前测试套件还有一个历史问题：部分脚本仍引用早期的 `query_devices`、`create_experiment` 等工具名，而当前工具层已经扩展为 87 个后端 API 工具。因此，若依赖安装完成后仍出现旧工具名相关失败，应优先更新测试，而不是回退工具实现。

## 6. 当前能力速览

当前 Agent 的主要链路：

```text
用户输入
  -> LabAgent
  -> LangGraph agent node 调用 DeepSeek
  -> LLM 判断是否需要工具
  -> tool_executor 执行业务工具
  -> 工具结果回到 LLM
  -> 返回最终响应
```

工具层已覆盖：

- 登录和会话认证。
- 机位预约、可用机位、房间、个人预约、取消预约。
- 教室预约、教室状态、教室列表和预约记录。
- 设备、耗材、设备借用记录。
- 用户查询、导师、最近导出文件。
- 报修记录、报修图片、结果和反馈。
- 工位、统计、巡查、数据中心申请和审批。

未登录时，除 `login_user` 外的业务工具默认不会请求后端，会直接返回“未登录”错误。

## 7. 常见问题

**`DEEPSEEK_API_KEY 环境变量未设置`**

确认 `.env` 存在，并且从项目根目录启动命令。`src/config/llm_config.py` 会通过 `python-dotenv` 读取 `.env`。

**`python: command not found`**

使用 `python3`，例如 `python3 -m src`。

**启动 Web 原型时报后端连接失败**

Web 原型和实验室管理系统后端是两个服务。`uvicorn src.webserver:app` 只启动 Agent Web 层；业务接口仍需要 `LAB_API_BASE_URL` 指向的后端可访问。

**登录后工具仍提示未认证**

Web 模式会在 Agent 执行后同步工具层的认证上下文。CLI 模式目前主要是对话入口，没有持久化登录态存储；如需稳定的登录态流程，优先走 Web session 或扩展 CLI 会话状态。

**测试结果和 README 不一致**

以当前源码和根目录 `README.md` 为准。测试和 `doc/ARCHITECTURE.md` 中有早期占位工具的遗留描述，需要后续同步。
