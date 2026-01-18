"""Tests for graph builder and workflow."""

from unittest.mock import MagicMock, patch

import pytest

from src.graph.builder import build_graph, get_all_tools, route_to_agent
from src.graph.state import MultiProjectState


def test_get_all_tools():
    """Test that all tools are collected."""
    tools = get_all_tools()

    # Should have file tools (3) + git tools (2) = 5 tools
    assert len(tools) >= 5

    tool_names = [tool.name for tool in tools]
    assert "read_file" in tool_names
    assert "write_file" in tool_names
    assert "search_code" in tool_names
    assert "git_status" in tool_names
    assert "git_commit" in tool_names


def test_route_to_agent_valid():
    """Test routing to valid agents."""
    state = MultiProjectState(
        messages=[],
        current_project="test",
        projects={},
        project_context=None,
        next_agent="developer",
        task="test",
    )

    result = route_to_agent(state)
    assert result == "developer"


def test_route_to_agent_end():
    """Test routing to end."""
    state = MultiProjectState(
        messages=[],
        current_project="test",
        projects={},
        project_context=None,
        next_agent="end",
        task="test",
    )

    result = route_to_agent(state)
    assert result == "__end__"


def test_route_to_agent_empty():
    """Test routing with empty next_agent."""
    state = MultiProjectState(
        messages=[],
        current_project="test",
        projects={},
        project_context=None,
        next_agent="",
        task="test",
    )

    result = route_to_agent(state)
    assert result == "__end__"


def test_route_to_agent_invalid():
    """Test routing with invalid agent name."""
    state = MultiProjectState(
        messages=[],
        current_project="test",
        projects={},
        project_context=None,
        next_agent="invalid_agent",
        task="test",
    )

    result = route_to_agent(state)
    assert result == "__end__"


@patch("src.graph.builder.create_checkpointer")
def test_build_graph(mock_checkpointer, mock_llm_client):
    """Test graph building and compilation."""
    from langgraph.checkpoint.memory import MemorySaver

    # Use a real MemorySaver instead of MagicMock
    mock_checkpointer.return_value = MemorySaver()

    graph = build_graph(mock_llm_client)

    assert graph is not None
    # Graph should be compiled
    assert hasattr(graph, "invoke")
    assert hasattr(graph, "stream")
