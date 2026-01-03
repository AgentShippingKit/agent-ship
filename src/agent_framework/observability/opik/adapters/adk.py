"""ADK Opik Adapter - Uses official OpikTracer for callback-based tracing.

Automatically maps ADK session_id to Opik thread_id.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

try:
    from opik.integrations.adk import OpikTracer
    HAS_ADK_INTEGRATION = True
except ImportError:
    HAS_ADK_INTEGRATION = False

try:
    import opik
    from opik.api_objects.opik_client import Opik
    HAS_OPIK = True
except ImportError:
    HAS_OPIK = False

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.observability.opik.base_opik_observer import BaseOpikObserver

logger = logging.getLogger(__name__)


class AdkOpikObserver(BaseOpikObserver):
    """Opik observer for Google ADK using official OpikTracer.
    
    Features:
    - Automatic session_id → thread_id mapping
    - Callback-based span creation (agent, model, tool)
    - Hierarchical trace structure via track_adk_agent_recursive
    """

    def __init__(self, agent_config: AgentConfig):
        super().__init__(agent_config)
        self._opik_tracer: Optional[Any] = None
        self._initialize_tracer()

    def _initialize_tracer(self):
        """Initialize OpikTracer for ADK."""
        if not HAS_ADK_INTEGRATION:
            logger.warning("opik.integrations.adk not available")
            return
            
        try:
            self._opik_tracer = OpikTracer(
                name=self.agent_config.agent_name,
                tags=["adk", self.agent_config.agent_name],
                metadata={
                    "agent_name": self.agent_config.agent_name,
                    "engine": "adk"
                }
            )
            logger.info(f"OpikTracer initialized for {self.agent_config.agent_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize OpikTracer: {e}")

    # ADK Callback implementations - delegate to OpikTracer
    def before_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        if self._opik_tracer:
            try:
                self._opik_tracer.before_agent_callback(callback_context, **kwargs)
            except Exception as e:
                logger.debug(f"before_agent_callback error: {e}")

    def after_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        if self._opik_tracer:
            try:
                self._opik_tracer.after_agent_callback(callback_context, **kwargs)
            except Exception as e:
                logger.debug(f"after_agent_callback error: {e}")

    def before_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        if self._opik_tracer:
            try:
                self._opik_tracer.before_model_callback(callback_context, **kwargs)
            except Exception as e:
                logger.debug(f"before_model_callback error: {e}")

    def after_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Capture token usage from llm_response after model call."""
        if not self._opik_tracer:
            return
        
        try:
            # Extract token usage from llm_response
            llm_response = kwargs.get('llm_response')
            if llm_response and hasattr(llm_response, 'usage_metadata'):
                usage = llm_response.usage_metadata
                # Handle both OpenAI format (LiteLLM) and Google format
                prompt_tokens = (
                    getattr(usage, 'prompt_tokens', 0) or 
                    getattr(usage, 'prompt_token_count', 0) or 0
                )
                completion_tokens = (
                    getattr(usage, 'completion_tokens', 0) or 
                    getattr(usage, 'candidates_token_count', 0) or 0
                )
                total_tokens = (
                    getattr(usage, 'total_tokens', 0) or 
                    getattr(usage, 'total_token_count', 0) or 
                    prompt_tokens + completion_tokens
                )
                
                logger.debug(f"Token usage - prompt: {prompt_tokens}, completion: {completion_tokens}, total: {total_tokens}")
                
                # Update the current span with usage info
                try:
                    import opik
                    current_span = opik.get_current_span()
                    if current_span:
                        current_span.update(
                            usage={
                                "prompt_tokens": prompt_tokens,
                                "completion_tokens": completion_tokens,
                                "total_tokens": total_tokens,
                            }
                        )
                        logger.debug(f"Updated span with token usage")
                except Exception as span_e:
                    logger.debug(f"Failed to update span with usage: {span_e}")
            
            # Call OpikTracer's after_model_callback (it may handle span ending)
            try:
                self._opik_tracer.after_model_callback(callback_context, **kwargs)
            except Exception as e:
                logger.debug(f"OpikTracer after_model_callback error (expected for token format): {e}")
                
        except Exception as e:
            logger.debug(f"after_model_callback error: {e}")

    def before_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        if self._opik_tracer:
            try:
                self._opik_tracer.before_tool_callback(callback_context, **kwargs)
            except Exception as e:
                logger.debug(f"before_tool_callback error: {e}")

    def after_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        if self._opik_tracer:
            try:
                self._opik_tracer.after_tool_callback(callback_context, **kwargs)
            except Exception as e:
                logger.debug(f"after_tool_callback error: {e}")

    @property
    def opik_tracer(self) -> Optional[Any]:
        """Access underlying OpikTracer for track_adk_agent_recursive."""
        return self._opik_tracer

    # Decorator methods - fallback to @track if needed
    def trace_agent_execution(self, trace_name: str = None):
        """Not used by ADK - callbacks handle tracing."""
        def decorator(func):
            return func
        return decorator

    def trace_tool_execution(self, tool_name: str):
        """Not used by ADK - callbacks handle tracing."""
        def decorator(func):
            return func
        return decorator

    def trace_llm_call(self, model_name: str):
        """Not used by ADK - callbacks handle tracing."""
        def decorator(func):
            return func
        return decorator
