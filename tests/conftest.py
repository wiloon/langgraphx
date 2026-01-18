"""Test fixtures and utilities."""

from unittest.mock import MagicMock

import pytest

from src.config.projects import ProjectRegistry
from src.graph.state import MultiProjectState, ProjectContext, ProjectInfo
from src.llm.proxy_client import LLMClient


@pytest.fixture
def mock_llm_client() -> MagicMock:
    """Create a mock LLM client for testing.

    Returns:
        Mock LLMClient
    """
    mock = MagicMock(spec=LLMClient)
    mock.get_chat_model.return_value = MagicMock()
    return mock


@pytest.fixture
def sample_project_info() -> ProjectInfo:
    """Create sample project info for testing.

    Returns:
        Sample ProjectInfo
    """
    return ProjectInfo(
        name="test_project",
        type="python",
        description="Test project for unit tests",
        path="/tmp/test_project",
        tech_stack={"language": "python", "version": "3.11"},
        tools={"test": "pytest", "lint": "ruff"},
        conventions=["Use type hints", "Follow PEP 8"],
        coding_standards={"line_length": 100},
        test_framework="pytest",
        coverage_target=80,
    )


@pytest.fixture
def sample_project_context(sample_project_info: ProjectInfo) -> ProjectContext:
    """Create sample project context for testing.

    Args:
        sample_project_info: Sample project info

    Returns:
        Sample ProjectContext
    """
    return ProjectContext(
        info=sample_project_info,
        examples={
            "developer": {
                "implement_feature": [
                    {
                        "input": "Add logging",
                        "output": "import logging\nlogger = logging.getLogger(__name__)",
                    }
                ]
            }
        },
    )


@pytest.fixture
def sample_state(sample_project_context: ProjectContext) -> MultiProjectState:
    """Create sample workflow state for testing.

    Args:
        sample_project_context: Sample project context

    Returns:
        Sample MultiProjectState
    """
    return MultiProjectState(
        messages=[],
        current_project="test_project",
        projects={"test_project": sample_project_context["info"]},
        project_context=sample_project_context,
        next_agent="",
        task="Test task",
    )


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory with config files.

    Args:
        tmp_path: pytest tmp_path fixture

    Returns:
        Path to temporary project directory
    """
    project_dir = tmp_path / "projects" / "test_project"
    project_dir.mkdir(parents=True)

    # Create config.yaml
    config_content = """
name: test_project
type: python
description: Test project
path: /tmp/test_project
tech_stack:
  language: python
  version: "3.11"
tools:
  test: pytest
conventions:
  - Use type hints
coding_standards:
  line_length: 100
test_framework: pytest
coverage_target: 80
"""
    (project_dir / "config.yaml").write_text(config_content)

    # Create examples.yaml
    examples_content = """
developer:
  implement_feature:
    - input: "Add logging"
      output: "import logging"
"""
    (project_dir / "examples.yaml").write_text(examples_content)

    return tmp_path / "projects"


@pytest.fixture
def project_registry(temp_project_dir):
    """Create a ProjectRegistry with temp projects.

    Args:
        temp_project_dir: Temporary project directory

    Returns:
        ProjectRegistry instance
    """
    return ProjectRegistry(temp_project_dir)
