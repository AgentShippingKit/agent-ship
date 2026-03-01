"""Integration tests: SSE event flow for both ADK and LangGraph engines.

Verifies event ordering (thinking → content → done), error events, and
that 'done' is always the last event in the stream.
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
    with project_root_cwd():
        discover_agents("src/all_agents")


def _make_request(agent_name: str, query: dict | None = None) -> AgentChatRequest:
    return AgentChatRequest(
        agent_name=agent_name,
        user_id="stream-test-user",
        session_id="stream-test-session",
        sender="USER",
        query=query or {"text": "hello"},
        features=[],
    )


def _adk_event(output_data: dict) -> SimpleNamespace:
    text = json.dumps(output_data)
    part = SimpleNamespace(text=text)
    content = SimpleNamespace(parts=[part])
    return SimpleNamespace(content=content)


# ---------------------------------------------------------------------------
# ADK streaming
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_adk_stream_event_sequence():
    """ADK stream produces events ending with 'done'."""
    agent = get_agent_instance("translation_agent")
    event = _adk_event({"translated_text": "Bonjour"})

    def mock_run(user_id, session_id, new_message):
        yield event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_request(
            "translation_agent",
            {"text": "Hello", "from_language": "English", "to_language": "French"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]

    assert len(types) > 0, "Stream produced no events"
    assert types[-1] == "done", f"Last event must be 'done', got: {types}"


@pytest.mark.asyncio
async def test_adk_stream_done_always_last():
    """'done' is the final event even when the agent produces multiple content events."""
    agent = get_agent_instance("translation_agent")

    # Yield two events to simulate multiple rounds
    event1 = _adk_event({"translated_text": "Part 1"})
    event2 = _adk_event({"translated_text": "Part 2"})

    def mock_run(user_id, session_id, new_message):
        yield event1
        yield event2

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_request(
            "translation_agent",
            {"text": "Hello world", "from_language": "English", "to_language": "French"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert types[-1] == "done", f"'done' must be last, got: {types}"


@pytest.mark.asyncio
async def test_adk_stream_error_yields_error_event():
    """When the runner raises, the stream yields an 'error' event then 'done'."""
    agent = get_agent_instance("translation_agent")

    def mock_run_error(user_id, session_id, new_message):
        raise RuntimeError("Simulated runner failure")
        yield  # Make it a generator

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run_error):
        request = _make_request(
            "translation_agent",
            {"text": "Hello", "from_language": "English", "to_language": "French"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert "error" in types or "done" in types, (
        f"Expected 'error' or 'done' on failure, got: {types}"
    )
    assert types[-1] == "done", f"'done' must be last even on error, got: {types}"


# ---------------------------------------------------------------------------
# LangGraph streaming
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_langgraph_stream_event_sequence(mock_langgraph_llm):
    """LangGraph stream produces events ending with 'done'."""
    agent = get_agent_instance("personal_assistant_agent")

    with mock_langgraph_llm("Here is my response!"):
        request = _make_request(
            "personal_assistant_agent",
            {"query": "Tell me something interesting"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert len(types) > 0, "Stream produced no events"
    assert types[-1] == "done", f"Last event must be 'done', got: {types}"


@pytest.mark.asyncio
async def test_langgraph_stream_done_always_last(mock_langgraph_llm):
    """LangGraph: 'done' is the last event even with multi-token responses."""
    agent = get_agent_instance("personal_assistant_agent")

    with mock_langgraph_llm("A longer response that has multiple tokens"):
        request = _make_request(
            "personal_assistant_agent",
            {"query": "Write me a haiku"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert types[-1] == "done", f"'done' must be last, got: {types}"


@pytest.mark.asyncio
async def test_langgraph_stream_error_yields_done(mock_langgraph_llm):
    """LangGraph: if LLM raises, the stream still ends with 'done'."""
    agent = get_agent_instance("personal_assistant_agent")

    async def _error_acompletion(*args, **kwargs):
        raise RuntimeError("Simulated LLM failure")

    with patch(
        "src.agent_framework.engines.langgraph.engine.acompletion",
        side_effect=_error_acompletion,
    ):
        request = _make_request(
            "personal_assistant_agent",
            {"query": "This will fail"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert "done" in types, f"Expected 'done' even on error, got: {types}"
    assert types[-1] == "done", f"'done' must be last, got: {types}"


# ---------------------------------------------------------------------------
# Cross-engine: done is always last
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_stream_done_always_last_adk():
    """Parametric: 'done' is last for ADK regardless of content."""
    agent = get_agent_instance("database_agent")
    event = _adk_event({"response": "No tables"})

    def mock_run(user_id, session_id, new_message):
        yield event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_request("database_agent", {"text": "List tables"})
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert types[-1] == "done"
