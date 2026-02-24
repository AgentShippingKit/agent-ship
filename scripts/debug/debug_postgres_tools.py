"""Debug why only 1 PostgreSQL MCP tool is being discovered."""

import asyncio
import sys
import os

sys.path.insert(0, "src")


async def debug_postgres_tools():
    """Check what tools the PostgreSQL MCP server actually returns."""
    from src.agent_framework.mcp.registry import MCPServerRegistry
    from src.agent_framework.mcp.client_manager import MCPClientManager

    print("\n" + "=" * 80)
    print("PostgreSQL MCP Tool Discovery Debug")
    print("=" * 80 + "\n")

    # Load registry
    MCPServerRegistry.reset_instance()
    registry = MCPServerRegistry.get_instance()

    postgres_config = registry.get_server("postgres")
    if not postgres_config:
        print("❌ PostgreSQL server not found in registry")
        return

    print(f"✓ Found PostgreSQL server config")
    print(f"  Transport: {postgres_config.transport}")
    print(f"  Command: {postgres_config.command}\n")

    # Get client and connect
    manager = MCPClientManager.get_instance()
    client = manager.get_client(postgres_config)

    print("Connecting to PostgreSQL MCP server...")
    try:
        tools = await asyncio.wait_for(client.list_tools(), timeout=10.0)
        print(f"✓ Connected and listed tools\n")
    except Exception as e:
        print(f"❌ Failed to list tools: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"📊 Tool Discovery Results")
    print("=" * 80)
    print(f"Total tools discovered: {len(tools)}\n")

    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool.name}")
        print(f"   Description: {tool.description}")
        print(f"   Input Schema: {tool.input_schema}")
        print()

    # Cleanup
    await manager.close_all()

    print("=" * 80)
    if len(tools) == 1:
        print("⚠️  WARNING: Only 1 tool found!")
        print("   Expected: list_tables, query, describe_table, append_insight")
        print("   This suggests the MCP server is not returning all tools.")
    else:
        print(f"✓ Found {len(tools)} tools - looks good!")


if __name__ == "__main__":
    try:
        asyncio.run(debug_postgres_tools())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
