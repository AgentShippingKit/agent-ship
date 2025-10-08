"""Session service factory for BaseAgent."""

import os
import logging
from typing import Tuple, Union
from google.adk.sessions import DatabaseSessionService, InMemorySessionService

logger = logging.getLogger(__name__)


class SessionServiceFactory:
    """Factory for creating session services based on configuration."""
    
    @staticmethod
    def create_session_service(agent_name: str) -> Tuple[Union[DatabaseSessionService, InMemorySessionService], bool]:
        """Create session service based on configuration.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Tuple of (session_service, use_database_sessions)
        """
        logger.info(f"Setting up session service for agent: {agent_name}")
        
        # Check if AGENT_SESSION_STORE_URI is defined
        session_store_uri = os.getenv('AGENT_SESSION_STORE_URI')
        
        if os.getenv('AGENT_SHORT_TERM_MEMORY') == 'Database':
            # Use DatabaseSessionService for persistent storage
            logger.info(f"Using DatabaseSessionService...")
            session_service = DatabaseSessionService(session_store_uri)
            use_database_sessions = True
        else:
            # Use InMemorySessionService for temporary storage
            logger.info("Using InMemorySessionService (no AGENT_SHORT_TERM_MEMORY=Database)")
            session_service = InMemorySessionService()
            use_database_sessions = False
            
        logger.info(f"Session service for agent: {agent_name} created")
        return session_service, use_database_sessions
