# Workflow: Adding a New Agent

> Step-by-step guide for creating a new agent role

---

## Prerequisites

- [ ] Understand project architecture (`docs/architecture.md`)
- [ ] Review existing agents in `src/agents/`
- [ ] Determine agent's unique responsibility

---

## Steps

### 1. Create Agent Module

**File**: `src/agents/<agent_name>.py`

```python
"""<Agent name> agent for <purpose>.

This agent is responsible for <specific responsibility>.
"""

from typing import Dict, Any
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage

def <agent_name>_node(state: MessagesState) -> Dict[str, Any]:
    """Execute <agent name> tasks.
    
    Args:
        state: Current graph state with messages and project context
        
    Returns:
        Updated state with agent's output
    """
    # 1. Get current project
    project = state["current_project"]
    project_info = state["projects"][project]
    
    # 2. Build system prompt with project context
    system_prompt = f"""
    You are a {<agent_role>} working on the {project} project.
    
    Project Type: {project_info['type']}
    Tech Stack: {project_info['tech_stack']}
    
    Your responsibilities:
    - <responsibility 1>
    - <responsibility 2>
    """
    
    # 3. Load project-specific tools (if needed)
    from langgraphx.config.projects import load_project_tools
    tools = load_project_tools(project)
    
    # 4. Create agent with tools
    from langgraph.prebuilt import create_react_agent
    from langgraphx.llm.proxy_client import get_llm_client
    
    llm = get_llm_client()
    agent = create_react_agent(llm, tools, prompt=system_prompt)
    
    # 5. Execute agent
    result = agent.invoke(state)
    
    # 6. Tag message with agent name
    result["messages"][-1] = AIMessage(
        content=result["messages"][-1].content,
        name=f"<agent_name>@{project}"
    )
    
    return result
```

---

### 2. Register in Graph

**File**: `src/graph/builder.py`

```python
# Add import
from langgraphx.agents.<agent_name> import <agent_name>_node

# Add node to graph
workflow.add_node("<agent_name>", <agent_name>_node)

# Add routing from supervisor
workflow.add_edge("<agent_name>", "supervisor")

# Update supervisor routing logic
def route_supervisor(state: MessagesState):
    # ... existing logic ...
    
    if <condition_for_this_agent>:
        return "<agent_name>"
    
    # ... rest of routing ...
```

---

### 3. Write Tests

**File**: `tests/agents/test_<agent_name>.py`

```python
"""Tests for <agent_name> agent."""

import pytest
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage

from langgraphx.agents.<agent_name> import <agent_name>_node


def test_<agent_name>_with_valid_state_succeeds():
    """Test that agent executes successfully with valid state."""
    state = MessagesState(
        messages=[HumanMessage(content="Test task")],
        current_project="rssx",
        projects={
            "rssx": {
                "name": "rssx",
                "type": "rust",
                "path": "/path/to/rssx",
                "tech_stack": {"language": "rust"}
            }
        },
        project_contexts={"rssx": {}}
    )
    
    result = <agent_name>_node(state)
    
    assert "messages" in result
    assert len(result["messages"]) > 0
    assert result["messages"][-1].name == "<agent_name>@rssx"


def test_<agent_name>_respects_project_context():
    """Test that agent uses correct project context."""
    # Test implementation
    pass


def test_<agent_name>_handles_error_gracefully():
    """Test that agent handles errors without crashing."""
    # Test implementation
    pass
```

Run tests:
```bash
pytest tests/agents/test_<agent_name>.py -v
```

---

### 4. Update Documentation

**File**: `docs/architecture.md`

Add agent description to "Agent Roles" section:

```markdown
#### 3.2.X <Agent Name> Agent

**Responsibilities**: 
- <responsibility 1>
- <responsibility 2>

**Tools**:
- <tool 1>
- <tool 2>

**Prompt Template**:
```
You are a <role> for the {project_name} project.
...
```
```

---

### 5. Add Project-Specific Prompts (Optional)

**File**: `projects/rssx/prompts/<agent_name>.txt`

```
Additional instructions specific to rssx project:
- <instruction 1>
- <instruction 2>
```

Load in agent:
```python
from pathlib import Path

prompt_file = Path(f"projects/{project}/prompts/<agent_name>.txt")
if prompt_file.exists():
    custom_prompt = prompt_file.read_text()
    system_prompt += f"\n\n{custom_prompt}"
```

---

## Checklist

- [ ] Agent module created in `src/agents/`
- [ ] Node registered in graph builder
- [ ] Routing logic updated in supervisor
- [ ] Unit tests written and passing
- [ ] Integration test with full graph
- [ ] Documentation updated in `docs/architecture.md`
- [ ] Type hints on all functions
- [ ] Docstrings in Google style
- [ ] Code formatted with black/isort
- [ ] All quality checks pass

---

## Common Mistakes

❌ **Hardcoding project name** - Always use `state["current_project"]`
❌ **Ignoring project context** - Load project-specific config and tools
❌ **Missing message tagging** - Tag with `agent@project` format
❌ **No error handling** - Wrap LLM calls in try/except
❌ **Forgetting tests** - Must have >80% coverage

---

## Example: Documenter Agent

See `src/agents/documenter.py` for a complete example.

---

Last updated: 2026-01-18
