"""Abstract MCP client interface.

Engine-agnostic: list_tools returns MCPToolInfo, call_tool takes name + args.
"""

from abc import ABC, abstractmethod
from typing import Any, List

from src.agent_framework.mcp.models import MCPToolInfo


class BaseMCPClient(ABC):
    """Abstract interface for an MCP server connection."""

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
