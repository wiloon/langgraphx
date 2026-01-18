"""Supervisor agent for task routing and coordination."""

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from src.graph.state import MultiProjectState


def supervisor_node(state: MultiProjectState, config: RunnableConfig) -> dict[str, str]:
    """Supervisor agent that analyzes tasks and routes to appropriate agent.

    Args:
        state: Current workflow state
        config: Runnable configuration

    Returns:
        Dictionary with 'next_agent' decision
    """
    # Get LLM from config
    llm = config["configurable"]["llm"]

    # Build system prompt
    system_prompt = """You are a supervisor agent coordinating a team of software development agents.

Your team consists of:
- architect: Designs system architecture, analyzes requirements, answers questions about code/project structure
- developer: Implements features, fixes bugs, and writes code
- reviewer: Reviews code for quality, best practices, and issues
- tester: Designs and implements tests

Routing Guidelines:
1. Information queries (checking versions, analyzing structure, reading docs) → architect
2. Implementation tasks (add feature, fix bug, write code) → developer
3. Code review requests (review code, check quality) → reviewer
4. Testing tasks (write tests, test coverage) → tester

Examples:
- "Check Go version" → architect (information query)
- "Read README file" → architect (information query)
- "Add error handling" → developer (implementation)
- "Review the HTTP client" → reviewer (code review)
- "Write unit tests" → tester (testing)

Analyze the user's task and determine which agent should handle it.
Respond with ONLY the agent name: architect, developer, reviewer, or tester
"""

    # Get task and current context
    task = state.get("task", "")
    current_project = state.get("current_project", "unknown")
    project_context = state.get("project_context")

    # Build context information
    context_info = f"Current project: {current_project}"
    if project_context:
        project_info = project_context["info"]
        context_info += f"\nProject type: {project_info['type']}"
        context_info += f"\nDescription: {project_info['description']}"

    # Create messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"{context_info}\n\nTask: {task}"),
    ]

    # Get routing decision
    response = llm.invoke(messages)
    next_agent = response.content.strip().lower()

    # Validate response
    valid_agents = {"architect", "developer", "reviewer", "tester"}
    if next_agent not in valid_agents:
        # Default to developer if unclear
        next_agent = "developer"

    return {"next_agent": next_agent}
