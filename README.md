# LangGraphX

Multi-Agent 协同软件开发系统

## 概述

LangGraphX 是一个基于 LangGraph 的智能多 agent 协同系统，让多个 AI agents 协作完成软件开发任务。系统支持多项目管理，能够智能地在不同项目之间切换和协作。

### 核心特性

- 🤖 **多 Agent 协作** - 架构师、开发者、审查者、测试员等角色协同工作
- 🎯 **多项目支持** - 通过上下文切换管理多个项目（rssx、enx 等）
- 🔧 **通用 Agent 架构** - 通用角色 + 项目上下文，易于扩展
- 🔌 **LLM 集成** - 通过 vscode-lm-proxy 访问 Claude Sonnet 4.5
- 📊 **状态管理** - 基于 LangGraph 的可持久化状态系统
- 🛠️ **项目感知工具** - 文件操作、Git、构建、测试等自动适配项目

## 架构亮点

### 通用 Agent + 项目上下文

```python
# 一套 agents 适用所有项目
agents = [
    architect_agent,   # 架构设计
    developer_agent,   # 代码实现
    reviewer_agent,    # 代码审查
    tester_agent      # 测试编写
]

# 通过动态加载项目配置和工具来适配不同项目
projects = {
    "rssx": {  # Rust 项目
        "type": "rust",
        "tools": ["cargo_build", "cargo_test", "clippy"]
    },
    "enx": {   # Elixir 项目
        "type": "elixir",
        "tools": ["mix_compile", "mix_test", "mix_format"]
    }
}
```

### 智能路由和编排

```
用户请求
    ↓
Supervisor Agent (分析意图，识别项目)
    ↓
├→ Architect → Developer → Reviewer → Tester →┐
│                                              │
└──────────────────────────────────────────────┘
         (循环直到任务完成)
```

## 快速开始

### 前置要求

1. **Python 3.11+**
2. **VS Code 1.101.0+**
3. **GitHub Copilot 订阅**
4. **vscode-lm-proxy 扩展**
   - 在 VS Code 中搜索 "LM Proxy" 并安装
   - 启动代理服务器 (命令面板: "LM Proxy: Start LM Proxy Server")

### 安装

```bash
# 克隆仓库
cd /Users/wiloon/workspace/projects/langgraphx

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 或使用 Poetry (推荐)
poetry install
```

### 配置

1. **多根工作区** (推荐)
   
   创建 `langgraphx.code-workspace`:
   ```json
   {
     "folders": [
       {"path": "."},
       {"path": "../rssx"},
       {"path": "../enx"}
     ]
   }
   ```

2. **项目配置**
   
   在 `projects/` 下为每个项目创建配置：
   ```bash
   projects/
   ├── rssx/
   │   └── config.yaml
   └── enx/
       └── config.yaml
   ```

3. **环境变量**
   
   ```bash
   cp .env.example .env
   # 编辑 .env 文件
   ```

### 使用示例

```python
from langgraphx import create_agent_system

# 初始化系统
system = create_agent_system(
    projects=[
        {"name": "rssx", "path": "/path/to/rssx"},
        {"name": "enx", "path": "/path/to/enx"}
    ]
)

# 执行任务
result = system.run(
    "在 rssx 项目中实现 RSS feed 解析功能",
    project="rssx"
)

# 跨项目任务
result = system.run(
    "比较 rssx 和 enx 的 HTTP 客户端实现"
)
```

## 项目结构

```
langgraphx/
├── docs/                      # 文档
│   ├── adr/                   # 架构决策记录
│   │   ├── 001-use-langgraph.md
│   │   ├── 002-generic-agents-vs-project-specific.md
│   │   ├── 003-vscode-lm-proxy-integration.md
│   │   └── 004-multi-project-state-management.md
│   ├── architecture.md        # 架构设计文档
│   └── development.md         # 开发指南 (TBD)
├── src/
│   ├── agents/               # Agent 实现
│   │   ├── supervisor.py
│   │   ├── architect.py
│   │   ├── developer.py
│   │   ├── reviewer.py
│   │   └── tester.py
│   ├── graph/                # LangGraph 工作流
│   │   ├── state.py          # 状态定义
│   │   ├── nodes.py          # 节点实现
│   │   └── builder.py        # 图构建
│   ├── tools/                # 工具实现
│   │   ├── file_tools.py
│   │   ├── git_tools.py
│   │   └── scoped.py         # 项目作用域包装
│   ├── llm/                  # LLM 客户端
│   │   └── proxy_client.py
│   ├── config/               # 配置管理
│   │   └── projects.py       # 项目注册
│   └── main.py               # 入口
├── projects/                 # 项目配置
│   ├── rssx/
│   │   ├── config.yaml
│   │   └── prompts/
│   └── enx/
│       ├── config.yaml
│       └── prompts/
├── tests/                    # 测试
├── examples/                 # 示例
├── pyproject.toml           # 项目配置
└── README.md

```

## 技术栈

- **编排框架**: [LangGraph](https://langchain-ai.github.io/langgraph/) 0.3.3+
- **LLM**: Claude Sonnet 4.5 (via vscode-lm-proxy)
- **语言**: Python 3.11+
- **状态管理**: LangGraph MessagesState + 自定义 MultiProjectState

## 文档

- 📖 [架构设计文档](docs/architecture.md) - 详细的系统架构说明
- 📋 [ADR 目录](docs/adr/) - 架构决策记录
  - [ADR-001: 使用 LangGraph](docs/adr/001-use-langgraph.md)
  - [ADR-002: 通用 Agent 架构](docs/adr/002-generic-agents-vs-project-specific.md)
  - [ADR-003: vscode-lm-proxy 集成](docs/adr/003-vscode-lm-proxy-integration.md)
  - [ADR-004: 多项目状态管理](docs/adr/004-multi-project-state-management.md)

## 开发状态

🚧 **当前阶段**: 文档和设计阶段

- ✅ 架构设计完成
- ✅ ADR 文档完成
- ⏳ 核心代码实现中
- ⏳ 测试编写中

## 为什么选择这个架构？

### 通用 Agent vs 项目特定 Agent

我们选择**通用 agent + 项目上下文**而非为每个项目创建专门的 agents：

- ✅ **可扩展性**: 添加新项目只需配置文件，无需修改代码
- ✅ **维护性**: 10个项目只需维护5个 agents，而非50个
- ✅ **一致性**: 所有项目使用统一的开发流程和质量标准
- ✅ **灵活性**: 支持跨项目任务和知识迁移

详见 [ADR-002](docs/adr/002-generic-agents-vs-project-specific.md)

### 单线程 vs 多线程状态

我们选择**单线程 + 项目标记**而非每个项目独立线程：

- ✅ **简单性**: 单一对话线程，符合用户心智模型
- ✅ **跨项目能力**: 可以自然地比较和迁移代码
- ✅ **状态管理**: 更简单的 checkpoint 管理

详见 [ADR-004](docs/adr/004-multi-project-state-management.md)

### vscode-lm-proxy vs 官方 API

我们使用 **vscode-lm-proxy** 桥接 GitHub Copilot：

- ✅ **成本**: 无需额外 API 费用，使用现有 Copilot 订阅
- ✅ **兼容性**: 提供 Anthropic 兼容 API，代码可移植
- ✅ **开发友好**: 本地部署，易于调试

详见 [ADR-003](docs/adr/003-vscode-lm-proxy-integration.md)

## 路线图

### Phase 1: MVP (当前)
- [x] 架构设计
- [ ] 核心框架实现
- [ ] 基础 agents (supervisor, developer)
- [ ] 基础工具 (文件操作)
- [ ] 单项目支持

### Phase 2: 多项目
- [ ] 项目注册和发现
- [ ] 多项目状态管理
- [ ] 项目切换和路由
- [ ] 所有角色 agents

### Phase 3: 增强
- [ ] 高级工具 (Git, 构建, 测试)
- [ ] 跨项目任务支持
- [ ] 可视化和监控
- [ ] 性能优化

### Phase 4: 生产化
- [ ] 完整测试覆盖
- [ ] 错误处理和恢复
- [ ] 文档完善
- [ ] 性能基准测试

## 贡献

欢迎贡献！请查看开发指南。

## 许可证

Apache License 2.0 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- [LangGraph](https://github.com/langchain-ai/langgraph) - 强大的 agent 编排框架
- [vscode-lm-proxy](https://github.com/ryonakae/vscode-lm-proxy) - VS Code LM API 代理
- [Anthropic](https://anthropic.com) - Claude 模型

---

**注意**: 本项目处于早期开发阶段，API 可能会变化。建议关注 releases 和 changelog。