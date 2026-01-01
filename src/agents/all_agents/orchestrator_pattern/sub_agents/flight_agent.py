"""Flight planning agent using Google ADK for flight search and booking."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from google.adk.tools import FunctionTool


class FlightPlannerInput(BaseModel):
    """Input for flight planner generation."""
    source: str = Field(description="The source of the trip.")
    destination: str = Field(description="The destination of the trip.")


class FlightPlannerOutput(BaseModel):
    """Output for flight planner generation."""
    flight_plan: str = Field(description="The flight plan.")


class FlightPlannerAgent(BaseAgent):
    """Agent for generating flight planner."""

    def __init__(self):
        """Initialize the flight planner agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=FlightPlannerInput,
            output_schema=FlightPlannerOutput
        )
    
    # No need to override chat() - base class handles it!
    # No need to override _create_tools() or _create_sub_agents() - defaults to empty list
