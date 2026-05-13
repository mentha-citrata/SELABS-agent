# 🚀 快速开始指南

## 安装和运行（5分钟）

### 步骤 1: 环境配置

```bash
# 进入项目目录
cd /Users/yuhanli/codeProject/SELABS-agent

# 创建 .env 文件
cp .env.example .env

# 编辑 .env，添加你的 DeepSeek API Key
# 用编辑器打开 .env，找到 DEEPSEEK_API_KEY=... 这一行，填入你的 API Key
```

**`.env` 文件示例**（编辑后的样子）：
```
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
DEEPSEEK_MODEL=deepseek-chat
LAB_API_BASE_URL=http://localhost:8000/api
LAB_API_TIMEOUT=30
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=2048
DEBUG=False
```

### 步骤 2: 安装依赖

```bash
# 使用 pip 安装所有依赖
pip install -r requirements.txt

# 或者使用 Python 3.12（如果系统有多个版本）
/opt/homebrew/bin/python3.12 -m pip install -r requirements.txt
```

### 步骤 3: 验证项目

```bash
# 运行验证脚本（检查项目结构，不需要 API Key）
python verify_project.py

# 或使用 Python 3.12
/opt/homebrew/bin/python3.12 verify_project.py
```

**预期输出**：
```
🔍 SELABS Agent 项目验证

============================================================
检查文件结构...
============================================================
✓ requirements.txt (xxx bytes)
✓ .env.example (xxx bytes)
... (其他文件)

... (更多输出)

🎉 所有检查通过！项目结构正确。
```

### 步骤 4: 启动 Agent

**交互式模式（推荐）**：
```bash
python main.py

# 或使用 Python 3.12
/opt/homebrew/bin/python3.12 main.py
```

**单条查询模式**：
```bash
python main.py "查询所有设备"
```

## 交互式使用示例

```
============================================================
欢迎使用实验室管理助手 Agent
============================================================

功能说明:
  • 查询设备、实验、预约等信息
  • 创建和修改实验、预约等
  • 支持自然语言交互

输入说明:
  • 输入 'quit' 或 'exit' 退出
  • 输入 'clear' 清空对话历史
  • 输入 'help' 获取帮助信息

============================================================

你: 查询一下有哪些实验设备

Agent 正在处理... 
Agent: [实验设备查询功能待实现，架构已支持调用] ...

你: 帮我预约一个讨靠仪器下午2点到3点
Agent 正在处理...
Agent: [预约创建功能待实现，架构已支持调用] ...

你: quit
再见! 👋
```

## 特殊命令

在交互式模式下输入以下命令：

| 命令 | 作用 |
|------|------|
| `help` | 显示使用帮助 |
| `clear` | 清空对话历史，开始新对话 |
| `quit` / `exit` | 退出 Agent |

## 项目架构速览

```
用户输入
    ↓
┌─────────────────┐
│  Agent Node     │ ← LLM 处理消息
│  (LLM.invoke)   │
└────────┬────────┘
         │
    是否调用工具？
    ↙          ↘
   否           是
    ↓           ↓
[End]    [Tool Executor] → 调用工具函数
         (query_devices, 
          create_experiment, 等)
         ↓
    返回结果
```

## 已实现的功能

✅ **Agent 框架**
- ReAct 风格的对话 Agent
- 多轮对话支持（保持对话历史）
- 工具调用和执行流程

✅ **LLM 集成**
- DeepSeek LLM 连接（通过 LangChain）
- 可配置的参数（温度、max_tokens 等）

✅ **工具占位符**（6 个工具，架构支持后续接入真实 API）
- `query_devices` - 查询设备
- `query_experiments` - 查询实验
- `query_reservations` - 查询预约
- `create_experiment` - 创建实验
- `create_reservation` - 创建预约
- `update_experiment` - 更新实验

✅ **错误处理**
- 统一的错误返回格式
- 用户友好的错误消息

## 后续开发指南

### 1. 实现真实的 API 调用

修改 `tools/tool_definitions.py`：

```python
from config.api_config import APIConfig
import requests

@tool
def query_devices(device_id: Optional[str] = None) -> dict:
    """查询设备信息"""
    try:
        # 实际 API 调用
        response = requests.get(
            f"{APIConfig.BASE_URL}/devices",
            params={"device_id": device_id},
            timeout=APIConfig.TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
```

### 2. 添加新工具

在 `tools/tool_definitions.py` 中添加新工具函数并加到 `TOOLS` 列表。

### 3. 跨模块的功能

参考 `agent/agent.py` 中的 `run_with_history()` 方法实现多轮对话。

## 常见问题

**Q: 怎样获取 DeepSeek API Key?**  
A: 访问 https://platform.deepseek.com，注册账号后在仪表板生成 API Key

**Q: 可以用其他 LLM 吗?**  
A: 可以。修改 `config/llm_config.py` 中的 LLM 配置

**Q: 如何调试 Agent 的工具调用?**  
A: 在 `.env` 中设置 `DEBUG=True`，查看详细的日志输出

**Q: 支持并发请求吗?**  
A: 当前版本是单线程设计。后续可集成异步支持

## 获取更多帮助

- 查看 [README.md](README.md) 了解详细的项目说明
- 查看各个模块的代码注释了解实现细节
- 检查 `verify_project.py` 诊断项目问题

---

**祝你好运！🎉**

有任何问题，欢迎反馈！
