"""Architect agent for system design and technical decisions."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from src.graph.state import MultiProjectState


def architect_node(state: MultiProjectState, config: RunnableConfig) -> dict[str, list]:
    """Architect agent that handles system design and architecture decisions.

    Args:
        state: Current workflow state
        config: Runnable configuration

    Returns:
        Dictionary with 'messages' to add to state
    """
    # Get LLM and tools from config
    llm = config["configurable"]["llm"]
    tools = config["configurable"].get("tools", [])

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Get project context
    project_context = state.get("project_context")
    if not project_context:
        return {
            "messages": [
                AIMessage(
                    content="Error: No project context available. Please select a project first."
                )
            ]
        }

    project_info = project_context["info"]
    examples = project_context.get("examples", {}).get("architect", {})

    # Build system prompt
    system_prompt = f"""You are a software architect working on the {project_info['name']} project.

Project Context:
- Type: {project_info['type']}
- Description: {project_info['description']}
- Tech Stack: {', '.join(f"{k}: {v}" for k, v in project_info['tech_stack'].items())}

Your responsibilities:
- Design system architecture
- Make technology decisions
- Define module boundaries
- Create technical specifications
- Consider scalability and maintainability

Conventions to follow:
{chr(10).join(f"- {c}" for c in project_info.get('conventions', []))}

Coding Standards:
{chr(10).join(f"- {k}: {v}" for k, v in project_info.get('coding_standards', {}).items())}
"""

    # Add few-shot examples if available
    if examples:
        system_prompt += "\n\nExample approaches:\n"
        for task_type, task_examples in examples.items():
            if task_examples:
                system_prompt += f"\n{task_type.replace('_', ' ').title()}:\n"
                first_example = task_examples[0]
                system_prompt += f"Input: {first_example.get('input', '')}\n"
                system_prompt += f"Output: {first_example.get('output', '')[:200]}...\n"

    # Get task and recent messages
    task = state.get("task", "")
    recent_messages = state.get("messages", [])[-3:]  # Last 3 messages for context

    # Build messages
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(recent_messages)
    messages.append(HumanMessage(content=f"Task: {task}"))

    # Invoke LLM
    response = llm_with_tools.invoke(messages)

    # Return messages to add to state
    return {"messages": [response], "next_agent": ""}
