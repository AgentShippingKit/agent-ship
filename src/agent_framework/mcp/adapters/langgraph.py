"""Convert MCP tools to LangChain StructuredTool with proper schema extraction."""

import json
import logging
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, create_model, Field

from src.agent_framework.mcp.models import MCPServerConfig, MCPToolInfo

logger = logging.getLogger(__name__)


def _create_args_schema(tool_info: MCPToolInfo) -> Type[BaseModel]:
    """Create a Pydantic model from MCP tool's input schema for LangChain.

    All fields are Optional — our wrapper's job is giving the LLM correct type
    hints, not enforcing the MCP server's own input validation. LLMs legitimately
    omit fields that have server-side defaults (e.g. Notion's sort/filter), and
    a Pydantic required-field error would kill the call before it reaches the server.
    """
    from pydantic import ConfigDict

    input_schema = tool_info.input_schema or {}
    properties = input_schema.get("properties", {})

    if not properties:
        return create_model(
            f"{tool_info.name}_Args",
            __config__=type("C", (), {"extra": "allow"})
        )

    field_definitions: Dict[str, Any] = {}

    for prop_name, prop_schema in properties.items():
        prop_type = prop_schema.get("type", "string")
        prop_desc = prop_schema.get("description", "")

        python_type: Any = str
        if prop_type == "integer":
            python_type = int
        elif prop_type == "number":
            python_type = float
        elif prop_type == "boolean":
            python_type = bool
        elif prop_type == "array":
            python_type = list
        elif prop_type == "object":
            python_type = dict

        # Always Optional — the MCP server handles its own required-field checks.
        # This prevents Pydantic from rejecting LLM calls that omit server-defaulted fields.
        field_definitions[prop_name] = (
            Optional[python_type],
            Field(None, description=prop_desc)
        )

    try:
        model = create_model(f"{tool_info.name}_Args", **field_definitions)
        model.model_config = ConfigDict(extra="allow")
        return model
    except Exception as e:
        logger.warning("Failed to create args schema for %s: %s", tool_info.name, e)
        return create_model(
            f"{tool_info.name}_Args",
            __config__=type("C", (), {"extra": "allow"})
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
        # Strip None values — optional fields not provided by the LLM should be
        # omitted entirely so the MCP server applies its own defaults.
        args = {k: v for k, v in kwargs.items() if v is not None}
        result = await client.call_tool(name, arguments=args)
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
