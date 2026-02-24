"""Verify tool documentation injection."""

import sys
sys.path.insert(0, "src")

from src.all_agents.postgres_mcp_agent.main_agent import PostgresMcpAgent

# Create agent
print("\nCreating PostgreSQL MCP agent...")
agent = PostgresMcpAgent()

# Access the engine and agent directly
print("\n" + "=" * 80)
print("SYSTEM PROMPT VERIFICATION")
print("=" * 80 + "\n")

# Try different paths to access the instruction
print(f"Agent type: {type(agent)}")
print(f"Has engine: {hasattr(agent, 'engine')}")

if hasattr(agent, 'engine'):
    engine = agent.engine
    print(f"Engine type: {type(engine)}")

    # Check if it's a MiddlewareEngine (wraps the real engine)
    if hasattr(engine, '_inner'):
        print("Found MiddlewareEngine, accessing inner engine...")
        engine = engine._inner
        print(f"Inner engine type: {type(engine)}")

    # Try accessing the agent
    if hasattr(engine, 'agent'):
        adk_agent = engine.agent
        print(f"\nADK Agent type: {type(adk_agent)}")
        print(f"Has instruction: {hasattr(adk_agent, 'instruction')}")

        if hasattr(adk_agent, 'instruction'):
            instruction = adk_agent.instruction
            print(f"\nInstruction length: {len(instruction)} characters")
            print("\n" + "-" * 80)
            print("FULL SYSTEM PROMPT:")
            print("-" * 80)
            print(instruction)
            print("-" * 80)

            # Verify tool documentation
            print("\n" + "=" * 80)
            print("VERIFICATION RESULTS")
            print("=" * 80)

            if "## Available Tools" in instruction:
                print("✅ Tool documentation section found")
            else:
                print("❌ Tool documentation section NOT found")

            if "### query" in instruction:
                print("✅ 'query' tool documented")
            else:
                print("❌ 'query' tool NOT documented")

            if "**Parameters:**" in instruction:
                print("✅ Parameter documentation found")
            else:
                print("❌ Parameter documentation NOT found")

            if "**Example:**" in instruction:
                print("✅ Usage examples found")
            else:
                print("❌ Usage examples NOT found")

            # Count the separator
            if "=" * 80 in instruction:
                print("✅ Separator found (tool docs were injected)")
            else:
                print("❌ Separator NOT found")
        else:
            print("\n❌ No instruction attribute on ADK agent")
    else:
        print("\n❌ No agent attribute on engine")
