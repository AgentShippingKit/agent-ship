import pathlib

import pytest

from src.agents.configs.agent_config import AgentConfig
from src.agents.core.config import load_agent_config


def _get_project_root():
    """Find the project root by looking for a marker file (like pyproject.toml)."""
    current = pathlib.Path(__file__).resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def test_load_agent_config_with_explicit_path():
    project_root = _get_project_root()
    yaml_path = project_root / "src" / "agents" / "all_agents" / "health_assistant_agent" / "main_agent.yaml"

    cfg = load_agent_config(agent_config=None, config_path=str(yaml_path), caller_file=None)

    assert isinstance(cfg, AgentConfig)
    assert cfg.agent_name == "health_assistant_agent"


def test_load_agent_config_requires_some_source(monkeypatch):
    """Test that load_agent_config raises ValueError when no source is provided.
    
    We need to mock the stack inspection to prevent it from finding the test file.
    """
    # Mock inspect.currentframe to return None, preventing stack-based detection
    import inspect
    
    def mock_currentframe():
        return None
    
    monkeypatch.setattr(inspect, "currentframe", mock_currentframe)
    
    # The error message can be either format, so we check for ValueError with any message
    with pytest.raises(ValueError) as exc_info:
        load_agent_config(agent_config=None, config_path=None, caller_file=None)
    
    # Verify the error message contains key phrases
    error_msg = str(exc_info.value)
    assert "Cannot auto-detect" in error_msg or "Config path could not be resolved" in error_msg
