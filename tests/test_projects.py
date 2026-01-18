"""Tests for ProjectRegistry."""

from pathlib import Path

import pytest

from src.config.projects import ProjectRegistry


def test_project_registry_discovery(project_registry):
    """Test automatic project discovery."""
    projects = project_registry.list_names()
    assert "test_project" in projects


def test_project_registry_get(project_registry):
    """Test getting project info."""
    project = project_registry.get("test_project")
    assert project["name"] == "test_project"
    assert project["type"] == "python"


def test_project_registry_get_not_found(project_registry):
    """Test getting non-existent project."""
    with pytest.raises(KeyError):
        project_registry.get("nonexistent")


def test_project_registry_load_context(project_registry):
    """Test loading project context with examples."""
    context = project_registry.load_context("test_project")
    assert context["info"]["name"] == "test_project"
    assert "developer" in context["examples"]


def test_detect_type_rust(tmp_path):
    """Test detecting Rust project."""
    project_dir = tmp_path / "rust_project"
    project_dir.mkdir()
    (project_dir / "Cargo.toml").touch()

    registry = ProjectRegistry(tmp_path)
    project_type = registry.detect_type(str(project_dir))
    assert project_type == "rust"


def test_detect_type_python(tmp_path):
    """Test detecting Python project."""
    project_dir = tmp_path / "python_project"
    project_dir.mkdir()
    (project_dir / "pyproject.toml").touch()

    registry = ProjectRegistry(tmp_path)
    project_type = registry.detect_type(str(project_dir))
    assert project_type == "python"


def test_detect_type_unknown(tmp_path):
    """Test detecting unknown project type."""
    project_dir = tmp_path / "unknown_project"
    project_dir.mkdir()

    registry = ProjectRegistry(tmp_path)
    project_type = registry.detect_type(str(project_dir))
    assert project_type == ""
