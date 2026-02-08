"""LangGraph-specific adapter for the engine-agnostic `SessionStore` interface.

This implementation provides a minimal session store that delegates conversation
history management to LangGraph's native checkpointer (AsyncPostgresSaver/InMemorySaver).

Reference: https://docs.langchain.com/oss/python/langgraph/add-memory
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Optional

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.agent_framework.session.base import SessionStore

logger = logging.getLogger(__name__)

# Global state for checkpointer (lazy async initialization)
_CHECKPOINTER: Optional[AsyncPostgresSaver | InMemorySaver] = None
_CHECKPOINTER_CTX = None  # Keep context manager reference
_CHECKPOINTER_LOCK = asyncio.Lock()
_CHECKPOINTER_INITIALIZED = False


async def _create_postgres_checkpointer(db_uri: str) -> AsyncPostgresSaver:
    """Create and setup a new AsyncPostgresSaver."""
    global _CHECKPOINTER_CTX
    
    logger.info("Creating AsyncPostgresSaver for LangGraph checkpointing")
    _CHECKPOINTER_CTX = AsyncPostgresSaver.from_conn_string(db_uri)
    checkpointer = await _CHECKPOINTER_CTX.__aenter__()
    await checkpointer.setup()
    logger.info("AsyncPostgresSaver initialized and setup complete")
    return checkpointer


async def _get_async_checkpointer(force_recreate: bool = False):
    """Create (or return cached) LangGraph async checkpointer based on env config.

    Follows LangGraph's pattern:
    - AsyncPostgresSaver: For production with PostgreSQL
    - InMemorySaver: For development/testing
    
    Reference: https://docs.langchain.com/oss/python/langgraph/add-memory
    """
    global _CHECKPOINTER, _CHECKPOINTER_INITIALIZED
    
    if _CHECKPOINTER_INITIALIZED and not force_recreate:
        return _CHECKPOINTER
    
    async with _CHECKPOINTER_LOCK:
        # Double-check after acquiring lock
        if _CHECKPOINTER_INITIALIZED and not force_recreate:
            return _CHECKPOINTER
            
        if os.getenv("AGENT_SHORT_TERM_MEMORY") == "Database":
            db_uri = os.getenv("AGENT_SESSION_STORE_URI")
            if not db_uri:
                raise RuntimeError(
                    "AGENT_SESSION_STORE_URI is not set; cannot initialize AsyncPostgresSaver"
                )
            
            _CHECKPOINTER = await _create_postgres_checkpointer(db_uri)
        else:
            logger.info("Using InMemorySaver for LangGraph short-term memory")
            _CHECKPOINTER = InMemorySaver()
        
        _CHECKPOINTER_INITIALIZED = True
        return _CHECKPOINTER


async def reset_checkpointer():
    """Reset the checkpointer connection (for handling connection timeouts)."""
    global _CHECKPOINTER, _CHECKPOINTER_INITIALIZED, _CHECKPOINTER_CTX
    
    async with _CHECKPOINTER_LOCK:
        logger.warning("Resetting LangGraph checkpointer due to connection issue")
        
        # Try to close existing context if it exists
        if _CHECKPOINTER_CTX is not None:
            try:
                await _CHECKPOINTER_CTX.__aexit__(None, None, None)
            except Exception as e:
                logger.debug("Error closing old checkpointer context: %s", e)
            _CHECKPOINTER_CTX = None
        
        _CHECKPOINTER = None
        _CHECKPOINTER_INITIALIZED = False


class LangGraphSessionStore(SessionStore):
    """SessionStore implementation for LangGraph engine.

    Uses LangGraph's native checkpointer (AsyncPostgresSaver or InMemorySaver)
    for conversation history management, respecting AGENT_SHORT_TERM_MEMORY
    and AGENT_SESSION_STORE_URI environment variables.
    
    The checkpointer is initialized lazily on first async access to handle
    the async context manager pattern properly.
    """

    def __init__(self, agent_name: str) -> None:
        self._agent_name = agent_name
        self._checkpointer: Optional[AsyncPostgresSaver | InMemorySaver] = None

    async def get_checkpointer(self):
        """Get the underlying LangGraph checkpointer (async lazy init).

        LangGraphEngine needs this to pass to StateGraph.compile(checkpointer=...)
        The checkpointer is shared across all LangGraphSessionStore instances.
        """
        if self._checkpointer is None:
            self._checkpointer = await _get_async_checkpointer()
        return self._checkpointer
    
    async def refresh_checkpointer(self):
        """Refresh the checkpointer (reconnect to database if needed)."""
        await reset_checkpointer()
        self._checkpointer = None
        return await self.get_checkpointer()

    async def ensure_session_exists(self, user_id: str, session_id: str) -> None:
        """Ensure a session exists (no-op for LangGraph checkpointer).

        LangGraph's checkpointer automatically creates thread state on first
        access, so we don't need explicit session creation here.
        """
        # Ensure checkpointer is initialized
        await self.get_checkpointer()
        
        logger.debug(
            "LangGraph session will be created on first use: agent=%s user_id=%s session_id=%s",
            self._agent_name,
            user_id,
            session_id,
        )

