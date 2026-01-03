"""Input/output helpers for BaseAgent."""

import json
import logging
from typing import Type

from pydantic import BaseModel

from src.service.models.base_models import AgentChatRequest

logger = logging.getLogger(__name__)


def create_input_from_request(input_schema: Type[BaseModel], request: AgentChatRequest) -> BaseModel:
    """Default logic for turning an `AgentChatRequest` into an input schema.

    Behaviour is unchanged from the previous BaseAgent implementation:
    - If `query` is a dict, try to unpack as kwargs into the schema.
    - Otherwise, try `text` field.
    - Otherwise, try first field.
    - Finally, fall back to passing the raw query.
    """

    query = request.query

    # If query is a dict, try to use it as kwargs
    if isinstance(query, dict):
        try:
            return input_schema(**query)
        except (TypeError, ValueError) as exc:
            logger.warning("Failed to create input from dict, trying with 'text' field: %s", exc)
            if hasattr(input_schema, "model_fields") and "text" in input_schema.model_fields:
                return input_schema(text=str(query))

    # If query is a string or other type, try 'text' field first
    if hasattr(input_schema, "model_fields"):
        if "text" in input_schema.model_fields:
            return input_schema(text=str(query))
        fields = list(input_schema.model_fields.keys())
        if fields:
            return input_schema(**{fields[0]: query})

    # Last resort: try to pass query directly
    return input_schema(query) if query else input_schema()


def build_schema_prompt(output_schema: Type[BaseModel]) -> str:
    """Build a system prompt addition that enforces the output schema.
    
    Args:
        output_schema: The Pydantic model to generate schema for.
        
    Returns:
        String containing the schema instruction and JSON example.
    """
    try:
        # Generate JSON schema
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)
        
        return f"""
## Output Format
You MUST respond with a valid JSON object matching this schema:
```json
{schema_json}
```
"""
    except Exception as e:
        logger.warning(f"Failed to build schema prompt: {e}")
        return ""


def parse_agent_response(output_schema: Type[BaseModel], result) -> BaseModel:
    """Parse agent response into an `output_schema` instance.
    
    Handles:
    - ADK Event objects
    - Standard dict/string responses
    - Markdown code block stripping
    """
    logger.info("Parsing agent response: %s", str(result)[:200])
    
    content_text = ""
    
    # 1. Extract text content from result
    if hasattr(result, "content") and result.content and hasattr(result.content, "parts"):
        # Handle ADK/LangGraph event object
        if result.content.parts:
            content_text = result.content.parts[0].text
            logger.info("Extracted content from parts: %s", content_text[:100])
    elif isinstance(result, str):
        content_text = result
        logger.info("Using string content: %s", content_text[:100])
    elif isinstance(result, dict):
        # If it's already a dict, try to validate directly
        try:
            return output_schema(**result)
        except Exception as e:
            logger.warning(f"Result was dict but failed validation: {e}")
            content_text = json.dumps(result)
            
    if not content_text:
        logger.error("No valid content found in the response")
        return None

    # 2. Clean up markdown code blocks if present
    content_text = content_text.strip()
    if content_text.startswith("```json"):
        content_text = content_text[7:]
    elif content_text.startswith("```"):
        content_text = content_text[3:]
    
    if content_text.endswith("```"):
        content_text = content_text[:-3]
        
    content_text = content_text.strip()

    # 3. Parse JSON and Validate
    try:
        logger.debug("Parsing cleaned response text: %s", content_text)
        parsed_data = json.loads(content_text)
        logger.debug("Parsed data: %s", parsed_data)
        return output_schema(**parsed_data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.error("Failed to parse output: %s", exc)
        # Fallback: Try to handle single field output if schema has only one field 'text' or similar
        # This is legacy behavior support
        if hasattr(output_schema, "model_fields") and len(output_schema.model_fields) == 1:
             field_name = list(output_schema.model_fields.keys())[0]
             try:
                 return output_schema(**{field_name: content_text})
             except:
                 pass
                 
        # Return raw content if it's a simple type, otherwise return None or raise
        return content_text
