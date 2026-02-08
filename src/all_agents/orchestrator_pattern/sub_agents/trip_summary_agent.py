"""Summary agent using Google ADK for trip plan summarization."""

from typing import List
from pydantic import BaseModel, Field
from src.all_agents.base_agent import BaseAgent
from google.adk.tools import FunctionTool


class TripSummaryInput(BaseModel):
    """Input for summary generation."""
    flight_plan: str = Field(description="The flight plan.")
    hotel_plan: str = Field(description="The hotel plan.")


class TripSummaryOutput(BaseModel):
    """Output for summary generation."""
    summary: str = Field(description="The summary of the trip.")


class TripSummaryAgent(BaseAgent):
    """Agent for generating trip summary."""

    def __init__(self):
        """Initialize the trip summary agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=TripSummaryInput,
            output_schema=TripSummaryOutput
        )
    
    # No need to override chat() - base class handles it!
    # No need to override _create_tools() or _create_sub_agents() - defaults to empty list
