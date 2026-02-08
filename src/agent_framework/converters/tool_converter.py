"""Tool Converter - Converts tools between different formats.

This converter handles the transformation of tools between universal format
and engine-specific formats (ADK, LangGraph).
"""

from typing import Any, Dict, List, Union
import logging

from src.agent_framework.tools.universal_tool import UniversalTool
from src.agent_framework.tools.adapters.adk import ADKToolAdapter
from src.agent_framework.tools.adapters.langgraph import LangGraphToolAdapter
from .base_converter import BaseConverter, ConversionError

logger = logging.getLogger(__name__)


class ToolConverter(BaseConverter[UniversalTool, Any]):
    """Converter for transforming universal tools to engine-specific formats."""
    
    def __init__(self, engine_type: str):
        """Initialize the tool converter for a specific engine.
        
        Args:
            engine_type: Target engine type ("adk" or "langgraph")
        """
        self.engine_type = engine_type.lower()
        
        if self.engine_type == "adk":
            self.adapter = ADKToolAdapter()
        elif self.engine_type == "langgraph":
            self.adapter = LangGraphToolAdapter()
        else:
            raise ValueError(f"Unsupported engine type: {engine_type}")
    
    def convert(self, data: UniversalTool) -> Any:
        """Convert a universal tool to engine-specific format.
        
        Args:
            data: The universal tool to convert
            
        Returns:
            Engine-specific tool instance
            
        Raises:
            ConversionError: If conversion fails
        """
        try:
            if not self.can_convert(data):
                raise ConversionError(f"Cannot convert {type(data)} to {self.engine_type} format")
            
            logger.debug(f"Converting tool {data.name} to {self.engine_type} format")
            return self.adapter.convert(data)
            
        except Exception as e:
            logger.error(f"Failed to convert tool {data.name}: {e}")
            raise ConversionError(f"Tool conversion failed: {e}")
    
    def can_convert(self, data: Any) -> bool:
        """Check if the data can be converted.
        
        Args:
            data: The data to check
            
        Returns:
            True if data is a UniversalTool, False otherwise
        """
        return isinstance(data, UniversalTool)
    
    def convert_batch(self, tools: List[UniversalTool]) -> List[Any]:
        """Convert multiple tools to engine-specific format.
        
        Args:
            tools: List of universal tools to convert
            
        Returns:
            List of engine-specific tool instances
        """
        converted_tools = []
        for tool in tools:
            try:
                converted_tools.append(self.convert(tool))
            except ConversionError as e:
                logger.warning(f"Skipping tool {tool.name} due to conversion error: {e}")
                continue
        
        return converted_tools
