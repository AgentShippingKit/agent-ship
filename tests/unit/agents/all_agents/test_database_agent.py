"""Tests for DatabaseAgent."""

import pytest
from unittest.mock import Mock
from src.agents.all_agents.tool_pattern.main_agent import DatabaseAgent
from src.models.base_models import AgentChatRequest, TextInput, TextOutput


@pytest.fixture
def agent():
    """Create a DatabaseAgent instance."""
    return DatabaseAgent()


def test_database_agent_initialization(agent):
    """Test that DatabaseAgent initializes correctly."""
    assert agent is not None
    assert agent.input_schema == TextInput
    assert agent.output_schema == TextOutput
    assert agent._get_agent_name() == "database_agent"


def test_database_agent_has_tools(agent):
    """Test that DatabaseAgent has tools configured."""
    tools = agent._create_tools()
    assert len(tools) > 0  # DatabaseAgent should have database tool


def test_database_agent_input_schema(agent):
    """Test that DatabaseAgent handles input schema correctly."""
    request = AgentChatRequest(
        agent_name="database",
        user_id="test_user",
        session_id="test_session",
        query="What tables are available?",
        features=[]
    )
    
    input_data = agent._create_input_from_request(request)
    assert isinstance(input_data, TextInput)
    assert input_data.text == "What tables are available?"


@pytest.mark.asyncio
async def test_database_agent_chat(mock_runner, mock_session_manager, agent):
    """Test that DatabaseAgent chat() works with mocked LLM."""
    # Mock the runner to return a database response
    mock_run = mock_runner({"response": "Tables: users, products, orders"})
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="database_agent",
        user_id="test_user",
        session_id="test_session",
        query="What tables are available?",
        features=[]
    )
    
    response = await agent.chat(request)
    
    assert response.success is True
    assert response.agent_name == "database_agent"
    assert isinstance(response.agent_response, TextOutput)
    assert "users" in response.agent_response.response.lower()
