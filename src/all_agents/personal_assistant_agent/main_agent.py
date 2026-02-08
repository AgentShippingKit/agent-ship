"""Personal assistant agent - a general-purpose assistant for answering questions and helping with tasks."""

from typing import List
from pydantic import BaseModel, Field
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import AgentChatRequest
from google.adk.tools import FunctionTool, AgentTool


class PersonalAssistantInput(BaseModel):
    """Input for answering questions and helping with tasks."""
    message: str = Field(description="The message to answer.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")


class PersonalAssistantOutput(BaseModel):
    """Output for answering questions and helping with tasks."""
    answer: str = Field(description="The answer to the question.")
    session_id: str = Field(description="The session id to answer the question.")
    user_id: str = Field(description="The user id to answer the question.")


class PersonalAssistantAgent(BaseAgent):
    """Agent for answering questions and helping with various tasks."""

    def __init__(self):
        """Initialize the personal assistant agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=PersonalAssistantInput,
            output_schema=PersonalAssistantOutput
        )

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema from request with message, session_id, and user_id."""
        return PersonalAssistantInput(
            message=request.query if isinstance(request.query, str) else str(request.query),
            session_id=request.session_id,
            user_id=request.user_id,
        )

    # Tools are configured via YAML (`tools` section in main_agent.yaml).
    # Add your custom tools in the YAML configuration.
