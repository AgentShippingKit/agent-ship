"""LangGraph Callback Handler for Observer Integration

This handler bridges LangGraph's callback system with our standard
BaseObserver interface, providing unified observability across engines.
"""

from typing import Any, Dict, Optional

try:
    from langgraph.callbacks.base import BaseCallbackHandler
except ImportError:
    # LangGraph not available - create dummy base class
    class BaseCallbackHandler:
        def __init__(self, *args, **kwargs):
            pass

from src.agent_framework.observability.base import BaseObserver


class LangGraphObserverHandler(BaseCallbackHandler):
    """LangGraph callback handler that delegates to BaseObserver."""
    
    run_inline: bool = False  # Required by LangChain callback manager
    ignore_chain: bool = False  # Required by LangChain callback manager
    ignore_llm: bool = False  # Required by LangChain callback manager
    ignore_tool: bool = False  # Required by LangChain callback manager
    raise_error: bool = True  # Required by LangChain callback manager
    
    def __init__(self, observer: BaseObserver):
        super().__init__()
        self.observer = observer
    
    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain (agent) starts execution."""
        context = {
            'query': inputs.get('input', ''),
            'session_id': kwargs.get('session_id', 'unknown'),
            'user_id': kwargs.get('user_id', 'unknown'),
            'inputs': inputs
        }
        self.observer.before_agent_callback(context)
    
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        """Called when a chain (agent) ends execution."""
        context = {
            'result': outputs.get('output', ''),
            'session_id': kwargs.get('session_id', 'unknown'),
            'outputs': outputs
        }
        self.observer.after_agent_callback(context)
    
    def on_chain_error(self, error: Exception, **kwargs) -> None:
        """Called when a chain (agent) encounters an error."""
        context = {
            'error': str(error),
            'session_id': kwargs.get('session_id', 'unknown')
        }
        self.observer.after_agent_callback(context)
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: list[str], **kwargs) -> None:
        """Called when LLM starts processing."""
        context = {
            'model_name': serialized.get('name', 'unknown_model'),
            'prompt': prompts[0] if prompts else '',
            'session_id': kwargs.get('session_id', 'unknown'),
            'prompts': prompts
        }
        self.observer.before_model_callback(context)
    
    def on_llm_end(self, response: Any, **kwargs) -> None:
        """Called when LLM finishes processing."""
        context = {
            'response': str(response),
            'session_id': kwargs.get('session_id', 'unknown')
        }
        self.observer.after_model_callback(context)
    
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        """Called when LLM encounters an error."""
        context = {
            'error': str(error),
            'session_id': kwargs.get('session_id', 'unknown')
        }
        self.observer.after_model_callback(context)
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when a tool starts execution."""
        context = {
            'tool_name': serialized.get('name', 'unknown_tool'),
            'tool_input': input_str,
            'session_id': kwargs.get('session_id', 'unknown')
        }
        self.observer.before_tool_callback(context)
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool finishes execution."""
        context = {
            'output': output,
            'session_id': kwargs.get('session_id', 'unknown')
        }
        self.observer.after_tool_callback(context)
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Called when a tool encounters an error."""
        context = {
            'error': str(error),
            'session_id': kwargs.get('session_id', 'unknown')
        }
        self.observer.after_tool_callback(context)


def create_langgraph_callback_config(observer: BaseObserver) -> Dict[str, Any]:
    """Create LangGraph callback configuration for an observer.
    
    Args:
        observer: BaseObserver instance
        
    Returns:
        Dictionary suitable for LangGraph's config parameter
    """
    return {
        "callbacks": [LangGraphObserverHandler(observer)],
        "recursion_limit": 50,  # Default recursion limit
        "tags": ["observability"]  # Tag for filtering traces
    }
