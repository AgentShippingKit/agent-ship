# Writing Tests

## Test Structure

Tests are organized in the `tests/` directory:

```
tests/
├── unit/
│   └── agents/
│       └── all_agents/
│           └── test_my_agent.py
└── integration/
    └── test_registry_discovery.py
```

## Example Agent Test

```python
import pytest
from unittest.mock import Mock
from src.all_agents.my_agent.main_agent import MyAgent
from src.service.models.base_models import AgentChatRequest

@pytest.fixture
def agent():
    return MyAgent()

def test_my_agent_initialization(agent):
    assert agent is not None
    assert agent._get_agent_name() == "my_agent"

@pytest.mark.asyncio
async def test_my_agent_chat(mock_runner, mock_session_manager, agent):
    mock_run = mock_runner({"text": "Hello, world!"})
    agent.runner = Mock()
    agent.runner.run = mock_run
    agent.session_manager = mock_session_manager
    
    request = AgentChatRequest(
        agent_name="my_agent",
        user_id="test-user",
        session_id="test-session",
        query="Hello",
        features=[]
    )
    
    response = await agent.chat(request)
    assert response.success is True
    assert response.agent_response.text == "Hello, world!"
```

## Test Fixtures

The framework provides test fixtures in `tests/conftest.py`:

- `mock_runner_response`: Creates mock ADK responses
- `mock_session_manager`: Mocks session management
- `mock_runner`: Mocks the Google ADK Runner

## Running Tests

```bash
# Run all tests
pipenv run pytest tests/ -v

# Run specific test file
pipenv run pytest tests/unit/agents/all_agents/test_my_agent.py -v
```
