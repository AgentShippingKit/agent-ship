"""Agent Registry - Modular AI agent management system."""

from typing import Union, List
from .core import AgentRegistry
from .discovery import AgentDiscovery

# Global registry instance
registry = AgentRegistry()

# Initialize discovery manager
discovery = AgentDiscovery(registry)

# Add discovery methods to the registry
def discover_agents(agents_dir: Union[str, List[str]] = None) -> None:
    """
    Discover agents in the specified directory(ies).
    
    Args:
        agents_dir: Path(s) to agent directory(ies). If None, uses configuration
            from settings.agent_directories. Can be:
            - Single string: "src/all_agents/framework"
            - List of strings: ["src/all_agents/framework", "src/all_agents/applications"]
    """
    if agents_dir is None:
        # Use configuration from settings
        from src.service.config import settings
        agents_dir = settings.agent_directories
    
    discovery.discover_agents(agents_dir)

def get_agent_instance(name: str, config=None):
    """Get an agent instance from the global registry."""
    return registry.get_agent_instance(name, config)

def has_agent_instance(name: str) -> bool:
    """Check if an agent instance exists."""
    return registry.has_agent_instance(name)

def clear_agent_instance(name: str) -> None:
    """Clear a specific agent instance."""
    registry.clear_agent_instance(name)

def clear_cache() -> None:
    """Clear all agent instances."""
    registry.clear_cache()

# Expose the main registry methods
def register_agent(name: str, agent_class, config=None) -> None:
    """Register an agent with the global registry."""
    registry.register_agent(name, agent_class, config)

def get_agent_class(name: str):
    """Get an agent class by name."""
    return registry.get_agent_class(name)

def list_agents():
    """Get list of all registered agent names."""
    return registry.list_agents()

def get_agent_info(name: str):
    """Get information about an agent."""
    return registry.get_agent_info(name)

# Make the registry instance available
__all__ = [
    'registry',
    'AgentRegistry', 
    'AgentDiscovery',
    'AgentSingletonManager',
    'discover_agents',
    'get_agent_instance',
    'has_agent_instance',
    'clear_agent_instance',
    'clear_cache',
    'register_agent',
    'get_agent_class',
    'list_agents',
    'get_agent_info'
]
