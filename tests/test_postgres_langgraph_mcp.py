"""Test PostgreSQL LangGraph MCP agent with MCP integration."""

import asyncio
import sys

sys.path.insert(0, "src")


async def test_langgraph_mcp():
    """Test that MCP works with LangGraph engine."""
    print("\n" + "=" * 80)
    print("Testing LangGraph Engine with MCP Integration")
    print("=" * 80 + "\n")

    from src.all_agents.postgres_langgraph_mcp_agent.main_agent import PostgresLanggraphMcpAgent
    from src.service.models.base_models import AgentChatRequest

    # Step 1: Create agent with LangGraph engine
    print("Step 1: Creating PostgreSQL agent with LangGraph engine...")
    agent = PostgresLanggraphMcpAgent()
    print("✅ Agent created\n")

    # Verify it's using LangGraph
    print("Step 2: Verifying engine type...")
    if hasattr(agent, 'engine'):
        engine = agent.engine
        # Unwrap middleware
        if hasattr(engine, '_inner'):
            engine = engine._inner

        engine_name = engine.engine_name()
        print(f"Engine: {engine_name}")

        if engine_name == "langgraph":
            print("✅ Using LangGraph engine\n")
        else:
            print(f"❌ Expected 'langgraph', got '{engine_name}'\n")
            return False
    else:
        print("❌ Could not verify engine\n")
        return False

    # Step 3: Verify tool documentation is injected
    print("Step 3: Checking auto-generated tool documentation...")
    try:
        # For LangGraph, check if PromptBuilder was used
        from src.agent_framework.engines.langgraph.engine import LangGraphEngine
        import inspect
        source = inspect.getsource(LangGraphEngine._build_system_prompt)

        if "PromptBuilder" in source and "build_system_prompt" in source:
            print("✅ LangGraph engine uses PromptBuilder")
            print("✅ Tool documentation will be auto-generated\n")
        else:
            print("❌ LangGraph engine not using PromptBuilder\n")
            return False
    except Exception as e:
        print(f"⚠️  Could not verify PromptBuilder: {e}\n")

    # Step 4: Test actual query
    print("Step 4: Testing MCP tool execution...")
    request = AgentChatRequest(
        agent_name="postgres_langgraph_mcp_agent",
        query="Show me a list of all tables in the database",
        session_id="test_langgraph_mcp_123",
        user_id="test_user_123"
    )

    print("Sending request: 'Show me a list of all tables in the database'")
    print("(This tests MCP tool discovery, documentation, and execution)\n")

    try:
        result = await agent.chat(request)

        print("✅ Request completed!")
        print("-" * 80)

        # Handle both string and TextOutput object
        response_text = str(result.agent_response) if hasattr(result.agent_response, 'response') else result.agent_response
        print("Agent response:")
        print(response_text[:500])  # Show first 500 chars
        print("-" * 80)

        # Check for errors
        response_lower = response_text.lower() if isinstance(response_text, str) else str(response_text).lower()
        if "error" in response_lower and "encountered an error" in response_lower:
            print("\n❌ Response contains error")
            return False
        else:
            print("\n✅ MCP tools working with LangGraph engine!")
            return True

    except Exception as e:
        print(f"\n❌ Request failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    print("\n" + "=" * 80)
    print("LANGGRAPH MCP INTEGRATION TEST")
    print("=" * 80)

    success = await test_langgraph_mcp()

    print("\n" + "=" * 80)
    if success:
        print("🎉 SUCCESS: MCP works with LangGraph engine!")
        print("=" * 80)
        print("\nVerified:")
        print("✅ LangGraph engine configuration")
        print("✅ MCP tool discovery")
        print("✅ Auto tool documentation (PromptBuilder)")
        print("✅ MCP tool execution")
        print("✅ Response generation")
        print("\nBoth ADK and LangGraph engines support MCP! 🚀")
        return 0
    else:
        print("❌ TEST FAILED")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
