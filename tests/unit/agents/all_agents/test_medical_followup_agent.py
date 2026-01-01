"""Tests for MedicalFollowupAgent."""

import pytest
from unittest.mock import Mock
from src.agents.all_agents.medical_followup_agent.main_agent import (
    MedicalFollowupAgent,
    FollowupQuestionsInput,
    FollowupQuestionsOutput
)
from src.models.base_models import AgentChatRequest, FeatureMap


@pytest.fixture
def agent():
    """Create a MedicalFollowupAgent instance."""
    return MedicalFollowupAgent()


def test_medical_followup_agent_initialization(agent):
    """Test that MedicalFollowupAgent initializes correctly."""
    assert agent is not None
    assert agent.input_schema == FollowupQuestionsInput
    assert agent.output_schema == FollowupQuestionsOutput
    assert agent._get_agent_name() == "medical_followup_agent"


def test_medical_followup_agent_input_schema(agent):
    """Test that MedicalFollowupAgent handles input schema correctly."""
    request = AgentChatRequest(
        agent_name="medical_followup_agent",
        user_id="test_user",
        session_id="test_session",
        query=[
            {"speaker": "Patient", "text": "I have chest pain"},
            {"speaker": "Doctor", "text": "Can you describe it?"}
        ],
        features=[
            FeatureMap(feature_name="max_followups", feature_value=3)
        ]
    )
    
    input_data = agent._create_input_from_request(request)
    assert isinstance(input_data, FollowupQuestionsInput)
    assert len(input_data.conversation_turns) == 2
    assert input_data.max_followups == 3


@pytest.mark.asyncio
async def test_medical_followup_agent_chat(mock_runner, mock_session_manager, agent):
    """Test that MedicalFollowupAgent chat() works with mocked LLM."""
    # Mock the runner to return followup questions
    mock_run = mock_runner({
        "followup_questions": [
            "What activities trigger the chest pain?",
            "Have you experienced similar pain before?",
            "Are you taking any medications?"
        ],
        "count": 3
    })
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="medical_followup_agent",
        user_id="test_user",
        session_id="test_session",
        query=[
            {"speaker": "Patient", "text": "I have chest pain"},
            {"speaker": "Doctor", "text": "Can you describe it?"}
        ],
        features=[
            FeatureMap(feature_name="max_followups", feature_value=3)
        ]
    )
    
    response = await agent.chat(request)
    
    assert response.success is True
    assert response.agent_name == "medical_followup_agent"
    assert isinstance(response.agent_response, FollowupQuestionsOutput)
    assert len(response.agent_response.followup_questions) > 0
    assert response.agent_response.count > 0
