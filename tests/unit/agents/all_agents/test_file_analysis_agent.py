"""Tests for FileAnalysisAgent."""

import pytest
from unittest.mock import Mock
from src.agents.all_agents.file_analysis_agent.main_agent import (
    FileAnalysisAgent,
    FileAnalysisInput,
    FileAnalysisOutput
)
from src.models.base_models import AgentChatRequest, Artifact


@pytest.fixture
def agent():
    """Create a FileAnalysisAgent instance."""
    return FileAnalysisAgent()


def test_file_analysis_agent_initialization(agent):
    """Test that FileAnalysisAgent initializes correctly."""
    assert agent is not None
    assert agent.input_schema == FileAnalysisInput
    assert agent.output_schema == FileAnalysisOutput
    assert agent._get_agent_name() == "file_analysis_agent"


def test_file_analysis_agent_has_tools(agent):
    """Test that FileAnalysisAgent has tools configured."""
    tools = agent._create_tools()
    assert len(tools) > 0  # FileAnalysisAgent should have Azure artifact tool


def test_file_analysis_agent_chat_without_artifacts(agent):
    """Test that FileAnalysisAgent returns error when no artifacts provided."""
    request = AgentChatRequest(
        agent_name="file_analysis_agent",
        user_id="test_user",
        session_id="test_session",
        query="",
        features=[],
        artifacts=[]  # No artifacts
    )
    
    # This should return an error response synchronously
    import asyncio
    response = asyncio.run(agent.chat(request))
    
    assert response.success is False
    assert "No artifacts" in response.agent_response or "artifacts" in str(response.agent_response).lower()


@pytest.mark.asyncio
async def test_file_analysis_agent_chat(mock_runner, mock_session_manager, agent):
    """Test that FileAnalysisAgent chat() works with mocked LLM."""
    # Mock the runner to return medical report analysis
    mock_run = mock_runner({
        "summary": "Patient shows signs of improvement",
        "key_findings": ["Blood pressure normalized", "Cholesterol levels improved"],
        "recommendations": ["Continue current medication", "Follow up in 3 months"]
    })
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="file_analysis_agent",
        user_id="test_user",
        session_id="test_session",
        query="",
        features=[],
        artifacts=[
            Artifact(
                artifact_name="report.pdf",
                artifact_path="medical-reports/test-report.pdf"
            )
        ]
    )
    
    response = await agent.chat(request)
    
    assert response.success is True
    assert response.agent_name == "file_analysis_agent"
    assert isinstance(response.agent_response, FileAnalysisOutput)
    assert len(response.agent_response.summary) > 0
    assert len(response.agent_response.key_findings) > 0
    assert len(response.agent_response.recommendations) > 0
