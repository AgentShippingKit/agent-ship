"""Response parsing module for BaseAgent."""

import logging
from typing import Any, Dict, Optional
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)


class ResponseParser:
    """Handles parsing and formatting of agent responses."""
    
    def __init__(self, model: LiteLlm):
        """Initialize the response parser.
        
        Args:
            model: The LLM model instance
        """
        self.model = model
        
    def parse_response(self, response: Any) -> Dict[str, Any]:
        """Parse the response from the model.
        
        Args:
            response: The response from the model
            
        Returns:
            Parsed response dictionary
        """
        logger.info(f"Parsing response: {response}")
        
        # Handle different response types
        if isinstance(response, dict):
            return response
        elif isinstance(response, str):
            return {"content": response}
        else:
            return {"content": str(response)}
    
    def format_response(self, parsed_response: Dict[str, Any]) -> str:
        """Format the parsed response for output.
        
        Args:
            parsed_response: The parsed response dictionary
            
        Returns:
            Formatted response string
        """
        logger.info(f"Formatting response: {parsed_response}")
        
        if "content" in parsed_response:
            return str(parsed_response["content"])
        else:
            return str(parsed_response)
    
    def extract_metadata(self, response: Any) -> Optional[Dict[str, Any]]:
        """Extract metadata from the response.
        
        Args:
            response: The response from the model
            
        Returns:
            Metadata dictionary or None
        """
        logger.info(f"Extracting metadata from response: {response}")
        
        if isinstance(response, dict) and "metadata" in response:
            return response["metadata"]
        return None
