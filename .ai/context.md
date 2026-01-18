# Project Context

> Quick reference for AI agents to understand the project

---

## What is LangGraphX?

Multi-agent collaborative software development system built on LangGraph.

**Purpose**: Enable multiple AI agents to cooperatively develop software projects.

---

## Key Facts

- **Framework**: LangGraph (state machine orchestration)
- **LLM**: Claude Sonnet 4.5 via vscode-lm-proxy
- **Language**: Python 3.11+
- **Architecture**: Generic agents + project context (NOT project-specific agents)

---

## Supported Projects

1. **rssx** - `/Users/wiloon/workspace/projects/rssx` (Rust)
2. **enx** - `/Users/wiloon/workspace/projects/enx` (Elixir)

Projects are managed through configuration, not separate agent implementations.

---

## Agent Roles

All agents are **generic** and adapt to projects via context:

- **Supervisor** - Routes tasks, manages project switching
- **Architect** - System design, tech decisions
- **Developer** - Code implementation
- **Reviewer** - Code review, quality checks
- **Tester** - Test design and implementation
- **Documenter** - Documentation maintenance

---

## State Management

**Single thread** with project tagging (not multi-thread):

```python
MultiProjectState = {
    "current_project": "rssx",       # Active project
    "projects": {...},                # All registered projects
    "project_contexts": {...},        # Per-project runtime state
    "messages": [...]                 # Shared conversation
}
```

---

## Core Principles

1. **Generic over Specific**: One agent works on all projects
2. **Context Injection**: Project details passed via state
3. **Tool Scoping**: Tools operate within project boundaries
4. **English Only**: All code, comments, docs in English
5. **Type Safety**: Mandatory type hints everywhere

---

## Project Structure

```
langgraphx/
├── .ai/                  # AI agent instructions (you are here)
├── docs/                 # Human documentation
├── src/
│   ├── agents/          # Agent implementations
│   ├── graph/           # LangGraph workflow
│   ├── tools/           # Project-scoped tools
│   ├── llm/             # LLM client (proxy)
│   └── config/          # Project registry
├── projects/            # Per-project configs
│   ├── rssx/config.yaml
│   └── enx/config.yaml
└── tests/
```

---

## Important Decisions

All architectural decisions are documented in `docs/adr/`:

- **ADR-001**: Why LangGraph (not AutoGen/CrewAI)
- **ADR-002**: Why generic agents (not project-specific)
- **ADR-003**: Why vscode-lm-proxy (cost + Copilot integration)
- **ADR-004**: Why single-thread state (not multi-thread)

---

## When to Read More

- **Detailed architecture**: See `docs/architecture.md`
- **Design rationale**: See `docs/adr/`
- **Task workflows**: See `.ai/workflows/`
- **Coding rules**: See `.ai/instructions.md` (this is mandatory)

---

## Quick Start for Tasks

1. **Identify project**: Which project (rssx/enx)?
2. **Check workflows**: `.ai/workflows/` for task type
3. **Load project config**: `projects/{name}/config.yaml`
4. **Use scoped tools**: All tools respect `project_path` in config
5. **Update state**: Modify `project_contexts[project]` not other projects

---

Last updated: 2026-01-18
