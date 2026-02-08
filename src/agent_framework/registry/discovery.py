"""Agent discovery module for automatically finding and registering agents."""

import os
import importlib
import logging
from typing import Optional, List, Union
from src.all_agents.base_agent import BaseAgent
from src.agent_framework.configs.agent_config import AgentConfig

logger = logging.getLogger(__name__)


class AgentDiscovery:
    """Handles automatic discovery of agents from the filesystem."""
    
    def __init__(self, registry):
        """Initialize the discovery with a registry instance."""
        self.registry = registry
    
    def discover_agents(self, agents_dir: Union[str, List[str]] = "src/all_agents") -> None:
        """
        Automatically discover and register agents from the agents directory(ies).
        
        Args:
            agents_dir: Path(s) to the agents directory(ies). Can be:
                - Single string path: "src/all_agents"
                - List of paths: ["src/all_agents/framework", "src/all_agents/applications"]
        """
        # Normalize to list
        if isinstance(agents_dir, str):
            agents_dirs = [agents_dir]
        else:
            agents_dirs = agents_dir
        
        for agents_dir in agents_dirs:
            logger.info(f"Discovering agents in {agents_dir}")
            
            if not os.path.exists(agents_dir):
                logger.warning(f"Agents directory {agents_dir} does not exist, skipping")
                continue
            
            # Walk through the agents directory
            for root, dirs, files in os.walk(agents_dir):
                # Skip __pycache__ directories
                dirs[:] = [d for d in dirs if d != '__pycache__']
                
                # Look for Python files that might contain agents
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        module_path = os.path.join(root, file)
                        self._try_register_agent_from_file(module_path)
    
    def _try_register_agent_from_file(self, file_path: str) -> None:
        """
        Try to register agents from a Python file.
        
        Args:
            file_path: Path to the Python file
        """
        try:
            # Convert file path to module path
            module_path = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Look for agent classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a class that inherits from BaseAgent
                if (isinstance(attr, type) and 
                    issubclass(attr, BaseAgent) and 
                    attr != BaseAgent):
                    
                    # Generate agent name
                    agent_name = self._generate_agent_name(attr_name)
                    
                    # Try to find a config file
                    config_path = self._find_config_file(file_path)
                    config = None
                    if config_path:
                        try:
                            config = AgentConfig.from_yaml(config_path)
                        except Exception as e:
                            logger.warning(f"Could not load config from {config_path}: {e}")
                    
                    self.registry.register_agent(agent_name, attr, config)
                    logger.info(f"Auto-registered agent '{agent_name}' from {file_path}")
        
        except Exception as e:
            logger.warning(f"Could not process file {file_path}: {e}")
    
    def _generate_agent_name(self, class_name: str) -> str:
        """
        Generate a consistent agent name from class name.
        
        Converts CamelCase class names to snake_case agent names by:
        1. Converting CamelCase to snake_case
        2. Removing 'agent' or '_agent' suffix if present
        3. Returning lowercase agent name
        
        Args:
            class_name: The class name in CamelCase format
            
        Returns:
            Generated agent name in snake_case format
        """
        import re
        
        # First convert CamelCase to snake_case
        agent_name = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', class_name).lower()
        
        # Remove 'agent' suffix if present
        if agent_name.endswith('_agent'):
            agent_name = agent_name[:-6]  # Remove '_agent' suffix
        elif agent_name.endswith('agent'):
            agent_name = agent_name[:-5]  # Remove 'agent' suffix
        
        if not agent_name:
            agent_name = class_name.lower()
        
        return agent_name
    
    def _find_config_file(self, agent_file_path: str) -> Optional[str]:
        """
        Find a configuration file for an agent.
        
        Args:
            agent_file_path: Path to the agent Python file
            
        Returns:
            Path to config file if found, None otherwise
        """
        # Look for YAML files in the same directory
        agent_dir = os.path.dirname(agent_file_path)
        
        for file in os.listdir(agent_dir):
            if file.endswith('.yaml') or file.endswith('.yml'):
                return os.path.join(agent_dir, file)
        
        return None
