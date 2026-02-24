"""Test PostgreSQL MCP server tools to diagnose issues."""

import asyncio
import json
import sys
import os

sys.path.insert(0, "src")


async def test_postgres_mcp():
    """Test all PostgreSQL MCP tools."""
    from src.agent_framework.mcp.registry import MCPServerRegistry
    from src.agent_framework.mcp.client_manager import MCPClientManager
    from src.agent_framework.mcp.tool_discovery import MCPToolDiscovery

    print("\n" + "=" * 70)
    print("PostgreSQL MCP Server Test")
    print("=" * 70 + "\n")

    # Load registry
    MCPServerRegistry.reset_instance()
    registry = MCPServerRegistry.get_instance()

    postgres_config = registry.get_server("postgres")
    if not postgres_config:
        print("❌ PostgreSQL server not found in registry")
        return False

    print(f"✓ Found PostgreSQL server config")
    print(f"  Transport: {postgres_config.transport}")
    print(f"  Command: {postgres_config.command}\n")

    # Get client
    manager = MCPClientManager.get_instance()
    client = manager.get_client(postgres_config)

    # Discover tools
    print("Step 1: Discovering tools...")
    discovery = MCPToolDiscovery()

    try:
        tools = await asyncio.wait_for(
            discovery.discover_tools(postgres_config),
            timeout=10.0
        )
    except asyncio.TimeoutError:
        print("❌ Tool discovery timed out")
        return False
    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    print(f"✓ Discovered {len(tools)} tools\n")

    # Print all tool schemas
    print("Step 2: Tool Schemas")
    print("-" * 70)
    for tool in tools:
        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Input Schema: {json.dumps(tool.input_schema, indent=2)}")

    print("\n" + "=" * 70)
    print("Step 3: Testing Each Tool")
    print("=" * 70 + "\n")

    # Test list_tables (should work)
    print("Test 1: list_tables")
    try:
        result = await client.call_tool("list_tables", {})
        print(f"✓ SUCCESS: {result}\n")
    except Exception as e:
        print(f"❌ FAILED: {e}\n")
        import traceback
        traceback.print_exc()

    # Test describe_table
    print("Test 2: describe_table (table: 'sessions')")
    # Try different parameter names
    for param_name in ["table", "table_name", "name"]:
        try:
            print(f"  Trying parameter: {param_name}")
            result = await client.call_tool("describe_table", {param_name: "sessions"})
            print(f"  ✓ SUCCESS with '{param_name}': {result}\n")
            break
        except Exception as e:
            print(f"  ❌ Failed with '{param_name}': {e}")

    # Test query
    print("\nTest 3: query (SELECT COUNT(*) FROM sessions)")
    # Try different parameter names
    for param_name in ["query", "sql", "statement"]:
        try:
            print(f"  Trying parameter: {param_name}")
            result = await client.call_tool("query", {param_name: "SELECT COUNT(*) FROM sessions"})
            print(f"  ✓ SUCCESS with '{param_name}': {result}\n")
            break
        except Exception as e:
            print(f"  ❌ Failed with '{param_name}': {e}")

    # Cleanup
    await manager.close_all()

    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_postgres_mcp())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
