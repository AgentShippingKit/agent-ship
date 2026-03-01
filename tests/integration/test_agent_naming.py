"""Integration tests: agent names in registry must match YAML agent_name.

These tests run auto-discovery and verify that each agent is registered under
the exact name declared in its YAML config (not a class-name-derived fallback).
No API keys are required.
"""

import pathlib

import pytest
import yaml

from src.agent_framework.registry import discover_agents, list_agents
from tests.integration.conftest import project_root_cwd


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _discover_and_get_names() -> set:
    with project_root_cwd():
        discover_agents("src/all_agents")
        return set(list_agents())


def _yaml_agent_names() -> dict[str, str]:
    """Return {yaml_file_path: agent_name} for every *main_agent.yaml* found.

    We only look at `main_agent.yaml` (the canonical per-agent config), not
    sub-agent YAMLs inside orchestrator subdirectories, because the discovery
    system maps each Python file to the first YAML it finds in that directory
    and sub-agent files may share a directory with a different YAML.
    """
    root = pathlib.Path(__file__).resolve().parent.parent.parent
    result = {}
    for yaml_path in (root / "src" / "all_agents").rglob("main_agent.yaml"):
        try:
            data = yaml.safe_load(yaml_path.read_text())
            if isinstance(data, dict) and "agent_name" in data:
                result[str(yaml_path)] = data["agent_name"]
        except Exception:
            pass
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_github_adk_agent_name():
    """Registry registers the agent as 'github_adk_mcp_agent' (from YAML)."""
    names = _discover_and_get_names()
    assert "github_adk_mcp_agent" in names, (
        f"'github_adk_mcp_agent' not found in registry. Found: {sorted(names)}"
    )


def test_github_langgraph_agent_name():
    """Registry registers the agent as 'github_langgraph_mcp_agent' (from YAML)."""
    names = _discover_and_get_names()
    assert "github_langgraph_mcp_agent" in names, (
        f"'github_langgraph_mcp_agent' not found in registry. Found: {sorted(names)}"
    )


def test_postgres_adk_agent_name():
    """Registry registers the agent as 'postgres_adk_mcp_agent' (from YAML)."""
    names = _discover_and_get_names()
    assert "postgres_adk_mcp_agent" in names, (
        f"'postgres_adk_mcp_agent' not found in registry. Found: {sorted(names)}"
    )


def test_postgres_langgraph_agent_name():
    """Registry registers the agent as 'postgres_langgraph_mcp_agent' (from YAML)."""
    names = _discover_and_get_names()
    assert "postgres_langgraph_mcp_agent" in names, (
        f"'postgres_langgraph_mcp_agent' not found in registry. Found: {sorted(names)}"
    )


def test_translation_agent_name():
    """Registry registers the agent as 'translation_agent' (from YAML)."""
    names = _discover_and_get_names()
    assert "translation_agent" in names, (
        f"'translation_agent' not found in registry. Found: {sorted(names)}"
    )


def test_all_agent_names_match_yaml():
    """For every discovered agent, its registry key matches its YAML agent_name.

    This guards against the class-name-derivation fallback overriding the YAML name.
    """
    yaml_names = _yaml_agent_names()  # {path: name}

    with project_root_cwd() as root:
        discover_agents("src/all_agents")
        registry_keys = set(list_agents())

    # Every YAML-declared name should appear in the registry
    for yaml_path, declared_name in yaml_names.items():
        assert declared_name in registry_keys, (
            f"Agent '{declared_name}' declared in {yaml_path} "
            f"was not found in registry. Registry contains: {sorted(registry_keys)}"
        )
