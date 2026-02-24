"""Convert MCP tools to Google ADK: use a BaseTool subclass so the LLM gets proper parameters.

ADK's FunctionTool builds the tool declaration from the function signature. A wrapper
with **kwargs has no named parameters, so ADK excludes them and the LLM sees a tool with
no parameters and won't know how to call it. We use a custom BaseTool that builds the
declaration from the MCP tool's input_schema (JSON Schema) so the model gets real parameters.
"""

import json
import logging
from typing import Any, Dict, Optional

from google.genai import types

from src.agent_framework.mcp.models import MCPServerConfig, MCPToolInfo

logger = logging.getLogger(__name__)


# Map JSON Schema type to google.genai types (FunctionDeclaration expects these)
_JSON_TYPE_TO_GENAI = {
    "string": "STRING",
    "integer": "INTEGER",
    "number": "NUMBER",
    "boolean": "BOOLEAN",
    "array": "ARRAY",
    "object": "OBJECT",
}


def _json_schema_property_to_genai(prop: Dict[str, Any]) -> Dict[str, Any]:
    """Convert one JSON Schema property to genai Schema property format."""
    out: Dict[str, Any] = {}
    if "description" in prop:
        out["description"] = prop["description"]
    raw_type = prop.get("type", "string")
    if isinstance(raw_type, list):
        raw_type = next((t for t in raw_type if t != "null"), raw_type[0] if raw_type else "string")
    out["type"] = _JSON_TYPE_TO_GENAI.get(raw_type, "STRING")
    if raw_type == "array" and "items" in prop:
        out["items"] = _json_schema_property_to_genai(prop["items"])
    if raw_type == "object" and "properties" in prop:
        out["properties"] = {
            k: _json_schema_property_to_genai(v) for k, v in prop["properties"].items()
        }
    return out


def _mcp_input_schema_to_genai_parameters(input_schema: Dict[str, Any]) -> Optional[types.Schema]:
    """Convert MCP tool input_schema (JSON Schema) to genai types.Schema for FunctionDeclaration."""
    if not input_schema:
        return None
    props = input_schema.get("properties")
    if not props:
        return None
    properties = {k: _json_schema_property_to_genai(v) for k, v in props.items()}
    required = input_schema.get("required", list(properties.keys()))
    schema = types.Schema(type="OBJECT", properties=properties)
    schema.required = required
    return schema


def _create_mcp_adk_tool_class() -> type:
    """Build MCPAdkTool as a subclass of ADK BaseTool so Runner/Agent accept it."""
    from google.adk.tools.base_tool import BaseTool

    class MCPAdkTool(BaseTool):
        """MCP tool for ADK: declaration comes from MCP input_schema so the LLM gets parameters."""

        def __init__(self, tool_info: MCPToolInfo, server_config: MCPServerConfig) -> None:
            super().__init__(
                name=tool_info.name,
                description=tool_info.description or f"MCP tool: {tool_info.name}",
            )
            self._tool_info = tool_info
            self._server_config = server_config

        def _get_declaration(self) -> Optional[types.FunctionDeclaration]:
            params = _mcp_input_schema_to_genai_parameters(self._tool_info.input_schema)
            return types.FunctionDeclaration(
                name=self._tool_info.name,
                description=self.description,
                parameters=params,
            )

        async def run_async(self, *, args: Dict[str, Any], tool_context: Any) -> Any:
            from src.agent_framework.mcp.client_manager import MCPClientManager

            try:
                client = MCPClientManager.get_instance().get_client(self._server_config)
                # Pass empty dict for tools with no params, not None
                result = await client.call_tool(
                    self._tool_info.name, arguments=args if args is not None else {}
                )
                if result is None:
                    return ""
                if isinstance(result, (dict, list)):
                    return json.dumps(result, default=str)
                return str(result)
            except Exception as e:
                # Return error as string so ADK can include it in the conversation
                # This prevents the "missing tool response" error from OpenAI
                import traceback
                error_details = traceback.format_exc()
                error_msg = f"Error executing MCP tool '{self._tool_info.name}': {str(e)}\n{error_details}"
                logger.error(error_msg)
                # Return just the error message to the LLM, not the full traceback
                return f"Error executing tool '{self._tool_info.name}': {str(e) or 'Unknown error'}"

    return MCPAdkTool


MCPAdkTool = _create_mcp_adk_tool_class()


def to_adk_tool(tool_info: MCPToolInfo, server_config: MCPServerConfig) -> Any:
    """Wrap an MCP tool for ADK so the LLM receives name, description, and parameters.
    Client is resolved at invoke time from server_config so it uses the correct event loop.
    """
    return MCPAdkTool(tool_info, server_config)
