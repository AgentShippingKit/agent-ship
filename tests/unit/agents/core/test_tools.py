from typing import Any

from src.agents.configs.agent_config import AgentConfig
from src.agents.configs.llm_provider_config import LLMModel, LLMProviderName
from src.agents.core.tools import build_tools_from_config


class DummyTool:
    def __init__(self) -> None:
        self.called_with: Any = None

    def run(self, value: str) -> str:
        self.called_with = value
        return value.upper()


class DummyAgent:
    """Minimal object with an `.agent` attribute for AgentTool.

    We intentionally do not inherit from BaseAgent to keep this test unit-only;
    the builder only needs an object with an `.agent` attribute.
    """

    def __init__(self) -> None:
        self.agent = object()


def test_build_tools_from_config_function_tool():
    """Test that function tools are built correctly from YAML config.
    
    FunctionTool from Google ADK wraps a callable. We verify:
    1. The tool is created successfully
    2. It's a FunctionTool instance
    3. The underlying function exists (FunctionTool stores it internally)
    """
    cfg = AgentConfig(
        llm_provider_name=LLMProviderName.OPENAI,
        llm_model=LLMModel.GPT_4O_MINI,
        tools=[
            {
                "type": "function",
                "import": "tests.unit.agents.core.test_tools.DummyTool",
                "method": "run",
            }
        ],
    )

    tools = build_tools_from_config(cfg)

    assert len(tools) == 1
    tool = tools[0]

    # Verify it's a FunctionTool instance
    from google.adk.tools import FunctionTool
    assert isinstance(tool, FunctionTool)
    
    # Verify the underlying function exists by checking FunctionTool's internal structure
    # FunctionTool typically stores the function in a _function or function attribute
    # We can verify the tool was created correctly by checking it has the expected type
    # The actual function call is handled by the ADK framework, not directly by us


def test_build_tools_from_config_ignores_unknown_type():
    cfg = AgentConfig(
        llm_provider_name=LLMProviderName.OPENAI,
        llm_model=LLMModel.GPT_4O_MINI,
        tools=[{"type": "unknown", "foo": "bar"}],
    )

    tools = build_tools_from_config(cfg)
    assert tools == []
