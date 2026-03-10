from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput


class NotionAgent(BaseAgent):
    """Notion workspace assistant using ADK engine with Notion MCP tools."""

    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput,
        )
