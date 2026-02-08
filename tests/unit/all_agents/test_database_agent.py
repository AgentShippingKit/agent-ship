"""Tests for DatabaseAgent."""

import pytest
from unittest.mock import Mock
from src.all_agents.tool_pattern.main_agent import DatabaseAgent
from src.service.models.base_models import AgentChatRequest, TextInput, TextOutput


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
    """Test that DatabaseAgent has a tools config (list; may be empty if database tool not enabled in YAML)."""
    assert agent.agent_config.tools is not None
    assert isinstance(agent.agent_config.tools, list)


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
    # Mock the engine.run() method instead of runner
    from unittest.mock import AsyncMock
    mock_output = TextOutput(response="Tables: users, products, orders")
    agent.engine = Mock()
    agent.engine.run = AsyncMock(return_value=mock_output)
    
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
