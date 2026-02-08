"""Opik Observer - Factory for engine-specific implementations.

Usage:
    from src.agent_framework.observability.opik import OpikObserver
    
    observer = OpikObserver(agent_config)  # Auto-detects engine
    
    # ADK: callbacks automatically wired
    # LangGraph: use context managers
    with observer.thread("conv_123"):
        with observer.trace("run"):
            result = graph.invoke({...})
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.observability.opik.base_opik_observer import BaseOpikObserver

if TYPE_CHECKING:
    from src.agent_framework.observability.opik.adapters.adk import AdkOpikObserver
    from src.agent_framework.observability.opik.adapters.langgraph import LangGraphOpikObserver

logger = logging.getLogger(__name__)


def OpikObserver(agent_config: AgentConfig) -> BaseOpikObserver:
    """Factory function returning the correct Opik observer for the engine.
    
    Args:
        agent_config: Agent configuration with execution_engine field
        
    Returns:
        AdkOpikObserver if engine is 'adk'
        LangGraphOpikObserver if engine is 'langgraph'
    """
    engine = getattr(agent_config, 'execution_engine', 'adk')
    agent_name = getattr(agent_config, 'agent_name', 'unknown')
    
    # Handle both string and enum values
    engine_str = str(engine).lower()
    if hasattr(engine, 'value'):
        engine_str = str(engine.value).lower()
    
    logger.info(f"Creating OpikObserver for {agent_name} with engine={engine}")
    
    if engine_str == 'langgraph':
        from src.agent_framework.observability.opik.adapters.langgraph import LangGraphOpikObserver
        logger.info(f"Created LangGraphOpikObserver for {agent_name}")
        return LangGraphOpikObserver(agent_config)
    else:
        from src.agent_framework.observability.opik.adapters.adk import AdkOpikObserver
        logger.info(f"Created AdkOpikObserver for {agent_name}")
        return AdkOpikObserver(agent_config)


# Export for convenience
__all__ = ['OpikObserver', 'BaseOpikObserver']
