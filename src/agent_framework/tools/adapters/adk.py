"""ADK Tool Adapter - Converts Universal Tools to ADK Format

This adapter provides the conversion logic for transforming universal tools
into ADK-specific FunctionTool and AgentTool instances.
"""

from typing import Any
import asyncio
import logging

from src.agent_framework.tools.universal_tool import UniversalTool

logger = logging.getLogger(__name__)


class ADKToolAdapter:
    """Adapter for converting Universal Tools to ADK format."""
    
    @staticmethod
    def convert(universal_tool: UniversalTool) -> Any:
        """Convert a universal tool to ADK format.
        
        Args:
            universal_tool: The universal tool to convert
            
        Returns:
            ADK FunctionTool or AgentTool instance
        """
        try:
            from google.adk.tools import FunctionTool, AgentTool
        except ImportError as e:
            logger.error(f"Failed to import ADK tools: {e}")
            raise ImportError("ADK is not installed. Install with: pip install google-adk")
        
        if universal_tool.tool_type == "agent":
            return ADKToolAdapter._convert_agent_tool(universal_tool)
        else:
            return ADKToolAdapter._convert_function_tool(universal_tool)
    
    @staticmethod
    def _convert_function_tool(universal_tool: UniversalTool) -> Any:
        """Convert a universal function tool to ADK FunctionTool.
        
        Args:
            universal_tool: The universal function tool
            
        Returns:
            ADK FunctionTool instance
        """
        from google.adk.tools import FunctionTool
        
        if universal_tool.coroutine:
            # ADK doesn't support async directly, create a sync wrapper
            def sync_wrapper(**kwargs):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(universal_tool.coroutine(**kwargs))
                finally:
                    loop.close()
            
            return FunctionTool(sync_wrapper)
        else:
            return FunctionTool(universal_tool.func)
    
    @staticmethod
    def _convert_agent_tool(universal_tool: UniversalTool) -> Any:
        """Convert a universal agent tool to ADK AgentTool.
        
        Args:
            universal_tool: The universal agent tool
            
        Returns:
            ADK AgentTool instance
        """
        from google.adk.tools import AgentTool
        
        if not hasattr(universal_tool, 'agent_instance'):
            raise ValueError("Agent tools require agent_instance attribute")
        
        return AgentTool(universal_tool.agent_instance)
