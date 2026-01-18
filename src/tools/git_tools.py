"""Git operation tools for agents."""

import subprocess
from pathlib import Path
from typing import Any

from langchain_core.tools import tool


@tool
def git_status(project_path: str) -> dict[str, Any]:
    """Get git status of the project repository.

    Args:
        project_path: Absolute path to the project root

    Returns:
        Dictionary with 'status' output or 'error' on failure
    """
    try:
        abs_project_path = Path(project_path).resolve()

        if not abs_project_path.exists():
            return {
                "error": f"Project path not found: {project_path}",
                "suggestion": "Verify project path is correct",
            }

        # Check if directory is a git repository
        git_dir = abs_project_path / ".git"
        if not git_dir.exists():
            return {
                "error": "Not a git repository",
                "suggestion": "Initialize git with: git init",
            }

        # Run git status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=abs_project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "error": f"Git command failed: {result.stderr}",
                "suggestion": "Check git repository state",
            }

        # Parse porcelain output
        lines = result.stdout.strip().split("\n") if result.stdout.strip() else []
        changes = []

        for line in lines:
            if len(line) >= 3:
                status = line[:2]
                file_path = line[3:]
                changes.append({"status": status.strip(), "file": file_path})

        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=abs_project_path,
            capture_output=True,
            text=True,
            timeout=5,
        )

        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        return {
            "branch": current_branch,
            "changes": changes,
            "clean": len(changes) == 0,
            "total_changes": len(changes),
        }

    except subprocess.TimeoutExpired:
        return {
            "error": "Git command timed out",
            "suggestion": "Repository might be too large or unresponsive",
        }
    except FileNotFoundError:
        return {
            "error": "Git not found",
            "suggestion": "Install git: https://git-scm.com/downloads",
        }
    except Exception as e:
        return {
            "error": f"Git status failed: {str(e)}",
            "suggestion": "Verify git repository is valid",
        }


@tool
def git_commit(message: str, project_path: str, files: list[str] | None = None) -> dict[str, Any]:
    """Commit changes to git repository.

    Args:
        message: Commit message
        project_path: Absolute path to the project root
        files: Optional list of specific files to commit (None = all changes)

    Returns:
        Dictionary with 'success' message or 'error' on failure
    """
    try:
        abs_project_path = Path(project_path).resolve()

        if not abs_project_path.exists():
            return {
                "error": f"Project path not found: {project_path}",
                "suggestion": "Verify project path is correct",
            }

        # Check if directory is a git repository
        git_dir = abs_project_path / ".git"
        if not git_dir.exists():
            return {
                "error": "Not a git repository",
                "suggestion": "Initialize git with: git init",
            }

        # Validate commit message
        if not message or len(message.strip()) < 3:
            return {
                "error": "Commit message too short",
                "suggestion": "Provide a descriptive commit message (min 3 characters)",
            }

        # Stage files
        if files:
            # Stage specific files
            for file in files:
                result = subprocess.run(
                    ["git", "add", file],
                    cwd=abs_project_path,
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    return {
                        "error": f"Failed to stage file {file}: {result.stderr}",
                        "suggestion": "Check if file exists and is tracked",
                    }
        else:
            # Stage all changes
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=abs_project_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return {
                    "error": f"Failed to stage changes: {result.stderr}",
                    "suggestion": "Check git repository state",
                }

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=abs_project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            # Check if there are no changes to commit
            if "nothing to commit" in result.stdout.lower():
                return {
                    "error": "No changes to commit",
                    "suggestion": "Make changes first or check git status",
                }
            return {
                "error": f"Commit failed: {result.stderr}",
                "suggestion": "Check git configuration (user.name, user.email)",
            }

        # Parse commit output for commit hash
        commit_hash = ""
        for line in result.stdout.split("\n"):
            if "commit" in line.lower() or "[" in line:
                commit_hash = line.strip()
                break

        return {
            "success": "Changes committed successfully",
            "message": message,
            "commit": commit_hash,
            "files_staged": len(files) if files else "all",
        }

    except subprocess.TimeoutExpired:
        return {
            "error": "Git command timed out",
            "suggestion": "Operation took too long",
        }
    except FileNotFoundError:
        return {
            "error": "Git not found",
            "suggestion": "Install git: https://git-scm.com/downloads",
        }
    except Exception as e:
        return {
            "error": f"Git commit failed: {str(e)}",
            "suggestion": "Verify git repository and configuration",
        }


def get_git_tools() -> list[Any]:
    """Get list of all git operation tools.

    Returns:
        List of git tools
    """
    return [git_status, git_commit]
