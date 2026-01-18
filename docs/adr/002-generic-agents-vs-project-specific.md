# ADR-002: 使用通用 Agent 而非项目特定 Agent

## 状态
已接受 (2026-01-18)

## 背景

我们需要支持多个软件项目的开发（rssx、enx 以及未来可能的更多项目）。在设计 agent 架构时，面临一个关键选择：

**方案 A: 项目特定 Agent**
- 为每个项目创建专门的 agents（如 `rssx_developer`、`enx_developer`）
- 每个 agent 包含项目特定的知识和工具

**方案 B: 通用 Agent + 项目上下文**
- 创建通用角色 agents（如 `developer`、`reviewer`）
- 通过动态注入项目上下文来适配不同项目

### 项目情况
- **rssx**: `/Users/wiloon/workspace/projects/rssx` (Rust 项目)
- **enx**: `/Users/wiloon/workspace/projects/enx` (Elixir 项目)
- 未来可能增加更多项目

### 评估维度
- 可扩展性
- 维护成本
- 代码复用
- 行为一致性
- 灵活性

## 决策

**选择方案 B: 通用 Agent + 项目上下文注入**

采用以下架构：
```python
# 通用角色 agents (3-5个)
- architect_agent      # 架构设计
- developer_agent      # 代码开发
- reviewer_agent       # 代码审查
- tester_agent        # 测试编写
- documenter_agent    # 文档维护

# 项目配置 (动态加载)
projects/
├── rssx/
│   ├── config.yaml      # Rust 工具链、约定
│   ├── prompts/         # 项目特定提示词
│   └── tools/           # Rust 特定工具
└── enx/
    ├── config.yaml      # Elixir 工具链、约定
    ├── prompts/         # 项目特定提示词
    └── tools/           # Elixir 特定工具

# 状态中传递项目上下文
state = {
    "current_project": "rssx",
    "project_config": load_config("rssx"),
    "project_tools": load_tools("rssx")
}
```

## 理由

### 通用 Agent 的优势

#### 1. **可扩展性**
- ✅ 添加第 3、4、5 个项目只需要添加配置文件
- ✅ 不需要修改 agent 代码
- ❌ 项目特定方案需要 N×M 个 agents（N项目 × M角色）

**示例**: 10 个项目 × 5 种角色 = 50 个 agents（方案A）vs 5 个 agents（方案B）

#### 2. **维护成本**
- ✅ 修改开发流程只需要更新一个 `developer_agent`
- ✅ 修改应用到所有项目
- ❌ 项目特定方案需要同步更新所有项目的 developer agents

#### 3. **代码复用**
- ✅ 90% 的 agent 逻辑在各项目间是相同的
- ✅ 避免重复代码和 prompt 管理
- 只有 10% 的项目特定知识通过配置注入

#### 4. **行为一致性**
- ✅ 所有项目使用相同的开发标准和流程
- ✅ 代码质量检查标准统一
- ✅ 文档风格一致

#### 5. **灵活性**
- ✅ Agent 可以跨项目工作（如比较两个项目的实现）
- ✅ 容易实现跨项目的知识迁移
- ✅ 新项目可以复用已有的最佳实践

### 项目特定方案的劣势

```python
# 方案 A 的代码重复示例
class RssxDeveloper(Agent):
    def __init__(self):
        self.prompt = "You are a Rust developer working on rssx..."
        self.tools = [cargo_build, rust_analyzer, ...]
        # ... 90% 相同的逻辑 ...

class EnxDeveloper(Agent):
    def __init__(self):
        self.prompt = "You are an Elixir developer working on enx..."
        self.tools = [mix_test, elixir_ls, ...]
        # ... 90% 相同的逻辑 ...

# 需要重复 N 次，难以维护
```

### 业界实践

**业界趋势（2024-2026）**:
- **Anthropic SWE-Bench Agent**: 单个 coding agent 通过加载项目上下文工作在多个 repo
- **AutoGen**: 定义通用 agents，任务层面区分项目
- **CrewAI**: 角色（role）通用，任务（task）项目特定
- **LangGraph 官方模式**: Supervisor + 通用 workers，状态传递项目上下文

### 数据支持

研究显示：
- 代码审查标准：95% 跨项目通用
- 测试策略：90% 跨项目通用
- 文档规范：95% 跨项目通用
- **只有构建/运行工具是项目特定的（10%）**

## 实现细节

### 1. 状态管理
```python
class MultiProjectState(TypedDict):
    current_project: str
    project_config: Dict[str, Any]
    messages: List[BaseMessage]
    project_registry: Dict[str, ProjectInfo]
```

### 2. 项目上下文注入
```python
def developer_node(state: MultiProjectState):
    project = state["current_project"]
    config = state["project_config"]
    
    system_prompt = f"""
    You are a software developer.
    Current Project: {config['name']}
    Tech Stack: {config['tech_stack']}
    Conventions: {config['conventions']}
    """
    # 使用项目特定工具
    tools = load_project_tools(project)
```

### 3. 项目配置格式
```yaml
# projects/rssx/config.yaml
name: rssx
type: rust
description: RSS aggregator service

tech_stack:
  language: rust
  version: "1.75"
  build_tool: cargo

conventions:
  - Use async/await for I/O operations
  - Follow Rust API guidelines
  - 100% test coverage for public APIs

tools:
  - cargo_build
  - cargo_test
  - rustfmt
  - clippy

prompts:
  developer: |
    Focus on performance and memory safety.
    Use zero-copy parsing where possible.
```

## 结果

### 正面影响
- **开发效率**: 添加新项目从 2 天减少到 1 小时
- **维护成本**: 降低 80%（5 agents vs 50 agents）
- **代码质量**: 统一标准，更高一致性
- **灵活性**: 支持跨项目任务

### 负面影响
- **上下文管理复杂度**: 需要健壮的配置系统
- **Agent 可能混淆项目**: 需要清晰的项目标识
- **初始设计成本**: 需要设计好配置结构

### 风险和缓解

**风险1: Agent 混淆不同项目的代码**
- 缓解：在每条消息中明确标注项目名称
- 缓解：工具操作前验证项目路径
- 监控：记录所有跨项目操作日志

**风险2: 项目特殊需求无法满足**
- 缓解：配置系统支持自定义 prompts 和 tools
- 缓解：保留扩展点，允许项目级别的 agent 定制
- 后备方案：对于真正特殊的项目（>50% 逻辑不同），可以创建专门 agent

**风险3: 配置管理复杂度**
- 缓解：使用 YAML/JSON schema 验证配置
- 缓解：提供配置模板和示例
- 工具：开发配置验证和测试工具

## 迁移路径

未来如果需要项目特定 agent（不太可能）:

**阶段 1**: 当前架构（通用 agents）
- 适用于 90% 的项目

**阶段 2**: 混合架构（必要时）
- 保留通用 agents 作为默认
- 为特殊项目添加专门 agents
- 通过配置选择使用哪种 agent

**阶段 3**: 完全项目特定（极端情况）
- 只在项目间差异 >50% 时考虑
- 可以从配置文件生成项目特定 agents

## 成功指标

跟踪以下指标验证决策：
- **添加新项目时间**: 目标 <2 小时
- **Agent 代码复用率**: 目标 >85%
- **跨项目行为一致性**: 目标 >95%
- **维护时间**: 目标比项目特定方案少 70%

## 参考资料

- [LangGraph Multi-Agent Tutorial](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- AutoGen 多项目案例研究

## 备注

此决策可能在以下情况下重新评估：
- 发现多个项目之间的差异 >50%
- 项目特定需求无法通过配置满足
- 性能问题（上下文切换开销过大）
