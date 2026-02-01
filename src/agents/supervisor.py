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

    # Check if this is a re-entry after an agent completed work
    messages = state.get("messages", [])
    recent_work = []
    if len(messages) > 1:
        # Get recent agent outputs
        for msg in messages[-5:]:
            if hasattr(msg, "content") and msg.content:
                # Handle both string and list content
                content = msg.content
                if isinstance(content, list):
                    # Extract text from list of content blocks
                    text_parts = []
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            text_parts.append(item["text"])
                        elif isinstance(item, str):
                            text_parts.append(item)
                    content = " ".join(text_parts)

                if isinstance(content, str) and content:
                    recent_work.append(content[:200])  # First 200 chars

    # Build system prompt
    system_prompt = """You are a supervisor agent coordinating a team of software development agents.

Your team consists of:
- architect: Analyzes requirements, investigates project structure, searches for files
- developer: Implements features, modifies files, writes code  
- reviewer: Reviews code for quality, best practices, and issues
- tester: Designs and implements tests

Multi-Step Workflow Logic:
1. If architect has investigated and found information → route to developer to make changes
2. If developer has made changes → optionally route to reviewer (or end if simple task)
3. If reviewer found issues → route back to developer
4. Task is COMPLETE when:
   - Architect answered a query (information-only tasks)
   - Developer successfully modified files
   - Tests passed
   
CRITICAL: Respond with ONLY ONE WORD:
- "architect" - to investigate/search/analyze
- "developer" - to implement/modify/write code  
- "reviewer" - to review code
- "tester" - to write/run tests
- "end" - if task is complete

Examples:
Initial: "Check config file" → architect
After architect found file → developer (to make changes) or end (if just checking)
Initial: "Modify ingress.yaml" → architect (to find file first)
After architect found file → developer (to modify it)
After developer modified → end (or reviewer for complex changes)
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

    # Add recent work context
    if recent_work:
        context_info += f"\n\nRecent agent work:\n" + "\n".join(recent_work[-2:])

    # Create messages
    prompt = f"""{context_info}

Original task: {task}

Based on the task and recent work, what should be the next step?
Respond with ONLY: architect, developer, reviewer, tester, or end"""

    messages_to_send = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt),
    ]

    # Get routing decision
    response = llm.invoke(messages_to_send)
    next_agent = response.content.strip().lower()

    # Validate response
    valid_agents = {"architect", "developer", "reviewer", "tester", "end"}
    if next_agent not in valid_agents:
        # If architect already did work, default to developer
        # Otherwise default to architect for investigation
        if recent_work and any("tool" in w.lower() or "search" in w.lower() for w in recent_work):
            next_agent = "developer"
        else:
            next_agent = "architect"

    return {"next_agent": next_agent}
