"""Database information fetching agent."""

import logging
import opik
from typing import List
from src.agents.all_agents.base_agent import BaseAgent
from src.agents.configs.agent_config import AgentConfig
from src.agents.tools.database_tool import DatabaseInfoTool
from src.models.base_models import TextInput, TextOutput, AgentChatRequest, AgentChatResponse
from google.adk.tools import FunctionTool


logger = logging.getLogger(__name__)


class DatabaseAgent(BaseAgent):
    """Agent for fetching database information and performing queries."""

    def __init__(self):
        """Initialize the database agent."""
        agent_config = AgentConfig.from_yaml("src/agents/all_agents/tool_pattern/main_agent.yaml")
        super().__init__(
            agent_config=agent_config,
            input_schema=TextInput,
            output_schema=TextOutput
        )

    async def chat(self, agent_chat_request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the database agent."""
        logger.info(f"Database agent chat request: {agent_chat_request}")
        
        # Run the agent with the input
        result = await self.run(
            user_id=agent_chat_request.user_id,
            session_id=agent_chat_request.session_id,
            input_data=TextInput(text=str(agent_chat_request.query))
        )
        
        # Return the response
        return AgentChatResponse(
            agent_name=self._get_agent_name(),
            user_id=agent_chat_request.user_id,
            session_id=agent_chat_request.session_id,
            success=True,
            agent_response=result.response if hasattr(result, 'response') else str(result)
        )

    def _create_sub_agents(self) -> List[BaseAgent]:
        """Create the sub-agents for the database agent."""
        logger.info("Creating database sub-agents")
        return []

    def _create_tools(self) -> List[FunctionTool]:
        """Create the tools for the database agent."""
        logger.info("Creating database tools")
        # Create FunctionTool directly with the correct parameters
        database_tool = DatabaseInfoTool()
        logger.info(f"Database tool: {database_tool}")
        
        return [FunctionTool(database_tool.run)]
