"""Tester agent for test design and implementation."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from src.graph.state import MultiProjectState


def tester_node(state: MultiProjectState, config: RunnableConfig) -> dict[str, list]:
    """Tester agent that designs and implements tests.

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
    examples = project_context.get("examples", {}).get("tester", {})

    # Build system prompt
    system_prompt = f"""You are a test engineer for the {project_info['name']} project.

Project Context:
- Type: {project_info['type']}
- Description: {project_info['description']}
- Language: {project_info['tech_stack'].get('language', 'unknown')}
- Test Framework: {project_info.get('test_framework', 'N/A')}
- Coverage Target: {project_info.get('coverage_target', 80)}%
- Project Path: {project_info['path']}

Your responsibilities:
- Design comprehensive test strategies
- Implement unit tests for all public APIs
- Create integration tests for critical paths
- Ensure test coverage meets target
- Write clear, maintainable test code
- Document test scenarios

Testing Strategy:
- Unit tests for all public APIs
- Integration tests for critical paths
- Edge cases and error conditions
- Performance tests where applicable
- Test coverage target: {project_info.get('coverage_target', 80)}%

Test Tools:
- Build: {project_info['tools'].get('build', 'N/A')}
- Test: {project_info['tools'].get('test', 'N/A')}

Available tools:
- read_file: Read existing code to understand what to test
- write_file: Create test files
- search_code: Find untested code
"""

    # Add few-shot examples if available
    if examples:
        system_prompt += "\n\nExample test designs:\n"
        for task_type, task_examples in examples.items():
            if task_examples:
                system_prompt += f"\n{task_type.replace('_', ' ').title()}:\n"
                first_example = task_examples[0]
                system_prompt += f"Input: {first_example.get('input', '')}\n"
                system_prompt += f"Output:\n{first_example.get('output', '')[:300]}...\n"

    # Get task and recent messages
    task = state.get("task", "")
    recent_messages = state.get("messages", [])[-5:]  # Last 5 messages for context

    # Build messages
    messages = [SystemMessage(content=system_prompt)]
    messages.extend(recent_messages)
    messages.append(HumanMessage(content=f"Testing task: {task}"))

    # Invoke LLM
    response = llm_with_tools.invoke(messages)

    # Return messages to add to state
    return {"messages": [response], "next_agent": ""}
