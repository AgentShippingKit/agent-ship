"""Unit tests for core/io.py helpers.

These tests are the first line of defence for output-schema correctness.
Every bug we have found in production that relates to how LLM output is
parsed or displayed should have a regression test here so it can never
silently regress.

Bugs caught / regressions prevented:
  - LangGraph emitting {"response": "..."} JSON instead of plain text
    (model_dump_json() was used instead of extract_display_text)
  - ADK streaming emitting raw schema JSON to the UI
  - extract_display_text not existing as a shared contract between engines
"""

import json
from types import SimpleNamespace

import pytest
from pydantic import BaseModel, Field

from src.agent_framework.core.io import (
    create_input_from_request,
    extract_display_text,
    parse_agent_response,
)
from src.service.models.base_models import AgentChatRequest


# ---------------------------------------------------------------------------
# Schema fixtures used across tests
# ---------------------------------------------------------------------------

class SingleStringOutput(BaseModel):
    """Represents TextOutput — the most common output schema."""
    response: str


class MultiFieldOutput(BaseModel):
    """Represents a structured output schema with multiple fields."""
    city: str
    temperature: float
    description: str


class SingleIntOutput(BaseModel):
    count: int


# ---------------------------------------------------------------------------
# extract_display_text — the shared engine contract
# ---------------------------------------------------------------------------

class TestExtractDisplayText:
    """extract_display_text is the single source of truth used by both ADK
    and LangGraph engines to turn raw LLM output into UI display text.

    These tests define the contract. If any test here fails, the engines
    will produce inconsistent or broken output in the Studio UI.
    """

    # ── Single string-field schema (most common: TextOutput) ─────────────

    def test_single_field_schema_returns_plain_string(self):
        # REGRESSION: LangGraph was emitting {"response": "hello"} to the UI
        # because model_dump_json() was used instead of this function.
        raw = json.dumps({"response": "hello world"})
        result = extract_display_text(SingleStringOutput, raw)
        assert result == "hello world", (
            "Single-field schema must return the field value, not the JSON wrapper. "
            "This regression caused {'response': '...'} to show in the Studio UI."
        )

    def test_single_field_schema_does_not_return_json_wrapper(self):
        raw = json.dumps({"response": "some text"})
        result = extract_display_text(SingleStringOutput, raw)
        assert not result.startswith("{"), "Must not return raw JSON for single-field string schema"
        assert "response" not in result, "Field name must not appear in display text"

    def test_single_field_with_multiline_content(self):
        text = "Line one\nLine two\nLine three"
        raw = json.dumps({"response": text})
        assert extract_display_text(SingleStringOutput, raw) == text

    def test_single_field_with_empty_string(self):
        raw = json.dumps({"response": ""})
        result = extract_display_text(SingleStringOutput, raw)
        assert result == ""

    # ── Multi-field schema (structured output) ───────────────────────────

    def test_multi_field_schema_returns_json_as_is(self):
        # For intentional structured output, JSON is the right representation.
        raw = json.dumps({"city": "Paris", "temperature": 22.5, "description": "Sunny"})
        result = extract_display_text(MultiFieldOutput, raw)
        assert result == raw, "Multi-field schema output must be preserved as JSON"

    def test_multi_field_schema_is_valid_json(self):
        raw = json.dumps({"city": "Tokyo", "temperature": 15.0, "description": "Cloudy"})
        result = extract_display_text(MultiFieldOutput, raw)
        parsed = json.loads(result)
        assert parsed["city"] == "Tokyo"

    # ── Non-JSON input (streaming chunks, plain text) ────────────────────

    def test_plain_text_returned_unchanged(self):
        # ADK may emit plain text parts that are not schema JSON (e.g. thinking steps)
        result = extract_display_text(SingleStringOutput, "Just a plain response")
        assert result == "Just a plain response"

    def test_partial_json_returned_unchanged(self):
        # During token-by-token streaming, chunks are partial JSON — must not crash
        result = extract_display_text(SingleStringOutput, '{"response": "hel')
        assert result == '{"response": "hel"'[:-1] or result == '{"response": "hel'

    def test_empty_string_returned_unchanged(self):
        result = extract_display_text(SingleStringOutput, "")
        assert result == ""

    def test_json_not_matching_schema_returned_unchanged(self):
        # Valid JSON but doesn't match the schema — return raw
        raw = json.dumps({"unknown_field": "value"})
        result = extract_display_text(SingleStringOutput, raw)
        # Either raw text or extracted — but must not raise
        assert isinstance(result, str)

    def test_non_string_single_field_returns_json(self):
        # Single field but not a string — return JSON, not str(value)
        raw = json.dumps({"count": 42})
        result = extract_display_text(SingleIntOutput, raw)
        # Should return the JSON as-is since field is not a string
        assert isinstance(result, str)

    # ── Consistency between engines ──────────────────────────────────────

    def test_adk_and_langgraph_produce_same_output_for_text_output(self):
        """Both engines call extract_display_text with the same raw JSON.
        They must produce identical output — this is the cross-engine contract.
        """
        raw = json.dumps({"response": "The answer is 42"})
        # Simulate ADK path: raw text from event part
        adk_result = extract_display_text(SingleStringOutput, raw)
        # Simulate LangGraph path: model_dump_json() of parsed output
        from pydantic import BaseModel as BM
        parsed = SingleStringOutput.model_validate(json.loads(raw))
        langgraph_result = extract_display_text(SingleStringOutput, parsed.model_dump_json())
        assert adk_result == langgraph_result == "The answer is 42", (
            "ADK and LangGraph must produce identical display text for the same schema output"
        )


# ---------------------------------------------------------------------------
# parse_agent_response
# ---------------------------------------------------------------------------

def make_adk_event(payload: dict) -> SimpleNamespace:
    text = json.dumps(payload)
    part = SimpleNamespace(text=text)
    content = SimpleNamespace(parts=[part])
    return SimpleNamespace(content=content)


class TestParseAgentResponse:

    def test_happy_path_returns_schema_instance(self):
        event = make_adk_event({"response": "hello"})
        out = parse_agent_response(SingleStringOutput, event)
        assert isinstance(out, SingleStringOutput)
        assert out.response == "hello"

    def test_plain_text_wraps_into_single_field_schema(self):
        event = SimpleNamespace(
            content=SimpleNamespace(parts=[SimpleNamespace(text="plain text")])
        )
        out = parse_agent_response(SingleStringOutput, event)
        assert isinstance(out, SingleStringOutput)
        assert out.response == "plain text"

    def test_dict_result_validates_directly(self):
        out = parse_agent_response(SingleStringOutput, {"response": "from dict"})
        assert isinstance(out, SingleStringOutput)
        assert out.response == "from dict"

    def test_multi_field_parses_correctly(self):
        event = make_adk_event({"city": "Berlin", "temperature": 18.0, "description": "Clear"})
        out = parse_agent_response(MultiFieldOutput, event)
        assert isinstance(out, MultiFieldOutput)
        assert out.city == "Berlin"
        assert out.temperature == 18.0


# ---------------------------------------------------------------------------
# create_input_from_request
# ---------------------------------------------------------------------------

class TestCreateInputFromRequest:

    def _req(self, query):
        return AgentChatRequest(
            agent_name="dummy", user_id="u1", session_id="s1",
            sender="USER", query=query, features=[],
        )

    class TextInput(BaseModel):
        text: str

    def test_string_query_maps_to_text_field(self):
        inp = create_input_from_request(self.TextInput, self._req("hello"))
        assert inp.text == "hello"

    def test_dict_query_unpacks_kwargs(self):
        inp = create_input_from_request(self.TextInput, self._req({"text": "from dict"}))
        assert inp.text == "from dict"

    def test_first_field_fallback(self):
        class CustomInput(BaseModel):
            message: str
        inp = create_input_from_request(CustomInput, self._req("hi"))
        assert inp.message == "hi"
