"""Agent configuration module for BaseAgent."""

import logging
from src.agents.configs.agent_config import AgentConfig
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)


class AgentConfigurator:
    """Handles agent configuration and setup."""
    
    def __init__(self, agent_config: AgentConfig):
        """Initialize the agent configurator.
        
        Args:
            agent_config: The agent configuration
        """
        self.agent_config = agent_config
        
    def get_agent_name(self) -> str:
        """Get the name of the agent."""
        logger.info(f"Getting agent name: {self.agent_config.agent_name}")
        return self.agent_config.agent_name
    
    def get_agent_description(self) -> str:
        """Get the description of the agent."""
        logger.info(f"Getting description: {self.agent_config.description}")
        return self.agent_config.description

    def get_instruction_template(self) -> str:
        """Get the instruction template of the agent."""
        logger.info(f"Getting instruction template: {self.agent_config.instruction_template}")
        return self.agent_config.instruction_template

    def get_model(self) -> LiteLlm:
        """Get the model of the agent."""
        logger.info(f"Getting model: {self.agent_config.model.value}")
        return LiteLlm(self.agent_config.model.value)
    
    def get_agent_config(self) -> AgentConfig:
        """Get the configuration of the agent."""
        logger.info(f"Getting agent config: {self.agent_config}")
        return self.agent_config
