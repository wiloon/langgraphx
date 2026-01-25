# Using uv with LangGraphX

This project uses **uv** for Python version and dependency management.

## Quick Start

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Run the system
python -m src.main

# Or use uv directly (no activation needed)
uv run python -m src.main
```

## Development Commands

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Add new dependency
uv pip install <package-name>
uv pip freeze >> requirements.txt  # if needed

# Run tests
uv run pytest tests/ -v

# Run linters
uv run ruff check src/
uv run black src/
uv run mypy src/

# Verify setup
uv run python scripts/verify_setup.py
```

## Python Version Management

```bash
# Show current Python version
cat .python-version  # Shows: 3.14

# List available Python versions
uv python list

# Change Python version
uv python pin 3.15  # when 3.15 is released

# Recreate environment with new version
rm -rf .venv
uv venv
uv pip install -e ".[dev]"
```

## Why uv?

- ⚡ **10-100x faster** than pip
- 🐍 **Python version management** built-in (replaces pyenv)
- 🔒 **Consistent** dependency resolution
- 🎯 **Modern** Python tooling for 2026

## Environment Info

- **Python Version**: 3.14.2
- **Package Manager**: uv 0.9.26
- **Virtual Environment**: `.venv/`
- **Version Lock**: `.python-version`

## Troubleshooting

### Environment issues
```bash
# Clean and rebuild
rm -rf .venv
uv venv
uv pip install -e ".[dev]"
```

### Import errors
```bash
# Make sure environment is activated
source .venv/bin/activate

# Or use uv run
uv run python your_script.py
```

### Python version issues
```bash
# Check current version
uv python list

# Ensure correct version is pinned
cat .python-version
```
