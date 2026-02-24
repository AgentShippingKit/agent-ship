"""Unit tests for MCPClientManager and STDIO client construction."""

import pytest

from src.agent_framework.mcp.client_manager import MCPClientManager
from src.agent_framework.mcp.clients.stdio import StdioMCPClient
from src.agent_framework.mcp.models import MCPServerConfig, MCPTransport


@pytest.fixture(autouse=True)
def reset_manager():
    MCPClientManager.reset_instance()
    yield
    MCPClientManager.reset_instance()


def test_manager_singleton():
    a = MCPClientManager.get_instance()
    b = MCPClientManager.get_instance()
    assert a is b


def test_get_client_stdio_returns_client():
    config = MCPServerConfig(
        id="fs",
        transport=MCPTransport.STDIO,
        command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
        env={"MCP_FILESYSTEM_ROOT": "/tmp"},
    )
    manager = MCPClientManager.get_instance()
    client = manager.get_client(config)
    assert client is not None
    assert isinstance(client, StdioMCPClient)


def test_get_client_same_id_returns_same_instance():
    config = MCPServerConfig(
        id="fs",
        transport=MCPTransport.STDIO,
        command=["echo"],
    )
    manager = MCPClientManager.get_instance()
    a = manager.get_client(config)
    b = manager.get_client(config)
    assert a is b


def test_get_client_unsupported_transport_raises():
    config = MCPServerConfig(
        id="sse_server",
        transport=MCPTransport.SSE,
        url="https://example.com/sse",
    )
    manager = MCPClientManager.get_instance()
    with pytest.raises(ValueError) as exc_info:
        manager.get_client(config)
    assert "Unsupported MCP transport" in str(exc_info.value)
    assert "stdio" in str(exc_info.value).lower()


def test_stdio_client_requires_stdio_transport():
    config = MCPServerConfig(
        id="x",
        transport=MCPTransport.HTTP,
        url="https://example.com",
    )
    with pytest.raises(ValueError) as exc_info:
        StdioMCPClient(config)
    assert "stdio" in str(exc_info.value).lower()


def test_stdio_client_requires_command():
    config = MCPServerConfig(
        id="x",
        transport=MCPTransport.STDIO,
        command=None,
    )
    with pytest.raises(ValueError) as exc_info:
        StdioMCPClient(config)
    assert "command" in str(exc_info.value).lower()


def test_stdio_client_accepts_valid_config():
    config = MCPServerConfig(
        id="fs",
        transport=MCPTransport.STDIO,
        command=["python", "-c", "print(1)"],
    )
    client = StdioMCPClient(config)
    assert client is not None
