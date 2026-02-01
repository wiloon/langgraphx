"""CLI entry point for LangGraphX."""

import argparse
import sys
from typing import Any

from langchain_core.messages import HumanMessage

from src.config.projects import create_project_registry
from src.graph.builder import create_graph, get_all_tools
from src.llm.proxy_client import create_llm_client


def run_task(
    task: str,
    project: str | None = None,
    registry=None,
    graph=None,
    llm_client=None,
    tools=None,
) -> None:
    """Execute a single task.

    Args:
        task: Task description
        project: Project name (optional, uses first project if not specified)
        registry: Project registry instance
        graph: Compiled graph instance
        llm_client: LLM client instance
        tools: Available tools list
    """
    # Use provided project or default to first available
    projects = registry.list_names()
    current_project = project if project and project in projects else projects[0]

    print(f"\n🔄 Processing task with {current_project}...\n")

    # Load project context
    context = registry.load_context(current_project)

    # Prepare state
    initial_state: dict[str, Any] = {
        "messages": [HumanMessage(content=task)],
        "current_project": current_project,
        "projects": {p: registry.get(p) for p in projects},
        "project_context": context,
        "next_agent": "",
        "task": task,
    }

    # Configure graph
    config = {
        "configurable": {
            "llm": llm_client.get_chat_model(),
            "tools": tools,
            "thread_id": f"{current_project}_session",
        }
    }

    # Execute workflow
    for event in graph.stream(initial_state, config):
        for node_name, node_output in event.items():
            print(f"📍 {node_name.upper()}")

            if "messages" in node_output:
                messages = node_output["messages"]
                if messages:
                    last_message = messages[-1]
                    print(f"💬 {last_message.content}\n")

            if "next_agent" in node_output and node_output["next_agent"]:
                print(f"➡️  Routing to: {node_output['next_agent']}\n")

    print("✅ Task completed!\n")


def main() -> None:
    """Main CLI entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="LangGraphX - Multi-Agent Development System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task to execute (if not provided, enters interactive mode)",
    )
    parser.add_argument(
        "-p",
        "--project",
        help="Project to use (default: first available project)",
    )
    parser.add_argument(
        "-l",
        "--list-projects",
        action="store_true",
        help="List available projects and exit",
    )

    args = parser.parse_args()

    print("🤖 LangGraphX - Multi-Agent Development System")
    print("=" * 60)

    try:
        # Initialize components
        print("\n📦 Initializing components...")

        # Create LLM client
        print("  - Connecting to vscode-lm-proxy...")
        llm_client = create_llm_client()
        print("  ✓ LLM client ready")

        # Load project registry
        print("  - Loading project registry...")
        registry = create_project_registry()
        projects = registry.list_names()
        print(f"  ✓ Found {len(projects)} projects: {', '.join(projects)}")

        # Build graph
        print("  - Building workflow graph...")
        graph = create_graph(llm_client)
        print("  ✓ Graph compiled")

        # Get tools
        tools = get_all_tools()
        print(f"  ✓ Loaded {len(tools)} tools")

        print("\n✅ System ready!\n")

        # Handle --list-projects flag
        if args.list_projects:
            print("📂 Available projects:")
            for project in projects:
                info = registry.get(project)
                print(f"  - {project} ({info['type']}): {info['description']}")
            return

        # Handle direct task execution
        if args.task:
            try:
                run_task(
                    task=args.task,
                    project=args.project,
                    registry=registry,
                    graph=graph,
                    llm_client=llm_client,
                    tools=tools,
                )
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback

                traceback.print_exc()
                sys.exit(1)
            return

        # Interactive loop
        print("Available commands:")
        print("  - Type your task to execute")
        print("  - 'projects' to list available projects")
        print("  - 'quit' or 'exit' to exit")
        print()

        current_project = (
            args.project
            if args.project and args.project in projects
            else (projects[0] if projects else None)
        )
        if current_project:
            print(f"📁 Active project: {current_project}\n")

        while True:
            try:
                user_input = input("💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Goodbye!")
                    break

                if user_input.lower() == "projects":
                    print("\n📂 Available projects:")
                    for project in projects:
                        info = registry.get(project)
                        print(f"  - {project} ({info['type']}): {info['description']}")
                    print()
                    continue

                # Check if switching project
                if user_input.lower().startswith("use "):
                    project_name = user_input[4:].strip()
                    if project_name in projects:
                        current_project = project_name
                        print(f"\n✓ Switched to project: {current_project}\n")
                    else:
                        print(f"\n❌ Project not found: {project_name}")
                        print(f"Available: {', '.join(projects)}\n")
                    continue

                if not current_project:
                    print("❌ No project selected. Use 'use <project_name>' to select a project.")
                    continue

                # Execute task using shared function
                try:
                    run_task(
                        task=user_input,
                        project=current_project,
                        registry=registry,
                        graph=graph,
                        llm_client=llm_client,
                        tools=tools,
                    )
                except Exception as e:
                    print(f"\n❌ Error: {e}\n")
                    import traceback

                    traceback.print_exc()

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Type 'quit' to exit.\n")
                continue

            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback

                traceback.print_exc()
                print()

    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("\n💡 Make sure:")
        print("  1. vscode-lm-proxy is running on port 4000")
        print("  2. PostgreSQL database is accessible")
        print("  3. Check .env file configuration")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
