"""Unit tests for AgentConfig MCP server references and resolution."""

import json
import os
from pathlib import Path

import pytest

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.configs.llm.llm_provider_config import LLMModel, LLMProviderName
from src.agent_framework.mcp.registry import MCPServerRegistry


@pytest.fixture(autouse=True)
def reset_mcp_registry():
    """Reset MCP registry singleton so tests don't share state."""
    MCPServerRegistry.reset_instance()
    yield
    MCPServerRegistry.reset_instance()


def test_agent_config_without_mcp_servers():
    """Agents without mcp_servers have empty mcp_servers list."""
    config = AgentConfig(
        llm_provider_name=LLMProviderName.OPENAI,
        llm_model=LLMModel.GPT_4O_MINI,
        agent_name="test",
        mcp_servers=None,
    )
    assert config.mcp_servers == []

    config2 = AgentConfig(
        llm_provider_name=LLMProviderName.OPENAI,
        llm_model=LLMModel.GPT_4O_MINI,
        agent_name="test2",
        mcp_servers=[],
    )
    assert config2.mcp_servers == []


def test_agent_config_mcp_unknown_server_raises(tmp_path):
    """Referencing an MCP server not in the registry raises ValueError."""
    mcp_file = tmp_path / ".mcp.settings.json"
    mcp_file.write_text(json.dumps({"servers": {}}), encoding="utf-8")
    os.environ["MCP_SERVERS_CONFIG"] = str(mcp_file)
    try:
        MCPServerRegistry.reset_instance()
        with pytest.raises(ValueError) as exc_info:
            AgentConfig(
                llm_provider_name=LLMProviderName.OPENAI,
                llm_model=LLMModel.GPT_4O_MINI,
                agent_name="test",
                mcp_servers=[{"id": "nonexistent_server"}],
            )
        assert "nonexistent_server" in str(exc_info.value)
        assert "not found" in str(exc_info.value).lower()
    finally:
        os.environ.pop("MCP_SERVERS_CONFIG", None)


def test_agent_config_mcp_resolves_and_merges(tmp_path):
    """MCP refs are resolved from registry; overrides (env, timeout, tools) are merged."""
    mcp_file = tmp_path / ".mcp.settings.json"
    mcp_file.write_text(
        json.dumps({
            "servers": {
                "fs": {
                    "transport": "stdio",
                    "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
                    "env": {"MCP_FILESYSTEM_ROOT": "/global/path"},
                    "timeout": 30,
                },
            }
        }),
        encoding="utf-8",
    )
    os.environ["MCP_SERVERS_CONFIG"] = str(mcp_file)
    try:
        MCPServerRegistry.reset_instance()
        config = AgentConfig(
            llm_provider_name=LLMProviderName.OPENAI,
            llm_model=LLMModel.GPT_4O_MINI,
            agent_name="test",
            mcp_servers=[
                {
                    "id": "fs",
                    "timeout": 60,
                    "env": {"MCP_FILESYSTEM_ROOT": "/agent/path", "EXTRA": "1"},
                    "tools": ["read_file", "write_file"],
                },
            ],
        )
        assert len(config.mcp_servers) == 1
        resolved = config.mcp_servers[0]
        assert resolved.id == "fs"
        assert resolved.timeout == 60
        assert resolved.env.get("MCP_FILESYSTEM_ROOT") == "/agent/path"
        assert resolved.env.get("EXTRA") == "1"
        assert resolved.tools == ["read_file", "write_file"]
    finally:
        os.environ.pop("MCP_SERVERS_CONFIG", None)


def test_agent_config_mcp_string_shorthand(tmp_path):
    """mcp_servers can be a list of server id strings (shorthand for [{ id: id }])."""
    mcp_file = tmp_path / ".mcp.settings.json"
    mcp_file.write_text(
        json.dumps({
            "servers": {
                "github": {"transport": "sse", "url": "https://mcp.github.com/sse"},
            }
        }),
        encoding="utf-8",
    )
    os.environ["MCP_SERVERS_CONFIG"] = str(mcp_file)
    try:
        MCPServerRegistry.reset_instance()
        config = AgentConfig(
            llm_provider_name=LLMProviderName.OPENAI,
            llm_model=LLMModel.GPT_4O_MINI,
            agent_name="test",
            mcp_servers=["github"],
        )
        assert len(config.mcp_servers) == 1
        assert config.mcp_servers[0].id == "github"
        assert config.mcp_servers[0].url == "https://mcp.github.com/sse"
    finally:
        os.environ.pop("MCP_SERVERS_CONFIG", None)


def test_from_yaml_loads_mcp_servers_when_present(tmp_path):
    """from_yaml loads mcp_servers from YAML and resolves them via registry."""
    mcp_file = tmp_path / "mcp_servers.yaml"
    mcp_file.write_text(
        "servers:\n  db:\n    transport: http\n    url: https://mcp.db.example.com\n",
        encoding="utf-8",
    )
    agent_yaml = tmp_path / "main_agent.yaml"
    agent_yaml.write_text(
        """
agent_name: yaml_mcp_agent
description: Test agent with MCP
llm_provider_name: openai
llm_model: gpt-4o-mini
temperature: 0.4
instruction_template: "You are helpful."
tools: []
mcp_servers:
  - id: db
    timeout: 45
""",
        encoding="utf-8",
    )
    os.environ["MCP_SERVERS_CONFIG"] = str(mcp_file)
    try:
        MCPServerRegistry.reset_instance()
        config = AgentConfig.from_yaml(str(agent_yaml))
        assert config.agent_name == "yaml_mcp_agent"
        assert len(config.mcp_servers) == 1
        assert config.mcp_servers[0].id == "db"
        assert config.mcp_servers[0].url == "https://mcp.db.example.com"
        assert config.mcp_servers[0].timeout == 45
    finally:
        os.environ.pop("MCP_SERVERS_CONFIG", None)
