# LangGraphX 架构设计文档

## 1. 系统概述

LangGraphX 是一个基于 LangGraph 的多 agent 协同开发系统，旨在让多个 AI agents 协作完成软件开发任务。系统支持多项目管理，能够在不同项目（rssx、enx 等）之间智能切换和协作。

### 1.1 核心目标

- **多 Agent 协作**: 不同角色的 agents（架构师、开发者、审查者、测试员）协同工作
- **多项目支持**: 单一系统管理多个软件项目，通过上下文切换而非 agent 复制
- **灵活编排**: 基于任务需求动态路由和调度 agents
- **可扩展性**: 易于添加新项目、新 agents、新工具

### 1.2 技术栈

- **编排框架**: LangGraph 0.3.3+
- **LLM 访问**: vscode-lm-proxy (桥接 GitHub Copilot)
- **模型**: Claude Sonnet 4.5 (via Copilot subscription)
- **语言**: Python 3.11+
- **状态管理**: LangGraph MessagesState + 自定义 MultiProjectState

## 2. 架构图

### 2.1 系统层次架构

```
┌─────────────────────────────────────────────────────────────┐
│                    用户接口层 (User Interface)                 │
│  - CLI / REPL                                                │
│  - VS Code Extension (未来)                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              编排层 (Orchestration Layer)                     │
│  ┌────────────────────────────────────────────────────┐     │
│  │  LangGraph 工作流引擎                                │     │
│  │  - StateGraph                                       │     │
│  │  - Supervisor Agent (路由决策)                       │     │
│  │  - Checkpoint 管理                                   │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│                Agent 层 (Agent Layer)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Architect │  │Developer │  │ Reviewer │  │  Tester  │   │
│  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  所有 agents 都是通用的，通过项目上下文注入来适配项目           │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│               工具层 (Tool Layer)                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  项目感知工具 (Project-Scoped Tools)                  │   │
│  │  - File Operations (read/write/search)              │   │
│  │  - Git Operations (status/commit/branch)            │   │
│  │  - Build Tools (cargo/mix/npm)                      │   │
│  │  - Test Tools (cargo test/mix test)                 │   │
│  │  - Code Analysis (linting/formatting)               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              基础设施层 (Infrastructure Layer)                │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │ Project      │  │ LLM Client  │  │ Config       │       │
│  │ Registry     │  │ (Proxy)     │  │ Manager      │       │
│  └──────────────┘  └─────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │  vscode-lm-proxy (Port 4000)                     │       │
│  │    ↓                                              │       │
│  │  GitHub Copilot API                              │       │
│  │    ↓                                              │       │
│  │  Claude Sonnet 4.5                               │       │
│  └──────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Agent 协作流程

```
用户请求
   │
   ▼
┌────────────────┐
│   Supervisor   │  ← 分析意图，识别项目和任务
│     Agent      │
└────────┬───────┘
         │
         ├──→ 确定目标项目 (rssx/enx/...)
         │
         ├──→ 选择工作流
         │
         ▼
    ┌─────────┐
    │ Routing │
    └────┬────┘
         │
    ┌────┴────┬─────────┬──────────┐
    │         │         │          │
    ▼         ▼         ▼          ▼
┌─────────┐ ┌──────┐ ┌────────┐ ┌──────┐
│Architect│ │ Dev  │ │Reviewer│ │Tester│
└────┬────┘ └──┬───┘ └───┬────┘ └──┬───┘
     │         │         │          │
     │    加载项目上下文   │          │
     │    ├─ config      │          │
     │    ├─ tools       │          │
     │    └─ prompts     │          │
     │         │         │          │
     └────┬────┴────┬────┴──────┬───┘
          │         │           │
          ▼         ▼           ▼
     ┌─────────────────────────────┐
     │   Project-Scoped Tools      │
     │   (在正确项目路径下执行)       │
     └─────────────────────────────┘
                  │
                  ▼
         修改项目文件、提交代码等
```

### 2.3 多项目状态管理

```
MultiProjectState
├── messages: List[Message]          # 共享对话历史
│   └── 每条消息标记 agent@project
│
├── current_project: "rssx"          # 当前活动项目
│
├── projects: Dict                   # 项目注册表
│   ├── "rssx": ProjectInfo
│   │   ├── name: "rssx"
│   │   ├── path: "/Users/.../rssx"
│   │   ├── type: "rust"
│   │   ├── tech_stack: {...}
│   │   └── git_branch: "main"
│   │
│   └── "enx": ProjectInfo
│       ├── name: "enx"
│       ├── path: "/Users/.../enx"
│       ├── type: "elixir"
│       └── ...
│
├── project_contexts: Dict           # 项目运行时上下文
│   ├── "rssx": Context
│   │   ├── pending_changes: [...]
│   │   ├── last_build_status: "success"
│   │   ├── last_test_status: "passed"
│   │   └── recent_errors: []
│   │
│   └── "enx": Context
│       └── ...
│
└── task_project_map: Dict          # 任务到项目的映射
    └── "implement-feature-x": "rssx"
```

## 3. 核心组件设计

### 3.1 Supervisor Agent

**职责**: 
- 分析用户请求
- 识别目标项目
- 选择合适的 agent 和工作流
- 管理 agent 之间的协作

**输入**:
- 用户消息
- 当前状态（包含所有项目信息）

**输出**:
- 路由决策（下一个调用的 agent）
- 更新后的状态（如项目切换）

**实现模式**:
```python
def supervisor_node(state: MultiProjectState) -> Command:
    # 1. 分析用户意图
    intent = analyze_user_intent(state["messages"][-1])
    
    # 2. 确定目标项目
    target_project = identify_project(intent, state["projects"])
    
    # 3. 如果项目切换，更新状态
    if target_project != state["current_project"]:
        state["current_project"] = target_project
    
    # 4. 选择下一个 agent
    next_agent = select_agent(intent)
    
    # 5. 返回路由命令
    return Command(
        update=state,
        goto=next_agent
    )
```

### 3.2 Role-Based Agents

#### 3.2.1 Architect Agent

**职责**: 系统架构设计、技术选型、模块划分

**工具**:
- 代码结构分析
- 依赖关系图生成
- 架构文档生成

**提示词模板**:
```
You are a software architect working on the {project_name} project.

Project Context:
- Type: {project_type}
- Tech Stack: {tech_stack}
- Current Architecture: {architecture_summary}

Your responsibilities:
- Design system architecture
- Make technology decisions
- Define module boundaries
- Create technical specifications

Conventions:
{project_conventions}
```

#### 3.2.2 Developer Agent

**职责**: 代码实现、问题修复、重构

**工具**:
- 文件读写
- 代码搜索
- Git 操作
- 构建工具

**提示词模板**:
```
You are a software developer working on the {project_name} project.

Project Context:
- Language: {language}
- Framework: {framework}
- Build Tool: {build_tool}

Current Status:
- Branch: {git_branch}
- Last Build: {build_status}
- Recent Changes: {recent_changes}

Your responsibilities:
- Implement features
- Fix bugs
- Refactor code
- Write clean, maintainable code

Coding Standards:
{coding_standards}
```

#### 3.2.3 Reviewer Agent

**职责**: 代码审查、质量检查、最佳实践建议

**工具**:
- 静态分析
- 代码风格检查
- 复杂度分析

**提示词模板**:
```
You are a code reviewer for the {project_name} project.

Review Criteria:
- Code quality and readability
- Best practices adherence
- Performance considerations
- Security concerns
- Test coverage

Project Standards:
{code_standards}
```

#### 3.2.4 Tester Agent

**职责**: 测试设计、测试实现、测试执行

**工具**:
- 测试框架
- 覆盖率工具
- 测试运行器

**提示词模板**:
```
You are a test engineer for the {project_name} project.

Testing Strategy:
- Unit tests for all public APIs
- Integration tests for critical paths
- Test coverage target: {coverage_target}%

Test Framework: {test_framework}
```

### 3.3 Project Registry

**职责**: 管理所有项目的注册、发现和配置

**接口**:
```python
class ProjectRegistry:
    def register(self, name: str, path: str) -> ProjectInfo:
        """注册新项目"""
        
    def get(self, name: str) -> ProjectInfo:
        """获取项目信息"""
        
    def list(self) -> List[ProjectInfo]:
        """列出所有项目"""
        
    def detect_type(self, path: str) -> str:
        """自动检测项目类型"""
        # 检查 Cargo.toml -> rust
        # 检查 mix.exs -> elixir
        # 检查 package.json -> javascript
        # ...
        
    def load_config(self, name: str) -> Dict:
        """加载项目配置"""
        # 从 projects/{name}/config.yaml 读取
        
    def load_tools(self, name: str) -> List[Tool]:
        """加载项目特定工具"""
```

**配置格式**:
```yaml
# projects/rssx/config.yaml
name: rssx
type: rust
description: RSS aggregator service

tech_stack:
  language: rust
  version: "1.75"
  framework: tokio
  build_tool: cargo

conventions:
  - Use async/await for I/O
  - Follow Rust API guidelines
  - Comprehensive error handling with Result<T, E>

tools:
  build: cargo build --release
  test: cargo test
  lint: cargo clippy
  format: cargo fmt

prompts:
  architect: |
    Focus on performance and zero-copy parsing.
  developer: |
    Use idiomatic Rust patterns.
    Prefer composition over inheritance.
```

### 3.4 Tool System

#### 3.4.1 Tool 抽象

所有工具都是项目感知的：

```python
from langchain_core.tools import tool
from langgraph.graph import RunnableConfig

@tool
def read_file(file_path: str, config: RunnableConfig) -> str:
    """Read a file from the current project
    
    Args:
        file_path: Relative path within the project
        config: Contains project_path in configurable
    """
    project_path = config["configurable"]["project_path"]
    full_path = Path(project_path) / file_path
    
    # 安全检查
    if not full_path.resolve().is_relative_to(project_path):
        raise ValueError(f"Path {file_path} is outside project boundary")
    
    return full_path.read_text()
```

#### 3.4.2 工具分类

**通用工具** (适用所有项目):
- `read_file(path)` - 读取文件
- `write_file(path, content)` - 写入文件
- `list_files(directory)` - 列出文件
- `search_code(pattern)` - 搜索代码
- `git_status()` - Git 状态
- `git_commit(message)` - Git 提交

**项目特定工具** (根据项目类型加载):
- **Rust 项目**:
  - `cargo_build()` - 构建
  - `cargo_test()` - 测试
  - `cargo_clippy()` - Lint
  
- **Elixir 项目**:
  - `mix_compile()` - 编译
  - `mix_test()` - 测试
  - `mix_format()` - 格式化

#### 3.4.3 工具加载机制

```python
def load_project_tools(project_name: str, project_type: str) -> List[Tool]:
    """动态加载项目工具"""
    
    # 1. 加载通用工具
    tools = [
        read_file,
        write_file,
        list_files,
        search_code,
        git_status,
        git_commit
    ]
    
    # 2. 根据项目类型加载特定工具
    if project_type == "rust":
        tools.extend([
            cargo_build,
            cargo_test,
            cargo_clippy,
            cargo_doc
        ])
    elif project_type == "elixir":
        tools.extend([
            mix_compile,
            mix_test,
            mix_format,
            mix_deps_get
        ])
    
    # 3. 加载项目自定义工具（如果有）
    custom_tools_path = f"projects/{project_name}/tools"
    if Path(custom_tools_path).exists():
        tools.extend(load_custom_tools(custom_tools_path))
    
    return tools
```

### 3.5 LLM Client

**职责**: 封装 vscode-lm-proxy 访问，提供统一接口

```python
from anthropic import Anthropic

class LLMClient:
    def __init__(self, base_url: str = "http://localhost:4000/anthropic"):
        self.client = Anthropic(
            api_key="dummy",  # proxy 不验证
            base_url=base_url
        )
    
    def create_message(self, messages, model="claude-sonnet-4.5", **kwargs):
        """创建消息"""
        return self.client.messages.create(
            model=model,
            messages=messages,
            **kwargs
        )
    
    def stream_message(self, messages, model="claude-sonnet-4.5", **kwargs):
        """流式创建消息"""
        with self.client.messages.stream(
            model=model,
            messages=messages,
            **kwargs
        ) as stream:
            for text in stream.text_stream:
                yield text
    
    def health_check(self) -> bool:
        """健康检查"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False
```

## 4. 工作流设计

### 4.1 LangGraph 图结构

```python
from langgraph.graph import StateGraph, START, END

# 创建图
workflow = StateGraph(MultiProjectState)

# 添加节点
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("architect", architect_node)
workflow.add_node("developer", developer_node)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("tester", tester_node)

# 添加边
workflow.add_edge(START, "supervisor")

# Supervisor 可以路由到任何 agent
workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        "architect": "architect",
        "developer": "developer",
        "reviewer": "reviewer",
        "tester": "tester",
        "end": END
    }
)

# 各 agent 完成后返回 supervisor
workflow.add_edge("architect", "supervisor")
workflow.add_edge("developer", "supervisor")
workflow.add_edge("reviewer", "supervisor")
workflow.add_edge("tester", "supervisor")

# 编译图
graph = workflow.compile(
    checkpointer=MemorySaver()  # 或 PostgresSaver
)
```

### 4.2 典型工作流示例

#### 示例 1: 实现新功能

```
用户: "在 rssx 项目中实现 RSS feed 解析功能"

1. Supervisor 分析
   ├─ 识别项目: rssx
   ├─ 识别任务: 实现新功能
   └─ 路由到: Architect

2. Architect
   ├─ 设计功能架构
   ├─ 定义接口
   ├─ 选择依赖库 (e.g., feed-rs)
   └─ 返回: 设计文档

3. Supervisor 路由到: Developer

4. Developer
   ├─ 创建模块文件 (src/feed_parser.rs)
   ├─ 实现解析逻辑
   ├─ 添加错误处理
   └─ 返回: 实现代码

5. Supervisor 路由到: Reviewer

6. Reviewer
   ├─ 检查代码质量
   ├─ 验证错误处理
   ├─ 提出改进建议
   └─ 返回: 审查意见

7. Developer 根据反馈修改 (如果需要)

8. Supervisor 路由到: Tester

9. Tester
   ├─ 设计测试用例
   ├─ 实现单元测试
   ├─ 运行测试
   └─ 返回: 测试结果

10. Supervisor
    └─ 任务完成，返回用户
```

#### 示例 2: 跨项目任务

```
用户: "从 rssx 中提取 HTTP client 逻辑到 enx"

1. Supervisor 分析
   ├─ 识别源项目: rssx
   ├─ 识别目标项目: enx
   ├─ 任务类型: 代码迁移
   └─ 需要两个项目的上下文

2. 在 rssx 上下文
   Developer 提取 HTTP client 代码

3. Supervisor 切换到 enx 上下文

4. 在 enx 上下文
   ├─ Architect: 设计集成方案
   ├─ Developer: 适配到 Elixir (翻译 Rust -> Elixir)
   ├─ Tester: 编写测试
   └─ 完成迁移
```

## 5. 数据流

### 5.1 状态流转

```
初始化
  │
  ▼
MultiProjectState 创建
  ├─ 注册所有项目 (rssx, enx)
  ├─ 设置默认项目
  └─ 初始化上下文
  │
  ▼
用户消息进入
  │
  ▼
Supervisor 处理
  ├─ 分析消息
  ├─ 更新 current_project (如需切换)
  └─ 选择下一个 agent
  │
  ▼
Agent 执行
  ├─ 获取项目配置 (从 state)
  ├─ 加载项目工具
  ├─ 执行任务
  └─ 更新状态
     ├─ 添加消息到 messages
     ├─ 更新 project_contexts
     └─ 记录工具输出
  │
  ▼
返回 Supervisor (或结束)
  │
  ▼
Checkpoint 保存
```

### 5.2 配置传递

```
graph.invoke(state, config)
  │
  config = {
    "configurable": {
      "thread_id": "main",
      "project_path": "/Users/.../rssx",
      "project_name": "rssx"
    }
  }
  │
  ▼
传递给所有节点
  │
  ▼
工具调用时可访问 config
  │
  def read_file(path, config: RunnableConfig):
      project_path = config["configurable"]["project_path"]
      # 使用 project_path 确定完整路径
```

## 6. 安全和边界

### 6.1 文件系统安全

**原则**: 所有文件操作必须在项目边界内

```python
def validate_path(file_path: str, project_path: str) -> Path:
    """验证路径在项目内"""
    full_path = Path(project_path) / file_path
    resolved = full_path.resolve()
    
    if not resolved.is_relative_to(project_path):
        raise ValueError(
            f"Security: Path {file_path} is outside project boundary"
        )
    
    return resolved
```

### 6.2 Git 操作安全

- 所有 Git 操作在正确的 working directory 执行
- 提交前显示 diff 给用户确认
- 分支创建/切换前检查未提交更改

### 6.3 代码执行安全

- 构建和测试命令从配置文件读取（不接受任意命令）
- 超时机制防止无限循环
- 沙箱环境（Docker）用于不受信任的代码执行（可选）

## 7. 可观测性

### 7.1 日志

```python
import structlog

logger = structlog.get_logger()

# 在每个操作记录日志
logger.info(
    "agent_execution",
    agent="developer",
    project="rssx",
    action="write_file",
    file="src/main.rs"
)
```

### 7.2 指标

- Agent 执行时间
- 工具调用次数
- 项目切换频率
- LLM token 使用量
- 成功/失败率

### 7.3 调试

- LangGraph Studio 可视化
- Checkpoint 回放
- 详细的错误堆栈
- 状态快照导出

## 8. 扩展点

### 8.1 添加新项目

1. 在 `projects/` 创建项目配置
2. 添加到项目注册表
3. 自动检测项目类型和工具

### 8.2 添加新 Agent

1. 定义 agent 节点函数
2. 添加到工作流图
3. 更新 supervisor 的路由逻辑

### 8.3 添加新工具

1. 使用 `@tool` 装饰器定义工具
2. 注册到相应项目类型
3. 文档化工具用途

### 8.4 自定义工作流

1. 创建新的 StateGraph
2. 定义特定的节点和边
3. 注册为可选工作流

## 9. 部署考虑

### 9.1 开发环境

- VS Code + vscode-lm-proxy 扩展
- Python 虚拟环境
- 所有项目在本地文件系统

### 9.2 生产环境（未来）

- 迁移到官方 Anthropic API
- PostgreSQL checkpoint 存储
- 容器化部署
- API 服务封装

## 10. 性能优化

### 10.1 状态大小控制

- 定期清理历史消息（保留最近 N 条）
- 项目上下文懒加载
- 工具输出摘要而非完整保存

### 10.2 并发执行

- 使用 LangGraph 的 `Send` API 并行执行独立任务
- 多项目任务可并行处理

### 10.3 缓存

- 项目配置缓存
- 工具加载缓存
- LLM 响应缓存（相同输入）

## 11. 参考架构决策

详细的架构决策记录在 ADR 文档中：

- [ADR-001: 使用 LangGraph](adr/001-use-langgraph.md)
- [ADR-002: 通用 Agent vs 项目特定 Agent](adr/002-generic-agents-vs-project-specific.md)
- [ADR-003: vscode-lm-proxy 集成](adr/003-vscode-lm-proxy-integration.md)
- [ADR-004: 多项目状态管理](adr/004-multi-project-state-management.md)
