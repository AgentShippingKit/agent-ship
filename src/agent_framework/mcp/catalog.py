"""MCP Server Catalog - Defines available MCP servers for the platform."""

import os
from typing import Dict, Any, Optional, List
from enum import Enum


class MCPTransportType(str, Enum):
    """MCP transport types."""
    STDIO = "stdio"
    SSE = "sse"


class MCPServerDefinition:
    """Definition of an MCP server in the catalog."""

    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        transport: MCPTransportType,
        requires_auth: bool = False,
        url: Optional[str] = None,
        command: Optional[List[str]] = None,
        args_template: Optional[List[str]] = None,
        oauth: Optional[Dict[str, Any]] = None,
        config_template: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
    ):
        """Initialize MCP server definition.

        Args:
            id: Unique server identifier
            name: Display name
            description: Server description
            transport: Transport type (stdio or sse)
            requires_auth: Whether authentication is required
            url: Base URL (for SSE servers)
            command: Command to execute (for STDIO servers)
            args_template: Command arguments template (for STDIO servers)
            oauth: OAuth configuration (for SSE servers)
            config_template: Configuration template for user config
            enabled: Whether server is enabled
        """
        self.id = id
        self.name = name
        self.description = description
        self.transport = transport
        self.requires_auth = requires_auth
        self.url = url
        self.command = command
        self.args_template = args_template
        self.oauth = oauth or {}
        self.config_template = config_template or {}
        self.enabled = enabled

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation.

        Returns:
            Dictionary with server definition
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "transport": self.transport.value,
            "requires_auth": self.requires_auth,
            "url": self.url,
            "command": self.command,
            "args_template": self.args_template,
            "oauth": self.oauth,
            "config_template": self.config_template,
            "enabled": self.enabled,
        }


# MCP Server Catalog
# Add new MCP servers here
MCP_SERVER_CATALOG: Dict[str, MCPServerDefinition] = {
    # ============================================
    # OAuth-based SSE Servers
    # ============================================

    "github": MCPServerDefinition(
        id="github",
        name="GitHub",
        description="Access GitHub repos, issues, PRs, and code search",
        transport=MCPTransportType.SSE,
        requires_auth=True,
        url="https://api.github.com/mcp",  # Placeholder - update when GitHub MCP available
        oauth={
            "provider": "github",
            "authorize_url": "https://github.com/login/oauth/authorize",
            "token_url": "https://github.com/login/oauth/access_token",
            "scopes": ["repo", "read:org"],
            "client_id_env": "GITHUB_OAUTH_CLIENT_ID",
            "client_secret_env": "GITHUB_OAUTH_CLIENT_SECRET",
        },
        enabled=True,
    ),

    "slack": MCPServerDefinition(
        id="slack",
        name="Slack",
        description="Send messages, read channels, and manage Slack workspaces",
        transport=MCPTransportType.SSE,
        requires_auth=True,
        url="https://slack.com/api/mcp",  # Placeholder - update when Slack MCP available
        oauth={
            "provider": "slack",
            "authorize_url": "https://slack.com/oauth/v2/authorize",
            "token_url": "https://slack.com/api/oauth.v2.access",
            "scopes": ["chat:write", "channels:read", "channels:history"],
            "client_id_env": "SLACK_OAUTH_CLIENT_ID",
            "client_secret_env": "SLACK_OAUTH_CLIENT_SECRET",
        },
        enabled=True,
    ),

    "gdrive": MCPServerDefinition(
        id="gdrive",
        name="Google Drive",
        description="Access and manage Google Drive files and folders",
        transport=MCPTransportType.SSE,
        requires_auth=True,
        url="https://www.googleapis.com/mcp",  # Placeholder
        oauth={
            "provider": "google",
            "authorize_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "scopes": ["https://www.googleapis.com/auth/drive.readonly"],
            "client_id_env": "GOOGLE_OAUTH_CLIENT_ID",
            "client_secret_env": "GOOGLE_OAUTH_CLIENT_SECRET",
        },
        enabled=False,  # Disabled by default until Google Drive MCP is available
    ),

    # ============================================
    # STDIO Servers (No Auth Required)
    # ============================================

    "postgres": MCPServerDefinition(
        id="postgres",
        name="PostgreSQL",
        description="Query PostgreSQL databases with natural language",
        transport=MCPTransportType.STDIO,
        requires_auth=False,
        command=["npx", "-y", "@modelcontextprotocol/server-postgres"],
        args_template=["{connection_string}"],
        config_template={
            "connection_string": {
                "type": "string",
                "description": "PostgreSQL connection string (postgresql://user:pass@host:port/db)",
                "required": True,
                "example": "postgresql://user:password@localhost:5432/mydb",
            }
        },
        enabled=True,
    ),

    "memory": MCPServerDefinition(
        id="memory",
        name="Memory",
        description="Persistent key-value storage for agent memory",
        transport=MCPTransportType.STDIO,
        requires_auth=False,
        command=["npx", "-y", "@modelcontextprotocol/server-memory"],
        args_template=[],
        enabled=True,
    ),

    "filesystem": MCPServerDefinition(
        id="filesystem",
        name="Filesystem",
        description="Read and write files on the local filesystem",
        transport=MCPTransportType.STDIO,
        requires_auth=False,
        command=["npx", "-y", "@modelcontextprotocol/server-filesystem"],
        args_template=["{allowed_directories}"],
        config_template={
            "allowed_directories": {
                "type": "string",
                "description": "Comma-separated list of allowed directories",
                "required": True,
                "example": "/home/user/documents,/tmp",
            }
        },
        enabled=True,
    ),

    "fetch": MCPServerDefinition(
        id="fetch",
        name="Fetch",
        description="Fetch web pages and extract content",
        transport=MCPTransportType.STDIO,
        requires_auth=False,
        command=["npx", "-y", "@modelcontextprotocol/server-fetch"],
        args_template=[],
        enabled=True,
    ),

    "brave-search": MCPServerDefinition(
        id="brave-search",
        name="Brave Search",
        description="Web search using Brave Search API",
        transport=MCPTransportType.STDIO,
        requires_auth=False,
        command=["npx", "-y", "@modelcontextprotocol/server-brave-search"],
        args_template=[],
        config_template={
            "api_key": {
                "type": "string",
                "description": "Brave Search API key",
                "required": True,
                "env_var": "BRAVE_API_KEY",
            }
        },
        enabled=True,
    ),
}


def get_server(server_id: str) -> Optional[MCPServerDefinition]:
    """Get server definition by ID.

    Args:
        server_id: Server identifier

    Returns:
        Server definition or None if not found
    """
    return MCP_SERVER_CATALOG.get(server_id)


def list_servers(
    transport: Optional[MCPTransportType] = None,
    requires_auth: Optional[bool] = None,
    enabled_only: bool = True,
) -> List[MCPServerDefinition]:
    """List servers from catalog with optional filtering.

    Args:
        transport: Filter by transport type
        requires_auth: Filter by auth requirement
        enabled_only: Only return enabled servers

    Returns:
        List of server definitions
    """
    servers = list(MCP_SERVER_CATALOG.values())

    if enabled_only:
        servers = [s for s in servers if s.enabled]

    if transport is not None:
        servers = [s for s in servers if s.transport == transport]

    if requires_auth is not None:
        servers = [s for s in servers if s.requires_auth == requires_auth]

    return servers


def get_oauth_config(server_id: str) -> Optional[Dict[str, Any]]:
    """Get OAuth configuration for a server.

    Args:
        server_id: Server identifier

    Returns:
        OAuth config dict or None
    """
    server = get_server(server_id)
    if not server or not server.oauth:
        return None

    # Resolve OAuth credentials from environment
    oauth_config = server.oauth.copy()

    if "client_id_env" in oauth_config:
        client_id = os.getenv(oauth_config["client_id_env"])
        if client_id:
            oauth_config["client_id"] = client_id

    if "client_secret_env" in oauth_config:
        client_secret = os.getenv(oauth_config["client_secret_env"])
        if client_secret:
            oauth_config["client_secret"] = client_secret

    return oauth_config


def validate_oauth_credentials(server_id: str) -> bool:
    """Check if OAuth credentials are configured for a server.

    Args:
        server_id: Server identifier

    Returns:
        True if credentials are available, False otherwise
    """
    oauth_config = get_oauth_config(server_id)
    if not oauth_config:
        return False

    return (
        oauth_config.get("client_id") is not None
        and oauth_config.get("client_secret") is not None
    )


def get_stdio_command(server_id: str, config: Dict[str, Any]) -> List[str]:
    """Build STDIO command with configured arguments.

    Args:
        server_id: Server identifier
        config: User configuration dict

    Returns:
        Full command as list of strings
    """
    server = get_server(server_id)
    if not server or server.transport != MCPTransportType.STDIO:
        raise ValueError(f"Server {server_id} is not a STDIO server")

    command = server.command.copy() if server.command else []

    if server.args_template:
        # Replace template variables with config values
        for arg_template in server.args_template:
            # Simple template substitution: {variable_name}
            arg = arg_template
            for key, value in config.items():
                arg = arg.replace(f"{{{key}}}", str(value))
            command.append(arg)

    return command
