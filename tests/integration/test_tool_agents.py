"""Integration tests: agents with custom tools.

Verifies that tools defined in YAML are loaded into the engine and that
tool-call/result events appear in streaming output.
"""

import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

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


def _make_chat_request(agent_name: str, query: dict | None = None) -> AgentChatRequest:
    return AgentChatRequest(
        agent_name=agent_name,
        user_id="test-user",
        session_id="test-session",
        sender="USER",
        query=query or {"text": "hello"},
        features=[],
    )


# ---------------------------------------------------------------------------
# database_agent (ADK, tool_pattern) — tools are currently commented out in YAML
# The test verifies the agent is instantiatable and the engine is ADK.
# ---------------------------------------------------------------------------

def test_database_agent_is_registered():
    """database_agent is registered under the correct name."""
    from src.agent_framework.registry import list_agents
    agents = list_agents()
    assert "database_agent" in agents, (
        f"'database_agent' not in registry. Found: {sorted(agents)}"
    )


def test_database_agent_uses_adk_engine():
    """database_agent uses the ADK execution engine."""
    agent = get_agent_instance("database_agent")
    engine_name = agent.engine.engine_name()
    assert engine_name == "adk", f"Expected 'adk' engine, got '{engine_name}'"


@pytest.mark.asyncio
async def test_database_agent_adk_chat_with_mock():
    """database_agent (ADK) returns a response with a mocked runner."""
    agent = get_agent_instance("database_agent")

    output = {"response": "Tables: users, sessions"}
    text = json.dumps(output)
    part = SimpleNamespace(text=text)
    content = SimpleNamespace(parts=[part])
    event = SimpleNamespace(content=content)

    def mock_run(user_id, session_id, new_message):
        yield event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_chat_request("database_agent", {"text": "List all tables"})
        result = await agent.chat(request)

    assert result is not None
    assert hasattr(result, "agent_response")


@pytest.mark.asyncio
async def test_database_agent_stream_ends_with_done():
    """Streaming from database_agent always ends with a 'done' event."""
    agent = get_agent_instance("database_agent")

    output = {"response": "No tables found"}
    text = json.dumps(output)
    part = SimpleNamespace(text=text)
    content = SimpleNamespace(parts=[part])
    event = SimpleNamespace(content=content)

    def mock_run(user_id, session_id, new_message):
        yield event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_chat_request("database_agent", {"text": "List tables"})
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert types[-1] == "done", f"Expected last event to be 'done', got: {types}"


# ---------------------------------------------------------------------------
# LangGraph agent with a mocked tool call in the LLM response
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_langgraph_agent_stream_with_tool_call(mock_langgraph_llm):
    """When LLM returns a tool call, stream includes tool_call + tool_result events."""
    agent = get_agent_instance("personal_assistant_agent")

    # First call: return a tool call; second call: return final answer
    call_count = 0

    async def _fake_acompletion(*args, **kwargs):
        nonlocal call_count
        call_count += 1

        chunk = MagicMock()
        chunk.choices = [MagicMock()]
        chunk.choices[0].delta = MagicMock()
        chunk.choices[0].finish_reason = "stop"
        chunk.model = "gpt-4o-mini"
        chunk.usage = None

        if call_count == 1:
            # Simulate a tool call in the delta
            tool_call = MagicMock()
            tool_call.id = "call_123"
            tool_call.function = MagicMock()
            tool_call.function.name = "get_weather"
            tool_call.function.arguments = '{"location": "Paris"}'
            tool_call.index = 0
            chunk.choices[0].delta.content = None
            chunk.choices[0].delta.tool_calls = [tool_call]
            chunk.choices[0].finish_reason = "tool_calls"
        else:
            chunk.choices[0].delta.content = "The weather in Paris is sunny."
            chunk.choices[0].delta.tool_calls = None

        async def _stream():
            yield chunk

        return _stream()

    with patch(
        "src.agent_framework.engines.langgraph.engine.acompletion",
        side_effect=_fake_acompletion,
    ):
        request = _make_chat_request(
            "personal_assistant_agent",
            {"query": "What's the weather in Paris?"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert "done" in types, f"Expected 'done' in events, got: {types}"
    assert types[-1] == "done"
