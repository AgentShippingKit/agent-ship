"""Base observer - Standard callback interface for observability.

Provides default no-op implementations. Override in subclasses for actual
observability (Opik, Braintrust, etc.).
"""

from abc import ABC
from typing import Any, Callable, Dict, Optional
from src.agent_framework.configs.agent_config import AgentConfig


class BaseObserver(ABC):
    """Standard base observer with callback interface.
    
    Default implementations are no-ops. Subclasses override for actual
    observability providers.
    """

    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.active_traces: Dict[str, Any] = {}

    # Callbacks - default no-op
    def before_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback before agent execution."""
        pass

    def after_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback after agent execution."""
        pass

    def before_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback before model call."""
        pass

    def after_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback after model call."""
        pass

    def before_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback before tool execution."""
        pass

    def after_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback after tool execution."""
        pass

    def before_node_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback before LangGraph node execution."""
        pass

    def after_node_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Callback after LangGraph node execution."""
        pass

    # Decorators - default identity
    def trace_agent_execution(self, trace_name: str = None):
        """Decorator for agent execution."""
        def decorator(func: Callable) -> Callable:
            return func
        return decorator

    def trace_tool_execution(self, tool_name: str):
        """Decorator for tool execution."""
        def decorator(func: Callable) -> Callable:
            return func
        return decorator

    def trace_llm_call(self, model_name: str):
        """Decorator for LLM calls."""
        def decorator(func: Callable) -> Callable:
            return func
        return decorator
