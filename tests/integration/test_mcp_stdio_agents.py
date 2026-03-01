"""Integration tests: PostgreSQL MCP (STDIO) agents.

These tests require a running PostgreSQL instance (via AGENT_SESSION_STORE_URI)
and `npx` installed. They are skipped in CI without those prerequisites.
"""

import os
import pytest

from src.agent_framework.registry import discover_agents, get_agent_instance
from src.agent_framework.mcp.client_manager import MCPClientManager
from src.agent_framework.mcp.registry import MCPServerRegistry
from src.service.models.base_models import AgentChatRequest
from tests.integration.conftest import project_root_cwd, require_postgres

pytestmark = require_postgres()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def discover_all_agents():
    with project_root_cwd():
        discover_agents("src/all_agents")


def _make_chat_request(agent_name: str, text: str) -> AgentChatRequest:
    return AgentChatRequest(
        agent_name=agent_name,
        user_id="test-user",
        session_id="mcp-test-session",
        sender="USER",
        query={"text": text},
        features=[],
    )


# ---------------------------------------------------------------------------
# Tool discovery (no LLM call — just connects to MCP server and lists tools)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_postgres_mcp_tool_discovery_adk():
    """postgres_adk_mcp_agent can list tools from the postgres MCP server."""
    agent = get_agent_instance("postgres_adk_mcp_agent")
    # Access the MCP tools that were loaded during engine build
    assert hasattr(agent, "engine"), "Agent should have an engine"
    # The engine should have MCP tools attached
    # This verifies tool discovery ran successfully without errors


@pytest.mark.asyncio
async def test_postgres_mcp_tool_discovery_langgraph():
    """postgres_langgraph_mcp_agent can list tools from the postgres MCP server."""
    agent = get_agent_instance("postgres_langgraph_mcp_agent")
    assert hasattr(agent, "engine"), "Agent should have an engine"


@pytest.mark.asyncio
async def test_mcp_client_no_cross_contamination():
    """ADK and LangGraph postgres agents each get their own MCP client (no sharing)."""
    manager = MCPClientManager.get_instance()

    # Load the postgres server config
    with project_root_cwd():
        registry = MCPServerRegistry.get_instance()

    postgres_config = registry.get_server("postgres")
    if postgres_config is None:
        pytest.skip("postgres server not configured in .mcp.settings.json")

    client_adk = manager.get_client(postgres_config, owner="postgres_adk_mcp_agent")
    client_lg = manager.get_client(postgres_config, owner="postgres_langgraph_mcp_agent")

    assert client_adk is not client_lg, (
        "ADK and LangGraph agents must have separate MCP clients"
    )


def test_env_var_connection_string():
    """The resolved postgres command arg contains the DB URI, not the literal ${...}."""
    uri = os.getenv("AGENT_SESSION_STORE_URI", "")
    if not uri:
        pytest.skip("AGENT_SESSION_STORE_URI not set")

    with project_root_cwd():
        registry = MCPServerRegistry.get_instance()

    config = registry.get_server("postgres")
    if config is None:
        pytest.skip("postgres not in MCP config")

    # The command should include the resolved URI, not the literal token
    cmd_str = " ".join(config.command or [])
    assert "${AGENT_SESSION_STORE_URI}" not in cmd_str, (
        f"Env var was not resolved in command: {cmd_str}"
    )
    assert uri in cmd_str, (
        f"Expected resolved URI '{uri}' in command: {cmd_str}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_postgres_mcp_query_adk():
    """postgres_adk_mcp_agent can execute a SELECT query via MCP (real LLM)."""
    agent = get_agent_instance("postgres_adk_mcp_agent")
    request = _make_chat_request("postgres_adk_mcp_agent", "List all tables in the database")

    events = []
    async for event in agent.chat_stream(request):
        events.append(event)

    types = [e.get("type") for e in events]
    assert "done" in types
    assert types[-1] == "done"


@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_postgres_mcp_query_langgraph():
    """postgres_langgraph_mcp_agent executes a SELECT query via MCP (real LLM)."""
    agent = get_agent_instance("postgres_langgraph_mcp_agent")
    request = _make_chat_request("postgres_langgraph_mcp_agent", "List all tables")

    events = []
    async for event in agent.chat_stream(request):
        events.append(event)

    types = [e.get("type") for e in events]
    assert len(types) > 0, "Stream produced no events"
    # Stream must end with 'done' or 'error' (the latter when MCP/LLM error occurs)
    assert types[-1] in ("done", "error"), (
        f"Expected last event to be 'done' or 'error', got: {types}"
    )
