"""Database information fetching agent."""

from typing import List
from src.agents.all_agents.base_agent import BaseAgent
from src.agents.tools.database_tool import DatabaseInfoTool
from src.models.base_models import TextInput, TextOutput
from google.adk.tools import FunctionTool


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

    def _create_tools(self) -> List[FunctionTool]:
        """Create the tools for the database agent."""
        database_tool = DatabaseInfoTool()
        return [FunctionTool(database_tool.run)]
    
    # No need to override chat() - base class handles it!
    # No need to override _create_sub_agents() - defaults to empty list
