# 📐 系统架构设计文档

## 目录
1. [整体架构](#整体架构)
2. [数据流](#数据流)
3. [核心模块](#核心模块)
4. [状态管理](#状态管理)
5. [工具系统](#工具系统)
6. [扩展指南](#扩展指南)

---

## 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     用户交互层                                 │
│  (main.py - CLI 交互式模式 / 单查询模式)                      │
└────────────────────┬────────────────────────────────────────┘
                     │ 用户输入
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Agent                            │
│                   (agent/agent.py)                            │
│                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │  Agent Node  │───▶│  Decision    │───▶│  Tool        │   │
│  │ (LLM.invoke) │    │  (Should use │    │  Executor    │   │
│  │              │    │   tool?)     │    │  Node        │   │
│  └──────────────┘    └──────────────┘    └──────────────┘   │
│         ▲                                         │            │
│         └─────────────────────────────────────────┘            │
│                    (循环)                                      │
│                                                                │
│  ┌─────────────────────────────────┐                          │
│  │      Agent 状态 (AgentState)    │                          │
│  │  - messages: List[BaseMessage]  │                          │
│  │  - 维护对话历史                  │                          │
│  └─────────────────────────────────┘                          │
└────────────────────┬────────────────────────────────────────┘
                     │ 工具调用
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   工具执行层                                   │
│              (tools/tool_definitions.py)                      │
│                                                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐          │
│  │ query_*      │ │ create_*     │ │ update_*     │          │
│  │ (查询操作)   │ │ (创建操作)   │ │ (更新操作)   │          │
│  └──────────────┘ └──────────────┘ └──────────────┘          │
└────────────────────┬────────────────────────────────────────┘
                     │ API 调用
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                 实验室管理系统 API                              │
│          (待实现 - tools/api_client.py)                       │
│                                                                │
│  • /devices      (设备模块)                                    │
│  • /experiments  (实验模块)                                    │
│  • /reservations (预约模块)                                    │
│  • 等...                                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 数据流

### 单轮对话流程

```
1. 用户输入
   "查询有哪些显微镜设备"
        ↓
2. 构建初始状态
   {
     "messages": [
       HumanMessage("查询有哪些显微镜设备")
     ]
   }
        ↓
3. Agent Node 运行
   • 调用 LLM（DeepSeek）
   • LLM 分析用户意图
   • LLM 返回工具调用决策
   
   LLM 响应:
   {
     "tool_calls": [
       {
         "name": "query_devices",
         "id": "tool_1",
         "args": {"device_type": "显微镜"}
       }
     ]
   }
        ↓
4. 判断是否需要工具
   • should_use_tool() 检查工具调用列表
   • 有工具调用 → "tool" 分支
        ↓
5. Tool Executor Node 运行
   • 提取工具名称和参数
   • 调用 query_devices(device_type="显微镜")
   • 获取执行结果（目前是占位符）
   
   工具返回:
   {
     "status": "pending",
     "message": "设备查询功能待实现",
     "query_params": {"device_type": "显微镜"}
   }
   
   • 添加 ToolMessage 到状态
        ↓
6. 返回 Agent Node（循环）
   • LLM 收到工具结果
   • LLM 处理结果，生成自然语言响应
   
   LLM 响应:
   "正在处理您的查询...目前支持的设备有..."
   
   • 检查是否还需要工具 → 无 → "end" 分支
        ↓
7. End Node 运行
   • 返回最终状态
        ↓
8. 提取响应并返回给用户
   "正在处理您的查询...目前支持的设备有..."
```

### 多轮对话流程

```
用户消息 1: "查询设备"
    ↓
Agent 处理并返回结果
    ↓
用户消息 2: "其中哪个支持实时成像?"
    ↓
Agent 处理时可以访问消息历史:
[
  HumanMessage("查询设备"),
  AIMessage("...设备列表..."),
  ToolMessage("query_devices 结果"),
  HumanMessage("其中哪个支持实时成像?"),
]
    ↓
LLM 可基于上下文理解新问题
    ↓
返回回答
```

---

## 核心模块

### 1. **config 模块** - 配置管理

**llm_config.py**
```python
get_llm() → ChatOpenAI
```
- 初始化 DeepSeek LLM 连接
- 加载环境变量配置
- 可配置参数：温度、max_tokens 等

**api_config.py**
```python
class APIConfig
  - BASE_URL: API 基础地址
  - TIMEOUT: 请求超时
  - ENDPOINTS: API 端点映射
```
- 存储实验室 API 配置
- 定义 6 个主要模块的端点

### 2. **tools 模块** - 工具定义

**tool_definitions.py** - 使用 `@tool` 装饰器定义工具

```python
@tool
def query_devices(...) → dict

@tool
def query_experiments(...) → dict

@tool
def query_reservations(...) → dict

@tool
def create_experiment(...) → dict

@tool
def create_reservation(...) → dict

@tool
def update_experiment(...) → dict

TOOLS = [...]  # 导出给 Agent 使用
```

**特点**：
- 占位符实现，返回结构化数据
- 包含清晰的文档字符串（LLM 可理解）
- 支持可选参数和多种操作类型
- 易于后续替换为真实 API 调用

### 3. **agent 模块** - Agent 核心

**state.py** - 状态定义

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], "对话消息列表"]
```

**agent.py** - Agent 实现

```python
class LabAgent:
    def __init__(self)
    
    def _build_graph(self) → StateGraph
    def _agent_node(state) → state  # LLM 处理
    def _tool_executor_node(state) → state  # 执行工具
    def _should_use_tool(state) → str  # 判断条件
    def _end_node(state) → state  # 返回响应
    
    def run(user_message) → str  # 单轮对话
    def run_with_history(messages) → str  # 多轮对话
```

**核心机制**：
- 使用 StateGraph 构建有向图
- 四个节点：agent、tool_executor、end、decision
- 条件边：根据 LLM 输出判断是否使用工具
- 循环支持：工具执行后回到 agent 重新思考

### 4. **utils 模块** - 工具函数

**error_handler.py**
```python
def handle_api_error(error) → str  # API 错误处理
def handle_llm_error(error) → str  # LLM 错误处理
def format_tool_result(result) → dict  # 结果格式化
```

---

## 状态管理

### AgentState 结构

```python
{
    "messages": [
        HumanMessage("用户第一句"),
        AIMessage("Agent 第一个响应"),
        ToolMessage("工具执行结果"),
        HumanMessage("用户第二句"),
        AIMessage("Agent 第二个响应"),
        ...
    ]
}
```

**消息类型**：
- `HumanMessage`: 用户输入
- `AIMessage`: LLM 生成的回复（可能包含工具调用指令）
- `ToolMessage`: 工具执行结果

**消息流向**：
1. 用户输入 → HumanMessage
2. Agent 调用 LLM → AIMessage（包含 tool_calls 或最终响应）
3. 检查是否有 tool_calls → 如果有，执行并创建 ToolMessage
4. 重新调用 LLM，提供之前的所有消息和工具结果
5. LLM 基于历史进行理解和回复

---

## 工具系统

### 工具定义约定

每个工具使用 `@tool` 装饰器，支持以下特性：

```python
@tool
def tool_name(
    param1: str,
    param2: Optional[int] = None
) -> dict:
    """清晰的中文文档说明
    
    这个文档会被 LLM 读取用于理解工具功能
    
    Args:
        param1: 参数说明
        param2: 参数说明
        
    Returns:
        dict: 返回值说明
    """
    # 实现逻辑
    return {...}
```

### 当前工具列表

| 工具 | 类型 | 参数 | 说明 |
|------|------|------|------|
| `query_devices` | 查询 | device_id, device_type | 查询设备信息 |
| `query_experiments` | 查询 | experiment_id, status | 查询实验 |
| `query_reservations` | 查询 | user_id, device_id | 查询预约 |
| `create_experiment` | 创建 | name, description, device_id | 创建实验 |
| `create_reservation` | 创建 | user_id, device_id, time | 创建预约 |
| `update_experiment` | 修改 | experiment_id, status | 更新实验 |

### 工具执行流程

```
1. LLM 分析用户意图
   ↓
2. LLM 决定调用哪个工具（可能多个）
   ↓
3. LLM 返回 tool_calls 列表:
   [
     {
       "name": "query_devices",
       "id": "tool_1",
       "args": {"device_type": "显微镜"}
     }
   ]
   ↓
4. Tool Executor 遍历 tool_calls
   ↓
5. 对每个 tool call:
   - 从 TOOLS 字典获取工具函数
   - 调用工具: tool.invoke(args)
   - 捕获异常，返回统一错误格式
   ↓
6. 创建 ToolMessage 添加到状态
   ↓
7. 返回 Agent Node（LLM 再次处理）
```

---

## 扩展指南

### 添加新工具

**步骤 1**: 在 `tools/tool_definitions.py` 中定义

```python
@tool
def new_feature(param1: str) -> dict:
    """新功能的中文说明"""
    # 实现逻辑
    return {"status": "pending", "message": "功能待实现"}
```

**步骤 2**: 添加到 TOOLS 列表

```python
TOOLS = [
    # ... 现有工具
    new_feature,
]
```

**步骤 3**: 测试工具

```python
from tools.tool_definitions import new_feature
result = new_feature.invoke({"param1": "test"})
print(result)
```

### 实现真实 API 调用

**示例**：实现 query_devices

```python
import requests
from config.api_config import APIConfig
from utils.error_handler import handle_api_error

@tool
def query_devices(device_id: Optional[str] = None, 
                   device_type: Optional[str] = None) -> dict:
    """查询设备信息"""
    try:
        # 构建请求参数
        params = {}
        if device_id:
            params["id"] = device_id
        if device_type:
            params["type"] = device_type
        
        # 发送 HTTP 请求
        response = requests.get(
            f"{APIConfig.BASE_URL}/devices",
            params=params,
            timeout=APIConfig.TIMEOUT
        )
        response.raise_for_status()
        
        # 返回 API 响应
        return response.json()
        
    except requests.exceptions.RequestException as e:
        return {
            "error": handle_api_error(e),
            "details": str(e)
        }
    except Exception as e:
        return {
            "error": handle_api_error(e),
            "details": str(e)
        }
```

### 自定义 Agent 行为

修改 `agent/agent.py` 中的方法：

```python
def _agent_node(self, state: AgentState) -> AgentState:
    """可自定义 LLM 调用行为"""
    # 例如：添加系统提示词
    system_prompt = """你是实验室管理助手..."""
    
    # 例如：修改模型温度
    custom_llm = self.llm.with_config(
        temperature=0.5
    )
    
    # 自定义逻辑...
```

### 添加认证和日志

**添加简单日志**：

```python
import logging

logger = logging.getLogger(__name__)

# 在 Agent 中
logger.info(f"User query: {user_message}")
logger.debug(f"Tool calls: {tool_calls}")
logger.error(f"API error: {error}")
```

---

## 性能和扩展性

### 当前限制

- **单线程**: 一次只处理一个对话
- **消息历史**: 所有消息存在内存中
- **Token 限制**: API 请求可能受 token 限制

### 优化方向

1. **异步支持**: 使用 `aiohttp` 进行并发 API 调用
2. **消息压缩**: 对长对话进行摘要处理
3. **缓存**: 缓存常见查询结果
4. **数据库**: 使用数据库存储对话历史

---

## 调试技巧

### 启用调试模式

在 `.env` 中设置：
```
DEBUG=True
```

### 查看 LLM 的决策

在 `agent.py` 中修改 `_agent_node`：

```python
print(f"LLM Response: {response}")
print(f"Tool Calls: {response.tool_calls}")
```

### 追踪状态变化

```python
print(f"State before: {state}")
# 执行操作
print(f"State after: {state}")
```

---

## 总结

本架构采用 ReAct（Reasoning + Acting）模式，具有以下特点：

✅ **清晰的数据流**: 用户输入 → 判断 → 工具执行 → 响应
✅ **灵活的循环**: 支持多步骤推理和多次工具调用
✅ **易于扩展**: 新工具只需添加函数并加到列表
✅ **多轮对话**: 自动维护消息历史
✅ **错误容错**: 统一的错误处理机制

适合构建复杂的 AI 助手和自动化系统。
