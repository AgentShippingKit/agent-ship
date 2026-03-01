"""Shared fixtures for integration tests."""

import os
import pathlib
from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agent_framework.mcp.client_manager import MCPClientManager
from src.agent_framework.mcp.registry import MCPServerRegistry
from src.agent_framework.registry import clear_cache as clear_agent_cache


def get_project_root() -> pathlib.Path:
    """Find project root by locating pyproject.toml."""
    current = pathlib.Path(__file__).resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root (no pyproject.toml)")


@contextmanager
def project_root_cwd():
    """Context manager: cd to project root, restore on exit."""
    root = get_project_root()
    original = os.getcwd()
    try:
        os.chdir(str(root))
        yield root
    finally:
        os.chdir(original)


@pytest.fixture(autouse=True)
def reset_mcp_singletons():
    """Reset MCP singletons before and after each test."""
    MCPServerRegistry.reset_instance()
    MCPClientManager.reset_instance()
    yield
    MCPServerRegistry.reset_instance()
    MCPClientManager.reset_instance()


@pytest.fixture(autouse=True)
def reset_agent_instance_cache():
    """Clear agent singleton instances before each test."""
    clear_agent_cache()
    yield
    clear_agent_cache()


# ---------------------------------------------------------------------------
# Skip helpers
# ---------------------------------------------------------------------------

def require_openai_key():
    """pytest.mark.skipif decorator — skips if OPENAI_API_KEY not set."""
    return pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set",
    )


def require_postgres():
    """pytest.mark.skipif decorator — skips if AGENT_SESSION_STORE_URI not set."""
    return pytest.mark.skipif(
        not os.getenv("AGENT_SESSION_STORE_URI"),
        reason="AGENT_SESSION_STORE_URI not set (postgres not running)",
    )


def require_auth_db():
    """pytest.mark.skipif — skips if AGENTSHIP_AUTH_DB_URI not set."""
    return pytest.mark.skipif(
        not os.getenv("AGENTSHIP_AUTH_DB_URI"),
        reason="AGENTSHIP_AUTH_DB_URI not set",
    )


# ---------------------------------------------------------------------------
# LangGraph LLM mock factory
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_langgraph_llm():
    """Return a factory that patches litellm.acompletion with a streaming mock.

    Usage::

        def test_something(mock_langgraph_llm):
            with mock_langgraph_llm("Hello world"):
                result = await agent.chat(request)
    """

    def _make_mock(response_text: str = "Test response"):
        async def _fake_acompletion(*args, **kwargs):
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta = MagicMock()
            chunk.choices[0].delta.content = response_text
            chunk.choices[0].delta.tool_calls = None
            chunk.choices[0].finish_reason = "stop"
            chunk.model = "gpt-4o-mini"
            chunk.usage = None

            async def _stream():
                yield chunk

            return _stream()

        return patch(
            "src.agent_framework.engines.langgraph.engine.acompletion",
            side_effect=_fake_acompletion,
        )

    return _make_mock


# ---------------------------------------------------------------------------
# ADK runner mock factory
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_adk_runner():
    """Return a factory that creates a mock ADK Runner response.

    Usage::

        def test_something(mock_adk_runner):
            import json
            from types import SimpleNamespace
            mock_run = mock_adk_runner({"translated_text": "Hola"})
            with patch.object(agent.engine.runner, 'run', mock_run):
                result = await agent.chat(request)
    """
    import json
    from types import SimpleNamespace

    def _make_run(output_data: dict):
        text = json.dumps(output_data)
        part = SimpleNamespace(text=text)
        content = SimpleNamespace(parts=[part])
        event = SimpleNamespace(content=content)

        def _run(user_id, session_id, new_message):
            yield event

        return _run

    return _make_run
