"""Tool factory for creating tool components.

This factory provides a clean interface for creating different
tools based on configuration, with proper validation and error handling.
"""

from typing import List, Dict, Any, Optional
import importlib
import logging

from src.agent_framework.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ToolFactory:
    """Factory for creating tool components.
    
    This factory creates tool instances based on configuration,
    with support for both framework and domain-specific tools.
    """
    
    @staticmethod
    def create(tool_config: Dict[str, Any]) -> BaseTool:
        """Create a single tool based on configuration.
        
        Args:
            tool_config: Tool configuration dictionary containing:
                - type: Tool type (function, agent, etc.)
                - id: Tool identifier
                - import: Import path for tool class
                - method: Method name to call (if applicable)
                - config: Additional tool configuration
                
        Returns:
            Instantiated tool instance
            
        Raises:
            ValueError: If tool configuration is invalid
            ImportError: If tool cannot be imported
            AttributeError: If tool method is not found
        """
        tool_type = tool_config.get('type')
        tool_id = tool_config.get('id')
        import_path = tool_config.get('import')
        method_name = tool_config.get('method')
        tool_config_data = tool_config.get('config', {})
        
        if not import_path:
            raise ValueError(f"Tool '{tool_id}' missing required 'import' field")
        
        try:
            # Import the tool module
            module_path, class_name = import_path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            tool_class = getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.error(f"Failed to import tool '{tool_id}' from '{import_path}': {e}")
            raise ImportError(f"Cannot import tool '{tool_id}': {e}")
        
        try:
            # Create tool instance
            if tool_type == 'function':
                # For function tools, we might need to wrap a function
                if method_name:
                    # Create an instance of the class first
                    tool_instance = tool_class()
                    tool_function = getattr(tool_instance, method_name)
                    return ToolFactory._create_function_tool(tool_id, tool_function, tool_config_data)
                else:
                    # Assume the class itself is a tool
                    return tool_class(**tool_config_data)
            elif tool_type == 'agent':
                # For agent tools
                return tool_class(**tool_config_data)
            else:
                # Default: try to instantiate the class
                return tool_class(**tool_config_data)
        except Exception as e:
            logger.error(f"Failed to create tool '{tool_id}': {e}")
            raise ValueError(f"Cannot create tool '{tool_id}': {e}")
    
    @staticmethod
    def create_batch(tool_configs: List[Dict[str, Any]]) -> List[BaseTool]:
        """Create multiple tools from configuration list.
        
        Args:
            tool_configs: List of tool configuration dictionaries
            
        Returns:
            List of instantiated tool objects
            
        Raises:
            ValueError: If any tool configuration is invalid
        """
        tools = []
        errors = []
        
        for tool_config in tool_configs:
            try:
                tool = ToolFactory.create(tool_config)
                tools.append(tool)
            except Exception as e:
                tool_id = tool_config.get('id', 'unknown')
                errors.append(f"Failed to create tool '{tool_id}': {e}")
                logger.error(f"Failed to create tool '{tool_id}': {e}")
        
        if errors:
            logger.warning(f"Failed to create {len(errors)} tools: {errors}")
        
        return tools
    
    @staticmethod
    def _create_function_tool(tool_id: str, tool_function: callable, config: Dict[str, Any]) -> BaseTool:
        """Create a function tool from a Python function.
        
        Args:
            tool_id: Tool identifier
            tool_function: Python function to wrap
            config: Tool configuration
            
        Returns:
            Tool instance wrapping the function
        """
        from src.agent_framework.tools.base_tool import BaseTool
        
        class FunctionToolWrapper(BaseTool):
            def __init__(self, name: str, description: str, function: callable):
                super().__init__(name, description)
                self.function = function
            
            def run(self, input: str) -> str:
                try:
                    if isinstance(input, str):
                        # Try to parse as JSON if it looks like JSON
                        import json
                        try:
                            args = json.loads(input)
                            if isinstance(args, dict):
                                return self.function(**args)
                            else:
                                return self.function(args)
                        except json.JSONDecodeError:
                            return self.function(input)
                    else:
                        return self.function(input)
                except Exception as e:
                    return f"Error executing {self.name}: {str(e)}"
            
            def to_function_tool(self):
                """Convert to Google ADK FunctionTool."""
                from google.adk.tools import FunctionTool
                
                def wrapper_func(input: str) -> str:
                    return self.run(input)
                
                wrapper_func.__name__ = self.name
                wrapper_func.__doc__ = self.description
                
                return FunctionTool(wrapper_func)
        
        # Extract description from function docstring or config
        description = config.get('description', tool_function.__doc__ or f"Function tool: {tool_id}")
        
        return FunctionToolWrapper(
            name=tool_id,
            description=description,
            function=tool_function
        )
