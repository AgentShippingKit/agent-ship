"""Integration tests: MCP client manager and server registry infrastructure.

Verifies per-agent client isolation, singleton caching, and env-var resolution
in server command arguments — without requiring a running MCP server.
"""

import os
import tempfile
import json

import pytest

from src.agent_framework.mcp.client_manager import MCPClientManager
from src.agent_framework.mcp.models import MCPServerConfig, MCPTransport
from src.agent_framework.mcp.registry import MCPServerRegistry


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def stdio_config() -> MCPServerConfig:
    """Minimal STDIO server config for testing (no process is spawned)."""
    return MCPServerConfig(
        id="test-server",
        transport=MCPTransport.STDIO,
        command=["echo", "hello"],
    )


@pytest.fixture
def manager() -> MCPClientManager:
    """Fresh MCPClientManager instance (not the singleton)."""
    return MCPClientManager()


# ---------------------------------------------------------------------------
# Per-agent isolation
# ---------------------------------------------------------------------------

def test_per_agent_client_isolation(stdio_config, manager):
    """Different owner → different client instances for the same server."""
    client_a = manager.get_client(stdio_config, owner="agent_a")
    client_b = manager.get_client(stdio_config, owner="agent_b")
    assert client_a is not client_b, (
        "Expected separate client instances for different owners"
    )


def test_same_owner_same_instance(stdio_config, manager):
    """Same owner → the same cached client instance is returned."""
    client_first = manager.get_client(stdio_config, owner="agent_x")
    client_second = manager.get_client(stdio_config, owner="agent_x")
    assert client_first is client_second, (
        "Expected the same cached client for the same owner"
    )


def test_no_owner_shared_instance(stdio_config, manager):
    """No owner → single shared instance (backward compat)."""
    c1 = manager.get_client(stdio_config, owner="")
    c2 = manager.get_client(stdio_config, owner="")
    assert c1 is c2


def test_singleton_reset_clears_cache():
    """MCPClientManager.reset_instance() drops singleton so next call creates fresh one."""
    inst1 = MCPClientManager.get_instance()
    MCPClientManager.reset_instance()
    inst2 = MCPClientManager.get_instance()
    assert inst1 is not inst2


# ---------------------------------------------------------------------------
# Env-var resolution in server registry
# ---------------------------------------------------------------------------

def _write_config(path: str, servers: dict) -> None:
    with open(path, "w") as f:
        json.dump({"servers": servers}, f)


def test_env_var_resolution_in_args(tmp_path, monkeypatch):
    """${AGENT_SESSION_STORE_URI} in command args is resolved to its value."""
    monkeypatch.setenv("AGENT_SESSION_STORE_URI", "postgresql://user:pass@localhost:5432/db")

    config_file = tmp_path / "mcp.json"
    _write_config(str(config_file), {
        "postgres": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-postgres", "${AGENT_SESSION_STORE_URI}"],
        }
    })

    monkeypatch.setenv("MCP_SERVERS_CONFIG", str(config_file))
    registry = MCPServerRegistry()  # fresh instance (not singleton)

    config = registry.get_server("postgres")
    assert config is not None, "Server 'postgres' not found in registry"

    # The last arg should be the resolved connection string, not the literal token
    resolved_args = config.command or []
    last_arg = resolved_args[-1] if resolved_args else ""
    assert last_arg == "postgresql://user:pass@localhost:5432/db", (
        f"Expected resolved URI, got: {last_arg!r}"
    )
    assert "${AGENT_SESSION_STORE_URI}" not in last_arg


def test_env_var_unresolved_stays_literal(tmp_path, monkeypatch):
    """Unknown ${VAR} placeholders remain unchanged (no error raised)."""
    monkeypatch.delenv("NONEXISTENT_VAR_XYZ_AGENTSHIP", raising=False)

    config_file = tmp_path / "mcp.json"
    _write_config(str(config_file), {
        "myserver": {
            "command": "npx",
            "args": ["-y", "some-mcp-server", "${NONEXISTENT_VAR_XYZ_AGENTSHIP}"],
        }
    })

    monkeypatch.setenv("MCP_SERVERS_CONFIG", str(config_file))
    registry = MCPServerRegistry()

    config = registry.get_server("myserver")
    assert config is not None

    resolved_args = config.command or []
    last_arg = resolved_args[-1] if resolved_args else ""
    assert last_arg == "${NONEXISTENT_VAR_XYZ_AGENTSHIP}", (
        f"Expected literal placeholder, got: {last_arg!r}"
    )


def test_registry_loads_servers_key(tmp_path, monkeypatch):
    """Registry handles both 'servers' and 'mcpServers' as root key."""
    for root_key in ("servers", "mcpServers"):
        config_file = tmp_path / f"mcp_{root_key}.json"
        data = {root_key: {"my-tool": {"command": "node", "args": ["server.js"]}}}
        config_file.write_text(json.dumps(data))

        monkeypatch.setenv("MCP_SERVERS_CONFIG", str(config_file))
        registry = MCPServerRegistry()
        assert registry.get_server("my-tool") is not None, (
            f"Failed to load server under root key '{root_key}'"
        )


def test_registry_list_server_ids(tmp_path, monkeypatch):
    """list_server_ids() returns all configured server IDs."""
    config_file = tmp_path / "mcp.json"
    _write_config(str(config_file), {
        "server-a": {"command": "node", "args": ["a.js"]},
        "server-b": {"command": "node", "args": ["b.js"]},
    })

    monkeypatch.setenv("MCP_SERVERS_CONFIG", str(config_file))
    registry = MCPServerRegistry()

    ids = set(registry.list_server_ids())
    assert ids == {"server-a", "server-b"}
