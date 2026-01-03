"""Utility functions for path resolution in agents."""

import os
from typing import Optional


def resolve_config_path(config_filename: Optional[str] = None, relative_to: Optional[str] = None) -> str:
    """
    Resolve a configuration file path relative to the calling agent file.
    
    Convention: YAML filename should match the Python filename.
    Example: main_agent.py → main_agent.yaml
    
    This function helps agents load their YAML config files using relative paths,
    making the code portable and independent of the project structure.
    
    Args:
        config_filename: Name of the config file. If None, automatically derives from Python filename.
                         Example: "main_agent.yaml" or None (auto-detect)
        relative_to: Path to resolve relative to. If None, uses caller's file location.
                     Typically pass __file__ from the agent module.
    
    Returns:
        Absolute path to the configuration file.
    
    Example:
        ```python
        # Option 1: Explicit filename
        config_path = resolve_config_path("main_agent.yaml", __file__)
        
        # Option 2: Auto-detect from Python filename (recommended)
        config_path = resolve_config_path(relative_to=__file__)
        # If __file__ is "main_agent.py", finds "main_agent.yaml"
        
        agent_config = AgentConfig.from_yaml(config_path)
        ```
    """
    if relative_to is None:
        # If no reference point, assume it's an absolute path or relative to cwd
        if config_filename is None:
            raise ValueError("Either config_filename or relative_to must be provided")
        return config_filename
    
    # Get the directory of the file that called this function
    agent_dir = os.path.dirname(os.path.abspath(relative_to))
    
    # If config_filename not provided, derive from Python filename
    if config_filename is None:
        python_filename = os.path.basename(relative_to)
        # Remove .py extension and add .yaml
        config_filename = os.path.splitext(python_filename)[0] + ".yaml"
    
    # Join with the config filename
    config_path = os.path.join(agent_dir, config_filename)
    
    # Return absolute path
    return os.path.abspath(config_path)


def find_config_file(directory: str, config_name: str = "main_agent.yaml") -> Optional[str]:
    """
    Find a configuration file in a directory.
    
    Searches for common config file names in the specified directory.
    
    Args:
        directory: Directory to search in
        config_name: Name of the config file to find
    
    Returns:
        Path to config file if found, None otherwise
    """
    config_path = os.path.join(directory, config_name)
    
    if os.path.exists(config_path):
        return os.path.abspath(config_path)
    
    # Try alternative names
    alternatives = [
        config_name.replace(".yaml", ".yml"),
        "config.yaml",
        "config.yml",
        "agent.yaml",
        "agent.yml"
    ]
    
    for alt_name in alternatives:
        alt_path = os.path.join(directory, alt_name)
        if os.path.exists(alt_path):
            return os.path.abspath(alt_path)
    
    return None
