"""Singleton manager for MCP server connections.

Returns a shared client per server config (by id). Clients are created on first use.
"""

import logging
from typing import Dict, Optional

from src.agent_framework.mcp.clients.base import BaseMCPClient
from src.agent_framework.mcp.clients.stdio import StdioMCPClient
from src.agent_framework.mcp.models import MCPServerConfig, MCPTransport

logger = logging.getLogger(__name__)


class MCPClientManager:
    """Manages MCP client instances per server (singleton, cache by config.id)."""

    _instance: Optional["MCPClientManager"] = None

    def __init__(self) -> None:
        self._clients: Dict[str, BaseMCPClient] = {}

    def get_client(self, server_config: MCPServerConfig) -> BaseMCPClient:
        """Get or create an MCP client for the given server config.
        Clients are cached by server_config.id.
        """
        sid = server_config.id
        if sid not in self._clients:
            self._clients[sid] = self._create_client(server_config)
            logger.debug("Created MCP client for server %s", sid)
        return self._clients[sid]

    def _create_client(self, config: MCPServerConfig) -> BaseMCPClient:
        """Create a new client for the given config (by transport)."""
        if config.transport == MCPTransport.STDIO:
            return StdioMCPClient(config)
        raise ValueError(
            f"Unsupported MCP transport '{config.transport.value}' for server '{config.id}'. "
            "Only stdio is implemented."
        )

    async def close_all(self) -> None:
        """Close all cached clients (e.g. on shutdown)."""
        for sid, client in list(self._clients.items()):
            try:
                await client.close()
            except Exception as e:
                logger.warning("Error closing MCP client %s: %s", sid, e)
        self._clients.clear()

    @classmethod
    def get_instance(cls) -> "MCPClientManager":
        """Return the singleton manager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for tests)."""
        cls._instance = None
