#!/usr/bin/env python3
"""Verify LangGraphX setup and configuration."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> None:
    """Run verification checks."""
    print("🔍 LangGraphX Setup Verification")
    print("=" * 60)
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Project Registry
    checks_total += 1
    try:
        from src.config.projects import create_project_registry
        registry = create_project_registry()
        projects = registry.list_names()
        print(f"\n✅ Check 1/5: Project Registry")
        print(f"   Found {len(projects)} projects: {', '.join(projects)}")
        
        # Validate each project path
        for name in projects:
            proj = registry.get(name)
            # proj is a ProjectInfo object with .path attribute
            proj_path = getattr(proj, 'path', proj.get('path') if isinstance(proj, dict) else None)
            if proj_path:
                path_exists = Path(proj_path).exists()
                status = "✓" if path_exists else "✗"
                print(f"   {status} {name}: {proj_path}")
                if not path_exists:
                    print(f"      WARNING: Path does not exist!")
        
        checks_passed += 1
    except Exception as e:
        print(f"\n❌ Check 1/5: Project Registry")
        print(f"   Error: {e}")
    
    # Check 2: LLM Client
    checks_total += 1
    try:
        from src.llm.proxy_client import create_llm_client
        llm = create_llm_client()
        print(f"\n✅ Check 2/5: LLM Client")
        model_name = getattr(llm, 'model_name', 'vscode-lm-proxy')
        print(f"   Connected to: {model_name}")
        checks_passed += 1
    except Exception as e:
        print(f"\n❌ Check 2/5: LLM Client")
        print(f"   Error: {e}")
        print(f"   Hint: Ensure vscode-lm-proxy is running on port 4000")
    
    # Check 3: Tools
    checks_total += 1
    try:
        from src.graph.builder import get_all_tools
        tools = get_all_tools()
        print(f"\n✅ Check 3/5: Tools")
        print(f"   Loaded {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}")
        checks_passed += 1
    except Exception as e:
        print(f"\n❌ Check 3/5: Tools")
        print(f"   Error: {e}")
    
    # Check 4: Agents
    checks_total += 1
    try:
        from src.agents import supervisor, developer, architect, reviewer, tester
        agents = ['supervisor', 'developer', 'architect', 'reviewer', 'tester']
        print(f"\n✅ Check 4/5: Agents")
        print(f"   Available agents: {', '.join(agents)}")
        checks_passed += 1
    except Exception as e:
        print(f"\n❌ Check 4/5: Agents")
        print(f"   Error: {e}")
    
    # Check 5: Graph
    checks_total += 1
    try:
        from src.graph.builder import create_graph
        llm = create_llm_client()
        graph = create_graph(llm)
        print(f"\n✅ Check 5/5: Graph")
        print(f"   Graph compiled successfully")
        checks_passed += 1
    except Exception as e:
        print(f"\n❌ Check 5/5: Graph")
        print(f"   Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Results: {checks_passed}/{checks_total} checks passed")
    
    if checks_passed == checks_total:
        print("🎉 All checks passed! System is ready.")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
