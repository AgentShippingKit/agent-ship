"""MCP (Model Context Protocol) server integration.

Public API for configuration and client management.
"""

from src.agent_framework.mcp.client_manager import MCPClientManager
from src.agent_framework.mcp.models import (
    MCPAuthConfig,
    MCPAuthType,
    MCPServerConfig,
    MCPServerReference,
    MCPToolInfo,
    MCPTransport,
)
from src.agent_framework.mcp.registry import MCPServerRegistry

__all__ = [
    "MCPAuthConfig",
    "MCPAuthType",
    "MCPClientManager",
    "MCPServerConfig",
    "MCPServerReference",
    "MCPServerRegistry",
    "MCPToolInfo",
    "MCPTransport",
]
