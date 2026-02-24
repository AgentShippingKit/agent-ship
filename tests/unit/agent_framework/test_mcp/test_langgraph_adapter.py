"""Unit tests for LangGraph MCP adapter schema extraction."""

import pytest
from pydantic import BaseModel, Field
from typing import Optional

from src.agent_framework.mcp.adapters.langgraph import _create_args_schema, to_langgraph_tool
from src.agent_framework.mcp.models import MCPServerConfig, MCPToolInfo, MCPTransport


class TestCreateArgsSchema:
    """Test dynamic Pydantic model generation from MCP tool schemas."""

    def test_creates_schema_with_required_string_field(self):
        """Test creating schema with required string parameter."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query string"
                    }
                },
                "required": ["query"]
            }
        )

        schema_class = _create_args_schema(tool_info)

        # Should create model with correct field
        assert "query" in schema_class.model_fields
        field = schema_class.model_fields["query"]
        assert field.annotation == str
        assert field.is_required()
        assert field.description == "The query string"

    def test_creates_schema_with_optional_field(self):
        """Test creating schema with optional parameter."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name field"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Result limit"
                    }
                },
                "required": ["name"]  # Only name is required
            }
        )

        schema_class = _create_args_schema(tool_info)

        # Should create model with required and optional fields
        assert "limit" in schema_class.model_fields
        assert "name" in schema_class.model_fields
        # name should be required, limit should be optional
        assert schema_class.model_fields["name"].is_required()
        assert not schema_class.model_fields["limit"].is_required()

    def test_creates_schema_with_multiple_types(self):
        """Test creating schema with different parameter types."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "count": {"type": "integer"},
                    "ratio": {"type": "number"},
                    "enabled": {"type": "boolean"},
                    "tags": {"type": "array"},
                    "metadata": {"type": "object"}
                },
                "required": ["name", "count"]
            }
        )

        schema_class = _create_args_schema(tool_info)

        # Should map all JSON Schema types to Python types
        assert schema_class.model_fields["name"].annotation == str
        assert schema_class.model_fields["count"].annotation == int
        # ratio and enabled are optional, so wrapped in Optional
        assert "enabled" in schema_class.model_fields
        assert "tags" in schema_class.model_fields
        assert "metadata" in schema_class.model_fields

    def test_treats_all_as_required_when_no_required_list(self):
        """Test that all properties are required when 'required' array is missing."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                }
                # No 'required' array
            }
        )

        schema_class = _create_args_schema(tool_info)

        # Both should be required
        assert schema_class.model_fields["param1"].is_required()
        assert schema_class.model_fields["param2"].is_required()

    def test_creates_generic_schema_when_no_properties(self):
        """Test fallback to generic schema when no properties defined."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test tool",
            input_schema={}  # No properties
        )

        schema_class = _create_args_schema(tool_info)

        # Should create model that accepts extra fields
        assert schema_class.__name__ == "test_tool_Args"

    def test_creates_generic_schema_when_empty(self):
        """Test fallback when input_schema has no properties."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test tool",
            input_schema={"type": "object"}  # Valid but empty
        )

        schema_class = _create_args_schema(tool_info)

        # Should create generic model
        assert schema_class.__name__ == "test_tool_Args"

    def test_handles_schema_creation_errors(self):
        """Test that errors in schema creation fall back to generic schema."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test tool",
            input_schema={
                "type": "object",
                "properties": {
                    "invalid": {
                        "type": "unknown_type"  # Invalid type
                    }
                },
                "required": ["invalid"]
            }
        )

        # Should not raise, but create generic schema
        schema_class = _create_args_schema(tool_info)
        assert schema_class.__name__ == "test_tool_Args"

    def test_preserves_field_descriptions(self):
        """Test that field descriptions are preserved in schema."""
        tool_info = MCPToolInfo(
            name="query_tool",
            description="Query tool",
            input_schema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["sql"]
            }
        )

        schema_class = _create_args_schema(tool_info)

        # Description should be in field
        field = schema_class.model_fields["sql"]
        assert field.description == "The SQL query to execute"

    def test_creates_unique_model_names(self):
        """Test that different tools get different model names."""
        tool1 = MCPToolInfo(name="tool1", description="First", input_schema={})
        tool2 = MCPToolInfo(name="tool2", description="Second", input_schema={})

        schema1 = _create_args_schema(tool1)
        schema2 = _create_args_schema(tool2)

        # Should have different names
        assert schema1.__name__ == "tool1_Args"
        assert schema2.__name__ == "tool2_Args"
        assert schema1 is not schema2


class TestToLanggraphTool:
    """Test conversion of MCP tool to LangGraph StructuredTool."""

    @pytest.fixture
    def server_config(self):
        """Create test server config."""
        return MCPServerConfig(
            id="test_server",
            transport=MCPTransport.STDIO,
            command=["echo", "test"]
        )

    def test_creates_structured_tool_with_schema(self, server_config):
        """Test that to_langgraph_tool creates StructuredTool with proper schema."""
        tool_info = MCPToolInfo(
            name="query",
            description="Execute SQL query",
            input_schema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query"
                    }
                },
                "required": ["sql"]
            }
        )

        tool = to_langgraph_tool(tool_info, server_config)

        # Should create StructuredTool
        assert tool.name == "query"
        assert tool.description == "Execute SQL query"

        # Should have args_schema with correct fields
        assert hasattr(tool, 'args_schema')
        assert "sql" in tool.args_schema.model_fields

    def test_uses_default_description_when_none(self, server_config):
        """Test that tool uses default description when not provided."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description=None,
            input_schema={}
        )

        tool = to_langgraph_tool(tool_info, server_config)

        # Should have default description
        assert "MCP tool: test_tool" in tool.description

    def test_tool_name_matches_mcp_tool(self, server_config):
        """Test that LangChain tool name matches MCP tool name."""
        tool_info = MCPToolInfo(
            name="my_custom_tool",
            description="Custom tool",
            input_schema={}
        )

        tool = to_langgraph_tool(tool_info, server_config)

        # Name should match exactly
        assert tool.name == "my_custom_tool"

    @pytest.mark.asyncio
    async def test_tool_function_is_async(self, server_config):
        """Test that created tool has async coroutine."""
        tool_info = MCPToolInfo(
            name="test_tool",
            description="Test",
            input_schema={}
        )

        tool = to_langgraph_tool(tool_info, server_config)

        # Should have coroutine
        assert tool.coroutine is not None
        assert callable(tool.coroutine)
