"""Azure artifact reading agent for PDF files from Azure Blob Storage."""

from typing import List
from pydantic import BaseModel, Field
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import AgentChatRequest, AgentChatResponse
from src.agents.tools.azure_artifact_reading_tool import AzureArtifactTool
from google.adk.tools import FunctionTool


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

    def _create_tools(self) -> List[FunctionTool]:
        """Create the tools for the agent."""
        azure_tool = AzureArtifactTool()
        return [FunctionTool(azure_tool.run)]
    
    # No need to override _create_sub_agents() - defaults to empty list
