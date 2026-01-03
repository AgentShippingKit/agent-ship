"""History facts agent using Google ADK for history facts generation."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent


class HistoryFactsInput(BaseModel):
    """Input for history facts generation."""
    query: str = Field(description="The query to get the history facts for.")


class HistoryFactsOutput(BaseModel):
    """Output for history facts generation."""
    facts: List[str] = Field(description="The history facts for the query.")


class HistoryFactsAgent(BaseAgent):
    """Agent for generating history facts."""

    def __init__(self):
        """Initialize the history facts agent."""
        # Config auto-loads from main_agent.yaml, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=HistoryFactsInput,
            output_schema=HistoryFactsOutput
        )
    
    # No need to override chat() - base class handles it!
    # No need to override _create_tools() or _create_sub_agents() - defaults to empty list