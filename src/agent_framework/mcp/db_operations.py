"""Database operations for MCP OAuth."""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import secrets

from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from .token_encryption import encrypt_token, decrypt_token

logger = logging.getLogger(__name__)


class MCPDatabaseOperations:
    """Database operations for MCP OAuth."""

    def __init__(self, database_url: str):
        """Initialize database operations.

        Args:
            database_url: PostgreSQL connection URL
        """
        self.engine = create_engine(database_url, poolclass=NullPool)

    def create_auth_session(
        self,
        user_id: str,
        server_id: str,
        state_token: str,
        expires_in_seconds: int = 300
    ) -> str:
        """Create OAuth session for CLI polling.

        Args:
            user_id: User identifier
            server_id: MCP server ID
            state_token: CSRF protection token
            expires_in_seconds: Session expiration (default 5 minutes)

        Returns:
            Session ID
        """
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)

        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO mcp_auth_sessions
                    (session_id, user_id, server_id, state_token, expires_at)
                    VALUES (:session_id, :user_id, :server_id, :state_token, :expires_at)
                """),
                {
                    "session_id": session_id,
                    "user_id": user_id,
                    "server_id": server_id,
                    "state_token": state_token,
                    "expires_at": expires_at,
                }
            )
            conn.commit()

        logger.info(f"Created auth session {session_id} for user {user_id}, server {server_id}")
        return session_id

    def get_auth_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get OAuth session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session dict or None if not found
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT session_id, user_id, server_id, state_token, status,
                           error_message, created_at, expires_at, completed_at
                    FROM mcp_auth_sessions
                    WHERE session_id = :session_id
                """),
                {"session_id": session_id}
            ).fetchone()

            if result:
                return {
                    "session_id": result[0],
                    "user_id": result[1],
                    "server_id": result[2],
                    "state_token": result[3],
                    "status": result[4],
                    "error_message": result[5],
                    "created_at": result[6],
                    "expires_at": result[7],
                    "completed_at": result[8],
                }
            return None

    def update_auth_session_status(
        self,
        session_id: str,
        status: str,
        error_message: Optional[str] = None
    ):
        """Update OAuth session status.

        Args:
            session_id: Session identifier
            status: New status (completed, expired, error)
            error_message: Optional error message
        """
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE mcp_auth_sessions
                    SET status = :status,
                        error_message = :error_message,
                        completed_at = CASE WHEN :status = 'completed' THEN NOW() ELSE NULL END
                    WHERE session_id = :session_id
                """),
                {
                    "session_id": session_id,
                    "status": status,
                    "error_message": error_message,
                }
            )
            conn.commit()

        logger.info(f"Updated auth session {session_id} to status: {status}")

    def store_oauth_token(
        self,
        user_id: str,
        server_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        token_type: str = "Bearer",
        expires_in: Optional[int] = None,
        scope: Optional[str] = None
    ):
        """Store encrypted OAuth token.

        Args:
            user_id: User identifier
            server_id: MCP server ID
            access_token: Access token (will be encrypted)
            refresh_token: Optional refresh token (will be encrypted)
            token_type: Token type (usually "Bearer")
            expires_in: Token lifetime in seconds
            scope: OAuth scopes (space-separated)
        """
        # Encrypt tokens
        encrypted_access = encrypt_token(access_token)
        encrypted_refresh = encrypt_token(refresh_token) if refresh_token else None

        # Calculate expiration
        expires_at = None
        if expires_in:
            expires_at = datetime.now() + timedelta(seconds=expires_in)

        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO mcp_oauth_tokens
                    (user_id, server_id, access_token, refresh_token, token_type, expires_at, scope)
                    VALUES (:user_id, :server_id, :access_token, :refresh_token, :token_type, :expires_at, :scope)
                    ON CONFLICT (user_id, server_id)
                    DO UPDATE SET
                        access_token = EXCLUDED.access_token,
                        refresh_token = EXCLUDED.refresh_token,
                        token_type = EXCLUDED.token_type,
                        expires_at = EXCLUDED.expires_at,
                        scope = EXCLUDED.scope,
                        updated_at = NOW()
                """),
                {
                    "user_id": user_id,
                    "server_id": server_id,
                    "access_token": encrypted_access,
                    "refresh_token": encrypted_refresh,
                    "token_type": token_type,
                    "expires_at": expires_at,
                    "scope": scope,
                }
            )
            conn.commit()

        logger.info(f"Stored OAuth token for user {user_id}, server {server_id}")

    def get_oauth_token(self, user_id: str, server_id: str) -> Optional[Dict[str, Any]]:
        """Get OAuth token for user and server.

        Args:
            user_id: User identifier
            server_id: MCP server ID

        Returns:
            Token dict with decrypted tokens, or None
        """
        with self.engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT access_token, refresh_token, token_type, expires_at, scope
                    FROM mcp_oauth_tokens
                    WHERE user_id = :user_id AND server_id = :server_id
                """),
                {"user_id": user_id, "server_id": server_id}
            ).fetchone()

            if result:
                # Decrypt tokens
                access_token = decrypt_token(result[0])
                refresh_token = decrypt_token(result[1]) if result[1] else None

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": result[2],
                    "expires_at": result[3],
                    "scope": result[4],
                }
            return None

    def create_user_connection(
        self,
        user_id: str,
        server_id: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """Create or update user MCP connection.

        Args:
            user_id: User identifier
            server_id: MCP server ID
            config: Optional server-specific configuration
        """
        import json

        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO mcp_user_connections (user_id, server_id, config, connected_at)
                    VALUES (:user_id, :server_id, :config, NOW())
                    ON CONFLICT (user_id, server_id)
                    DO UPDATE SET
                        status = 'active',
                        config = EXCLUDED.config,
                        updated_at = NOW()
                """),
                {
                    "user_id": user_id,
                    "server_id": server_id,
                    "config": json.dumps(config) if config else None,
                }
            )
            conn.commit()

        logger.info(f"Created connection for user {user_id}, server {server_id}")

    def get_user_connections(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all MCP connections for a user.

        Args:
            user_id: User identifier

        Returns:
            List of connection dicts
        """
        with self.engine.connect() as conn:
            results = conn.execute(
                text("""
                    SELECT server_id, status, config, connected_at, last_used_at
                    FROM mcp_user_connections
                    WHERE user_id = :user_id
                    ORDER BY connected_at DESC
                """),
                {"user_id": user_id}
            ).fetchall()

            return [
                {
                    "server_id": row[0],
                    "status": row[1],
                    "config": row[2],
                    "connected_at": row[3].isoformat() if row[3] else None,
                    "last_used_at": row[4].isoformat() if row[4] else None,
                }
                for row in results
            ]

    def delete_user_connection(self, user_id: str, server_id: str):
        """Delete user MCP connection and associated tokens.

        Args:
            user_id: User identifier
            server_id: MCP server ID
        """
        with self.engine.connect() as conn:
            # Delete OAuth token
            conn.execute(
                text("DELETE FROM mcp_oauth_tokens WHERE user_id = :user_id AND server_id = :server_id"),
                {"user_id": user_id, "server_id": server_id}
            )

            # Delete connection
            conn.execute(
                text("DELETE FROM mcp_user_connections WHERE user_id = :user_id AND server_id = :server_id"),
                {"user_id": user_id, "server_id": server_id}
            )

            conn.commit()

        logger.info(f"Deleted connection for user {user_id}, server {server_id}")

    def update_last_used(self, user_id: str, server_id: str):
        """Update last used timestamp for a connection.

        Args:
            user_id: User identifier
            server_id: MCP server ID
        """
        with self.engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE mcp_user_connections
                    SET last_used_at = NOW()
                    WHERE user_id = :user_id AND server_id = :server_id
                """),
                {"user_id": user_id, "server_id": server_id}
            )
            conn.commit()
