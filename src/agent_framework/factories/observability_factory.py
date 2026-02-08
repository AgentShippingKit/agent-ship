"""Clean Observability Factory

Creates observability components using the standard callback architecture.
Supports multiple providers (Opik, Braintrust, etc.) with fallback to base no-op.
"""

import logging
from typing import Optional

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.observability.base import BaseObserver
from src.agent_framework.observability.opik import OpikObserver

logger = logging.getLogger(__name__)


class ObservabilityFactory:
    """Factory for creating observability components with provider support."""
    
    @staticmethod
    def create_observer(agent_config: AgentConfig) -> BaseObserver:
        """Create an observer for the given agent configuration.
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            BaseObserver instance (Opik or base no-op fallback)
        """
        provider = getattr(agent_config, 'observability_provider', 'opik').lower()
        engine = getattr(agent_config, 'execution_engine', 'unknown')
        agent_name = getattr(agent_config, 'agent_name', 'unknown')
        
        logger.info(f"ObservabilityFactory: Creating observer for {agent_name} (provider={provider}, engine={engine})")
        
        try:
            if provider == 'opik':
                observer = OpikObserver(agent_config=agent_config)
                logger.info(f"ObservabilityFactory: Created {type(observer).__name__} for {agent_name}")
                return observer
            elif provider == 'braintrust':
                logger.warning("Braintrust observer not yet implemented, using no-op")
                return BaseObserver(agent_config=agent_config)
            elif provider in ('none', 'noop', 'disabled'):
                return BaseObserver(agent_config=agent_config)
            else:
                logger.warning(f"Unknown observability provider '{provider}', using no-op")
                return BaseObserver(agent_config=agent_config)
                
        except Exception as exc:
            logger.error(f"Failed to create {provider} observer: {exc}, using no-op fallback")
            return BaseObserver(agent_config=agent_config)
