"""Translation agent using Google ADK for multi-language text translation."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from google.adk.tools import FunctionTool
from src.agents.configs.agent_config import AgentConfig
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import FeatureMap, AgentChatRequest, AgentChatResponse
import logging
import opik
import json

logger = logging.getLogger(__name__)

class TranslationInput(BaseModel):
    """Input for translation generation."""
    text: str = Field(description="The text to translate.")
    from_language: str = Field(description="The language of the text to translate from.")
    to_language: str = Field(description="The language of the text to translate to.")

class TranslationOutput(BaseModel):
    """Output for translation generation."""
    translated_text: str = Field(description="The translated text.")


class TranslationAgent(BaseAgent):
    """Agent for generating translation."""

    def __init__(self):
        """Initialize the translation agent."""
        agent_config = AgentConfig.from_yaml("src/agents/all_agents/single_agent_pattern/main_agent.yaml")

        super().__init__(
            agent_config=agent_config,
            input_schema=TranslationInput,
            output_schema=TranslationOutput
        )
        self._setup_agent() # Setup the Google ADK agent with tools
        logger.info(f"Translation Agent initialized: {self.agent_config}")

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        logger.debug(f"Chatting with the agent: {self._get_agent_name()}")

        try:
            result = await self.run(
                request.user_id,
                request.session_id,
                TranslationInput(
                    text=request.query["text"],
                    from_language=request.query["from_language"],
                    to_language=request.query["to_language"]
                )
            )

            logger.info(f"Result from translation agent: {result}")

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result
            )
        except Exception as e:
            logger.error(f"Error in translation agent: {e}")
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(e)}"
            )
    
    def _create_sub_agents(self) -> List[BaseAgent]:
        """Create the sub-agents for the translation agent."""
        logger.info("Creating translation sub-agents")
        return []

    def _create_tools(self) -> List[FunctionTool]:
        """Create tools for the agent."""
        return []


if __name__ == "__main__":
    import asyncio
    import hashlib
    
    async def main():
        agent = TranslationAgent()
        
        # Generate a deterministic session ID
        user_id = "123"
        session_id = hashlib.md5(f"{user_id}".encode()).hexdigest()[:8]
        print(f"Generated session ID: {session_id}")
        
        query = {"text": "Hello, how are you?", "from_language": "en", "to_language": "es"}

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