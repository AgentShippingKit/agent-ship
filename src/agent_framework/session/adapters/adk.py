"""ADK-specific adapter for the engine-agnostic `SessionStore` interface.

This module reuses ADK's own `DatabaseSessionService` / `InMemorySessionService`
and encapsulates the small amount of session bootstrap logic we previously had
in `SessionServiceFactory` and `SessionManager`.
"""

from __future__ import annotations

import logging
import os

from google.adk.sessions import DatabaseSessionService, InMemorySessionService

from src.agent_framework.session.base import SessionStore


logger = logging.getLogger(__name__)


class AdkSessionStore(SessionStore):
    """ADK-backed implementation of `SessionStore`.

    This keeps all ADK behavior intact while exposing a framework-agnostic
    interface for engines to depend on.
    """

    def __init__(self, agent_name: str) -> None:
        self._agent_name = agent_name

        session_store_uri = os.getenv("AGENT_SESSION_STORE_URI")

        if os.getenv("AGENT_SHORT_TERM_MEMORY") == "Database":
            if not session_store_uri:
                logger.warning("AGENT_SESSION_STORE_URI not set, falling back to InMemorySessionService")
                logger.info("Using ADK InMemorySessionService for short-term memory")
                self._session_service = InMemorySessionService()
                self._use_database_sessions = False
            else:
                logger.info("Using ADK DatabaseSessionService for short-term memory")
                self._session_service = DatabaseSessionService(session_store_uri)
                self._use_database_sessions = True
        else:
            logger.info("Using ADK InMemorySessionService for short-term memory")
            self._session_service = InMemorySessionService()
            self._use_database_sessions = False

    @property
    def session_service(self):
        """Expose the underlying ADK session service for Runner wiring.

        AdkEngine still needs to pass a `session_service` into `Runner`, but
        higher-level code should *not* depend on this attribute.
        """

        return self._session_service

    async def ensure_session_exists(self, user_id: str, session_id: str) -> None:
        """Create session if it doesn't exist (handle duplicates gracefully)."""
        logger.info("Ensuring ADK session exists: %s for user: %s", session_id, user_id)

        try:
            await self._session_service.create_session(
                app_name=self._agent_name,
                user_id=user_id,
                session_id=session_id,
            )
            logger.info("Created new ADK session: %s", session_id)
        except Exception as create_error:  # pragma: no cover - defensive logging
            msg = str(create_error).lower()
            if "duplicate key" in msg or "already exists" in msg:
                logger.info(
                    "ADK session already exists: %s for user: %s", session_id, user_id
                )
            else:
                logger.error("Failed to create ADK session: %s", create_error)
                raise

