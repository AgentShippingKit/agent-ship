"""Trip planning orchestrator agent using Google ADK to coordinate multiple sub-agents."""

from typing import List
from pydantic import BaseModel, Field
from src.all_agents.base_agent import BaseAgent, AgentType
from google.adk.tools import AgentTool
from google.adk.tools import FunctionTool
from src.all_agents.orchestrator_pattern.sub_agents.flight_agent import FlightPlannerAgent
from src.all_agents.orchestrator_pattern.sub_agents.hotel_agent import HotelPlannerAgent
from src.all_agents.orchestrator_pattern.sub_agents.trip_summary_agent import TripSummaryAgent


class TripPlannerInput(BaseModel):
    """Input for trip planning generation."""
    source: str = Field(description="The source of the trip.")
    destination: str = Field(description="The destination of the trip.")


class TripPlannerOutput(BaseModel):
    """Output for trip planning generation."""
    flight_plan: str = Field(description="The flight plan.")
    hotel_plan: str = Field(description="The hotel plan.")
    summary: str = Field(description="The summary of the trip.")


class TripPlannerAgent(BaseAgent):
    """Agent for generating trip planner."""

    def __init__(self):
        """Initialize the trip planner agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=TripPlannerInput,
            output_schema=TripPlannerOutput,
            agent_type=AgentType.LLM_AGENT
        )

    # Tools are now configured via YAML (`tools` section in main_agent.yaml).
    # No need to override _create_tools() or _create_sub_agents().


if __name__ == "__main__":
    import asyncio
    import hashlib
    from src.service.models.base_models import AgentChatRequest
    
    async def main():
        agent = TripPlannerAgent()
        
        # Generate a deterministic session ID
        user_id = "123"
        session_id = hashlib.md5(f"{user_id}".encode()).hexdigest()[:8]
        print(f"Generated session ID: {session_id}")
        
        query = {"source": "New York", "destination": "Los Angeles"}

        # Create proper input using the schema
        request = AgentChatRequest(
            agent_name=agent._get_agent_name(),
            user_id=user_id,
            session_id=session_id,
            query=query,
            features=[]
        )
        
        result = await agent.chat(request=request)
        print(f"Result: {result}")
    
    asyncio.run(main())
