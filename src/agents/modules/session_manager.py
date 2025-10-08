"""Session management module for BaseAgent."""

import logging
from typing import Union
from google.adk.sessions import DatabaseSessionService, InMemorySessionService

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages session creation and retrieval for agents."""
    
    def __init__(self, session_service: Union[DatabaseSessionService, InMemorySessionService], 
                 agent_name: str, use_database_sessions: bool):
        """Initialize the session manager.
        
        Args:
            session_service: The session service instance
            agent_name: Name of the agent
            use_database_sessions: Whether using database or in-memory sessions
        """
        self.session_service = session_service
        self.agent_name = agent_name
        self._use_database_sessions = use_database_sessions
        
    async def ensure_session_exists(self, user_id: str, session_id: str) -> None:
        """Create session if it doesn't exist (handle duplicates gracefully).
        
        Args:
            user_id: User identifier
            session_id: Session identifier
        """
        logger.info(f"Ensuring session exists: {session_id} for user: {user_id}")
        
        # Try to create the session - if it already exists, that's fine
        try:
            await self.session_service.create_session(
                app_name=self.agent_name,
                user_id=user_id,
                session_id=session_id
            )
            logger.info(f"Created new session: {session_id}")
        except Exception as create_error:
            # If creation fails due to duplicate key, session already exists
            if "duplicate key" in str(create_error).lower() or "already exists" in str(create_error).lower():
                logger.info(f"Session already exists: {session_id} for user: {user_id}")
            else:
                logger.error(f"Failed to create session: {create_error}")
                raise create_error
    
    def get_session_service(self):
        """Get the session service instance."""
        return self.session_service
