"""Pytest configuration and shared fixtures for agent tests."""

import logging
import pytest
import json
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch

# Suppress Opik logging errors during tests
# These occur because Opik background threads try to log after test completion
logging.getLogger("opik").setLevel(logging.CRITICAL)
logging.getLogger("httpx").setLevel(logging.CRITICAL)


# Disable observability during tests by default
@pytest.fixture(autouse=True)
def disable_observability(monkeypatch):
    """Disable Opik observability during tests to speed them up."""
    # Mock the create_observer function to return None
    monkeypatch.setattr("src.agent_framework.factories.observability_factory.ObservabilityFactory.create_observer", lambda agent_config: None)


# Use in-memory sessions for tests to avoid database dependency
@pytest.fixture(autouse=True)
def use_in_memory_sessions(monkeypatch):
    """Force in-memory sessions for tests to avoid database setup."""
    # Override environment variables to use in-memory sessions
    monkeypatch.setenv("AGENT_SHORT_TERM_MEMORY", "InMemory")


@pytest.fixture
def mock_runner_response():
    """Create a mock ADK response event with JSON content."""
    
    def create_response(output_data: dict):
        """Create a mock ADK response event with the given output data."""
        text_content = json.dumps(output_data)
        part = SimpleNamespace(text=text_content)
        content = SimpleNamespace(parts=[part])
        return SimpleNamespace(content=content)
    
    return create_response


@pytest.fixture
def mock_session_manager():
    """Create a mock session manager."""
    mock_manager = Mock()
    mock_manager.ensure_session_exists = AsyncMock(return_value=None)
    return mock_manager


@pytest.fixture
def mock_runner(mock_runner_response):
    """Create a mock Google ADK Runner that returns a fake response."""
    
    def create_mock_run(output_data: dict):
        """Create a mock run() method that yields a response with the given output."""
        def mock_run(user_id: str, session_id: str, new_message):
            """Mock runner.run() that yields a fake response."""
            yield mock_runner_response(output_data)
        return mock_run
    
    return create_mock_run
