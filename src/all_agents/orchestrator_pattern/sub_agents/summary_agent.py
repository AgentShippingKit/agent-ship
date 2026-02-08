
"""Summary agent using Google ADK for trip plan summarization."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import AgentChatRequest, AgentChatResponse
import logging

logger = logging.getLogger(__name__)

class SummaryInput(BaseModel):
    """Input for summary generation."""
    flight_plan: str = Field(description="The flight plan.")
    hotel_plan: str = Field(description="The hotel plan.")

class SummaryOutput(BaseModel):
    """Output for summary generation."""
    summary: str = Field(description="The summary of the trip.")


class SummaryAgent(BaseAgent):
    """Agent for generating summary."""    

    def __init__(self):
        """Initialize the summary agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=SummaryInput,
            output_schema=SummaryOutput
        )

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                SummaryInput(
                    flight_plan=request.query["flight_plan"],
                    hotel_plan=request.query["hotel_plan"]
                )
            )

            logger.info(f"Result from summary agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in summary agent: {e}")
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    # Tools and sub-agents are configured via YAML (`tools` section in summary_agent.yaml).
    # No need to override _create_tools() or _create_sub_agents().


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = HotelPlannerAgent()
        
        # Generate a deterministic session ID
        user_id = "123"
        session_id = hashlib.md5(f"{user_id}".encode()).hexdigest()[:8]
        print(f"Generated session ID: {session_id}")
        
        query = {"destination": "Los Angeles"}

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