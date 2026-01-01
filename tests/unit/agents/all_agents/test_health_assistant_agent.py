"""Tests for HealthAssistantAgent."""

import pytest
from unittest.mock import Mock
from src.agents.all_agents.health_assistant_agent.main_agent import HealthAssistantAgent, HealthAssistantInput, HealthAssistantOutput
from src.models.base_models import AgentChatRequest


@pytest.fixture
def agent():
    """Create a HealthAssistantAgent instance."""
    return HealthAssistantAgent()


def test_health_assistant_agent_initialization(agent):
    """Test that HealthAssistantAgent initializes correctly."""
    assert agent is not None
    assert agent.input_schema == HealthAssistantInput
    assert agent.output_schema == HealthAssistantOutput
    assert agent._get_agent_name() == "health_assistant_agent"


def test_health_assistant_agent_has_tools(agent):
    """Test that HealthAssistantAgent has tools configured."""
    tools = agent._create_tools()
    assert len(tools) > 0  # HealthAssistantAgent should have conversation_insights_summary agent as tool


def test_health_assistant_agent_input_schema(agent):
    """Test that HealthAssistantAgent handles input schema correctly."""
    request = AgentChatRequest(
        agent_name="health_assistant_agent",
        user_id="test_user",
        session_id="test_session",
        query="What were the key findings from my last doctor visit?",
        features=[]
    )
    
    input_data = agent._create_input_from_request(request)
    assert isinstance(input_data, HealthAssistantInput)
    assert input_data.message == "What were the key findings from my last doctor visit?"
    assert input_data.user_id == "test_user"
    assert input_data.session_id == "test_session"


@pytest.mark.asyncio
async def test_health_assistant_agent_chat(mock_runner, mock_session_manager, agent):
    """Test that HealthAssistantAgent chat() works with mocked LLM."""
    # Mock the runner to return a health assistant response
    mock_run = mock_runner({
        "answer": "Based on your last visit, the key findings were...",
        "session_id": "test_session",
        "user_id": "test_user"
    })
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="health_assistant_agent",
        user_id="test_user",
        session_id="test_session",
        query="What were the key findings from my last doctor visit?",
        features=[]
    )
    
    response = await agent.chat(request)
    
    assert response.success is True
    assert response.agent_name == "health_assistant_agent"
    assert isinstance(response.agent_response, HealthAssistantOutput)
    assert len(response.agent_response.answer) > 0
