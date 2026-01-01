"""Input/output helpers for BaseAgent."""

import json
import logging
from typing import Type

from pydantic import BaseModel

from src.models.base_models import AgentChatRequest

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


def parse_agent_response(output_schema: Type[BaseModel], result) -> BaseModel:
    """Parse the ADK event into an `output_schema` instance or a raw value.

    This mirrors the previous `_parse_agent_response` logic.
    """

    logger.debug("Parsing agent response: %s", result)
    if not (result and hasattr(result, "content") and result.content and result.content.parts):
        logger.error("No valid content found in the response")
        return None

    content_text = result.content.parts[0].text

    try:
        logger.debug("Parsing agent response text: %s", content_text)
        parsed_data = json.loads(content_text)
        logger.debug("Parsed data: %s", parsed_data)
        return output_schema(**parsed_data)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.error("Failed to parse output: %s", exc)
        # Fallback: return the raw content
        return content_text
