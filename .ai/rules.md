# Hard Rules

> Non-negotiable requirements for all code and commits

---

## Language

- ✅ **MUST**: All code, comments, docstrings, docs in English
- ❌ **NEVER**: Chinese in code or technical documentation
- ⚠️ **Exception**: User-facing UI text if explicitly required

---

## Type Safety

- ✅ **MUST**: Type hints on all function parameters and returns
- ❌ **NEVER**: Use `any` without explicit justification
- ✅ **MUST**: Use `Optional[T]` for nullable values

---

## Testing

- ✅ **MUST**: Write tests for all new functions
- ✅ **MUST**: Achieve >80% coverage for new code
- ❌ **NEVER**: Commit without running test suite
- ✅ **MUST**: Tests pass before commit

---

## Error Handling

- ✅ **MUST**: Use specific exception types
- ❌ **NEVER**: Catch and silence exceptions (`except: pass`)
- ✅ **MUST**: Log errors with context

---

## Code Quality

- ✅ **MUST**: Run `black`, `isort`, `mypy`, `ruff` before commit
- ✅ **MUST**: Keep functions under 50 lines
- ❌ **NEVER**: Leave debug print statements
- ❌ **NEVER**: Hardcode paths, URLs, API keys

---

## Documentation

- ✅ **MUST**: Google-style docstrings for all public functions
- ✅ **MUST**: Update README when adding major features
- ❌ **NEVER**: Leave TODO without issue link

---

## Project Scoping

- ✅ **MUST**: All file operations use `project_path` from config
- ✅ **MUST**: Validate paths within project boundary
- ❌ **NEVER**: Access files outside assigned project
- ❌ **NEVER**: Modify multiple projects in single operation without explicit approval

---

## Git

- ✅ **MUST**: Use conventional commit format
- ✅ **MUST**: Commits must be atomic (one logical change)
- ❌ **NEVER**: Commit generated files or secrets
- ✅ **MUST**: Write meaningful commit messages

---

## Dependencies

- ✅ **MUST**: Pin versions in `pyproject.toml` or `requirements.txt`
- ❌ **NEVER**: Add dependencies without justification
- ✅ **MUST**: Document why each dependency is needed

---

## Security

- ❌ **NEVER**: Execute arbitrary user input as code
- ❌ **NEVER**: Log sensitive information
- ✅ **MUST**: Validate all external inputs
- ✅ **MUST**: Use timeouts for external calls

---

## Architecture

- ✅ **MUST**: Follow single responsibility principle
- ❌ **NEVER**: Create project-specific agents (use generic + context)
- ✅ **MUST**: Use dependency injection
- ❌ **NEVER**: Use global mutable state

---

## Performance

- ✅ **MUST**: Use async/await for I/O operations
- ❌ **NEVER**: Block event loop with CPU-intensive work
- ✅ **MUST**: Set timeouts on all external calls
- ✅ **MUST**: Clean up resources (use context managers)

---

**Violation of any rule marked ❌ NEVER is a critical error.**

Last updated: 2026-01-18
