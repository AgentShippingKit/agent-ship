import pathlib

from src.agent_framework.registry import discover_agents, list_agents, clear_cache


def _get_project_root():
    """Find the project root by looking for a marker file (like pyproject.toml)."""
    current = pathlib.Path(__file__).resolve()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def test_discover_agents_registers_expected_names():
    """Light integration: discovery populates the global registry.

    We call `discover_agents` against the real `src/all_agents` tree
    and assert that a few known agents are present.
    
    Note: discovery uses relative paths from the project root to convert
    file paths to module paths. We use a relative path here.
    """

    project_root = _get_project_root()
    
    # Change to project root directory so relative paths work correctly
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(str(project_root))
        
        # Use relative path - discovery expects paths relative to project root
        agents_root = "src/all_agents"
        
        # Ensure registry is clean before and after
        clear_cache()
        
        # Discover agents - this should find agents in subdirectories
        discover_agents(agents_root)
        names = set(list_agents())
        
        # At minimum, we should have discovered some agents
        assert len(names) > 0, (
            f"No agents discovered. Checked directory: {agents_root} "
            f"(absolute: {project_root / agents_root}). "
            f"Make sure the directory exists and contains agent Python files."
        )
        
        # Check for expected agents by their YAML-declared agent_name values
        expected_names = [
            "trip_planner_agent",  # TripPlannerAgent (orchestrator)
            "translation_agent",   # TranslationAgent (single-agent)
            "file_analysis_agent", # FileAnalysisAgent
            "personal_assistant_agent",  # PersonalAssistantAgent
            "database_agent",      # DatabaseAgent (tool pattern)
        ]

        found_any = any(name in names for name in expected_names)
        assert found_any, (
            f"None of the expected agents found. "
            f"Expected at least one of: {expected_names}. "
            f"Found: {sorted(names)}"
        )
    finally:
        os.chdir(original_cwd)
