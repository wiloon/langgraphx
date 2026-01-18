# Workflow: Adding a New Tool

> Step-by-step guide for creating agent tools

---

## Prerequisites

- [ ] Understand tool system (`docs/architecture.md` section 3.4)
- [ ] Review existing tools in `src/tools/`
- [ ] Determine tool category (generic or project-specific)

---

## Tool Categories

**Generic Tools** - Work across all projects:
- File operations (read/write/list)
- Git operations (status/commit/diff)
- Search operations (grep/semantic)

**Project-Specific Tools** - Depend on project type:
- Rust: `cargo_build`, `cargo_test`, `clippy`
- Elixir: `mix_compile`, `mix_test`, `mix_format`
- Python: `pytest`, `mypy`, `black`

---

## Steps for Generic Tool

### 1. Create Tool Function

**File**: `src/tools/<category>_tools.py`

```python
"""<Category> tools for agents.

Tools for <purpose description>.
"""

from pathlib import Path
from typing import Optional
from langgraph.graph import RunnableConfig
from langchain_core.tools import tool


@tool
def <tool_name>(
    <param1>: <type>,
    <param2>: <type>,
    config: RunnableConfig
) -> <return_type>:
    """<Tool description>.
    
    <Detailed description of what the tool does, when to use it,
    and any important considerations.>
    
    Args:
        <param1>: <Description>
        <param2>: <Description>
        config: Runtime configuration with project_path in configurable
        
    Returns:
        <Description of return value>
        
    Raises:
        <ExceptionType>: <When this is raised>
        
    Example:
        >>> result = <tool_name>(<args>, config=config)
        >>> print(result)
        <expected output>
    """
    # 1. Extract project path from config
    project_path = Path(config["configurable"]["project_path"])
    
    # 2. Validate inputs
    if not <param1>:
        raise ValueError("<Error message>")
    
    # 3. Build full path (if file operation)
    if <working_with_files>:
        full_path = project_path / <param1>
        
        # Security: Validate path is within project
        if not full_path.resolve().is_relative_to(project_path):
            raise ValueError(f"Path {<param1>} is outside project boundary")
    
    # 4. Perform operation
    try:
        result = <operation>
        return result
    except <SpecificException> as e:
        raise <CustomException>(f"<Error message>: {e}") from e
```

---

### 2. Register Tool

**File**: `src/tools/__init__.py`

```python
from src.tools.<category>_tools import <tool_name>

__all__ = [
    # ... existing tools ...
    "<tool_name>",
]
```

**File**: `src/config/projects.py`

```python
def get_generic_tools() -> List[Tool]:
    """Get tools available for all projects."""
    from src.tools import <tool_name>
    
    return [
        # ... existing tools ...
        <tool_name>,
    ]
```

---

### 3. Write Tests

**File**: `tests/tools/test_<category>_tools.py`

```python
"""Tests for <category> tools."""

import pytest
from pathlib import Path
from langgraph.graph import RunnableConfig

from src.tools.<category>_tools import <tool_name>


@pytest.fixture
def mock_config(tmp_path):
    """Create mock configuration."""
    return RunnableConfig(
        configurable={
            "project_path": str(tmp_path),
            "project_name": "test_project"
        }
    )


def test_<tool_name>_with_valid_input_succeeds(mock_config):
    """Test tool with valid input."""
    result = <tool_name>(<valid_args>, config=mock_config)
    assert result == <expected>


def test_<tool_name>_with_invalid_input_raises_error(mock_config):
    """Test tool with invalid input."""
    with pytest.raises(ValueError, match="<error pattern>"):
        <tool_name>(<invalid_args>, config=mock_config)


def test_<tool_name>_validates_path_boundary(mock_config):
    """Test that tool prevents path traversal."""
    with pytest.raises(ValueError, match="outside project boundary"):
        <tool_name>("../../etc/passwd", config=mock_config)


def test_<tool_name>_handles_missing_file_gracefully(mock_config):
    """Test error handling for missing files."""
    # Test implementation
    pass
```

---

## Checklist

- [ ] Tool created with `@tool` decorator
- [ ] Type hints on all parameters
- [ ] Google-style docstring with examples
- [ ] `config: RunnableConfig` parameter
- [ ] Path validation for file operations
- [ ] Timeout for long operations
- [ ] Specific exception types
- [ ] Error messages with context
- [ ] Unit tests with >80% coverage
- [ ] Integration test with agent
- [ ] Registered in tool loader
- [ ] Documented in architecture.md

---

## Common Mistakes

❌ **No path validation** - Always validate paths within project boundary
❌ **No timeout** - Subprocess calls must have timeout
❌ **Generic exceptions** - Use specific exception types
❌ **Missing config param** - All tools need `config: RunnableConfig`
❌ **Hardcoded paths** - Use config["configurable"]["project_path"]
❌ **No error handling** - Wrap operations in try/except
❌ **Unsafe shell execution** - Validate/whitelist commands

---

Last updated: 2026-01-18
