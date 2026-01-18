"""LangGraph workflow builder."""

from typing import Any, Literal

from langgraph.graph import END, StateGraph

from src.agents.architect import architect_node
from src.agents.developer import developer_node
from src.agents.reviewer import reviewer_node
from src.agents.supervisor import supervisor_node
from src.agents.tester import tester_node
from src.graph.checkpointer import create_checkpointer
from src.graph.state import MultiProjectState
from src.llm.proxy_client import LLMClient
from src.tools.file_tools import get_file_tools
from src.tools.git_tools import get_git_tools


def route_to_agent(
    state: MultiProjectState,
) -> Literal["architect", "developer", "reviewer", "tester", "__end__"]:
    """Route to next agent based on supervisor's decision.

    Args:
        state: Current workflow state

    Returns:
        Name of next agent or END
    """
    next_agent = state.get("next_agent", "")

    if not next_agent or next_agent == "end":
        return "__end__"

    # Validate agent exists
    valid_agents = {"architect", "developer", "reviewer", "tester"}
    if next_agent in valid_agents:
        return next_agent  # type: ignore

    # Default to end if invalid
    return "__end__"


def build_graph(llm_client: LLMClient) -> CompiledGraph:
    """Build and compile the LangGraph worAny

    Args:
        llm_client: LLM client for agents

    Returns:
        Compiled graph ready for execution
    """
    # Create workflow
    workflow = StateGraph(MultiProjectState)

    # Add agent nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("architect", architect_node)
    workflow.add_node("developer", developer_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("tester", tester_node)

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add routing edges from supervisor
    workflow.add_conditional_edges("supervisor", route_to_agent)

    # Add edges back to supervisor from agents (for multi-step workflows)
    # For now, agents go directly to END after completing their task
    workflow.add_edge("architect", END)
    workflow.add_edge("developer", END)
    workflow.add_edge("reviewer", END)
    workflow.add_edge("tester", END)

    # Create checkpointer for state persistence
    checkpointer = create_checkpointer()

    # Compile graph with checkpointer
    compiled_graph = workflow.compile(checkpointer=checkpointer)

    return compiled_graph


def create_graph(llm_client: LLMClient) -> Any:
    """Factory function to create configured graph.

    Args:
        llm_client: LLM client for agents

    Returns:
        Compiled graph ready for execution
    """
    return build_graph(llm_client)


def get_all_tools() -> list[Any]:
    """Get all available tools for agents.

    Returns:
        List of all tools
    """
    tools = []
    tools.extend(get_file_tools())
    tools.extend(get_git_tools())
    return tools
