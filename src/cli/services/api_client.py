"""HTTP client for AgentShip FastAPI service."""

import httpx
from typing import Dict, List, Optional, Any


class AgentShipAPI:
    """Client for interacting with AgentShip FastAPI service."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """Initialize API client.

        Args:
            base_url: Base URL of FastAPI service
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def get_catalog(self) -> List[Dict[str, Any]]:
        """Get available MCP servers from catalog.

        Returns:
            List of server definitions
        """
        response = self.client.get("/mcp/catalog")
        response.raise_for_status()
        return response.json()

    def get_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's connected MCP servers.

        Args:
            user_id: User identifier

        Returns:
            List of user's connections
        """
        response = self.client.get(f"/mcp/connections", params={"user_id": user_id})
        response.raise_for_status()
        return response.json()

    def get_server_info(self, server_id: str) -> Dict[str, Any]:
        """Get detailed information about an MCP server.

        Args:
            server_id: Server identifier

        Returns:
            Server definition
        """
        response = self.client.get(f"/mcp/catalog/{server_id}")
        response.raise_for_status()
        return response.json()

    def initiate_oauth(
        self,
        server_id: str,
        user_id: str,
        scopes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Initiate OAuth flow for MCP server.

        Args:
            server_id: Server identifier
            user_id: User identifier
            scopes: Optional comma-separated OAuth scopes

        Returns:
            Dict with auth_url and session_id
        """
        payload = {
            "server_id": server_id,
            "user_id": user_id
        }
        if scopes:
            payload["scopes"] = scopes.split(',')

        response = self.client.post("/mcp/auth/initiate", json=payload)
        response.raise_for_status()
        return response.json()

    def check_auth_status(self, session_id: str) -> Dict[str, Any]:
        """Check OAuth authentication status.

        Args:
            session_id: OAuth session identifier

        Returns:
            Dict with status and details
        """
        response = self.client.get(f"/mcp/auth/status/{session_id}")
        response.raise_for_status()
        return response.json()

    def disconnect(self, user_id: str, server_id: str) -> Dict[str, Any]:
        """Disconnect from MCP server.

        Args:
            user_id: User identifier
            server_id: Server identifier

        Returns:
            Success confirmation
        """
        response = self.client.delete(
            f"/mcp/connections/{server_id}",
            params={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    def test_connection(self, user_id: str, server_id: str) -> Dict[str, Any]:
        """Test MCP server connection and list tools.

        Args:
            user_id: User identifier
            server_id: Server identifier

        Returns:
            Connection status and available tools
        """
        response = self.client.get(
            f"/mcp/test/{server_id}",
            params={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    def list_tools(self, user_id: str, server_id: str) -> List[Dict[str, Any]]:
        """List available tools from MCP server.

        Args:
            user_id: User identifier
            server_id: Server identifier

        Returns:
            List of tool definitions
        """
        response = self.client.get(
            f"/mcp/tools/{server_id}",
            params={"user_id": user_id}
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close HTTP client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
