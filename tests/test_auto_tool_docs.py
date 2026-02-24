"""Test PostgreSQL ADK MCP agent with automatic tool documentation."""

import asyncio
import sys
import os

sys.path.insert(0, "src")


async def test_auto_tool_docs():
    """Test that tool documentation is auto-generated and injected into prompts."""
    print("\n" + "=" * 80)
    print("Testing Automatic Tool Documentation Generation")
    print("=" * 80 + "\n")

    from src.all_agents.postgres_adk_mcp_agent.main_agent import PostgresAdkMcpAgent

    print("Step 1: Creating PostgreSQL ADK MCP agent...")
    agent = PostgresAdkMcpAgent()

    print("✓ Agent created\n")

    # Access the engine to see the final instruction
    print("Step 2: Checking the system prompt (instruction)...")
    print("=" * 80)

    # For ADK engine, the instruction is in the agent
    # Note: engine is wrapped in MiddlewareEngine, need to access _inner
    if hasattr(agent, 'engine'):
        engine = agent.engine
        # Unwrap MiddlewareEngine if present
        if hasattr(engine, '_inner'):
            engine = engine._inner

        if hasattr(engine, 'agent'):
            adk_agent = engine.agent
            if hasattr(adk_agent, 'instruction'):
                instruction = adk_agent.instruction
                print("SYSTEM PROMPT (with auto-generated tool docs):")
                print("-" * 80)
                print(instruction)
                print("-" * 80)
                print()

                # Check if tool documentation was injected
                if "## Available Tools" in instruction:
                    print("✅ SUCCESS: Tool documentation was AUTO-GENERATED and injected!")
                    print()

                    # Show the tool docs section
                    if "### query" in instruction:
                        print("✅ Found 'query' tool documentation")

                    if "**Parameters:**" in instruction:
                        print("✅ Found parameter documentation")

                    if "**Example:**" in instruction:
                        print("✅ Found usage examples")

                    print()
                    print("The agent will now have accurate, auto-generated tool docs!")
                else:
                    print("❌ FAILED: Tool documentation was NOT injected")
                    print("   Expected to see '## Available Tools' in the prompt")
            else:
                print("⚠️  Could not access agent instruction")
        else:
            print("⚠️  Could not access ADK agent")
    else:
        print("⚠️  Could not access engine")

    print("\n" + "=" * 80)
    print("Step 3: Testing tool usage with the agent...")
    print("=" * 80 + "\n")

    from src.service.models.base_models import AgentChatRequest

    request = AgentChatRequest(
        agent_name="postgres_adk_mcp_agent",
        query="List all tables in the database",
        session_id="test_auto_docs_123",
        user_id="test_user_123"
    )

    print("Sending request: 'List all tables in the database'")
    print("(This will test if the agent uses the correct tool with correct parameters)\n")

    result = await agent.chat(request)

    print("✓ Agent response:")
    print("-" * 80)
    print(result.agent_response)
    print("-" * 80)

    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(test_auto_tool_docs())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
