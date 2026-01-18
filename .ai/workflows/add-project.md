# Workflow: Adding Project Support

> Step-by-step guide for registering a new project

---

## Prerequisites

- [ ] Project exists and is accessible
- [ ] Know project type (rust, elixir, python, etc.)
- [ ] Have project path

---

## Steps

### 1. Create Project Config Directory

```bash
mkdir -p projects/<project_name>
mkdir -p projects/<project_name>/prompts
```

---

### 2. Create Project Configuration

**File**: `projects/<project_name>/config.yaml`

```yaml
# Project metadata
name: <project_name>
type: <rust|elixir|python|javascript|typescript>
description: <Brief project description>

# Technical stack
tech_stack:
  language: <language>
  version: "<version>"
  framework: <framework_name>  # Optional
  build_tool: <cargo|mix|npm|pip>

# Coding conventions (project-specific)
conventions:
  - <Convention 1>
  - <Convention 2>
  - <Convention 3>

# Build and test commands
tools:
  build: <command to build>
  test: <command to run tests>
  lint: <command to lint>
  format: <command to format>
  
# Dependencies (optional)
dependencies:
  - <dep1>
  - <dep2>
```

**Example for Rust project**:
```yaml
name: rssx
type: rust
description: RSS feed aggregator service

tech_stack:
  language: rust
  version: "1.75"
  framework: tokio
  build_tool: cargo

conventions:
  - Use async/await for I/O operations
  - Follow Rust API Guidelines
  - Comprehensive error handling with Result<T, E>
  - Use zero-copy parsing where possible

tools:
  build: cargo build --release
  test: cargo test
  lint: cargo clippy -- -D warnings
  format: cargo fmt --check

dependencies:
  - tokio
  - serde
  - feed-rs
```

---

### 3. Configure Workspace (Multi-Root)

**File**: `<workspace_name>.code-workspace`

Add project to folders:

```json
{
  "folders": [
    {"path": "."},
    {"path": "../rssx"},
    {"path": "../enx"},
    {"path": "../<new_project>"}  // Add this
  ],
  "settings": {
    "vscode-lm-proxy.port": 4000
  }
}
```

---

### 4. Test Project Registration

```python
# test_project_discovery.py
def test_new_project_discovered():
    """Test that new project is discovered."""
    from src.config.projects import discover_projects
    
    projects = discover_projects()
    
    assert "<project_name>" in projects
    assert projects["<project_name>"]["type"] == "<type>"
    assert projects["<project_name>"]["path"].exists()
```

---

## Checklist

- [ ] Project config directory created
- [ ] `config.yaml` with all required fields
- [ ] Project-specific prompts added (optional)
- [ ] Workspace configuration updated
- [ ] Project type detection working
- [ ] Project-specific tools loaded
- [ ] Tests pass for project discovery
- [ ] Can switch to project in conversation
- [ ] Agents can execute tasks on project

---

Last updated: 2026-01-18
