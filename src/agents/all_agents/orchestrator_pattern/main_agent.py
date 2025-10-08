"""Trip planning orchestrator agent using Google ADK to coordinate multiple sub-agents."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.configs.agent_config import AgentConfig
from src.agents.all_agents.base_agent import BaseAgent, AgentType
from src.models.base_models import AgentChatRequest, AgentChatResponse
from google.adk import Agent
from google.adk.tools import AgentTool
from google.adk.tools import FunctionTool
from src.agents.all_agents.orchestrator_pattern.sub_agents.flight_agent import FlightPlannerAgent
from src.agents.all_agents.orchestrator_pattern.sub_agents.hotel_agent import HotelPlannerAgent
from src.agents.all_agents.orchestrator_pattern.sub_agents.summary_agent import SummaryAgent
import logging


logger = logging.getLogger(__name__)

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
        agent_config = AgentConfig.from_yaml("src/agents/all_agents/orchestrator_pattern/main_agent.yaml")

        super().__init__(
            agent_config=agent_config,
            input_schema=TripPlannerInput,
            output_schema=TripPlannerOutput,
            agent_type=AgentType.LLM_AGENT
        )
        self._setup_agent() # Setup the Google ADK agent with tools
        logger.info(f"Trip Planner Agent initialized: {self.agent_config}")

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                TripPlannerInput(
                    source=request.query["source"],
                    destination=request.query["destination"]
                )
            )

            logger.info(f"Result from trip planner agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in trip planner agent: {e}")
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    def _create_sub_agents(self) -> List[Agent]:
        """Create the sub-agents for the agent."""
        return []
    
    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        flight_agent = FlightPlannerAgent()
        hotel_agent = HotelPlannerAgent()
        summary_agent = SummaryAgent()
        flight_agent_tool = AgentTool(flight_agent.agent)
        hotel_agent_tool = AgentTool(hotel_agent.agent)
        summary_agent_tool = AgentTool(summary_agent.agent)
        return [flight_agent_tool, hotel_agent_tool, summary_agent_tool]


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = TripPlannerAgent()
        
        # Generate a deterministic session ID
        user_id = "123"
        session_id = hashlib.md5(f"{user_id}".encode()).hexdigest()[:8]
        print(f"Generated session ID: {session_id}")
        
        query = {"source": "New York", "destination": "Los Angeles"}

        features = []

        # Create proper input using the schema
        request = AgentChatRequest(
            agent_name=agent._get_agent_name(),
            user_id=user_id,
            session_id=session_id,
            query=query,
            features=features
        )
        
        result = await agent.chat(request=request)

        logger.info(f"Result: {result}")
    
    asyncio.run(main())