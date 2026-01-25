"""Project registry for managing multi-project configurations."""

import os
from pathlib import Path
from typing import Any

import yaml

from src.graph.state import ProjectContext, ProjectInfo


class ProjectRegistry:
    """Registry for managing project configurations."""

    def __init__(self, projects_dir: str | Path = "projects") -> None:
        """Initialize project registry.

        Args:
            projects_dir: Directory containing project configurations
        """
        self.projects_dir = Path(projects_dir)
        self._projects: dict[str, ProjectInfo] = {}
        self._examples: dict[str, dict[str, Any]] = {}

        # Auto-discover and load projects
        self._discover_projects()

    def _discover_projects(self) -> None:
        """Discover and load all projects from projects directory."""
        if not self.projects_dir.exists():
            return

        for project_dir in self.projects_dir.iterdir():
            if project_dir.is_dir():
                config_file = project_dir / "config.yaml"
                if config_file.exists():
                    self._load_project(project_dir.name)

    def _load_project(self, name: str) -> None:
        """Load project configuration and examples.

        Args:
            name: Project name
        """
        project_dir = self.projects_dir / name
        config_file = project_dir / "config.yaml"
        examples_file = project_dir / "examples.yaml"

        # Load config
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        # Validate required fields
        required_fields = ["name", "type", "description", "path", "tech_stack", "tools"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Project {name} missing required field: {field}")

        # Validate project path exists
        project_path = Path(config["path"])
        if not project_path.exists():
            raise ValueError(
                f"Project path does not exist: {config['path']}\n"
                f"Please ensure the project is cloned or update the path in {config_file}"
            )

        # Resolve symlinks to get real path
        config["path"] = str(project_path.resolve())

        self._projects[name] = ProjectInfo(**config)

        # Load examples if available
        if examples_file.exists():
            with open(examples_file, "r") as f:
                self._examples[name] = yaml.safe_load(f) or {}

    def register(self, name: str, path: str) -> ProjectInfo:
        """Register a new project by detecting its type and creating config.

        Args:
            name: Project name
            path: Absolute path to project directory

        Returns:
            ProjectInfo for the registered project

        Raises:
            ValueError: If project type cannot be detected
        """
        project_type = self.detect_type(path)
        if not project_type:
            raise ValueError(f"Could not detect project type for {path}")

        # Create basic config
        config = ProjectInfo(
            name=name,
            type=project_type,
            description=f"{project_type.capitalize()} project",
            path=path,
            tech_stack={"language": project_type},
            tools={},
            conventions=[],
            coding_standards={},
            test_framework="",
            coverage_target=80,
        )

        self._projects[name] = config
        return config

    def get(self, name: str) -> ProjectInfo:
        """Get project information by name.

        Args:
            name: Project name

        Returns:
            ProjectInfo for the project

        Raises:
            KeyError: If project not found
        """
        if name not in self._projects:
            raise KeyError(f"Project '{name}' not found. Available: {list(self._projects.keys())}")
        return self._projects[name]

    def list(self) -> list[ProjectInfo]:
        """List all registered projects.

        Returns:
            List of all ProjectInfo objects
        """
        return list(self._projects.values())

    def detect_type(self, path: str) -> str:
        """Auto-detect project type from files in directory.

        Args:
            path: Path to project directory

        Returns:
            Detected project type (rust, elixir, python, etc.)
        """
        project_path = Path(path)
        if not project_path.exists():
            return ""

        # Check for language-specific files
        if (project_path / "Cargo.toml").exists():
            return "rust"
        elif (project_path / "mix.exs").exists():
            return "elixir"
        elif (project_path / "pyproject.toml").exists() or (project_path / "setup.py").exists():
            return "python"
        elif (project_path / "package.json").exists():
            return "javascript"
        elif (project_path / "go.mod").exists():
            return "go"
        elif (project_path / "pom.xml").exists() or (project_path / "build.gradle").exists():
            return "java"

        return ""

    def load_config(self, name: str) -> dict[str, Any]:
        """Load raw project configuration.

        Args:
            name: Project name

        Returns:
            Raw configuration dictionary
        """
        return dict(self._projects[name])

    def load_context(self, name: str) -> ProjectContext:
        """Load complete project context including examples.

        Args:
            name: Project name

        Returns:
            ProjectContext with info and examples

        Raises:
            KeyError: If project not found
        """
        if name not in self._projects:
            raise KeyError(f"Project '{name}' not found")

        return ProjectContext(
            info=self._projects[name],
            examples=self._examples.get(name, {}),
        )

    def list_names(self) -> list[str]:
        """Get list of all project names.

        Returns:
            List of project names
        """
        return list(self._projects.keys())


def create_project_registry(projects_dir: str | Path = "projects") -> ProjectRegistry:
    """Factory function to create project registry.

    Args:
        projects_dir: Directory containing project configurations

    Returns:
        Configured ProjectRegistry instance
    """
    return ProjectRegistry(projects_dir)
