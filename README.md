# SELABS Agent - 实验室管理系统辅助 Agent

基于 LangGraph 框架和 DeepSeek LLM 的对话 Agent，用于实验室管理系统的智能助手。

## 📋 项目概述

- **框架**: LangGraph + LangChain
- **LLM**: DeepSeek 
- **语言**: Python 3.12+
- **架构**: ReAct（推理+执行）模式
- **功能**: 多轮对话、工具调用、自动决策

## 🏗️ 项目结构

```
SELABS-agent/
├── agent/                  # Agent 核心实现
│   ├── __init__.py
│   ├── state.py           # 状态定义
│   └── agent.py           # ReAct Agent 实现
├── config/                # 配置模块
│   ├── __init__.py
│   ├── llm_config.py     # DeepSeek LLM 配置
│   └── api_config.py     # 实验室 API 配置
├── tools/                # 工具定义
│   ├── __init__.py
│   └── tool_definitions.py  # 6 个工具函数
├── utils/                # 工具函数
│   ├── __init__.py
│   └── error_handler.py  # 错误处理
├── test/                 # 测试套件
│   ├── __init__.py
│   ├── test_basic.py        # 基础功能测试 (7 用例)
│   ├── test_integration.py  # 集成流程测试 (8 用例)
│   ├── test_report.py       # 测试报告生成器
│   └── verify_project.py    # 项目验证脚本
├── doc/                  # 项目文档
│   ├── __init__.py
│   ├── README.md           # 项目详细说明
│   ├── QUICKSTART.md       # 快速开始指南
│   └── ARCHITECTURE.md     # 架构设计文档
├── main.py              # CLI 入口程序
├── examples.py          # 使用示例
├── requirements.txt     # 依赖声明
├── .env.example         # 环境变量模板
├── .gitignore          # Git 忽略配置
└── README.md           # 本文件
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 进入项目目录
cd SELABS-agent

# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入 DEEPSEEK_API_KEY
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
```

### 2. 安装依赖

```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 验证项目

```bash
# 运行项目验证
python test/verify_project.py

# 运行基础功能测试
python test/test_basic.py

# 运行集成测试
python test/test_integration.py
```

### 4. 启动 Agent

```bash
# 交互模式
python main.py

# 单查询模式
python main.py "查询设备"
```

## 📚 文档说明

- **[doc/README.md](doc/README.md)** - 完整的项目说明和 API 文档
- **[doc/QUICKSTART.md](doc/QUICKSTART.md)** - 5分钟快速开始指南
- **[doc/ARCHITECTURE.md](doc/ARCHITECTURE.md)** - 详细的架构设计文档

## 🧪 测试说明

### 测试套件

| 测试文件 | 用例数 | 说明 |
|---------|--------|------|
| test/test_basic.py | 7 | 基础功能测试 |
| test/test_integration.py | 8 | 集成流程测试 |
| test/test_report.py | - | 测试报告生成 |
| test/verify_project.py | - | 项目结构验证 |

### 运行测试

```bash
# 基础功能测试
python test/test_basic.py

# 集成流程测试
python test/test_integration.py

# 生成测试报告
python test/test_report.py

# 项目结构验证
python test/verify_project.py
```

## 💡 功能特性

### Agent 框架
- ✓ ReAct（推理+执行）模式
- ✓ 基于 LangGraph 的状态管理
- ✓ 单轮和多轮对话支持
- ✓ 自动工具调用和结果处理

### 工具系统
- ✓ 6 个预置工具（3 查询 + 3 创建/修改）
- ✓ 占位符实现，支持后续扩展
- ✓ 工具自动选择和并行调用

### 交互模式
- ✓ 交互式 CLI（支持多轮对话）
- ✓ 单查询命令行模式
- ✓ 编程接口（易于系统集成）

## 📖 使用示例

### 交互模式

```bash
$ python main.py

你: 查询设备
Agent: [处理中...]

你: 帮我创建一个新实验
Agent: [处理中...]

你: quit
再见!
```

### 编程使用

```python
from agent.agent import LabAgent

agent = LabAgent()

# 单轮对话
response = agent.run("查询设备")

# 多轮对话
messages = ["查询设备", "显微镜在哪里？"]
response = agent.run_with_history(messages)
```

## 🔧 配置说明

编辑 `.env` 文件配置以下环境变量：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| DEEPSEEK_API_KEY | DeepSeek API 密钥 | 必需 |
| DEEPSEEK_MODEL | LLM 模型名称 | deepseek-chat |
| LAB_API_BASE_URL | 实验室 API 基础 URL | http://localhost:8000/api |
| LAB_API_TIMEOUT | API 请求超时(秒) | 30 |
| AGENT_TEMPERATURE | LLM 温度参数(0-1) | 0.7 |
| AGENT_MAX_TOKENS | LLM 最大输出 token | 2048 |

## 📊 测试结果

最新测试（2026-05-13）：

```
基础功能测试: 7/7 ✓
集成流程测试: 8/8 ✓
项目结构验证: ✓
------
总计: 15/15 ✓
```

详见 [test_report.py](test/test_report.py) 的完整报告。

## 🛠️ 后续开发

### 实现真实 API 调用

编辑 `tools/tool_definitions.py`，将占位符替换为实际 API 调用：

```python
@tool
def query_devices(...) -> dict:
    """查询设备"""
    response = requests.get(f"{APIConfig.BASE_URL}/devices")
    return response.json()
```

### 添加新工具

1. 在 `tools/tool_definitions.py` 中定义新工具
2. 添加到 `TOOLS` 列表
3. LLM 自动可用！

## 📝 许可证

待定

## 👥 贡献

欢迎提交 Issue 和 Pull Request

---

**快速链接**：
- 📖 [完整文档](doc/README.md)
- 🚀 [快速开始](doc/QUICKSTART.md)
- 🏗️ [架构设计](doc/ARCHITECTURE.md)
- 🧪 [测试](test/)

**需要帮助？** 查看 `doc/QUICKSTART.md` 或 `doc/README.md` 获取详细信息。
