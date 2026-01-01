"""Tests for TripPlannerAgent."""

import pytest
from unittest.mock import Mock
from src.agents.all_agents.orchestrator_pattern.main_agent import TripPlannerAgent, TripPlannerInput, TripPlannerOutput
from src.models.base_models import AgentChatRequest


@pytest.fixture
def agent():
    """Create a TripPlannerAgent instance."""
    return TripPlannerAgent()


def test_trip_planner_agent_initialization(agent):
    """Test that TripPlannerAgent initializes correctly."""
    assert agent is not None
    assert agent.input_schema == TripPlannerInput
    assert agent.output_schema == TripPlannerOutput
    assert agent._get_agent_name() == "trip_planner_agent"


def test_trip_planner_agent_has_tools(agent):
    """Test that TripPlannerAgent has sub-agent tools configured."""
    tools = agent._create_tools()
    assert len(tools) > 0  # TripPlannerAgent should have flight, hotel, and summary agents as tools


def test_trip_planner_agent_input_schema(agent):
    """Test that TripPlannerAgent handles input schema correctly."""
    request = AgentChatRequest(
        agent_name="trip_planner",
        user_id="test_user",
        session_id="test_session",
        query={
            "source": "New York",
            "destination": "Paris"
        },
        features=[]
    )
    
    input_data = agent._create_input_from_request(request)
    assert isinstance(input_data, TripPlannerInput)
    assert input_data.source == "New York"
    assert input_data.destination == "Paris"


@pytest.mark.asyncio
async def test_trip_planner_agent_chat(mock_runner, mock_session_manager, agent):
    """Test that TripPlannerAgent chat() works with mocked LLM."""
    # Mock the runner to return a trip plan response
    mock_run = mock_runner({
        "flight_plan": "Flight from NYC to Paris",
        "hotel_plan": "Hotel in Paris city center",
        "summary": "Complete trip plan for NYC to Paris"
    })
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="trip_planner_agent",
        user_id="test_user",
        session_id="test_session",
        query={
            "source": "New York",
            "destination": "Paris"
        },
        features=[]
    )
    
    response = await agent.chat(request)
    
    assert response.success is True
    assert response.agent_name == "trip_planner_agent"
    assert isinstance(response.agent_response, TripPlannerOutput)
    assert "flight_plan" in response.agent_response.model_dump()
    assert "hotel_plan" in response.agent_response.model_dump()
    assert "summary" in response.agent_response.model_dump()
