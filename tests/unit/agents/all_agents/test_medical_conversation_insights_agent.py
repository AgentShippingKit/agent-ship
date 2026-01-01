"""Tests for MedicalConversationInsightsAgent."""

import pytest
from unittest.mock import Mock
from src.agents.all_agents.medical_conversation_insights_agent.main_agent import (
    MedicalConversationInsightsAgent,
    ConversationInsightsInput,
    ConversationInsightsOutput
)
from src.models.base_models import AgentChatRequest, FeatureMap


@pytest.fixture
def agent():
    """Create a MedicalConversationInsightsAgent instance."""
    return MedicalConversationInsightsAgent()


def test_medical_conversation_insights_agent_initialization(agent):
    """Test that MedicalConversationInsightsAgent initializes correctly."""
    assert agent is not None
    assert agent.input_schema == ConversationInsightsInput
    assert agent.output_schema == ConversationInsightsOutput
    assert agent._get_agent_name() == "medical_conversation_insights_agent"


def test_medical_conversation_insights_agent_input_schema(agent):
    """Test that MedicalConversationInsightsAgent handles input schema correctly."""
    request = AgentChatRequest(
        agent_name="medical_conversation_insights_agent",
        user_id="test_user",
        session_id="test_session",
        query=[
            {"speaker": "Patient", "text": "I have chest pain"},
            {"speaker": "Doctor", "text": "Can you describe it?"}
        ],
        features=[
            FeatureMap(feature_name="summary_length", feature_value=200),
            FeatureMap(feature_name="num_of_key_findings", feature_value=3),
            FeatureMap(feature_name="num_of_action_items", feature_value=3)
        ]
    )
    
    input_data = agent._create_input_from_request(request)
    assert isinstance(input_data, ConversationInsightsInput)
    assert len(input_data.conversation_turns) == 2
    assert input_data.summary_length == 200
    assert input_data.num_of_key_findings == 3
    assert input_data.num_of_action_items == 3


@pytest.mark.asyncio
async def test_medical_conversation_insights_agent_chat(mock_runner, mock_session_manager, agent):
    """Test that MedicalConversationInsightsAgent chat() works with mocked LLM."""
    # Mock the runner to return conversation insights
    mock_run = mock_runner({
        "summary": "Patient reported chest pain, doctor asked for description",
        "key_findings": ["Chest pain reported", "Needs further evaluation", "Patient is concerned"],
        "action_items": ["Schedule follow-up", "Order tests", "Monitor symptoms"]
    })
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="medical_conversation_insights_agent",
        user_id="test_user",
        session_id="test_session",
        query=[
            {"speaker": "Patient", "text": "I have chest pain"},
            {"speaker": "Doctor", "text": "Can you describe it?"}
        ],
        features=[
            FeatureMap(feature_name="summary_length", feature_value=200),
            FeatureMap(feature_name="num_of_key_findings", feature_value=3),
            FeatureMap(feature_name="num_of_action_items", feature_value=3)
        ]
    )
    
    response = await agent.chat(request)
    
    assert response.success is True
    assert response.agent_name == "medical_conversation_insights_agent"
    assert isinstance(response.agent_response, ConversationInsightsOutput)
    assert len(response.agent_response.summary) > 0
    assert len(response.agent_response.key_findings) > 0
    assert len(response.agent_response.action_items) > 0
