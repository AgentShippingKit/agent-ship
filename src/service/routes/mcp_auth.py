"""MCP OAuth authentication routes."""

import os
import logging
import secrets
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from src.agent_framework.mcp.registry import MCPServerRegistry
from src.agent_framework.mcp.db_operations import MCPDatabaseOperations

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mcp", tags=["MCP OAuth"])


# ============================================
# Request/Response Models
# ============================================

class InitiateOAuthRequest(BaseModel):
    """Request to initiate OAuth flow."""
    user_id: str
    server_id: str
    scopes: Optional[list[str]] = None


class InitiateOAuthResponse(BaseModel):
    """Response from OAuth initiation."""
    auth_url: str
    session_id: str
    expires_in: int


class AuthStatusResponse(BaseModel):
    """OAuth session status."""
    status: str  # pending, completed, expired, error
    server_id: Optional[str] = None
    connected_at: Optional[str] = None
    error_message: Optional[str] = None


class ConnectionInfo(BaseModel):
    """User MCP connection info."""
    server_id: str
    status: str
    connected_at: Optional[str]
    last_used_at: Optional[str]


# ============================================
# Helper Functions
# ============================================

def get_db() -> MCPDatabaseOperations:
    """Get database operations instance."""
    database_url = os.getenv("AGENTSHIP_AUTH_DB_URI")
    if not database_url:
        raise HTTPException(status_code=500, detail="AGENTSHIP_AUTH_DB_URI not configured")
    return MCPDatabaseOperations(database_url)


def get_callback_url() -> str:
    """Get OAuth callback URL."""
    base_url = os.getenv("OAUTH_CALLBACK_BASE_URL", "http://localhost:8000")
    return f"{base_url}/mcp/auth/callback"


def get_registry() -> MCPServerRegistry:
    """Get MCP server registry instance."""
    return MCPServerRegistry.get_instance()


def validate_oauth_credentials(server_id: str) -> bool:
    """Check if OAuth credentials are configured for server.

    Args:
        server_id: Server identifier

    Returns:
        True if credentials are set in environment, False otherwise
    """
    registry = get_registry()
    server = registry.get_server(server_id)

    if not server or not server.auth:
        return False

    auth_config = server.auth
    if auth_config.type.value != "oauth":
        return False

    # Resolve credentials from environment variables
    client_id = os.getenv(auth_config.client_id_env) if auth_config.client_id_env else None
    client_secret = os.getenv(auth_config.client_secret_env) if auth_config.client_secret_env else None

    return bool(client_id and client_secret)


# ============================================
# OAuth Flow Endpoints
# ============================================

@router.post("/auth/initiate", response_model=InitiateOAuthResponse)
async def initiate_oauth(request: InitiateOAuthRequest):
    """Initiate OAuth flow for MCP server.

    Args:
        request: OAuth initiation request

    Returns:
        Authorization URL and session ID for polling
    """
    logger.info(f"Initiating OAuth for user {request.user_id}, server {request.server_id}")

    # Get server from registry
    registry = get_registry()
    server = registry.get_server(request.server_id)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server {request.server_id} not found in registry")

    # Check if server requires OAuth (SSE/HTTP transport with auth)
    if server.transport not in ["sse", "http"] or not server.auth:
        raise HTTPException(
            status_code=400,
            detail=f"Server {request.server_id} does not require OAuth (STDIO server)"
        )

    # Get OAuth config from server auth
    auth_config = server.auth
    if not auth_config or auth_config.type.value != "oauth":
        raise HTTPException(status_code=500, detail=f"OAuth not configured for {request.server_id}")

    # Validate OAuth credentials are set
    if not validate_oauth_credentials(request.server_id):
        raise HTTPException(
            status_code=500,
            detail=f"OAuth credentials not configured for {request.server_id}. "
                   f"Set {auth_config.client_id_env} and {auth_config.client_secret_env}"
        )

    # Resolve OAuth credentials from environment
    client_id = os.getenv(auth_config.client_id_env)
    if not client_id:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth client_id not found in environment variable {auth_config.client_id_env}"
        )

    # Generate state token for CSRF protection
    state_token = secrets.token_urlsafe(32)

    # Create auth session in database
    db = get_db()
    session_id = db.create_auth_session(
        user_id=request.user_id,
        server_id=request.server_id,
        state_token=state_token,
        expires_in_seconds=300  # 5 minutes
    )

    # Build authorization URL
    callback_url = get_callback_url()
    scopes = request.scopes or auth_config.scopes

    if not auth_config.authorize_url:
        raise HTTPException(
            status_code=500,
            detail=f"OAuth authorize_url not configured for {request.server_id}"
        )

    auth_params = {
        "client_id": client_id,
        "redirect_uri": callback_url,
        "state": state_token,
        "scope": " ".join(scopes),
    }

    # Add response_type for OAuth 2.0
    if "github.com" in auth_config.authorize_url:
        # GitHub doesn't require response_type
        pass
    else:
        auth_params["response_type"] = "code"

    auth_url = f"{auth_config.authorize_url}?{urlencode(auth_params)}"

    logger.info(f"Created OAuth session {session_id}, redirecting to: {auth_url}")

    return InitiateOAuthResponse(
        auth_url=auth_url,
        session_id=session_id,
        expires_in=300
    )


@router.get("/auth/callback", response_class=HTMLResponse)
async def oauth_callback(
    code: str = Query(..., description="Authorization code"),
    state: str = Query(..., description="CSRF state token"),
    error: Optional[str] = Query(None, description="OAuth error"),
    error_description: Optional[str] = Query(None, description="OAuth error description"),
):
    """Handle OAuth callback from provider.

    Args:
        code: Authorization code
        state: CSRF state token
        error: Optional error from provider
        error_description: Optional error description

    Returns:
        HTML success or error page
    """
    logger.info(f"Received OAuth callback with state: {state}")

    # Handle OAuth errors
    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        return _render_error_page(f"{error}: {error_description or 'Authorization failed'}")

    # Find session by state token
    db = get_db()

    # Get session - we need to query by state token
    # Note: This is a simplified version; in production, add index on state_token
    with db.engine.connect() as conn:
        from sqlalchemy import text
        result = conn.execute(
            text("SELECT session_id, user_id, server_id FROM mcp_auth_sessions WHERE state_token = :state"),
            {"state": state}
        ).fetchone()

        if not result:
            logger.error(f"Invalid state token: {state}")
            return _render_error_page("Invalid or expired session")

        session_id, user_id, server_id = result

    logger.info(f"Found session {session_id} for user {user_id}, server {server_id}")

    # Get OAuth config from registry
    registry = get_registry()
    server = registry.get_server(server_id)
    if not server or not server.auth or server.auth.type.value != "oauth":
        logger.error(f"OAuth config not found for {server_id}")
        db.update_auth_session_status(session_id, "error", "OAuth configuration not found")
        return _render_error_page("OAuth configuration error")

    auth_config = server.auth

    # Exchange code for token
    try:
        token_data = await _exchange_code_for_token(
            auth_config=auth_config,
            code=code,
            redirect_uri=get_callback_url()
        )

        logger.info(f"Successfully exchanged code for token, server: {server_id}")

        # Store token
        db.store_oauth_token(
            user_id=user_id,
            server_id=server_id,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_type=token_data.get("token_type", "Bearer"),
            expires_in=token_data.get("expires_in"),
            scope=token_data.get("scope"),
        )

        # Create user connection
        db.create_user_connection(user_id=user_id, server_id=server_id)

        # Update session status
        db.update_auth_session_status(session_id, "completed")

        logger.info(f"OAuth flow completed for user {user_id}, server {server_id}")

        return _render_success_page(server_id)

    except Exception as e:
        logger.error(f"Error exchanging code for token: {e}", exc_info=True)
        db.update_auth_session_status(session_id, "error", str(e))
        return _render_error_page(f"Failed to complete authorization: {str(e)}")


@router.get("/auth/status/{session_id}", response_model=AuthStatusResponse)
async def get_auth_status(session_id: str):
    """Get OAuth session status (for CLI polling).

    Args:
        session_id: OAuth session identifier

    Returns:
        Session status
    """
    db = get_db()
    session = db.get_auth_session(session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if expired
    from datetime import datetime
    if session["expires_at"] < datetime.now() and session["status"] == "pending":
        db.update_auth_session_status(session_id, "expired")
        session["status"] = "expired"

    return AuthStatusResponse(
        status=session["status"],
        server_id=session["server_id"],
        connected_at=session["completed_at"].isoformat() if session.get("completed_at") else None,
        error_message=session.get("error_message"),
    )


# ============================================
# Connection Management Endpoints
# ============================================

@router.get("/connections")
async def list_connections(user_id: str = Query(..., description="User identifier")):
    """List user's MCP connections.

    Args:
        user_id: User identifier

    Returns:
        List of connections
    """
    db = get_db()
    connections = db.get_user_connections(user_id)
    return connections


@router.delete("/connections/{server_id}")
async def disconnect_server(
    server_id: str,
    user_id: str = Query(..., description="User identifier")
):
    """Disconnect from MCP server.

    Args:
        server_id: Server identifier
        user_id: User identifier

    Returns:
        Success message
    """
    db = get_db()
    db.delete_user_connection(user_id, server_id)

    logger.info(f"User {user_id} disconnected from {server_id}")

    return {"success": True, "message": f"Disconnected from {server_id}"}


# ============================================
# Catalog Endpoints (now using Registry)
# ============================================

@router.get("/catalog")
async def get_catalog():
    """Get available MCP servers from registry.

    Returns:
        List of server definitions
    """
    registry = get_registry()
    server_ids = registry.list_server_ids()

    servers = []
    for server_id in server_ids:
        server_config = registry.get_server(server_id)
        if server_config:
            # Convert MCPServerConfig to dict format expected by API
            # OAuth servers require authentication (SSE/HTTP transport + OAuth auth)
            requires_auth = (
                server_config.transport in ["sse", "http"] and
                server_config.auth.type.value == "oauth"
            )

            server_dict = {
                "id": server_config.id,
                "name": server_config.id.replace("_", " ").title(),  # Generate name from ID
                "description": server_config.description or f"{server_config.id} MCP server",
                "transport": server_config.transport,
                "requires_auth": requires_auth,
                "url": server_config.url,
                "command": server_config.command,
                "enabled": True,  # All servers in registry are enabled
            }
            servers.append(server_dict)

    return servers


@router.get("/catalog/{server_id}")
async def get_server_info(server_id: str):
    """Get detailed information about an MCP server.

    Args:
        server_id: Server identifier

    Returns:
        Server definition
    """
    registry = get_registry()
    server = registry.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server {server_id} not found")

    # OAuth servers require authentication (SSE/HTTP transport + OAuth auth)
    requires_auth = (
        server.transport in ["sse", "http"] and
        server.auth.type.value == "oauth"
    )

    # Convert MCPServerConfig to dict format expected by API
    return {
        "id": server.id,
        "name": server.id.replace("_", " ").title(),
        "description": server.description or f"{server.id} MCP server",
        "transport": server.transport,
        "requires_auth": requires_auth,
        "url": server.url,
        "command": server.command,
        "enabled": True,
    }


# ============================================
# Testing Endpoints
# ============================================

@router.get("/test/{server_id}")
async def test_connection(
    server_id: str,
    user_id: str = Query(..., description="User identifier")
):
    """Test MCP server connection and list tools.

    Args:
        server_id: Server identifier
        user_id: User identifier

    Returns:
        Connection status and available tools
    """
    try:
        from src.agent_framework.mcp.clients.sse import SSEMCPClientFactory

        # Create SSE client
        client = SSEMCPClientFactory.create_client(server_id, user_id)

        async with client:
            # Try to list tools
            tools = await client.list_tools()

            # Get token info
            db = get_db()
            token_data = db.get_oauth_token(user_id, server_id)

            token_expires = None
            if token_data and token_data.get("expires_at"):
                token_expires = token_data["expires_at"].isoformat()

            return {
                "status": "success",
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.input_schema,
                    }
                    for tool in tools
                ],
                "token_expires_at": token_expires,
            }

    except ValueError as e:
        # User-friendly errors (token expired, not connected, etc.)
        logger.warning(f"Test connection failed for {server_id}: {e}")
        return {
            "status": "error",
            "error": str(e),
            "tools": [],
        }

    except Exception as e:
        logger.error(f"Unexpected error testing {server_id}: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Connection test failed: {str(e)}",
            "tools": [],
        }


@router.get("/tools/{server_id}")
async def list_server_tools(
    server_id: str,
    user_id: str = Query(..., description="User identifier")
):
    """List available tools from MCP server.

    Args:
        server_id: Server identifier
        user_id: User identifier

    Returns:
        List of tool definitions
    """
    try:
        from src.agent_framework.mcp.clients.sse import SSEMCPClientFactory

        client = SSEMCPClientFactory.create_client(server_id, user_id)

        async with client:
            tools = await client.list_tools()

            return [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.input_schema,
                }
                for tool in tools
            ]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing tools from {server_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


# ============================================
# Helper Functions
# ============================================

async def _exchange_code_for_token(
    auth_config,
    code: str,
    redirect_uri: str
) -> dict:
    """Exchange authorization code for access token.

    Args:
        auth_config: MCPAuthConfig instance
        code: Authorization code
        redirect_uri: Callback URL

    Returns:
        Token data dict

    Raises:
        Exception: If token exchange fails
    """
    if not auth_config.token_url:
        raise Exception("OAuth token_url not configured")

    # Resolve OAuth credentials from environment
    client_id = os.getenv(auth_config.client_id_env) if auth_config.client_id_env else None
    client_secret = os.getenv(auth_config.client_secret_env) if auth_config.client_secret_env else None

    if not client_id or not client_secret:
        raise Exception("OAuth credentials not found in environment")

    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    # GitHub uses grant_type=authorization_code
    if "github.com" in auth_config.token_url:
        data["grant_type"] = "authorization_code"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(auth_config.token_url, data=data, headers=headers)

        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
            raise Exception(f"Token exchange failed: {response.status_code}")

        token_data = response.json()

        if "error" in token_data:
            raise Exception(f"OAuth error: {token_data.get('error_description', token_data['error'])}")

        return token_data


def _render_success_page(server_name: str) -> HTMLResponse:
    """Render OAuth success page.

    Args:
        server_name: Name of connected server

    Returns:
        HTML response
    """
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connected - AgentShip</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e2e8f0;
        }}
        .container {{
            width: 100%;
            max-width: 500px;
            padding: 20px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
            text-align: center;
        }}
        .success-icon {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: rgba(20, 184, 166, 0.2);
            color: #14b8a6;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            margin: 0 auto 24px;
        }}
        h1 {{
            font-size: 28px;
            margin-bottom: 16px;
            color: #f1f5f9;
        }}
        p {{
            color: #94a3b8;
            margin-bottom: 12px;
            line-height: 1.6;
        }}
        .small {{
            font-size: 14px;
            color: #64748b;
        }}
    </style>
    <script>
        setTimeout(() => {{
            window.close();
        }}, 3000);
    </script>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="success-icon">✓</div>
            <h1>Successfully Connected!</h1>
            <p>Your {server_name} account has been connected to AgentShip.</p>
            <p class="small">You can close this window and return to your terminal.</p>
            <p class="small">This window will close automatically in 3 seconds...</p>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html)


def _render_error_page(error_message: str) -> HTMLResponse:
    """Render OAuth error page.

    Args:
        error_message: Error message to display

    Returns:
        HTML response
    """
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - AgentShip</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #e2e8f0;
        }}
        .container {{
            width: 100%;
            max-width: 500px;
            padding: 20px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
            text-align: center;
        }}
        .error-icon {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            margin: 0 auto 24px;
        }}
        h1 {{
            font-size: 28px;
            margin-bottom: 16px;
            color: #f1f5f9;
        }}
        p {{
            color: #94a3b8;
            margin-bottom: 12px;
            line-height: 1.6;
        }}
        .error-message {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid #ef4444;
            border-radius: 8px;
            padding: 12px;
            color: #fca5a5;
            font-family: monospace;
            font-size: 14px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="error-icon">✕</div>
            <h1>Connection Failed</h1>
            <div class="error-message">{error_message}</div>
            <p>Please close this window and try again.</p>
        </div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html)
