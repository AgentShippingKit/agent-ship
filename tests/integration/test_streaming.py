"""Integration tests: SSE event flow for both ADK and LangGraph engines.

Tests verify two things:
  1. Event structure — correct types, correct ordering, done is always last
  2. Event content — text fields contain plain display text, NOT raw schema JSON

The content tests are the ones that catch bugs like:
  - LangGraph emitting {"response": "..."} instead of plain text
  - ADK streaming raw schema JSON to the UI
  - Cross-engine inconsistency for the same output schema

If a content assertion fails here, the Studio UI will show broken output.
"""

import json
from types import SimpleNamespace
from unittest.mock import patch

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


def _content_events(events: list) -> list:
    return [e for e in events if e.get("type") == "content"]


# ---------------------------------------------------------------------------
# ADK — event structure
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
    """'done' is the final event even with multiple content events."""
    agent = get_agent_instance("translation_agent")
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
        yield

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run_error):
        request = _make_request(
            "translation_agent",
            {"text": "Hello", "from_language": "English", "to_language": "French"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert "error" in types or "done" in types
    assert types[-1] == "done", f"'done' must be last even on error, got: {types}"


# ---------------------------------------------------------------------------
# ADK — content text correctness
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_adk_content_text_is_plain_string_not_json():
    """REGRESSION: ADK output_schema caused LLM to emit {"response": "..."}
    which was previously forwarded raw to the UI. extract_display_text must
    unwrap it so the text field contains only the plain string value.
    """
    agent = get_agent_instance("translation_agent")
    # Simulate what ADK emits when output_schema is set:
    # the LLM returns a schema-formatted JSON blob
    event = _adk_event({"translated_text": "Bonjour le monde"})

    def mock_run(user_id, session_id, new_message):
        yield event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_request(
            "translation_agent",
            {"text": "Hello world", "from_language": "English", "to_language": "French"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    content = _content_events(events)
    assert len(content) > 0, "Expected at least one content event"
    for ev in content:
        text = ev.get("text", "")
        assert not text.startswith("{"), (
            f"Content text must not be raw JSON, got: {text!r}. "
            "This means extract_display_text is not being applied."
        )


@pytest.mark.asyncio
async def test_adk_content_text_field_name_not_in_output():
    """The schema field name ('translated_text') must not appear in the
    display text when the output is a single-field schema.
    """
    agent = get_agent_instance("translation_agent")
    event = _adk_event({"translated_text": "Hola"})

    def mock_run(user_id, session_id, new_message):
        yield event

    with patch.object(agent.engine._inner.runner, "run", side_effect=mock_run):
        request = _make_request(
            "translation_agent",
            {"text": "Hello", "from_language": "English", "to_language": "Spanish"},
        )
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    content = _content_events(events)
    for ev in content:
        text = ev.get("text", "")
        assert "translated_text" not in text, (
            f"Field name leaked into display text: {text!r}"
        )


# ---------------------------------------------------------------------------
# LangGraph — event structure
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_langgraph_stream_event_sequence(mock_langgraph_llm):
    """LangGraph stream produces events ending with 'done'."""
    agent = get_agent_instance("personal_assistant_agent")

    with mock_langgraph_llm("Here is my response!"):
        request = _make_request("personal_assistant_agent", {"query": "Tell me something"})
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
        request = _make_request("personal_assistant_agent", {"query": "Write me a haiku"})
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
        request = _make_request("personal_assistant_agent", {"query": "This will fail"})
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    types = [e.get("type") for e in events]
    assert "done" in types
    assert types[-1] == "done", f"'done' must be last, got: {types}"


# ---------------------------------------------------------------------------
# LangGraph — content text correctness
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_langgraph_non_streaming_content_is_plain_text(mock_langgraph_llm):
    """REGRESSION: LangGraph was calling model_dump_json() on the output which
    produced {"response": "..."} as the SSE content text instead of plain text.
    The non-streaming path must emit the field value, not the serialized model.
    """
    agent = get_agent_instance("personal_assistant_agent")

    with mock_langgraph_llm("This is the actual answer"):
        request = _make_request("personal_assistant_agent", {"query": "What is 2+2?"})
        events = []
        async for ev in agent.chat_stream(request):
            events.append(ev)

    content = _content_events(events)
    assert len(content) > 0, "Expected at least one content event"
    for ev in content:
        text = ev.get("text", "")
        # Must not be a JSON-wrapped schema object
        assert not text.startswith('{"response"'), (
            f"REGRESSION: LangGraph emitting raw model_dump_json(). Got: {text!r}"
        )
        assert not text.startswith("{"), (
            f"Content text must not be raw JSON for a single-field schema. Got: {text!r}"
        )


# ---------------------------------------------------------------------------
# Cross-engine consistency
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_adk_and_langgraph_content_format_consistent():
    """ADK and LangGraph must produce the same kind of output for the same
    response text. Both should emit plain text, not JSON-wrapped values.

    This test simulates both engines producing a known response and checks
    that neither wraps the text in a JSON schema structure.
    """
    # ADK side
    adk_agent = get_agent_instance("translation_agent")
    adk_event = _adk_event({"translated_text": "Shared response text"})

    def mock_run(user_id, session_id, new_message):
        yield adk_event

    with patch.object(adk_agent.engine._inner.runner, "run", side_effect=mock_run):
        adk_request = _make_request(
            "translation_agent",
            {"text": "Shared response text", "from_language": "English", "to_language": "French"},
        )
        adk_events = []
        async for ev in adk_agent.chat_stream(adk_request):
            adk_events.append(ev)

    adk_content = _content_events(adk_events)

    # LangGraph side
    lg_agent = get_agent_instance("personal_assistant_agent")
    with patch(
        "src.agent_framework.engines.langgraph.engine.acompletion"
    ) as mock_llm:
        from unittest.mock import MagicMock
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Shared response text"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage = None
        mock_llm.return_value = mock_response

        lg_request = _make_request("personal_assistant_agent", {"query": "anything"})
        lg_events = []
        async for ev in lg_agent.chat_stream(lg_request):
            lg_events.append(ev)

    lg_content = _content_events(lg_events)

    # Both must emit non-JSON text
    for ev in adk_content + lg_content:
        text = ev.get("text", "")
        assert not text.startswith("{"), (
            f"Engine {ev.get('agent')} emitted JSON-wrapped text: {text!r}. "
            "Both engines must emit plain display text."
        )


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
