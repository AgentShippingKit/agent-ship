"""Automatic tool documentation generator for system prompts.

This module generates formatted tool documentation from tool schemas,
ensuring the LLM always has accurate, up-to-date information about available tools.
"""

import json
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ToolDocumentationGenerator:
    """Generates formatted tool documentation for system prompts.

    This ensures tool schemas are the single source of truth for documentation,
    preventing stale or incorrect tool descriptions in prompts.
    """

    @staticmethod
    def generate_tool_docs(tools: List[Any], engine_type: str = "adk") -> str:
        """Generate formatted tool documentation from tool schemas.

        Args:
            tools: List of tools (ADK tools, LangGraph tools, etc.)
            engine_type: Engine type ("adk" or "langgraph") for schema extraction

        Returns:
            Formatted markdown documentation string
        """
        if not tools:
            return "No tools available."

        docs = []
        docs.append("## Available Tools")
        docs.append("")
        docs.append("You have access to the following tools. Always use the exact parameter names shown:")
        docs.append("")

        for tool in tools:
            try:
                tool_doc = ToolDocumentationGenerator._generate_single_tool_doc(
                    tool, engine_type
                )
                if tool_doc:
                    docs.append(tool_doc)
                    docs.append("")
            except Exception as e:
                logger.warning(f"Failed to generate docs for tool: {e}")

        return "\n".join(docs)

    @staticmethod
    def _generate_single_tool_doc(tool: Any, engine_type: str) -> Optional[str]:
        """Generate documentation for a single tool.

        Args:
            tool: Tool instance
            engine_type: Engine type for schema extraction

        Returns:
            Formatted tool documentation or None if extraction fails
        """
        # Extract tool metadata
        name = ToolDocumentationGenerator._get_tool_name(tool, engine_type)
        description = ToolDocumentationGenerator._get_tool_description(tool, engine_type)
        parameters = ToolDocumentationGenerator._get_tool_parameters(tool, engine_type)

        if not name:
            return None

        # Format documentation
        lines = [f"### {name}"]

        if description:
            lines.append(f"**Description:** {description}")

        if parameters:
            lines.append("**Parameters:**")

            # Check if there are required parameters
            required_params = parameters.get("required", [])
            props = parameters.get("properties", {})

            if not props:
                lines.append("- No parameters required")
            else:
                for param_name, param_schema in props.items():
                    param_type = param_schema.get("type", "unknown")
                    param_desc = param_schema.get("description", "")
                    required = "**required**" if param_name in required_params else "optional"

                    param_doc = f"- `{param_name}` ({param_type}, {required})"
                    if param_desc:
                        param_doc += f": {param_desc}"
                    lines.append(param_doc)

            # Add usage example
            lines.append("")
            lines.append("**Example:**")
            example = ToolDocumentationGenerator._generate_example_call(
                name, props, required_params
            )
            lines.append(f"```json\n{example}\n```")
        else:
            lines.append("**Parameters:** None")

        return "\n".join(lines)

    @staticmethod
    def _get_tool_name(tool: Any, engine_type: str) -> Optional[str]:
        """Extract tool name."""
        if hasattr(tool, "name"):
            return tool.name
        if hasattr(tool, "__name__"):
            return tool.__name__
        return None

    @staticmethod
    def _get_tool_description(tool: Any, engine_type: str) -> Optional[str]:
        """Extract tool description."""
        if hasattr(tool, "description"):
            return tool.description
        if hasattr(tool, "__doc__"):
            return tool.__doc__
        return None

    @staticmethod
    def _get_tool_parameters(tool: Any, engine_type: str) -> Optional[Dict]:
        """Extract tool parameter schema.

        Returns JSON Schema-style parameter definition.
        """
        if engine_type == "adk":
            # ADK tools have _get_declaration() method
            if hasattr(tool, "_get_declaration"):
                try:
                    declaration = tool._get_declaration()
                    if declaration and hasattr(declaration, "parameters"):
                        params = declaration.parameters

                        # Convert genai Schema to JSON Schema format
                        if params:
                            result = {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }

                            if hasattr(params, "properties"):
                                for prop_name, prop_schema in params.properties.items():
                                    result["properties"][prop_name] = {
                                        "type": prop_schema.type.lower() if hasattr(prop_schema, "type") else "string",
                                        "description": prop_schema.description if hasattr(prop_schema, "description") else ""
                                    }

                            if hasattr(params, "required"):
                                result["required"] = list(params.required) if params.required else []

                            return result
                except Exception as e:
                    logger.debug(f"Failed to extract ADK tool parameters: {e}")

        elif engine_type == "langgraph":
            # LangGraph tools have args_schema
            if hasattr(tool, "args_schema"):
                try:
                    schema = tool.args_schema
                    if schema and hasattr(schema, "schema"):
                        return schema.schema()
                except Exception as e:
                    logger.debug(f"Failed to extract LangGraph tool parameters: {e}")

        return None

    @staticmethod
    def _generate_example_call(name: str, properties: Dict, required: List[str]) -> str:
        """Generate example tool call JSON.

        Args:
            name: Tool name
            properties: Parameter properties
            required: Required parameter names

        Returns:
            Formatted JSON example
        """
        example_args = {}

        for param_name, param_schema in properties.items():
            param_type = param_schema.get("type", "string")

            # Generate example value based on type
            if param_type == "string":
                example_args[param_name] = f"<{param_name}_value>"
            elif param_type == "integer":
                example_args[param_name] = 123
            elif param_type == "boolean":
                example_args[param_name] = True
            elif param_type == "array":
                example_args[param_name] = []
            elif param_type == "object":
                example_args[param_name] = {}
            else:
                example_args[param_name] = f"<{param_name}>"

        return json.dumps(example_args, indent=2)


class PromptBuilder:
    """Builds system prompts with automatic tool documentation injection."""

    @staticmethod
    def build_system_prompt(
        base_instruction: str,
        tools: List[Any],
        engine_type: str = "adk"
    ) -> str:
        """Build final system prompt with tool documentation.

        Args:
            base_instruction: Base instruction template from agent config
            tools: List of available tools
            engine_type: Engine type for tool schema extraction

        Returns:
            Complete system prompt with tool documentation
        """
        if not tools:
            return base_instruction

        # Generate tool documentation
        tool_docs = ToolDocumentationGenerator.generate_tool_docs(tools, engine_type)

        # Inject tool documentation into prompt
        # Add a separator and append tool docs
        separator = "\n\n" + "=" * 80 + "\n"
        return f"{base_instruction}{separator}{tool_docs}"
