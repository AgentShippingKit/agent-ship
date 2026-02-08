"""Database information fetching agent."""

from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput


class DatabaseAgent(BaseAgent):
    """Agent for fetching database information and performing queries."""

    def __init__(self):
        """Initialize the database agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput
        )

    # Tools are now configured via YAML (`tools` section in main_agent.yaml).
    # No need to override _create_tools() or _create_sub_agents().
