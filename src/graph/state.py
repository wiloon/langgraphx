"""State definitions for LangGraph workflow."""

from typing import Annotated, Any, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages


class ProjectInfo(TypedDict):
    """Project metadata."""

    name: str
    type: str  # rust, elixir, python, etc.
    description: str
    path: str
    tech_stack: dict[str, Any]
    tools: dict[str, str]
    conventions: list[str]
    coding_standards: dict[str, Any]
    test_framework: str
    coverage_target: int


class ProjectContext(TypedDict):
    """Project-specific context for agents."""

    info: ProjectInfo
    examples: dict[str, Any]  # Few-shot examples loaded from examples.yaml


class MultiProjectState(TypedDict):
    """State shared across all agents in the workflow."""

    # Message history (automatically merges new messages)
    messages: Annotated[list[AnyMessage], add_messages]

    # Current active project
    current_project: str

    # Registry of all available projects
    projects: dict[str, ProjectInfo]

    # Loaded context for the current project
    project_context: ProjectContext | None

    # Next agent to route to (set by supervisor)
    next_agent: str

    # Task description from user
    task: str
