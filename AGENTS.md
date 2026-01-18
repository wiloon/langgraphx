# AI Agent Guidelines

This is the index file for AI agent documentation. All detailed guidelines are in the `.ai/` directory.

## 📚 Quick Navigation

### Core Guidelines
- **[.ai/instructions.md](.ai/instructions.md)** - Mandatory coding standards and best practices
- **[.ai/context.md](.ai/context.md)** - 5-minute project overview
- **[.ai/rules.md](.ai/rules.md)** - Non-negotiable hard rules (DO/DON'T checklist)

### Step-by-Step Workflows
- **[.ai/workflows/add-agent.md](.ai/workflows/add-agent.md)** - How to create a new agent
- **[.ai/workflows/add-tool.md](.ai/workflows/add-tool.md)** - How to create a new tool
- **[.ai/workflows/add-project.md](.ai/workflows/add-project.md)** - How to register a new project

### Architecture Documentation (Human-Focused)
- **[docs/architecture.md](docs/architecture.md)** - Complete system architecture
- **[docs/adr/](docs/adr/)** - Architecture Decision Records

## 🚀 Getting Started

If you're an AI agent working on this project:

1. **First time?** Read [.ai/context.md](.ai/context.md) for a quick overview
2. **Need rules?** Check [.ai/rules.md](.ai/rules.md) for DO/DON'T lists
3. **Coding?** Follow [.ai/instructions.md](.ai/instructions.md) strictly
4. **Adding features?** Use the workflow guides in [.ai/workflows/](.ai/workflows/)

## 📋 Critical Rules Summary

- ✅ **English ONLY** for all code, comments, and documentation
- ✅ **Type hints mandatory** for all Python code
- ✅ **Test coverage required** for all new code
- ❌ **NEVER** commit secrets or credentials
- ❌ **NEVER** skip error handling

For complete rules, see [.ai/rules.md](.ai/rules.md).

## 💡 Project Overview

**langgraphx** is a multi-agent collaborative development system built with LangGraph 0.3.3+. It uses generic role-based agents (architect, developer, reviewer, tester) that adapt to different projects (rssx, enx) through context injection.

**Key Technologies:**
- LangGraph 0.3.3+ for workflow orchestration
- vscode-lm-proxy for LLM access via GitHub Copilot
- Claude Sonnet 4.5 as the primary LLM
- Python 3.11+ with strict type safety

For detailed architecture, see [docs/architecture.md](docs/architecture.md).

---

**Note:** This file is intentionally lightweight. All detailed documentation is organized in the `.ai/` directory for better maintainability.
