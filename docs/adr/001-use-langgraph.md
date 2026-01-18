# ADR-001: 使用 LangGraph 框架

## 状态
已接受 (2026-01-18)

## 背景

我们需要构建一个多 agent 协同开发系统，让多个 AI agents 能够协作完成软件开发任务（需求分析、架构设计、编码、测试、文档等）。需要选择一个合适的框架来组织和协调这些 agents。

### 需求
- 支持多个 agents 之间的协作和消息传递
- 支持复杂的工作流和决策路由
- 支持状态管理和检查点（checkpoint）
- 与 LLM API 良好集成
- 易于调试和可视化
- 开源且有活跃社区

### 评估的方案
1. **LangGraph** - LangChain 团队开发的状态机框架
2. **AutoGen** - Microsoft 的多 agent 框架
3. **CrewAI** - 面向任务的 agent 编排框架
4. **自研框架** - 从零开始构建

## 决策

**选择 LangGraph 作为核心框架**

## 理由

### LangGraph 的优势

1. **强大的状态管理**
   - 基于 `MessagesState` 的状态系统，自然适合对话式交互
   - 内置 checkpoint 机制，支持持久化和恢复
   - 支持分层状态和子图（subgraph）

2. **灵活的图结构**
   - 使用有向图表达工作流，比线性流程更灵活
   - 支持条件路由、循环、并行执行
   - `Command` API 支持动态路由决策

3. **与 LangChain 生态集成**
   - 可以直接使用 LangChain 的工具库（langchain-community）
   - 支持多种 LLM 提供商（Anthropic、OpenAI 等）
   - 丰富的工具和集成

4. **官方多 agent 模式**
   - 官方教程提供了多 agent 协作的最佳实践
   - Supervisor 模式适合我们的架构设计
   - 社区有大量真实案例

5. **开发体验**
   - 可视化工具（LangGraph Studio）
   - 良好的调试支持
   - 清晰的文档和示例

### 与其他方案对比

| 特性 | LangGraph | AutoGen | CrewAI | 自研 |
|------|-----------|---------|--------|------|
| 状态管理 | ✅ 强大 | ✅ 有 | ⚠️ 简单 | ❌ 需从零实现 |
| 工作流灵活性 | ✅ 图结构 | ⚠️ 对话式 | ⚠️ 任务式 | ✅ 完全自定义 |
| LLM 集成 | ✅ 多提供商 | ✅ 多提供商 | ⚠️ 主要 OpenAI | ❌ 需自行集成 |
| 学习曲线 | ⚠️ 中等 | ⚠️ 中等 | ✅ 简单 | ❌ N/A |
| 社区活跃度 | ✅ 高 | ✅ 高 | ⚠️ 中 | ❌ N/A |
| 多项目支持 | ✅ 通过配置 | ✅ 通过配置 | ⚠️ 有限 | ✅ 完全自定义 |
| 开发时间 | ⚠️ 2-3周 | ⚠️ 2-3周 | ✅ 1周 | ❌ 2-3月 |

## 结果

### 正面影响
- 减少 50-70% 的底层框架代码开发时间
- 可以专注于 agent 逻辑和工具开发
- 获得成熟的状态管理和错误处理
- 可视化和调试工具开箱即用
- 社区支持和最佳实践参考

### 负面影响
- 需要学习 LangGraph 的概念和 API
- 框架本身的限制可能影响某些定制需求
- 依赖外部框架的更新和维护

### 风险和缓解

**风险1: 框架更新导致 breaking changes**
- 缓解：使用特定版本固定依赖，谨慎升级
- 监控：关注 LangGraph 的 changelog 和社区讨论

**风险2: 性能问题（图执行开销）**
- 缓解：合理设计图结构，避免过度复杂
- 监控：使用性能分析工具测量实际影响

**风险3: 学习曲线影响开发速度**
- 缓解：先实现简单 MVP，逐步掌握高级特性
- 参考官方教程和示例代码

## 参考资料

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [Multi-Agent Collaboration Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)

## 备注

此决策可能在以下情况下重新评估：
- LangGraph 项目停止维护或出现重大问题
- 发现框架无法满足核心需求
- 出现更优秀的替代方案
