"""Base Opik Observer - Common functionality for all engines.

Provides Opik configuration and shared utilities.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import Any, Dict, Optional

import opik

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.observability.base import BaseObserver

logger = logging.getLogger(__name__)


class BaseOpikObserver(BaseObserver):
    """Base class for Opik observers.
    
    Handles common Opik configuration. Subclasses implement engine-specific
    tracing (ADK callbacks, LangGraph context managers, etc.).
    """

    def __init__(self, agent_config: AgentConfig):
        super().__init__(agent_config)
        self._configure_opik()

    def _configure_opik(self):
        """Configure Opik based on agent configuration."""
        try:
            # Opik reads from environment variables and config file
            # Just call configure() to ensure it's initialized
            opik.configure()
            logger.info(f"Opik configured for agent {self.agent_config.agent_name}")
        except Exception as e:
            logger.warning(f"Failed to configure Opik: {e}")

    @abstractmethod
    def before_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called before agent execution."""
        pass

    @abstractmethod
    def after_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called after agent execution."""
        pass

    @abstractmethod
    def before_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called before LLM call."""
        pass

    @abstractmethod
    def after_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called after LLM call."""
        pass

    @abstractmethod
    def before_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called before tool execution."""
        pass

    @abstractmethod
    def after_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called after tool execution."""
        pass

    @abstractmethod
    def trace_agent_execution(self, trace_name: str = None):
        """Decorator/factory for agent execution tracing."""
        pass

    @abstractmethod
    def trace_tool_execution(self, tool_name: str):
        """Decorator/factory for tool execution tracing."""
        pass

    @abstractmethod
    def trace_llm_call(self, model_name: str):
        """Decorator/factory for LLM call tracing."""
        pass
