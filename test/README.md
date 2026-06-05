# 🧪 测试套件

SELABS Agent 项目的完整测试套件，包括基础功能测试、集成流程测试、项目验证和报告生成。

## 📋 测试文件说明

| 文件 | 描述 | 用例数 | 运行时间 |
|------|------|--------|---------|
| `test_basic.py` | 基础功能测试 | 7 | ~5s |
| `test_integration.py` | 集成流程测试 | 8 | ~10s |
| `test_report.py` | 测试报告生成 | - | ~5s |
| `verify_project.py` | 项目结构验证 | - | ~2s |
| `test_backend_full.py` | 后端接口完整测试 | - | ~30s |
| `diagnose_backend.py` | 后端接口诊断脚本 | - | ~15s |

## 🚀 快速运行

从项目根目录运行以下命令：

### 运行所有测试

```bash
# 基础功能测试
python test/test_basic.py

# 集成流程测试
python test/test_integration.py

# 生成完整报告
python test/test_report.py

# 验证项目结构
python test/verify_project.py

# 后端接口完整测试
python test/test_backend_full.py

# 后端接口诊断
python test/diagnose_backend.py
```

## 📊 测试覆盖

### 基础功能测试 (test_basic.py)

✓ 模块导入
✓ API 配置加载
✓ 工具调用
✓ Agent 状态定义
✓ 错误处理
✓ 环境变量配置
✓ Agent 初始化

**无需 API Key** - 可直接运行

### 集成流程测试 (test_integration.py)

✓ Agent 图结构
✓ 状态管理
✓ 工具调用流程
✓ 错误恢复机制
✓ 消息流转
✓ 多轮对话场景
✓ 配置系统
✓ 并行工具调用

**无需 API Key** - 使用 Mock LLM

### 项目验证 (verify_project.py)

✓ 文件结构完整性
✓ 模块导入正确性
✓ 工具定义有效性

## 📈 最新测试结果

```
测试时间: 2026-05-13 16:43:14

基础功能测试:  7/7 ✓
集成流程测试:  8/8 ✓
项目结构验证:  ✓

总计: 15 个检查项 全部通过 ✓
```

## 🔍 测试详情

### test_basic.py

基础功能测试 - 无需配置即可验证项目结构和基本功能

```bash
python test/test_basic.py

# 输出示例：
# 测试 1: 模块导入          ✓
# 测试 2: API 配置加载      ✓
# 测试 3: 工具调用          ✓
# 测试 4: Agent 状态定义   ✓
# 测试 5: 错误处理          ✓
# 测试 6: 环境变量配置     ✓
# 测试 7: Agent 初始化      ✓
# 
# ✅ 所有基础测试通过！
```

### test_integration.py

集成流程测试 - 验证 Agent 的完整工作流程

```bash
python test/test_integration.py

# 输出示例：
# 集成测试 1: Agent 图结构       ✓
# 集成测试 2: 状态管理            ✓
# 集成测试 3: 工具调用流程       ✓
# 集成测试 4: 错误恢复机制       ✓
# 集成测试 5: 消息流转            ✓
# 集成测试 6: 多轮对话场景       ✓
# 集成测试 7: 配置系统            ✓
# 集成测试 8: 并行工具调用       ✓
#
# ✅ 集成测试全部通过！
```

### test_report.py

生成完整的测试报告

```bash
python test/test_report.py

# 输出包括：
# - 测试结果概览
# - 项目统计信息
# - 已实现功能清单
# - 测试覆盖范围
# - 后续步骤
# - 诊断信息
```

### verify_project.py

验证项目结构

```bash
python test/verify_project.py

# 输出示例：
# 检查文件结构...          ✓
# 检查项目导入...          ✓
# 检查工具定义...          ✓
# 
# 🎉 所有检查通过！项目结构正确。
```

## ⚙️ 测试要求

- Python 3.12+
- 虚拟环境已激活
- 依赖包已安装 (`pip install -r requirements.txt`)

**API Key** - 基础测试和集成测试都不需要真实的 API Key

## 🐛 调试技巧

### 启用详细输出

测试脚本会自动输出详细信息。如需更多调试信息，编辑文件添加：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 运行单个测试函数

```python
# test_basic.py 中
python -c "from test.test_basic import test_imports; test_imports()"
```

### 检查依赖

```bash
python -c "import langgraph; import langchain; print('✓ 依赖正常')"
```

## 📝 添加新测试

1. 在 `test_basic.py` 或 `test_integration.py` 中添加新函数
2. 以 `test_` 开头命名
3. 在 `main()` 函数中调用该函数

示例：

```python
def test_new_feature():
    """测试新功能"""
    print("\n" + "="*60)
    print("测试: 新功能")
    print("="*60)
    
    try:
        # 测试代码
        assert True, "测试通过"
        print("✓ 新功能测试通过")
        return True
    except Exception as e:
        print(f"✗ 错误: {e}")
        return False
```

## 🎯 测试策略

- **单元测试**: 各个模块独立功能
- **集成测试**: 模块间的协作
- **端到端测试**: 完整的用户流程
- **性能测试**: 并发和响应时间

## 📞 常见问题

**Q: 测试失败怎么办？**  
A: 查看错误信息，检查依赖是否完整。运行 `test/verify_project.py` 诊断问题。

**Q: 需要 API Key 才能测试吗？**  
A: 不需要。基础和集成测试都不需要真实的 API Key。

**Q: 如何在 CI/CD 中运行？**  
A: 参见项目根目录的 QUICKSTART.md

---

**相关文档**：
- [项目 README](../README.md)
- [快速开始](../doc/QUICKSTART.md)
- [架构设计](../doc/ARCHITECTURE.md)
