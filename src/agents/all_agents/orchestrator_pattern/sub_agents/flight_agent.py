
"""Flight planning agent using Google ADK for flight search and booking."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src.agents.configs.agent_config import AgentConfig
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import FeatureMap, AgentChatRequest, AgentChatResponse
from google.adk import Agent
import logging
import opik
import json

logger = logging.getLogger(__name__)

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
        agent_config = AgentConfig.from_yaml("src/agents/all_agents/orchestrator_pattern/sub_agents/flight_agent.yaml")

        super().__init__(
            agent_config=agent_config,
            input_schema=FlightPlannerInput,
            output_schema=FlightPlannerOutput
        )
        self._setup_agent() # Setup the Google ADK agent with tools
        logger.info(f"Flight Planner Agent initialized: {self.agent_config}")

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                FlightPlannerInput(
                    source=request.query["source"],
                    destination=request.query["destination"]
                )
            )

            logger.info(f"Result from flight planner agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in flight planner agent: {e}")
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
        return []


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = FlightPlannerAgent()
        
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