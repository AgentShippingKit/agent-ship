"""Base class for all tools."""

from abc import ABC, abstractmethod


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