import pathlib

from src.agent_framework.configs.agent_config import AgentConfig


def _get_project_root():
    """Find the project root by looking for a marker file (like pyproject.toml)."""
    current = pathlib.Path(__file__).resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def test_from_yaml_loads_basic_fields():
    project_root = _get_project_root()
    yaml_path = project_root / "src" / "all_agents" / "file_analysis_agent" / "main_agent.yaml"

    config = AgentConfig.from_yaml(str(yaml_path))

    assert config.agent_name == "file_analysis_agent"
    assert config.model_provider is not None
    assert config.model is not None
    assert isinstance(config.tags, list)


def test_from_yaml_loads_tools_list_if_present():
    project_root = _get_project_root()
    # Use orchestrator (trip_planner) which has sub-agent tools
    yaml_path = project_root / "src" / "all_agents" / "orchestrator_pattern" / "main_agent.yaml"

    config = AgentConfig.from_yaml(str(yaml_path))

    assert isinstance(config.tools, list)
    assert any(tool.get("type") == "agent" for tool in config.tools)
