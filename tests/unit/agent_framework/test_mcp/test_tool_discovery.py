"""Unit tests for MCPToolDiscovery."""

import pytest

from src.agent_framework.mcp.models import MCPServerConfig, MCPToolInfo, MCPTransport
from src.agent_framework.mcp.tool_discovery import MCPToolDiscovery


@pytest.fixture
def mock_client():
    """Fake client that returns fixed tools without connecting."""

    class MockClient:
        def __init__(self, tools: list):
            self._tools = tools

        async def list_tools(self):
            return self._tools

        async def call_tool(self, name: str, arguments: dict | None = None):
            return {"result": "ok"}

    return MockClient(
        [
            MCPToolInfo(name="read_file", description="Read a file", input_schema={"type": "object"}),
            MCPToolInfo(name="write_file", description="Write a file", input_schema={"type": "object"}),
            MCPToolInfo(name="list_dir", description="List directory", input_schema={"type": "object"}),
        ]
    )


@pytest.mark.asyncio
async def test_discover_tools_returns_all_when_no_filter(mock_client, monkeypatch):
    """When server_config.tools is None, all tools are returned."""
    from src.agent_framework.mcp.client_manager import MCPClientManager

    monkeypatch.setattr(
        MCPClientManager,
        "get_client",
        lambda self, server_config: mock_client,
    )
    discovery = MCPToolDiscovery()
    config = MCPServerConfig(
        id="fs",
        transport=MCPTransport.STDIO,
        command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
    )
    tools = await discovery.discover_tools(config)
    assert len(tools) == 3
    names = [t.name for t in tools]
    assert "read_file" in names
    assert "write_file" in names
    assert "list_dir" in names


@pytest.mark.asyncio
async def test_discover_tools_filters_by_name(mock_client, monkeypatch):
    """When server_config.tools is set, only those tools are returned."""
    from src.agent_framework.mcp.client_manager import MCPClientManager

    monkeypatch.setattr(
        MCPClientManager,
        "get_client",
        lambda self, server_config: mock_client,
    )
    discovery = MCPToolDiscovery()
    config = MCPServerConfig(
        id="fs",
        transport=MCPTransport.STDIO,
        command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
        tools=["read_file", "list_dir"],
    )
    tools = await discovery.discover_tools(config)
    assert len(tools) == 2
    names = [t.name for t in tools]
    assert "read_file" in names
    assert "list_dir" in names
    assert "write_file" not in names
