import json
from types import SimpleNamespace

from pydantic import BaseModel, Field

from src.agents.core.io import create_input_from_request, parse_agent_response
from src.models.base_models import AgentChatRequest


class SimpleInput(BaseModel):
    text: str = Field(...)


class SimpleOutput(BaseModel):
    value: str


def make_fake_event(payload: dict) -> SimpleNamespace:
    text = json.dumps(payload)
    part = SimpleNamespace(text=text)
    content = SimpleNamespace(parts=[part])
    return SimpleNamespace(content=content)


def test_create_input_from_request_with_dict_query():
    req = AgentChatRequest(
        agent_name="dummy",
        user_id="u1",
        session_id="s1",
        sender="USER",
        query={"text": "hello"},
        features=[],
    )

    inp = create_input_from_request(SimpleInput, req)
    assert isinstance(inp, SimpleInput)
    assert inp.text == "hello"


def test_create_input_from_request_with_string_query():
    req = AgentChatRequest(
        agent_name="dummy",
        user_id="u1",
        session_id="s1",
        sender="USER",
        query="hello world",
        features=[],
    )

    inp = create_input_from_request(SimpleInput, req)
    assert inp.text == "hello world"


def test_parse_agent_response_happy_path():
    event = make_fake_event({"value": "ok"})
    out = parse_agent_response(SimpleOutput, event)
    assert isinstance(out, SimpleOutput)
    assert out.value == "ok"


def test_parse_agent_response_bad_json_returns_raw():
    # content.parts[0].text is not valid JSON
    event = SimpleNamespace(content=SimpleNamespace(parts=[SimpleNamespace(text="not-json")]))
    out = parse_agent_response(SimpleOutput, event)
    assert out == "not-json"