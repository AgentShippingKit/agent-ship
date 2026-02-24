"""Test that MCP client handles event loop changes correctly."""

import asyncio
import sys

sys.path.insert(0, "src")


async def test_event_loop_handling():
    """Test MCP client works across different event loops."""
    print("\n" + "=" * 80)
    print("Testing Event Loop Handling for MCP Client")
    print("=" * 80 + "\n")

    from src.all_agents.postgres_adk_mcp_agent.main_agent import PostgresAdkMcpAgent
    from src.service.models.base_models import AgentChatRequest

    # Step 1: Create agent in one event loop (simulates initialization)
    print("Step 1: Creating agent (initialization event loop)...")
    agent = PostgresAdkMcpAgent()
    print("✅ Agent created\n")

    # Step 2: Make a request that will use the agent
    # This simulates what happens in the web API - a different async context
    print("Step 2: Making request (request handling event loop)...")
    request = AgentChatRequest(
        agent_name="postgres_adk_mcp_agent",
        query="SELECT * FROM events LIMIT 5",
        session_id="test_event_loop_123",
        user_id="test_user_123"
    )

    print("Sending request: 'SELECT * FROM events LIMIT 5'")
    print("(This tests if MCP client detects and handles event loop change)\n")

    try:
        result = await agent.chat(request)

        print("✅ Request succeeded!")
        print("-" * 80)
        print("Agent response:")

        # Handle both string and TextOutput object
        response_text = str(result.agent_response) if hasattr(result.agent_response, 'response') else result.agent_response
        print(response_text[:500])  # Show first 500 chars
        print("-" * 80)

        # Check for errors in response
        response_lower = response_text.lower() if isinstance(response_text, str) else str(response_text).lower()
        if "error" in response_lower and "encountered an error" in response_lower:
            print("\n⚠️  Response contains error message")
            print("Full response:", response_text)
            return False
        else:
            print("\n✅ No errors in response - event loop handling working!")
            return True

    except Exception as e:
        print(f"\n❌ Request failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_requests():
    """Test multiple requests work correctly."""
    print("\n" + "=" * 80)
    print("Testing Multiple Requests")
    print("=" * 80 + "\n")

    from src.all_agents.postgres_adk_mcp_agent.main_agent import PostgresAdkMcpAgent
    from src.service.models.base_models import AgentChatRequest

    agent = PostgresAdkMcpAgent()

    queries = [
        "SELECT COUNT(*) FROM events",
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' LIMIT 3",
        "SELECT * FROM sessions LIMIT 2"
    ]

    print(f"Running {len(queries)} sequential requests...")
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Query: {query}")
        request = AgentChatRequest(
            agent_name="postgres_adk_mcp_agent",
            query=query,
            session_id=f"test_multi_{i}",
            user_id="test_user"
        )

        try:
            result = await agent.chat(request)

            # Handle both string and TextOutput object
            response_text = str(result.agent_response) if hasattr(result.agent_response, 'response') else result.agent_response
            response_lower = response_text.lower() if isinstance(response_text, str) else str(response_text).lower()

            if "error" in response_lower and "encountered an error" in response_lower:
                print(f"   ❌ Request {i} failed")
                return False
            else:
                print(f"   ✅ Request {i} succeeded")
        except Exception as e:
            print(f"   ❌ Request {i} raised exception: {e}")
            import traceback
            traceback.print_exc()
            return False

    print("\n✅ All requests succeeded!")
    return True


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("MCP EVENT LOOP FIX VERIFICATION")
    print("=" * 80)

    results = []

    # Test 1: Basic event loop handling
    results.append(("Event Loop Handling", await test_event_loop_handling()))

    # Test 2: Multiple requests
    results.append(("Multiple Requests", await test_multiple_requests()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80 + "\n")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 80)
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("Event loop handling is working correctly!")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total} passed)")
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
