"""Hotel planning agent using Google ADK for hotel search and booking."""

from typing import List
from pydantic import BaseModel, Field
from src.all_agents.base_agent import BaseAgent
from google.adk.tools import FunctionTool


class HotelPlannerInput(BaseModel):
    """Input for hotel planner generation."""
    destination: str = Field(description="The destination of the trip.")


class HotelPlannerOutput(BaseModel):
    """Output for hotel planner generation."""
    hotel_plan: str = Field(description="The hotel plan.")


class HotelPlannerAgent(BaseAgent):
    """Agent for generating hotel planner."""

    def __init__(self):
        """Initialize the hotel planner agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=HotelPlannerInput,
            output_schema=HotelPlannerOutput
        )
    
    # No need to override chat() - base class handles it!
    # No need to override _create_tools() or _create_sub_agents() - defaults to empty list
