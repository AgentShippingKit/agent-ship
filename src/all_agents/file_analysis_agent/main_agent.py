"""Azure artifact reading agent for PDF files from Azure Blob Storage."""

from pydantic import BaseModel, Field
from typing import List
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import AgentChatRequest, AgentChatResponse


class FileAnalysisInput(BaseModel):
    """Input for file analysis."""
    file_path: str = Field(description="The azure blob path to the file. Format: container/blob_name.")


class FileAnalysisOutput(BaseModel):
    """Output for file analysis."""
    summary: str = Field(description="The summary of the file.")
    key_findings: List[str] = Field(description="The key findings of the file.")
    recommendations: List[str] = Field(description="The recommendations of the file.")


class FileAnalysisAgent(BaseAgent):
    """Agent for analyzing files."""

    def __init__(self):
        """Initialize the file analysis agent."""
        # Config auto-loads, chat() is implemented by base class
        super().__init__(
            _caller_file=__file__,
            input_schema=FileAnalysisInput,
            output_schema=FileAnalysisOutput
        )

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent - custom implementation for artifact handling."""
        if not request.artifacts:
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response="No artifacts provided"
            )

        file_path = request.artifacts[0].artifact_path

        # Run the agent with the input
        result = await self.run(
            user_id=request.user_id,
            session_id=request.session_id,
            input_data=FileAnalysisInput(file_path=file_path)
        )
        
        return AgentChatResponse(
            agent_name=self._get_agent_name(),
            user_id=request.user_id,
            session_id=request.session_id,
            success=True,
            agent_response=result
        )

    # Tools are now configured via YAML (`tools` section in main_agent.yaml).
    # No need to override _create_tools() or _create_sub_agents().
