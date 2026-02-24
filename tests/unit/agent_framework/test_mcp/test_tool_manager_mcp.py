"""Unit tests for ToolManager MCP integration."""

import json
import os

import pytest

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.configs.llm.llm_provider_config import LLMModel, LLMProviderName
from src.agent_framework.mcp.models import MCPToolInfo
from src.agent_framework.mcp.registry import MCPServerRegistry
from src.agent_framework.tools.tool_manager import ToolManager


@pytest.fixture(autouse=True)
def reset_registry():
    MCPServerRegistry.reset_instance()
    yield
    MCPServerRegistry.reset_instance()


def test_create_tools_without_mcp_servers_unchanged():
    """Agents without mcp_servers get no MCP tools."""
    config = AgentConfig(
        llm_provider_name=LLMProviderName.OPENAI,
        llm_model=LLMModel.GPT_4O_MINI,
        agent_name="test",
        tools=[],
        mcp_servers=[],
    )
    tools_adk = ToolManager.create_tools(config, "adk")
    tools_lg = ToolManager.create_tools(config, "langgraph")
    assert tools_adk == []
    assert tools_lg == []


def test_create_tools_with_mcp_servers_returns_mcp_tools(tmp_path, monkeypatch):
    """When agent has mcp_servers and registry has a server, create_tools includes MCP tools.
    We patch MCPClientManager.get_client to return a fake client so no real MCP process is spawned.
    """
    mcp_file = tmp_path / ".mcp.settings.json"
    mcp_file.write_text(
        json.dumps({
            "servers": {
                "fs": {
                    "transport": "stdio",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                    "env": {"MCP_FILESYSTEM_ROOT": "/tmp"},
                },
            }
        }),
        encoding="utf-8",
    )
    os.environ["MCP_SERVERS_CONFIG"] = str(mcp_file)
    try:
        MCPServerRegistry.reset_instance()

        class FakeClient:
            async def list_tools(self):
                return [MCPToolInfo(name="read_file", description="Read file", input_schema={})]

            async def call_tool(self, name: str, arguments: dict | None = None):
                return "content"

        from src.agent_framework.mcp.client_manager import MCPClientManager

        monkeypatch.setattr(
            MCPClientManager,
            "get_client",
            lambda self, server_config: FakeClient(),
        )

        agent_config = AgentConfig(
            llm_provider_name=LLMProviderName.OPENAI,
            llm_model=LLMModel.GPT_4O_MINI,
            agent_name="test",
            tools=[],
            mcp_servers=[{"id": "fs"}],
        )

        tools_adk = ToolManager.create_tools(agent_config, "adk")
        tools_lg = ToolManager.create_tools(agent_config, "langgraph")

        assert len(tools_adk) == 1
        assert len(tools_lg) == 1
        assert tools_adk[0] is not None
        assert tools_lg[0] is not None
    finally:
        os.environ.pop("MCP_SERVERS_CONFIG", None)
