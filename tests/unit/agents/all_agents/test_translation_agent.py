"""Tests for TranslationAgent."""

import pytest
from unittest.mock import patch, Mock
from src.agents.all_agents.single_agent_pattern.main_agent import TranslationAgent, TranslationInput, TranslationOutput
from src.models.base_models import AgentChatRequest


@pytest.fixture
def agent():
    """Create a TranslationAgent instance."""
    return TranslationAgent()


def test_translation_agent_initialization(agent):
    """Test that TranslationAgent initializes correctly."""
    assert agent is not None
    assert agent.input_schema == TranslationInput
    assert agent.output_schema == TranslationOutput
    assert agent._get_agent_name() == "translation_agent"


def test_translation_agent_input_schema(agent):
    """Test that TranslationAgent handles input schema correctly."""
    request = AgentChatRequest(
        agent_name="translation",
        user_id="test_user",
        session_id="test_session",
        query={
            "text": "Hello, how are you?",
            "from_language": "en",
            "to_language": "es"
        },
        features=[]
    )
    
    input_data = agent._create_input_from_request(request)
    assert isinstance(input_data, TranslationInput)
    assert input_data.text == "Hello, how are you?"
    assert input_data.from_language == "en"
    assert input_data.to_language == "es"


@pytest.mark.asyncio
async def test_translation_agent_chat(mock_runner, mock_session_manager, agent):
    """Test that TranslationAgent chat() works with mocked LLM."""
    # Mock the runner to return a translation response
    mock_run = mock_runner({"translated_text": "Hola, ¿cómo estás?"})
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="translation_agent",
        user_id="test_user",
        session_id="test_session",
        query={
            "text": "Hello, how are you?",
            "from_language": "en",
            "to_language": "es"
        },
        features=[]
    )
    
    response = await agent.chat(request)
    
    assert response.success is True
    assert response.agent_name == "translation_agent"
    assert isinstance(response.agent_response, TranslationOutput)
    assert response.agent_response.translated_text == "Hola, ¿cómo estás?"
