"""Abstract MCP client interface.

Engine-agnostic: list_tools returns MCPToolInfo, call_tool takes name + args.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from src.agent_framework.mcp.models import MCPToolInfo, MCPServerConfig


class BaseMCPClient(ABC):
    """Abstract interface for an MCP server connection."""

    def __init__(self, config: MCPServerConfig):
        """Initialize base MCP client.

        Args:
            config: MCP server configuration
        """
        self.config = config

    @abstractmethod
    async def list_tools(self) -> List[MCPToolInfo]:
        """Return the list of tools offered by the server."""
        ...

    @abstractmethod
    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        """Invoke a tool by name with optional arguments. Returns result content or raises."""
        ...

    async def close(self) -> None:
        """Release the connection. Override in subclasses that hold resources."""
        pass
