# 📚 文档索引

欢迎来到 SELABS Agent 文档中心。

## 📖 文档清单

### [README.md](README.md) - 完整项目说明
详细的项目文档，包含：
- 项目结构和组织方式
- 完整的使用指南
- API 和工具参考
- 配置参数说明
- 故障排查方法
- 后续扩展指南

**阅读时间**: 20-30 分钟

### [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
5 分钟快速上手，包含：
- 逐步的配置步骤
- 启动命令和基本用法
- 对话示例
- 特殊命令说明
- 常见问题解答

**阅读时间**: 5-10 分钟

### [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计文档
深入理解系统设计，包含：
- 整体架构图和工作流程
- 核心模块说明
- 状态管理机制
- 工具系统设计
- 性能优化方向
- 扩展开发指南

### [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) - 后端接口测试总结
记录最近一次后端接口验证结果，包含：
- 登录与认证验证结果
- Core API 可用性与权限限制
- 后端技术栈与测试结论

**阅读时间**: 25-35 分钟

## 🎯 快速导航

### 我是新用户，想快速开始
→ 先看 [QUICKSTART.md](QUICKSTART.md)（5 分钟）  
→ 再看 [README.md](README.md) 中的使用示例（10 分钟）

### 我是开发者，想深入理解
→ 先看 [README.md](README.md)（20 分钟）  
→ 再看 [ARCHITECTURE.md](ARCHITECTURE.md)（30 分钟）  
→ 查看源代码注释

### 我想解决问题
→ 查看 [README.md](README.md#-故障排查)

### 我想扩展功能
→ 先看 [ARCHITECTURE.md](ARCHITECTURE.md#扩展指南)（10 分钟）  
→ 再看具体代码实现

### 我想配置环境
→ 查看 [QUICKSTART.md](QUICKSTART.md#步骤-1-环境配置)  
或 [README.md](README.md#-配置说明)

## 📚 按主题分类

### 🚀 快速开始
- [QUICKSTART.md](QUICKSTART.md) - 5 分钟快速开始
- [README.md - 快速开始章节](README.md#-快速开始)

### ⚙️ 配置和环境
- [README.md - 配置说明](README.md#-配置说明)
- [ARCHITECTURE.md - API 配置](ARCHITECTURE.md#3-api-模块---配置管理)

### 🛠️ 功能和 API
- [README.md - 可用工具](README.md#-可用工具当前占位符实现)
- [README.md - 对话示例](README.md#-对话示例)
- [ARCHITECTURE.md - 工具系统](ARCHITECTURE.md#工具系统)

### 🏗️ 架构和设计
- [ARCHITECTURE.md - 整体架构](ARCHITECTURE.md#整体架构)
- [ARCHITECTURE.md - 数据流](ARCHITECTURE.md#数据流)
- [ARCHITECTURE.md - 核心模块](ARCHITECTURE.md#核心模块)

### 🔧 开发和扩展
- [ARCHITECTURE.md - 扩展指南](ARCHITECTURE.md#扩展指南)
- [ARCHITECTURE.md - 其他优化](ARCHITECTURE.md#性能和扩展性)

### 🐛 问题排查
- [README.md - 故障排查](README.md#-故障排查)
- [QUICKSTART.md - 常见问题](QUICKSTART.md#-常见问题)
- [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md)

## 💡 关键概念

### Agent 工作流程
用户输入 → LLM 分析 → 判断是否需要工具 → 工具执行 → LLM 生成响应

详见 [ARCHITECTURE.md - 数据流](ARCHITECTURE.md#数据流)

### 支持的操作类型
1. **查询**: 查询设备、实验、预约信息
2. **创建**: 创建实验、预约
3. **更新**: 更新实验状态

### 工具列表
- query_devices - 查询设备信息
- query_experiments - 查询实验信息
- query_reservations - 查询预约信息
- create_experiment - 创建新实验
- create_reservation - 创建设备预约
- update_experiment - 更新实验状态

詳見 [README.md - 工具参考](README.md#-可用工具当前占位符实现)

## 📊 文档统计

| 文档 | 字数 | 代码例 | 表格 | 图表 |
|------|------|--------|------|------|
| README.md | ~6,000 | 8+ | 8+ | 2+ |
| QUICKSTART.md | ~4,000 | 5+ | 2+ | 1+ |
| ARCHITECTURE.md | ~12,000 | 15+ | 5+ | 5+ |
| **总计** | **22,000+** | **28+** | **15+** | **8+** |

## ⏱️ 推荐学习路径

### 初级 (30 分钟)
1. 本文 (2 min)
2. QUICKSTART.md (5 min)
3. README.md 的使用示例 (10 min)
4. 实际运行 Agent (10 min)
5. 阅读 test/README.md (3 min)

### 中级 (60 分钟)
1. README.md 完整阅读 (20 min)
2. ARCHITECTURE.md 浏览 (15 min)
3. 查看源代码 (15 min)
4. 编写测试用例 (10 min)

### 高级 (120+ 分钟)
1. ARCHITECTURE.md 详细阅读 (30 min)
2. 深入研究源代码 (40 min)
3. 扩展工具功能 (30 min)
4. 性能优化 (20+ min)

## 🔗 相关链接

- **项目根目录**: [../README.md](../README.md)
- **测试文档**: [../test/README.md](../test/README.md)
- **测试代码**: [../test/](../test/)
- **源代码**: [../](../)

## 📝 文档版本

最后更新: 2026-05-13  
文档版本: 1.0  
项目版本: 1.0

## 🤝 支持

遇到问题？  
→ 查看 [README.md - 故障排查](README.md#-故障排查)  
→ 查看 [test/README.md](../test/README.md) 运行测试  
→ 查看源代码中的注释

---

**开始阅读**: [QUICKSTART.md](QUICKSTART.md) ← 从这里开始！
