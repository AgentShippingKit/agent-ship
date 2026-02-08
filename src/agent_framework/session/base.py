"""Base abstractions for engine-agnostic session management.

This module defines the core `SessionStore` protocol and a simple factory
entrypoint. Concrete engine-specific adapters (e.g. ADK, LangGraph) live in
their own modules and are wired in here.
"""

from __future__ import annotations

from typing import Protocol


class SessionStore(Protocol):
    """Abstract interface for short-term session management.

    Engines should depend on this protocol rather than concrete session
    implementations. The initial surface area mirrors what we actually use
    today: ensuring that a session exists before running the agent.

    Note: Conversation history is managed by each engine in its own way:
    - ADK: Managed automatically by Runner's session_service
    - LangGraph: Managed by LangGraph's checkpointer (PostgresSaver/InMemorySaver)
    """

    async def ensure_session_exists(self, user_id: str, session_id: str) -> None:
        """Ensure a session exists for the given user & session identifiers."""
        ...


class SessionStoreFactory:
    """Factory for creating engine-specific `SessionStore` implementations."""

    @staticmethod
    def create(engine_name: str, agent_name: str) -> SessionStore:
        """Create a `SessionStore` for the given execution engine.

        Args:
            engine_name: Name of the execution engine (e.g., "adk", "langgraph").
            agent_name: Name of the agent for which the session store is created.

        Returns:
            A concrete `SessionStore` implementation.
        """
        if engine_name == "adk":
            # Direct import from clean adapter location
            from src.agent_framework.session.adapters.adk import AdkSessionStore
            return AdkSessionStore(agent_name=agent_name)

        if engine_name == "langgraph":
            # Direct import from clean adapter location
            from src.agent_framework.session.adapters.langgraph import LangGraphSessionStore
            return LangGraphSessionStore(agent_name=agent_name)

        raise ValueError(
            f"Unsupported engine_name '{engine_name}' for SessionStoreFactory. "
            "Expected one of: 'adk', 'langgraph'."
        )

