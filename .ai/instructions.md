# AI Agents Development Guide

> **Target Audience**: AI agents working on this project  
> **Purpose**: Mandatory standards and guidelines for code generation and modifications

---

## 🌐 Language Requirements

### **CRITICAL: ALL content MUST be in English**

#### ✅ MUST use English for:
- **All code comments** (inline and block comments)
- **All docstrings** (module, class, function, method)
- **All documentation files** (README, design docs, ADRs)
- **All commit messages**
- **All variable/function/class names**
- **All log messages**
- **All error messages**
- **All configuration file comments**

#### ⚠️ Exceptions (Chinese allowed):
- User-facing UI text (if explicitly required)
- Direct user responses in chat/CLI
- Project-specific Chinese terms in context only

#### Example:

```python
# ✅ CORRECT
def create_agent(name: str, role: str) -> Agent:
    """Create a new agent with specified role.
    
    Args:
        name: Agent identifier
        role: Agent's functional role (e.g., 'developer', 'reviewer')
        
    Returns:
        Configured Agent instance
    """
    logger.info(f"Creating agent: {name} with role: {role}")
    return Agent(name=name, role=role)

# ❌ WRONG - Chinese comments/docstrings
def create_agent(name: str, role: str) -> Agent:
    """创建一个新的 agent"""  # ❌ Chinese docstring
    # 记录日志  # ❌ Chinese comment
    return Agent(name=name, role=role)
```

---

## 📝 Documentation Standards

### Docstring Format

**Use Google Style** for all Python docstrings:

```python
def process_project(project_name: str, config: Dict[str, Any]) -> Result:
    """Process a project with given configuration.
    
    This function loads project context, validates configuration,
    and executes the processing pipeline.
    
    Args:
        project_name: Name of the project to process (e.g., 'rssx', 'enx')
        config: Configuration dictionary with project settings
            - path (str): Project root path
            - type (str): Project type ('rust', 'elixir', etc.)
            
    Returns:
        Result object containing:
            - success (bool): Whether processing succeeded
            - output (str): Processing output or error message
            
    Raises:
        ProjectNotFoundError: If project_name is not registered
        ConfigValidationError: If config is invalid
        
    Example:
        >>> result = process_project('rssx', {'path': '/path/to/rssx'})
        >>> print(result.success)
        True
    """
    pass
```

### Comment Guidelines

**When to comment:**
- ✅ Complex algorithms or non-obvious logic
- ✅ Workarounds for bugs or limitations
- ✅ Important decisions or trade-offs
- ✅ TODOs with context and issue links

**When NOT to comment:**
- ❌ Obvious code that speaks for itself
- ❌ Restating what the code does
- ❌ Outdated or obsolete information

```python
# ✅ GOOD - Explains WHY
# Use timeout to prevent infinite wait on proxy connection
# See: https://github.com/org/repo/issues/123
response = client.request(url, timeout=5)

# ❌ BAD - Obvious, no value
# Send HTTP request
response = client.request(url)
```

### README Sections

Every module should have a README with:
1. **Purpose**: What this module does
2. **Usage**: How to use it (with examples)
3. **Dependencies**: What it depends on
4. **Architecture**: How it's structured (if complex)

---

## 💻 Code Style

### Type Hints

**MANDATORY** for all function signatures:

```python
# ✅ CORRECT
from typing import Dict, List, Optional
from pathlib import Path

def load_config(
    path: Path,
    defaults: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Load configuration from file."""
    pass

# ❌ WRONG - Missing type hints
def load_config(path, defaults=None):
    """Load configuration from file."""
    pass
```

### Naming Conventions

- **Functions/methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

```python
# ✅ CORRECT
class ProjectRegistry:
    DEFAULT_TIMEOUT = 30  # Constant
    
    def __init__(self):
        self._projects: Dict[str, Project] = {}  # Private
    
    def register_project(self, name: str) -> None:  # Public method
        """Register a new project."""
        pass

# ❌ WRONG - Inconsistent naming
class project_registry:  # Should be PascalCase
    defaultTimeout = 30  # Should be UPPER_SNAKE_CASE
    
    def RegisterProject(self, name):  # Should be snake_case
        pass
```

### File Organization

```python
"""Module docstring at the top.

Describe what this module does and how to use it.
"""

# 1. Standard library imports
import os
import sys
from pathlib import Path

# 2. Third-party imports
import anthropic
from langgraph.graph import StateGraph

# 3. Local imports
from langgraphx.config import settings
from langgraphx.tools import read_file

# 4. Constants
DEFAULT_MODEL = "claude-sonnet-4.5"
MAX_RETRIES = 3

# 5. Type definitions
ProjectType = Literal["rust", "elixir", "python", "javascript"]

# 6. Classes and functions
class Agent:
    """Agent implementation."""
    pass

def create_agent() -> Agent:
    """Create agent."""
    pass

# 7. Main execution (if script)
if __name__ == "__main__":
    main()
```

### Error Handling

**Always use specific exceptions:**

```python
# ✅ CORRECT
class ProjectNotFoundError(Exception):
    """Raised when project is not registered."""
    pass

def get_project(name: str) -> Project:
    """Get project by name."""
    if name not in registry:
        raise ProjectNotFoundError(f"Project '{name}' not found")
    return registry[name]

# ❌ WRONG - Generic exception
def get_project(name: str) -> Project:
    if name not in registry:
        raise Exception("Project not found")  # Too generic
    return registry[name]
```

---

## ✅ Quality Gates

### Before Every Commit

**Run these checks** (MANDATORY):

```bash
# 1. Format code
black src/ tests/
isort src/ tests/

# 2. Type checking
mypy src/

# 3. Linting
ruff check src/ tests/

# 4. Run tests
pytest tests/ -v

# 5. Check coverage
pytest tests/ --cov=src --cov-report=term-missing
```

### Test Requirements

- ✅ **Unit tests** for all public functions
- ✅ **Integration tests** for agent workflows
- ✅ **Coverage**: Minimum 80% for new code
- ✅ **Test naming**: `test_<function>_<scenario>_<expected>`

```python
# ✅ GOOD test naming
def test_create_agent_with_valid_name_returns_agent():
    """Test that creating agent with valid name succeeds."""
    agent = create_agent("developer", "dev")
    assert agent.name == "developer"

def test_create_agent_with_empty_name_raises_error():
    """Test that creating agent with empty name fails."""
    with pytest.raises(ValueError):
        create_agent("", "dev")
```

### TODO Policy

**NO orphan TODOs** - Always link to issue:

```python
# ✅ CORRECT
# TODO(#123): Implement retry logic for failed LLM calls
# See: https://github.com/org/repo/issues/123
def call_llm(prompt: str) -> str:
    pass

# ❌ WRONG - No context or issue link
# TODO: fix this later
def call_llm(prompt: str) -> str:
    pass
```

---

## 🔧 Common Tasks

See detailed workflows in [.ai/workflows/](.ai/workflows/) directory:
- [Adding a new agent](.ai/workflows/add-agent.md)
- [Adding a new tool](.ai/workflows/add-tool.md)
- [Adding project support](.ai/workflows/add-project.md)

---

## 🚫 DO's and DON'Ts

### DO:
- ✅ Write self-documenting code with clear names
- ✅ Keep functions focused and small (<50 lines)
- ✅ Use type hints everywhere
- ✅ Write tests before or with code (TDD)
- ✅ Log important operations with context
- ✅ Validate inputs at function boundaries
- ✅ Handle errors gracefully with specific exceptions
- ✅ Use pathlib.Path for file operations
- ✅ Follow the existing code structure
- ✅ Ask (via comments) when requirements are unclear

### DON'T:
- ❌ Use `any` type without strong justification
- ❌ Catch and ignore exceptions (`except: pass`)
- ❌ Hardcode paths, URLs, or configuration
- ❌ Leave debug print statements
- ❌ Use mutable default arguments
- ❌ Write functions longer than 50 lines
- ❌ Commit code that fails tests
- ❌ Use deprecated APIs
- ❌ Mix concerns in a single function
- ❌ Forget to update documentation

---

## 🎯 Anti-Patterns to Avoid

### ❌ God Objects
```python
# WRONG - Class does too many things
class ProjectManager:
    def load_config(self): pass
    def build_project(self): pass
    def run_tests(self): pass
    def deploy(self): pass
    def send_email(self): pass  # Too many responsibilities!
```

### ❌ Mutable Defaults
```python
# WRONG - Mutable default
def add_tool(tools: List[Tool] = []) -> None:  # BUG!
    tools.append(new_tool)

# CORRECT
def add_tool(tools: Optional[List[Tool]] = None) -> None:
    if tools is None:
        tools = []
    tools.append(new_tool)
```

### ❌ String Typing
```python
# WRONG - Using strings for enums
def set_status(status: str) -> None:  # "success"? "Success"? "ok"?
    pass

# CORRECT - Use Literal or Enum
from typing import Literal
Status = Literal["success", "failed", "pending"]

def set_status(status: Status) -> None:
    pass
```

---

## 📚 Key Resources

- **Architecture**: Read [docs/architecture.md](docs/architecture.md) for system design
- **ADRs**: Check [docs/adr/](docs/adr/) for design decisions
- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Python Style**: https://peps.python.org/pep-0008/
- **Type Hints**: https://peps.python.org/pep-0484/

---

## 🔄 Workflow

### When Starting a Task:
1. Read relevant documentation (architecture, ADRs)
2. Understand the current code structure
3. Plan changes (create checklist if complex)
4. Write tests first (TDD)
5. Implement incrementally
6. Run quality checks
7. Update documentation
8. Commit with descriptive message

### Commit Message Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(agents): add documenter agent for doc generation

- Implement DocumenterAgent class with LLM integration
- Add support for README and docstring generation
- Include tests with 85% coverage

Closes #45
```

---

## ⚠️ Important Notes

1. **Language**: Remember, ALL code and documentation MUST be in English
2. **Tests**: No commits without tests for new functionality
3. **Types**: Type hints are not optional
4. **Documentation**: Code without docs is incomplete
5. **Quality**: Run all checks before committing
6. **Incremental**: Make small, focused commits

---

**This document will evolve as the project grows. Check for updates regularly.**

Last updated: 2026-01-18
