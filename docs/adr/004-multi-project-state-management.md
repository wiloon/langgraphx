# ADR-004: 多项目状态管理方案

## 状态
已接受 (2026-01-18)

## 背景

在 ADR-002 中，我们决定使用通用 agent + 项目上下文的架构。现在需要设计状态管理方案来支持多项目场景。

### 核心挑战

1. **状态隔离**: 不同项目的状态不应相互干扰
2. **上下文切换**: Agent 需要知道当前在处理哪个项目
3. **跨项目任务**: 某些任务可能涉及多个项目（如比较、迁移代码）
4. **持久化**: 状态需要支持保存和恢复（checkpoint）
5. **并发**: 可能同时处理多个项目的任务

### 评估的方案

**方案 A: 单线程 + 项目标记状态**
- 一个 `thread_id`，状态包含项目上下文
- 简单，易于跨项目推理

**方案 B: 多线程，每项目一线程**
- 每个项目独立的 `thread_id`
- 完全隔离，但跨项目协调复杂

**方案 C: 分层状态 + 命名空间**
- 使用 LangGraph 的 `checkpoint_ns` 实现分层
- 共享顶层，项目独立子层

## 决策

**选择方案 A: 单线程 + 项目标记状态**，结合方案 C 的命名空间思想

实现统一的状态结构，通过 `current_project` 字段标识当前活动项目，同时维护所有项目的独立上下文。

## 理由

### 方案 A 的优势

#### 1. **简单性**
- ✅ 单一对话线程，符合用户心智模型
- ✅ 不需要管理多个 thread_id
- ✅ checkpoint 管理更简单

#### 2. **跨项目能力**
- ✅ Agent 可以自然地比较不同项目
- ✅ 跨项目知识迁移更容易
- ✅ 用户可以在对话中自由切换项目

#### 3. **状态访问**
- ✅ 所有项目信息在同一状态中可见
- ✅ 便于实现项目间的依赖关系
- ✅ 历史记录包含所有项目的上下文

#### 4. **LangGraph 友好**
- ✅ 符合 LangGraph 的 `MessagesState` 设计
- ✅ 可以使用 `configurable` 传递项目上下文
- ✅ 支持 checkpoint 命名空间

### 状态结构设计

```python
from typing import TypedDict, Literal, Dict, List
from langgraph.graph import MessagesState

class ProjectInfo(TypedDict):
    """项目基本信息"""
    name: str                              # 项目名称
    path: str                              # 项目绝对路径
    type: Literal["rust", "elixir", "python", "javascript", "unknown"]
    description: str                       # 项目描述
    tech_stack: Dict[str, str]            # 技术栈详情
    git_branch: str | None                 # 当前分支
    
class ProjectContext(TypedDict):
    """项目运行时上下文"""
    pending_changes: List[str]             # 待提交的文件
    last_build_status: Literal["success", "failed", "pending", "unknown"]
    last_test_status: Literal["success", "failed", "pending", "unknown"]
    recent_errors: List[str]               # 最近的错误
    open_files: List[str]                  # 当前打开的文件

class MultiProjectState(MessagesState):
    """多项目 agent 系统的状态"""
    
    # 项目管理
    current_project: str                   # 当前活动项目名称
    projects: Dict[str, ProjectInfo]       # 所有注册的项目
    project_contexts: Dict[str, ProjectContext]  # 项目运行时上下文
    
    # 任务管理
    current_task: str | None               # 当前任务描述
    task_project_map: Dict[str, str]       # 任务 -> 项目映射
    
    # Agent 协作
    next_agent: str | None                 # 下一个要调用的 agent
    agent_outputs: Dict[str, List[str]]    # Agent 输出历史
    
    # 工具结果（按项目组织）
    tool_outputs: Dict[str, List[Dict]]    # 项目名 -> 工具输出列表
```

### 核心设计原则

#### 1. **显式项目标识**
所有操作都明确指定目标项目：

```python
def developer_node(state: MultiProjectState):
    project = state["current_project"]
    project_info = state["projects"][project]
    project_ctx = state["project_contexts"][project]
    
    # 所有操作都基于当前项目
    system_prompt = f"Working on project: {project}"
    # ...
```

#### 2. **隔离的项目上下文**
每个项目维护独立的运行时上下文：

```python
# 不同项目的构建状态是独立的
state["project_contexts"]["rssx"]["last_build_status"] = "success"
state["project_contexts"]["enx"]["last_build_status"] = "failed"
```

#### 3. **共享的对话历史**
所有项目共享消息历史，但消息带项目标签：

```python
from langchain_core.messages import HumanMessage, AIMessage

# 项目标签通过 name 字段
state["messages"].append(
    AIMessage(
        content="Code implemented successfully",
        name="developer@rssx"  # agent@project
    )
)
```

#### 4. **项目切换机制**
通过更新 `current_project` 实现项目切换：

```python
def switch_project(state: MultiProjectState, new_project: str):
    if new_project not in state["projects"]:
        raise ValueError(f"Unknown project: {new_project}")
    
    return {
        "current_project": new_project,
        "messages": [
            HumanMessage(
                content=f"Switched to project: {new_project}"
            )
        ]
    }
```

### 与 LangGraph 集成

#### 1. **配置传递**
使用 `RunnableConfig` 传递项目配置：

```python
from langgraph.graph import RunnableConfig

config = RunnableConfig(
    configurable={
        "thread_id": "main_conversation",
        "project_path": state["projects"][state["current_project"]]["path"],
        "project_name": state["current_project"],
    }
)

graph.invoke(state, config)
```

#### 2. **Checkpoint 命名空间**
使用命名空间组织不同项目的 checkpoint：

```python
# 保存项目特定的 checkpoint
config = {
    "configurable": {
        "thread_id": "main_thread",
        "checkpoint_ns": f"projects.{project_name}"
    }
}
```

#### 3. **工具作用域**
工具从配置中获取项目上下文：

```python
from langchain_core.tools import tool

@tool
def read_file(file_path: str, config: RunnableConfig) -> str:
    """Read a file from the current project"""
    project_path = config["configurable"]["project_path"]
    full_path = os.path.join(project_path, file_path)
    
    # 安全检查：确保路径在项目内
    if not full_path.startswith(project_path):
        raise ValueError("Path outside project boundary")
    
    with open(full_path) as f:
        return f.read()
```

## 实现细节

### 1. 状态初始化

```python
def create_initial_state(projects: List[Dict]) -> MultiProjectState:
    """创建初始状态"""
    state = MultiProjectState(
        messages=[],
        current_project=projects[0]["name"],  # 默认第一个项目
        projects={},
        project_contexts={},
        current_task=None,
        task_project_map={},
        next_agent=None,
        agent_outputs={},
        tool_outputs={}
    )
    
    # 注册所有项目
    for proj in projects:
        state["projects"][proj["name"]] = {
            "name": proj["name"],
            "path": proj["path"],
            "type": detect_project_type(proj["path"]),
            "description": proj.get("description", ""),
            "tech_stack": load_tech_stack(proj["path"]),
            "git_branch": get_git_branch(proj["path"])
        }
        
        # 初始化项目上下文
        state["project_contexts"][proj["name"]] = {
            "pending_changes": [],
            "last_build_status": "unknown",
            "last_test_status": "unknown",
            "recent_errors": [],
            "open_files": []
        }
    
    return state
```

### 2. 项目切换节点

```python
def project_router_node(state: MultiProjectState) -> MultiProjectState:
    """分析用户意图，决定目标项目"""
    last_message = state["messages"][-1].content
    
    # 使用 LLM 分析意图
    analysis = llm.invoke([
        SystemMessage(content="Determine which project the user is referring to."),
        HumanMessage(content=last_message)
    ])
    
    target_project = extract_project_name(analysis.content)
    
    if target_project and target_project != state["current_project"]:
        return {
            "current_project": target_project,
            "messages": [
                AIMessage(
                    content=f"Switching to project: {target_project}",
                    name="supervisor"
                )
            ]
        }
    
    return {}  # 无变化
```

### 3. 项目感知的 Agent

```python
def create_project_aware_agent(role: str):
    """创建项目感知的 agent"""
    
    def agent_node(state: MultiProjectState) -> dict:
        project = state["current_project"]
        project_info = state["projects"][project]
        
        # 构建项目特定的 prompt
        system_prompt = f"""
        You are a {role} working on the {project} project.
        
        Project Details:
        - Type: {project_info['type']}
        - Path: {project_info['path']}
        - Tech Stack: {project_info['tech_stack']}
        
        Current Status:
        - Build: {state['project_contexts'][project]['last_build_status']}
        - Tests: {state['project_contexts'][project]['last_test_status']}
        """
        
        # 加载项目特定工具
        tools = load_project_tools(project)
        
        # 创建配置
        config = RunnableConfig(
            configurable={
                "project_path": project_info["path"],
                "project_name": project
            }
        )
        
        # 执行 agent
        agent = create_react_agent(llm, tools, prompt=system_prompt)
        result = agent.invoke(state, config)
        
        # 更新项目上下文
        updates = {
            "messages": result["messages"],
            "agent_outputs": {
                **state["agent_outputs"],
                role: state["agent_outputs"].get(role, []) + [result["messages"][-1].content]
            }
        }
        
        return updates
    
    return agent_node
```

## 结果

### 正面影响

1. **用户体验**
   - ✅ 自然的对话流程，无需显式切换线程
   - ✅ 可以在对话中自由切换项目
   - ✅ 跨项目任务更直观

2. **开发效率**
   - ✅ 状态管理逻辑简单
   - ✅ 易于调试和可视化
   - ✅ Checkpoint 管理直接

3. **功能完整性**
   - ✅ 支持跨项目推理
   - ✅ 支持项目间依赖
   - ✅ 支持并行项目操作（通过 Send API）

### 负面影响

1. **状态大小**
   - ⚠️ 单个状态包含所有项目信息，可能较大
   - 缓解：只保留活跃项目的详细信息，其他项目懒加载

2. **错误隔离**
   - ⚠️ 一个项目的错误可能影响状态
   - 缓解：错误处理时明确标记项目，不影响其他项目上下文

3. **并发风险**
   - ⚠️ 同时操作多个项目需要仔细管理
   - 缓解：使用锁或原子更新保护项目上下文

### 风险和缓解

**风险1: Agent 混淆不同项目**
- **可能性**: 中等
- **影响**: 高（错误修改其他项目）
- **缓解**:
  - 在每次操作前验证 `current_project`
  - 工具调用前检查路径在正确项目内
  - 消息中明确标注项目名称
  - 添加项目边界检查

**风险2: 状态膨胀**
- **可能性**: 中等
- **影响**: 中等（性能下降）
- **缓解**:
  - 定期清理历史消息
  - 项目上下文懒加载
  - 使用增量 checkpoint

**风险3: 跨项目状态污染**
- **可能性**: 低
- **影响**: 高
- **缓解**:
  - 严格的状态更新规则
  - 项目上下文隔离
  - 单元测试覆盖状态管理

## 备选方案（未选择）

### 方案 B: 多线程方案

**优势**: 完全隔离，不会混淆
**劣势**: 
- 跨项目协调复杂
- 需要管理多个 thread_id
- 用户体验不佳（需要切换线程）

**适用场景**: 项目完全独立，无跨项目需求

### 方案 C: 纯命名空间方案

**优势**: LangGraph 原生支持
**劣势**:
- 需要频繁切换命名空间
- 跨命名空间访问复杂
- 不适合共享对话历史

**适用场景**: 项目需要完全独立的 checkpoint 历史

## 迁移路径

如果未来需要切换方案：

**阶段 1 → 阶段 2**: 单线程到多线程
- 按项目拆分状态
- 创建独立 thread_id
- 实现跨线程通信机制

**成本**: 中等（需要重构状态管理）

## 成功指标

- **状态大小**: 目标 <10MB per thread
- **项目切换延迟**: 目标 <100ms
- **跨项目错误率**: 目标 <1%（错误操作其他项目）
- **Checkpoint 保存时间**: 目标 <500ms

## 参考资料

- [LangGraph State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [LangGraph Checkpointing](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [LangGraph Configuration](https://langchain-ai.github.io/langgraph/concepts/low_level/#configuration)

## 备注

此决策可能在以下情况下重新评估：
- 状态大小超过可接受范围（>50MB）
- 跨项目错误率过高（>5%）
- 用户明确需要完全独立的项目线程
- 并发性能成为瓶颈
