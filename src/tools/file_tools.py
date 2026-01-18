"""File operation tools for agents."""

import os
from pathlib import Path
from typing import Any

from langchain_core.tools import tool


@tool
def read_file(file_path: str, project_path: str) -> dict[str, Any]:
    """Read contents of a file within the project directory.

    Args:
        file_path: Relative or absolute path to the file
        project_path: Absolute path to the project root

    Returns:
        Dictionary with 'content' on success or 'error' on failure
    """
    try:
        # Normalize paths
        abs_project_path = Path(project_path).resolve()
        
        # Handle both relative and absolute file paths
        if Path(file_path).is_absolute():
            abs_file_path = Path(file_path).resolve()
        else:
            abs_file_path = (abs_project_path / file_path).resolve()

        # Validate path is within project boundary
        try:
            abs_file_path.relative_to(abs_project_path)
        except ValueError:
            return {
                "error": f"Path outside project directory: {file_path}",
                "suggestion": f"File must be within {project_path}",
                "attempted_path": str(abs_file_path),
            }

        if not abs_file_path.exists():
            return {
                "error": f"File not found: {file_path}",
                "suggestion": "Check if the file path is correct",
                "attempted_path": str(abs_file_path),
            }

        if not abs_file_path.is_file():
            return {
                "error": f"Not a file: {file_path}",
                "suggestion": "Path points to a directory, not a file",
            }

        # Read file content
        with open(abs_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "content": content,
            "path": str(abs_file_path.relative_to(abs_project_path)),
            "absolute_path": str(abs_file_path),
            "size": len(content),
        }

    except PermissionError:
        return {
            "error": f"Permission denied: {file_path}",
            "suggestion": "Check file permissions",
        }
    except Exception as e:
        return {
            "error": f"Failed to read file: {str(e)}",
            "suggestion": "Verify file exists and is readable",
        }


@tool
def write_file(file_path: str, content: str, project_path: str) -> dict[str, Any]:
    """Write content to a file within the project directory.

    Args:
        file_path: Relative or absolute path to the file
        content: Content to write
        project_path: Absolute path to the project root

    Returns:
        Dictionary with 'success' message or 'error' on failure
    """
    try:
        # Normalize paths
        abs_project_path = Path(project_path).resolve()
        
        # Handle both relative and absolute file paths
        if Path(file_path).is_absolute():
            abs_file_path = Path(file_path).resolve()
        else:
            abs_file_path = (abs_project_path / file_path).resolve()

        # Validate path is within project boundary
        try:
            abs_file_path.relative_to(abs_project_path)
        except ValueError:
            return {
                "error": f"Path outside project directory: {file_path}",
                "suggestion": f"File must be within {project_path}",
                "attempted_path": str(abs_file_path),
            }

        # Create parent directories if they don't exist
        abs_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file content
        with open(abs_file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {
            "success": f"File written successfully: {file_path}",
            "path": str(abs_file_path.relative_to(abs_project_path)),
            "absolute_path": str(abs_file_path),
            "size": len(content),
        }

    except PermissionError:
        return {
            "error": f"Permission denied: {file_path}",
            "suggestion": "Check directory permissions",
        }
    except Exception as e:
        return {
            "error": f"Failed to write file: {str(e)}",
            "suggestion": "Verify directory exists and is writable",
        }


@tool
def search_code(query: str, project_path: str, file_extension: str = "") -> dict[str, Any]:
    """Search for code patterns in project files.

    Args:
        query: Search query (text to find)
        project_path: Absolute path to the project root
        file_extension: Optional file extension filter (e.g., ".rs", ".ex")

    Returns:
        Dictionary with 'matches' list or 'error' on failure
    """
    try:
        abs_project_path = Path(project_path).resolve()

        if not abs_project_path.exists():
            return {
                "error": f"Project path not found: {project_path}",
                "suggestion": "Verify project path is correct",
            }

        matches = []
        max_matches = 50  # Limit results to avoid overwhelming output

        # Walk through project directory
        for root, _dirs, files in os.walk(abs_project_path):
            # Skip hidden and common ignore directories
            skip_dirs = {".git", "__pycache__", "node_modules", "target", "_build", ".venv"}
            _dirs[:] = [d for d in _dirs if d not in skip_dirs and not d.startswith(".")]

            for file in files:
                # Apply extension filter
                if file_extension and not file.endswith(file_extension):
                    continue

                # Skip hidden files and common binaries
                if file.startswith(".") or file.endswith((".pyc", ".so", ".o")):
                    continue

                file_path = Path(root) / file
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if query.lower() in line.lower():
                                rel_path = file_path.relative_to(abs_project_path)
                                matches.append(
                                    {
                                        "file": str(rel_path),
                                        "line": line_num,
                                        "content": line.strip(),
                                    }
                                )

                                if len(matches) >= max_matches:
                                    return {
                                        "matches": matches,
                                        "truncated": True,
                                        "message": f"Showing first {max_matches} matches",
                                    }
                except (UnicodeDecodeError, PermissionError):
                    # Skip binary files and files without permission
                    continue

        return {"matches": matches, "total": len(matches)}

    except Exception as e:
        return {
            "error": f"Search failed: {str(e)}",
            "suggestion": "Verify project path and search query",
        }


def get_file_tools() -> list[Any]:
    """Get list of all file operation tools.

    Returns:
        List of file tools
    """
    return [read_file, write_file, search_code]
