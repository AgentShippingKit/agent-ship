"""LangGraph Tool Adapter - Converts Universal Tools to LangGraph Format

This adapter provides the conversion logic for transforming universal tools
into LangGraph-specific StructuredTool instances.
"""

from typing import Any
import logging

from src.agent_framework.tools.universal_tool import UniversalTool

logger = logging.getLogger(__name__)


class LangGraphToolAdapter:
    """Adapter for converting Universal Tools to LangGraph format."""
    
    @staticmethod
    def convert(universal_tool: UniversalTool) -> Any:
        """Convert a universal tool to LangGraph format.
        
        Args:
            universal_tool: The universal tool to convert
            
        Returns:
            LangGraph StructuredTool instance
        """
        try:
            from langchain_core.tools import StructuredTool
        except ImportError as e:
            logger.error(f"Failed to import LangGraph tools: {e}")
            raise ImportError("LangChain is not installed. Install with: pip install langchain-core")
        
        return StructuredTool.from_function(
            func=None,
            coroutine=universal_tool.coroutine or universal_tool.func,
            name=universal_tool.name,
            description=universal_tool.description,
            args_schema=universal_tool.input_schema,
        )
