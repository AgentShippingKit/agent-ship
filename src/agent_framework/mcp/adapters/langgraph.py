"""Convert MCP tools to LangChain StructuredTool with proper schema extraction."""

import json
import logging
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, create_model, Field

from src.agent_framework.mcp.models import MCPServerConfig, MCPToolInfo

logger = logging.getLogger(__name__)


def _create_args_schema(tool_info: MCPToolInfo) -> Type[BaseModel]:
    """Create a Pydantic model from MCP tool's input schema for LangChain.

    This ensures the LLM sees the correct parameter names and types,
    making tool calls more accurate.
    """
    input_schema = tool_info.input_schema or {}
    properties = input_schema.get("properties", {})
    required = set(input_schema.get("required", []))

    # If no required list but has properties, treat all as required
    # (MCP servers may not always specify required array)
    if not required and properties:
        required = set(properties.keys())

    if not properties:
        # No schema defined - use generic args
        return create_model(
            f"{tool_info.name}_Args",
            __config__={"extra": "allow"}
        )

    # Build field definitions from JSON Schema
    field_definitions: Dict[str, Any] = {}

    for prop_name, prop_schema in properties.items():
        # Extract field info
        prop_type = prop_schema.get("type", "string")
        prop_desc = prop_schema.get("description", "")
        is_required = prop_name in required

        # Map JSON Schema types to Python types
        python_type = str  # default
        if prop_type == "string":
            python_type = str
        elif prop_type == "integer":
            python_type = int
        elif prop_type == "number":
            python_type = float
        elif prop_type == "boolean":
            python_type = bool
        elif prop_type == "array":
            python_type = list
        elif prop_type == "object":
            python_type = dict

        # Create field with proper type and requirement
        if is_required:
            field_definitions[prop_name] = (
                python_type,
                Field(..., description=prop_desc)
            )
        else:
            field_definitions[prop_name] = (
                Optional[python_type],
                Field(None, description=prop_desc)
            )

    # Create dynamic Pydantic model
    try:
        return create_model(
            f"{tool_info.name}_Args",
            **field_definitions
        )
    except Exception as e:
        logger.warning(f"Failed to create args schema for {tool_info.name}: {e}")
        # Fallback to generic args
        return create_model(
            f"{tool_info.name}_Args",
            __config__={"extra": "allow"}
        )


def to_langgraph_tool(tool_info: MCPToolInfo, server_config: MCPServerConfig, agent_name: str = "") -> Any:
    """Wrap an MCP tool as a LangChain StructuredTool with proper schema.

    This extracts the MCP tool's input schema and creates a proper Pydantic model
    so the LLM knows exactly which parameters to pass.
    """
    from langchain_core.tools import StructuredTool

    name = tool_info.name
    description = tool_info.description or f"MCP tool: {name}"

    # Create proper args schema from MCP tool's input schema
    args_schema = _create_args_schema(tool_info)

    logger.debug(f"Created LangGraph tool '{name}' with schema fields: {list(args_schema.model_fields.keys())}")

    async def mcp_tool_fn(**kwargs: Any) -> str:
        from src.agent_framework.mcp.client_manager import MCPClientManager

        client = MCPClientManager.get_instance().get_client(server_config, owner=agent_name)
        result = await client.call_tool(name, arguments=kwargs if kwargs else {})
        if result is None:
            return ""
        if isinstance(result, (dict, list)):
            return json.dumps(result, default=str)
        return str(result)

    return StructuredTool.from_function(
        func=None,
        coroutine=mcp_tool_fn,
        name=name,
        description=description,
        args_schema=args_schema,
    )
