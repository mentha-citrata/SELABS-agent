# 实验室管理 Agent（LangGraph 版本）

基于 LangGraph 框架和 Python 实现的实验室管理系统辅助 Agent，采用 DeepSeek LLM 驱动。

## 📋 项目结构

```
SELABS-agent/
├── config/                      # 配置模块
│   ├── __init__.py
│   ├── llm_config.py           # DeepSeek LLM 配置
│   └── api_config.py           # 实验室 API 配置
├── tools/                       # 工具定义
│   ├── __init__.py
│   └── tool_definitions.py     # Agent 可用工具定义（占位符实现）
├── agent/                       # Agent 核心逻辑
│   ├── __init__.py
│   ├── state.py                # Agent 状态定义
│   └── agent.py                # Agent 主体实现（ReAct 模式）
├── utils/                       # 工具函数
│   ├── __init__.py
│   └── error_handler.py        # 错误处理模块
├── main.py                      # 程序入口
├── requirements.txt             # 项目依赖
├── .env.example                 # 环境变量示例
└── README.md                    # 此文件
```

## 🚀 快速开始

### 1. 环境配置

创建 `.env` 文件（基于 `.env.example`）：

```bash
cp .env.example .env
```

编辑 `.env` 并填入 DeepSeek API Key：

```
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
LAB_API_BASE_URL=http://localhost:8000/api
LAB_API_TIMEOUT=30
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2048
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行 Agent

**交互式模式（推荐）**：
```bash
python main.py
```

这将启动一个交互式命令行界面，支持多轮对话。

**单查询模式**：
```bash
python main.py "查询所有设备"
```

## 📚 技术架构

### Agent 工作流程

```
user_input
    ↓
[Agent Node] → LLM 处理消息，判断是否需要工具调用
    ↓
    ├─→ 否 → [End Node] → 返回响应
    │
    └─→ 是 → [Tool Executor Node] → 执行工具
         ↓
         循环回 [Agent Node]
```

### 核心组件

- **LLM 配置** (`config/llm_config.py`): 
  - 使用 LangChain 的 `ChatOpenAI` 连接 DeepSeek
  - 支持自定义温度、token 限制

- **Agent 状态** (`agent/state.py`):
  - 基于 `StateGraph` 的状态定义
  - 维护消息历史用于多轮对话

- **Agent 实现** (`agent/agent.py`):
  - **agent_node**: LLM 思考节点，调用 LLM 处理消息
  - **tool_executor_node**: 工具执行节点，运行选定的工具
  - **end_node**: 结束节点，返回最终响应
  - **条件判断**: 根据 LLM 输出决定是否调用工具

- **工具定义** (`tools/tool_definitions.py`):
  - 6 个占位符工具函数（支持后续扩展）
  - 包括查询类和创建/修改类操作
  - 使用 `@tool` 装饰器便于 LLM 调用

## 🛠️ 可用工具（当前占位符实现）

### 查询工具
- `query_devices()` - 查询设备信息
- `query_experiments()` - 查询实验信息
- `query_reservations()` - 查询完约信息

### 创建/修改工具
- `create_experiment()` - 创建新实验
- `create_reservation()` - 创建设备预约
- `update_experiment()` - 更新实验状态

## 💬 对话示例

```
你: 查询一下有哪些设备
Agent: 正在处理...
Agent: [设备查询功能待实现] ...

你: 帮我创建一个新的实验
Agent: 正在处理...
Agent: [实验创建功能待实现] ...
```

## 🔄 多轮对话支持

Agent 支持维护对话上下文，示例：

```
你: 查询设备列表
Agent: [查询结果]

你: 其中显微镜今天下午什么时候有空？
Agent: [分析前面的查询结果，查询预约信息]
```

## ⚙️ 配置说明

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 必需 |
| `DEEPSEEK_MODEL` | LLM 模型名称 | `deepseek-chat` |
| `LAB_API_BASE_URL` | 实验室 API 基础 URL | `http://localhost:8000/api` |
| `LAB_API_TIMEOUT` | API 请求超时时间（秒） | `30` |
| `AGENT_TEMPERATURE` | LLM 温度参数（0-1） | `0.7` |
| `AGENT_MAX_TOKENS` | LLM 最大输出 token 数 | `2048` |
| `DEBUG` | 是否启用调试模式 | `False` |

## 🔧 后续扩展指南

### 实现实际的 API 调用

修改 `tools/tool_definitions.py` 中的工具函数，调用实际的 API：

```python
@tool
def query_devices(device_id: Optional[str] = None) -> dict:
    """查询设备信息"""
    # 替换为实际 API 调用
    from requests import get
    response = get(f"{APIConfig.BASE_URL}/devices")
    return response.json()
```

### 添加新工具

在 `tools/tool_definitions.py` 中定义新工具，并添加到 `TOOLS` 列表：

```python
@tool
def new_tool(param: str) -> dict:
    """新工具的说明"""
    # 实现逻辑
    pass

TOOLS = [
    # ... 现有工具
    new_tool,
]
```

### 完善错误处理

在 `utils/error_handler.py` 中添加更详细的错误类型处理，替代通用错误消息。

### 数据持久化

添加数据库支持以保存对话历史和用户操作记录。

## 📝 命令参考

在交互模式下支持的特殊命令：

- `quit` / `exit` - 退出程序
- `clear` - 清空对话历史
- `help` - 显示帮助信息

## ⚠️ 注意事项

1. **API 密钥安全**：
   - 确保 `.env` 文件不被上传到版本控制
   - 使用环境变量管理敏感信息

2. **依赖版本**：
   - 项目使用特定版本的 langgraph 和 langchain
   - 更新依赖可能需要调整代码

3. **多轮对话**：
   - Agent 维护消息历史，长对话可能消耗更多 token
   - 使用 `clear` 命令重置对话历史

## 📞 故障排查

### 问题：`DEEPSEEK_API_KEY 环境变量未设置`
**解决**：确保 `.env` 文件存在且包含有效的 API Key

### 问题：导入错误
**解决**：确保所有依赖已安装：`pip install -r requirements.txt`

### 问题：LLM 响应缓慢
**解决**：检查网络连接和 DeepSeek API 服务状态

## 📄 许可证

待定

## 👥 贡献

欢迎提交 Issue 和 Pull Request
