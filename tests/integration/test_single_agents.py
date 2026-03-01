"""Integration tests: single agent chat and streaming with mocked LLM.

Both ADK and LangGraph engines are exercised using mock runners / mock LLM
so no real API keys are required.
"""

import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from src.agent_framework.registry import discover_agents, get_agent_instance
from src.service.models.base_models import AgentChatRequest
from tests.integration.conftest import project_root_cwd


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def discover_all_agents():
    """Discover agents once for this module (they accumulate in the global registry)."""
    with project_root_cwd():
        discover_agents("src/all_agents")


def _make_chat_request(agent_name: str, query: dict | None = None) -> AgentChatRequest:
    return AgentChatRequest(
        agent_name=agent_name,
        user_id="test-user",
        session_id="test-session",
        sender="USER",
        query=query or {"text": "hello"},
        features=[],
    )


def _adk_event(output_data: dict) -> SimpleNamespace:
    """Create a minimal ADK runner event."""
    text = json.dumps(output_data)
    part = SimpleNamespace(text=text)
    content = SimpleNamespace(parts=[part])
    return SimpleNamespace(content=content)


# ---------------------------------------------------------------------------
# ADK: translation_agent
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_translation_agent_adk_chat():
    """translation_agent (ADK) returns a properly shaped response with mocked runner."""
    agent = get_agent_instance("translation_agent")

    mock_event = _adk_event({"translated_text": "Hola mundo"})

    def mock_run(user_id, session_id, new_message):
        yield mock_event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_chat_request(
            "translation_agent",
            {"text": "Hello world", "from_language": "English", "to_language": "Spanish"},
        )
        result = await agent.chat(request)

    assert result is not None
    assert hasattr(result, "agent_response")


@pytest.mark.asyncio
async def test_translation_agent_adk_stream():
    """Streaming from translation_agent (ADK) produces thinking → content → done."""
    agent = get_agent_instance("translation_agent")

    mock_event = _adk_event({"translated_text": "Hola"})

    def mock_run(user_id, session_id, new_message):
        yield mock_event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_chat_request(
            "translation_agent",
            {"text": "Hi", "from_language": "English", "to_language": "Spanish"},
        )
        events = []
        async for event in agent.chat_stream(request):
            events.append(event)

    types = [e.get("type") for e in events]
    assert "done" in types, f"Expected 'done' event, got: {types}"
    # done must be last
    assert types[-1] == "done", f"Expected 'done' to be last, got: {types}"


# ---------------------------------------------------------------------------
# LangGraph: personal_assistant_agent
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_personal_assistant_langgraph_chat(mock_langgraph_llm):
    """personal_assistant_agent (LangGraph) returns a response with mocked LLM."""
    agent = get_agent_instance("personal_assistant_agent")

    with mock_langgraph_llm("I can help you with that!"):
        request = _make_chat_request(
            "personal_assistant_agent",
            {"query": "What is the weather today?"},
        )
        result = await agent.chat(request)

    assert result is not None
    assert hasattr(result, "agent_response")


@pytest.mark.asyncio
async def test_personal_assistant_langgraph_stream(mock_langgraph_llm):
    """LangGraph streaming produces at least one content event and ends with done."""
    agent = get_agent_instance("personal_assistant_agent")

    with mock_langgraph_llm("Sure, I can help!"):
        request = _make_chat_request(
            "personal_assistant_agent",
            {"query": "Tell me a joke"},
        )
        events = []
        async for event in agent.chat_stream(request):
            events.append(event)

    types = [e.get("type") for e in events]
    assert "done" in types, f"Expected 'done' event, got: {types}"
    assert types[-1] == "done", f"'done' must be last event, got: {types}"
    # At least one content or thinking event
    assert any(t in ("content", "thinking") for t in types), (
        f"Expected content or thinking event, got: {types}"
    )
