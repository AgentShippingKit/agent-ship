"""Core AgentRegistry class for managing AI agents."""

import logging
from typing import Dict, Type, Optional, List, Any
from src.agents.all_agents.base_agent import BaseAgent
from src.agents.configs.agent_config import AgentConfig

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Core registry for managing AI agents.
    
    This registry provides a centralized way to:
    - Register agents manually
    - Retrieve agents by name or type
    - Manage agent configurations
    - Handle singleton instances
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._agent_configs: Dict[str, AgentConfig] = {}
        self._agent_instances: Dict[str, BaseAgent] = {}
        logger.info("Agent registry initialized")
    
    def register_agent(self, name: str, agent_class: Type[BaseAgent], config: Optional[AgentConfig] = None) -> None:
        """
        Register an agent class with the registry.
        
        Args:
            name: Unique name for the agent
            agent_class: The agent class to register
            config: Optional configuration for the agent
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"Agent class {agent_class.__name__} must inherit from BaseAgent")
        
        self._agents[name] = agent_class
        if config:
            self._agent_configs[name] = config
        
        logger.info(f"Registered agent '{name}' with class {agent_class.__name__}")
    
    def get_agent_class(self, name: str) -> Type[BaseAgent]:
        """
        Get an agent class by name.
        
        Args:
            name: Name of the agent
            
        Returns:
            The agent class
            
        Raises:
            KeyError: If agent is not found
        """
        if name not in self._agents:
            available_agents = list(self._agents.keys())
            raise KeyError(f"Agent '{name}' not found. Available agents: {available_agents}")
        
        return self._agents[name]
    
    def get_agent_instance(self, name: str, config: Optional[AgentConfig] = None) -> BaseAgent:
        """
        Get or create an agent instance (singleton pattern).
        
        Args:
            name: Name of the agent
            config: Optional configuration override (only used for first creation)
            
        Returns:
            Agent instance (singleton)
        """
        # For singleton pattern, we only use the agent name as the key
        # Config is only used during first creation
        cache_key = name
        
        # Return existing instance if it exists
        if cache_key in self._agent_instances:
            logger.debug(f"Returning existing agent instance for '{name}'")
            return self._agent_instances[cache_key]
        
        # Get agent class
        agent_class = self.get_agent_class(name)
        
        # Use provided config or cached config (only for first creation)
        agent_config = config or self._agent_configs.get(name)
        
        # Create instance (only once)
        try:
            if agent_config:
                # Try to create with config first
                instance = agent_class(agent_config)
            else:
                # Try to create with default constructor
                instance = agent_class()
        except TypeError as e:
            # If the agent doesn't accept config parameter, try without it
            if "takes 1 positional argument but 2 were given" in str(e):
                logger.info(f"Agent {agent_class.__name__} doesn't accept config parameter, creating without it")
                instance = agent_class()
            else:
                raise
        
        # Cache the instance (singleton)
        self._agent_instances[cache_key] = instance
        
        logger.info(f"Created singleton agent instance for '{name}'")
        return instance
    
    def list_agents(self) -> List[str]:
        """Get list of all registered agent names."""
        return list(self._agents.keys())
    
    def get_agent_info(self, name: str) -> Dict[str, Any]:
        """
        Get information about an agent.
        
        Args:
            name: Name of the agent
            
        Returns:
            Dictionary with agent information
        """
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' not found")
        
        agent_class = self._agents[name]
        config = self._agent_configs.get(name)
        
        info = {
            "name": name,
            "class": agent_class.__name__,
            "module": agent_class.__module__,
            "description": getattr(agent_class, '__doc__', 'No description available'),
            "has_config": config is not None
        }
        
        if config:
            info["config"] = {
                "agent_name": config.agent_name,
                "description": config.description,
                "model": config.model.value,
                "provider": config.model_provider.name.value,
                "temperature": config.temperature
            }
        
        return info
    
    def has_agent_instance(self, name: str) -> bool:
        """
        Check if an agent instance already exists.
        
        Args:
            name: Name of the agent
            
        Returns:
            True if agent instance exists, False otherwise
        """
        return name in self._agent_instances
    
    def clear_cache(self) -> None:
        """Clear the agent instance cache (removes all singleton instances)."""
        self._agent_instances.clear()
        logger.info("Agent instance cache cleared (all singletons removed)")
    
    def clear_agent_instance(self, name: str) -> None:
        """
        Clear a specific agent instance from cache.
        
        Args:
            name: Name of the agent to clear
        """
        if name in self._agent_instances:
            del self._agent_instances[name]
            logger.info(f"Cleared agent instance for '{name}'")
        else:
            logger.warning(f"Agent instance '{name}' not found in cache")
    
    def __str__(self) -> str:
        """String representation of the registry."""
        agents_info = []
        for name in self._agents:
            info = self.get_agent_info(name)
            singleton_status = "✓" if self.has_agent_instance(name) else "○"
            agents_info.append(f"  {singleton_status} {name}: {info['class']} ({info['module']})")
        
        return f"AgentRegistry(agents={len(self._agents)}, instances={len(self._agent_instances)}):\n" + "\n".join(agents_info)
