from typing import Any

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.configs.llm.llm_provider_config import LLMModel, LLMProviderName
from src.agent_framework.factories.tool_factory import ToolFactory


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
                "id": "dummy_tool",
                "type": "function",
                "import": "tests.unit.agent_framework.core.test_tools.DummyTool",
                "method": "run",
            }
        ],
    )

    tools = ToolFactory.create_batch(cfg.tools)

    assert len(tools) == 1
    tool = tools[0]

    # Verify it's a BaseTool instance (our framework-agnostic wrapper)
    from src.agent_framework.tools.base_tool import BaseTool
    assert isinstance(tool, BaseTool)
    
    # Verify the tool has the expected properties
    assert tool.name == "dummy_tool"
    assert hasattr(tool, 'function')
    
    # Test that the tool works - pass input as JSON to match our factory's parsing
    import json
    result = tool.run(json.dumps({"value": "test input"}))
    assert result == "TEST INPUT"


def test_build_tools_from_config_ignores_unknown_type():
    cfg = AgentConfig(
        llm_provider_name=LLMProviderName.OPENAI,
        llm_model=LLMModel.GPT_4O_MINI,
        tools=[{"type": "unknown", "foo": "bar"}],
    )

    tools = ToolFactory.create_batch(cfg.tools)
    assert tools == []
