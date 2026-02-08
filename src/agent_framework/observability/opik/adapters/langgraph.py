"""LangGraph Opik Adapter - Uses callback-based tracing like ADK.

Follows the standard observer callback pattern:
- Standard callback interface (before_agent_callback, after_agent_callback, etc.)
- Opik client for trace/span management (compatible with older versions)
- Manual LLM span creation for LiteLLM calls
- Thread tracking via context variables
"""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Optional, Callable
from functools import wraps

try:
    import opik
    from opik import Opik, track
    HAS_OPIK = True
except ImportError:
    HAS_OPIK = False
    opik = None
    Opik = None

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.observability.opik.base_opik_observer import BaseOpikObserver

logger = logging.getLogger(__name__)

# Context variables for LangGraph thread and trace tracking
_thread_id: ContextVar[Optional[str]] = ContextVar('langgraph_thread_id', default=None)
_parent_trace: ContextVar[Optional[Any]] = ContextVar('langgraph_parent_trace', default=None)


class LangGraphOpikObserver(BaseOpikObserver):
    """Opik observer for LangGraph using callback-based tracing.

    Features:
    - Standard callback interface (before_agent_callback, after_agent_callback, etc.)
    - Uses Opik client for trace/span management
    - Manual LLM span creation for LiteLLM calls
    - Thread tracking via context variables
    - Proper span nesting: trace -> llm_span/tool_span
    """

    def __init__(self, agent_config: AgentConfig):
        super().__init__(agent_config)
        self._opik_client: Optional[Any] = None
        self._active_traces: Dict[str, Any] = {}  # session_id -> trace object
        self._active_spans: Dict[str, Any] = {}   # span_key -> span object
        self._span_start_times: Dict[str, float] = {}  # span_key -> start time
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Opik client."""
        if not HAS_OPIK or Opik is None:
            logger.warning("Opik not available")
            return

        try:
            self._opik_client = Opik()
            logger.info(f"Opik client initialized for {self.agent_config.agent_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize Opik client: {e}")

    def get_litellm_metadata(self) -> Dict[str, Any]:
        """Get metadata for LiteLLM calls including thread context."""
        metadata = {
            "agent_name": self.agent_config.agent_name,
            "engine": "langgraph",
        }
        thread_id = _thread_id.get()
        if thread_id:
            metadata["thread_id"] = thread_id
        return metadata

    @contextmanager
    def thread(self, thread_id: str):
        """Start a conversation thread. All traces inside belong to this thread."""
        token = _thread_id.set(thread_id)
        try:
            logger.debug(f"Started LangGraph thread: {thread_id}")
            yield
        finally:
            _thread_id.reset(token)
            logger.debug(f"Ended LangGraph thread: {thread_id}")

    # =========================================================================
    # Standard Callback Interface - Uses Opik client
    # =========================================================================

    def before_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called before agent execution - starts a trace or span (for sub-agents)."""
        if not HAS_OPIK or self._opik_client is None:
            return

        context = callback_context or {}
        session_id = context.get('session_id', 'default')
        query = context.get('query', '')
        thread_id = context.get('thread_id') or _thread_id.get()

        try:
            # Check if there's a parent trace (we're a sub-agent)
            parent_trace = _parent_trace.get()

            if parent_trace is not None:
                # We're a sub-agent - create a span under the parent trace
                agent_name = self.agent_config.agent_name or "unknown_agent"
                span_key = f"{session_id}:agent:{agent_name}"

                # Build descriptive input
                span_input = {
                    "query": query if query else "(delegated task)",
                }

                span = parent_trace.span(
                    name=f"Sub-Agent: {agent_name}",
                    type="general",  # Use "general" type for better Opik display
                    input=span_input,
                    metadata={
                        "agent_name": agent_name,
                        "engine": "langgraph",
                        "session_id": session_id,
                        "span_type": "sub_agent",
                    },
                    tags=["sub-agent", agent_name, "langgraph"],
                )

                # Store as a span (not a trace)
                self._active_spans[span_key] = span

                # Also store reference so LLM/tool spans can attach to this sub-agent span
                self._active_traces[session_id] = span

                logger.info(f"Started Opik sub-agent span for {self.agent_config.agent_name}")
            else:
                # We're the root agent - create a new trace
                trace_name = f"Agent: {self.agent_config.agent_name}"

                # Build descriptive input
                trace_input = {
                    "query": query if query else "(no query)",
                    "session_id": session_id,
                }
                if thread_id:
                    trace_input["thread_id"] = thread_id

                trace = self._opik_client.trace(
                    name=trace_name,
                    input=trace_input,
                    metadata={
                        "agent_name": self.agent_config.agent_name,
                        "engine": "langgraph",
                        "session_id": session_id,
                        "thread_id": thread_id,
                    },
                    tags=["langgraph", self.agent_config.agent_name],
                )

                # Store for cleanup in after_agent_callback
                self._active_traces[session_id] = trace

                # Set as parent trace for sub-agents
                _parent_trace.set(trace)

                # Set thread context variable so nested calls can access it
                if thread_id:
                    _thread_id.set(thread_id)

                logger.info(f"Started Opik trace for session={session_id}, thread_id={thread_id}")
        except Exception as e:
            logger.warning(f"Failed to start agent trace: {e}")

    def after_agent_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called after agent execution - ends the trace or span (for sub-agents)."""
        if not HAS_OPIK or self._opik_client is None:
            return

        context = callback_context or {}
        session_id = context.get('session_id', 'default')
        result = context.get('result', '')

        try:
            # Check if this is a sub-agent (span)
            span_key = f"{session_id}:agent:{self.agent_config.agent_name}"

            if span_key in self._active_spans:
                # We're a sub-agent - end the span
                span = self._active_spans.pop(span_key)

                # Also remove from traces dict
                if session_id in self._active_traces:
                    self._active_traces.pop(session_id)

                # Update span with output
                span.update(
                    output={"result": result[:500] if len(result) > 500 else result} if result else None,
                )

                # Check for errors
                error = context.get('error')
                if error:
                    span.update(metadata={"error": error})

                # End the span
                span.end()
                logger.info(f"Ended Opik sub-agent span for {self.agent_config.agent_name}")

            elif session_id in self._active_traces:
                # We're the root agent - end the trace
                trace = self._active_traces.pop(session_id)

                # Update trace with output
                trace.update(
                    output={"result": result[:500] if len(result) > 500 else result} if result else None,
                )

                # Check for errors
                error = context.get('error')
                if error:
                    trace.update(metadata={"error": error})

                # End the trace
                trace.end()

                # Reset parent trace context
                _parent_trace.set(None)

                logger.info(f"Ended Opik trace for session={session_id}")
            else:
                logger.warning(f"No active trace/span found for session={session_id}")
        except Exception as e:
            logger.warning(f"Failed to end agent trace: {e}")

    def _extract_last_user_message(self, messages: list) -> str:
        """Extract the last user message from messages list for display."""
        if not messages:
            return ""
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get('role') == 'user':
                content = msg.get('content', '')
                return content[:500] if len(content) > 500 else content
        return ""

    def before_node_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called before a LangGraph node execution - no-op, using flat structure."""
        pass

    def after_node_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called after a LangGraph node execution - no-op, using flat structure."""
        pass

    def before_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called before LLM call - creates an LLM span under the trace."""
        if not HAS_OPIK:
            return

        context = callback_context or {}
        session_id = context.get('session_id', 'default')
        model_name = context.get('model', 'unknown_model')
        messages = context.get('messages', [])
        provider = context.get('provider', 'unknown')
        iteration = context.get('iteration', 1)

        # Use unique key with timestamp to handle multiple LLM calls
        span_key = f"{session_id}:llm:{time.time()}"

        try:
            # Get the parent trace
            trace = self._active_traces.get(session_id)
            if trace is None:
                logger.debug(f"No active trace for LLM span: {model_name}")
                return

            # Record start time for duration calculation
            self._span_start_times[span_key] = time.time()

            # Extract last user message as the prompt for better visibility
            last_user_msg = self._extract_last_user_message(messages)

            # Get short model name (e.g., "gpt-4" from "openai/gpt-4")
            short_model = model_name.split('/')[-1] if '/' in model_name else model_name

            # Build descriptive input
            span_input = {
                "prompt": last_user_msg or "(continuing after tool results)",
                "messages": len(messages),
            }

            # Create a span under the trace for LLM call
            span = trace.span(
                name=f"LLM: {short_model}",
                type="llm",
                input=span_input,
                metadata={
                    "agent_name": self.agent_config.agent_name,
                    "model": model_name,
                    "provider": provider,
                    "iteration": iteration,
                },
                tags=["llm", short_model, "langgraph"],
            )

            # Store for cleanup in after_model_callback
            self._active_spans[span_key] = span
            # Also store the key in context for retrieval
            self._span_start_times[f"{session_id}:llm:current"] = span_key

            logger.debug(f"Started LLM span: {model_name}")
        except Exception as e:
            logger.warning(f"Failed to start LLM span: {e}")

    def after_model_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called after LLM call - ends the LLM span with decision and usage info."""
        if not HAS_OPIK:
            return

        context = callback_context or {}
        session_id = context.get('session_id', 'default')
        model_name = context.get('model', 'unknown_model')

        # Get the current span key
        current_key = f"{session_id}:llm:current"
        span_key = self._span_start_times.pop(current_key, None)

        try:
            if span_key and span_key in self._active_spans:
                span = self._active_spans.pop(span_key)
                self._span_start_times.pop(span_key, None)  # Clean up start time

                # Extract response content and decision
                response_content = context.get('response_content', '')
                decision = context.get('decision', 'unknown')
                tool_calls = context.get('tool_calls')

                # Extract token usage if available
                usage = context.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)
                total_tokens = usage.get('total_tokens', 0)

                # Build output with decision as the primary info
                output_data = {
                    "decision": decision,
                }

                # Add tool calls if present
                if tool_calls:
                    output_data["tools_to_call"] = tool_calls

                # Add response preview if it's a final response
                if decision == "final response" and response_content:
                    output_data["response"] = response_content[:300] if len(response_content) > 300 else response_content

                # Update span with output and usage
                update_kwargs = {
                    "output": output_data,
                }

                if total_tokens > 0:
                    update_kwargs["usage"] = {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": total_tokens,
                    }

                if context.get('error'):
                    update_kwargs["metadata"] = {"error": context.get('error')}

                span.update(**update_kwargs)

                # End the span
                span.end()
                logger.debug(f"Ended LLM span: {model_name}, decision: {decision}")
            else:
                logger.debug(f"No active LLM span found for session={session_id}")
        except Exception as e:
            logger.warning(f"Failed to end LLM span: {e}")

    def before_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called before tool execution - starts a span."""
        if not HAS_OPIK:
            return

        context = callback_context or {}
        tool_name = context.get('tool_name', 'unknown_tool')
        tool_input = context.get('tool_input', '')
        session_id = context.get('session_id', 'default')
        tool_type = context.get('tool_type', 'function')  # 'agent' or 'function'

        # Use unique key with timestamp to handle multiple calls to same tool
        span_key = f"{session_id}:tool:{tool_name}:{time.time()}"

        try:
            # Get the parent trace
            trace = self._active_traces.get(session_id)
            if trace is None:
                logger.debug(f"No active trace for tool span: {tool_name}")
                return

            # Parse tool_input if it's JSON string
            try:
                if tool_input and isinstance(tool_input, str):
                    parsed_input = json.loads(tool_input)
                else:
                    parsed_input = tool_input or {}
            except (json.JSONDecodeError, TypeError):
                parsed_input = {"raw_input": tool_input} if tool_input else {}

            # Format span name based on tool type
            if tool_type == 'agent':
                span_name = f"Agent Tool: {tool_name}"
                span_tags = ["agent-tool", tool_name, "langgraph"]
            else:
                span_name = f"Function Tool: {tool_name}"
                span_tags = ["function-tool", tool_name, "langgraph"]

            # Create a span under the trace
            span = trace.span(
                name=span_name,
                type="tool",
                input=parsed_input,
                metadata={
                    "agent_name": self.agent_config.agent_name,
                    "tool_name": tool_name,
                    "tool_type": tool_type,
                },
                tags=span_tags,
            )

            # Store for cleanup in after_tool_callback
            self._active_spans[span_key] = span
            # Store current key for retrieval
            self._span_start_times[f"{session_id}:tool:{tool_name}:current"] = span_key

            logger.debug(f"Started tool span: {tool_name}")
        except Exception as e:
            logger.warning(f"Failed to start tool span: {e}")

    def after_tool_callback(self, callback_context: Optional[Dict[str, Any]] = None, **kwargs) -> None:
        """Called after tool execution - ends the span."""
        if not HAS_OPIK:
            return

        context = callback_context or {}
        tool_name = context.get('tool_name', 'unknown_tool')
        output = context.get('output', '')
        session_id = context.get('session_id', 'default')

        # Get the current span key
        current_key = f"{session_id}:tool:{tool_name}:current"
        span_key = self._span_start_times.pop(current_key, None)

        try:
            if span_key and span_key in self._active_spans:
                span = self._active_spans.pop(span_key)

                # Parse output if it's JSON string for better display
                try:
                    if output and isinstance(output, str):
                        try:
                            parsed_output = json.loads(output)
                        except json.JSONDecodeError:
                            parsed_output = {"result": output[:500] if len(output) > 500 else output}
                    else:
                        parsed_output = {"result": str(output)[:500] if output else "(empty)"}
                except Exception:
                    parsed_output = {"result": str(output)[:500] if output else "(empty)"}

                # Update span with output
                span.update(output=parsed_output)

                # Check for errors
                error = context.get('error')
                if error:
                    span.update(metadata={"error": error})

                # End the span
                span.end()
                logger.debug(f"Ended tool span: {tool_name}")
            else:
                logger.debug(f"No active tool span found for {tool_name}")
        except Exception as e:
            logger.warning(f"Failed to end tool span: {e}")

    # =========================================================================
    # Decorator methods - for function-level tracing
    # =========================================================================

    def trace_agent_execution(self, trace_name: str = None):
        """Decorator for agent/node execution."""
        if not HAS_OPIK:
            def decorator(func: Callable) -> Callable:
                return func
            return decorator

        name = trace_name or f"{self.agent_config.agent_name}_execution"

        def decorator(func: Callable) -> Callable:
            @track(name=name, tags=['agent', self.agent_config.agent_name])
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def trace_tool_execution(self, tool_name: str):
        """Decorator for tool execution."""
        if not HAS_OPIK:
            def decorator(func: Callable) -> Callable:
                return func
            return decorator

        def decorator(func: Callable) -> Callable:
            @track(name=f"tool_{tool_name}", tags=['tool', tool_name])
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator

    def trace_llm_call(self, model_name: str):
        """Decorator for LLM calls."""
        if not HAS_OPIK:
            def decorator(func: Callable) -> Callable:
                return func
            return decorator

        def decorator(func: Callable) -> Callable:
            @track(name=f"llm_{model_name}", tags=['llm', model_name])
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
