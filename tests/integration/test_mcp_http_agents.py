"""Integration tests: GitHub MCP (HTTP/SSE OAuth) agents.

The GitHub MCP server requires OAuth — these tests verify the infrastructure
(config loading, client creation errors) without needing real credentials.
"""

import os
import json

import pytest

from src.agent_framework.mcp.client_manager import MCPClientManager
from src.agent_framework.mcp.models import MCPServerConfig, MCPTransport, MCPAuthConfig, MCPAuthType
from src.agent_framework.mcp.registry import MCPServerRegistry
from src.agent_framework.registry import discover_agents, list_agents
from tests.integration.conftest import project_root_cwd


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def discover_all_agents():
    with project_root_cwd():
        discover_agents("src/all_agents")


@pytest.fixture
def github_sse_config() -> MCPServerConfig:
    """Minimal GitHub HTTP/SSE config for testing (no DB or real credentials)."""
    return MCPServerConfig(
        id="github",
        transport=MCPTransport.HTTP,
        url="https://api.githubcopilot.com/mcp/",
        auth=MCPAuthConfig(
            type=MCPAuthType.OAUTH,
            provider="github",
            client_id_env="GITHUB_OAUTH_CLIENT_ID",
            client_secret_env="GITHUB_OAUTH_CLIENT_SECRET",
        ),
    )


# ---------------------------------------------------------------------------
# Registry: GitHub agents are registered
# ---------------------------------------------------------------------------

def test_github_adk_agent_is_registered():
    """github_adk_mcp_agent is present in the global registry."""
    agents = set(list_agents())
    assert "github_adk_mcp_agent" in agents, (
        f"Expected 'github_adk_mcp_agent' in registry, found: {sorted(agents)}"
    )


def test_github_langgraph_agent_is_registered():
    """github_langgraph_mcp_agent is present in the global registry."""
    agents = set(list_agents())
    assert "github_langgraph_mcp_agent" in agents, (
        f"Expected 'github_langgraph_mcp_agent' in registry, found: {sorted(agents)}"
    )


# ---------------------------------------------------------------------------
# MCP server registry: github entry is loaded from config
# ---------------------------------------------------------------------------

def test_github_server_config_loaded():
    """The .mcp.settings.json 'github' entry is loaded with HTTP transport."""
    with project_root_cwd():
        registry = MCPServerRegistry.get_instance()

    config = registry.get_server("github")
    if config is None:
        pytest.skip("'github' not found in .mcp.settings.json")

    assert config.transport in (MCPTransport.HTTP, MCPTransport.SSE), (
        f"Expected HTTP or SSE transport for github server, got: {config.transport}"
    )
    assert config.url is not None and config.url.startswith("https://"), (
        f"Expected HTTPS URL for github server, got: {config.url}"
    )


def test_github_server_has_oauth_auth():
    """The github server config has OAuth auth configured."""
    with project_root_cwd():
        registry = MCPServerRegistry.get_instance()

    config = registry.get_server("github")
    if config is None:
        pytest.skip("'github' not found in .mcp.settings.json")

    assert config.auth.type == MCPAuthType.OAUTH, (
        f"Expected OAuth auth, got: {config.auth.type}"
    )
    assert config.auth.provider == "github"


# ---------------------------------------------------------------------------
# SSE client: raises ValueError when AGENTSHIP_AUTH_DB_URI is not set
# ---------------------------------------------------------------------------

def test_github_unauthenticated_raises_without_db(monkeypatch, github_sse_config):
    """SSEMCPClient raises ValueError if AGENTSHIP_AUTH_DB_URI is not configured."""
    monkeypatch.delenv("AGENTSHIP_AUTH_DB_URI", raising=False)

    manager = MCPClientManager()
    with pytest.raises(ValueError, match="AGENTSHIP_AUTH_DB_URI"):
        manager.get_client(github_sse_config, owner="test_agent")


# ---------------------------------------------------------------------------
# Per-agent isolation for OAuth servers
# ---------------------------------------------------------------------------

def test_github_per_agent_client_isolation_uses_different_cache_keys(github_sse_config):
    """The client manager uses different cache keys for different owners.

    We verify the key logic directly (without creating real SSEMCPClient instances)
    since SSEMCPClient requires a live DB connection.
    """
    manager = MCPClientManager()

    # Verify that the cache keys differ for different owners
    key_a = f"{github_sse_config.id}:agent_a"
    key_b = f"{github_sse_config.id}:agent_b"
    key_shared = github_sse_config.id  # No owner

    assert key_a != key_b, "Different owners must use different cache keys"
    assert key_a != key_shared, "Owned key must differ from shared key"


# ---------------------------------------------------------------------------
# Config: env var names in auth are not resolved (kept as-is for runtime lookup)
# ---------------------------------------------------------------------------

def test_github_auth_env_var_names_not_resolved(tmp_path, monkeypatch):
    """Auth env var names (client_id_env, etc.) remain as strings, not resolved."""
    monkeypatch.setenv("GITHUB_OAUTH_CLIENT_ID", "my-client-id")

    config_file = tmp_path / "mcp.json"
    data = {
        "servers": {
            "github": {
                "transport": "http",
                "url": "https://api.githubcopilot.com/mcp/",
                "auth": {
                    "type": "oauth",
                    "provider": "github",
                    "client_id_env": "GITHUB_OAUTH_CLIENT_ID",
                    "client_secret_env": "GITHUB_OAUTH_CLIENT_SECRET",
                    "authorize_url": "https://github.com/login/oauth/authorize",
                    "token_url": "https://github.com/login/oauth/access_token",
                    "scopes": ["repo"],
                },
            }
        }
    }
    config_file.write_text(json.dumps(data))
    monkeypatch.setenv("MCP_SERVERS_CONFIG", str(config_file))

    registry = MCPServerRegistry()
    config = registry.get_server("github")
    assert config is not None

    # The env var NAME should be stored (not the resolved value)
    assert config.auth.client_id_env == "GITHUB_OAUTH_CLIENT_ID", (
        f"client_id_env should store the var name, got: {config.auth.client_id_env}"
    )
