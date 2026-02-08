"""Base class for all tools."""

from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable


class BaseTool(ABC):
    """Base class for all tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @property
    def tool_name(self) -> str:
        """Get the name of the tool."""
        return self.name
    
    @property
    def tool_description(self) -> str:
        """Get the description of the tool."""
        return self.description

    @abstractmethod
    def run(self, input: str) -> str:
        """Run the tool."""
        pass
    
    def to_function_tool(self):
        """Convert this tool to a Google ADK FunctionTool.
        
        This is a default implementation that can be overridden by subclasses.
        Uses functools.wraps to properly preserve function metadata.
        """
        from google.adk.tools import FunctionTool
        
        @wraps(self.run)
        def tool_function(input: str) -> str:
            """Tool function wrapper."""
            return self.run(input)
        
        # Set the name and description on the wrapper function
        tool_function.__name__ = self.tool_name
        tool_function.__doc__ = self.tool_description
        
        return FunctionTool(tool_function)