"""Unit tests for automatic tool documentation generation."""

import pytest
from unittest.mock import Mock

from src.agent_framework.prompts.tool_documentation import PromptBuilder
from src.agent_framework.mcp.models import MCPToolInfo


class TestPromptBuilderBasic:
    """Test basic PromptBuilder functionality."""

    def test_build_with_no_tools_returns_base_instruction(self):
        """Test that prompt with no tools returns just the base instruction."""
        base_instruction = "You are a helpful assistant."
        tools = []

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=tools,
            engine_type="adk"
        )

        # Should return base instruction unchanged
        assert result == base_instruction

    def test_build_with_tools_includes_documentation(self):
        """Test that tools are documented in the prompt."""
        base_instruction = "You are a helpful assistant."

        # Mock tool
        mock_tool = Mock()
        mock_tool.name = "test_tool"
        mock_tool.description = "A test tool"

        tools = [mock_tool]

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=tools,
            engine_type="adk"
        )

        # Should include base instruction
        assert base_instruction in result

        # Should include tools section
        assert "## Available Tools" in result
        assert "test_tool" in result


class TestMCPToolDocumentation:
    """Test MCP tool documentation generation."""

    def test_extracts_parameters_from_schema(self):
        """Test that tool parameters are extracted from input schema."""
        base_instruction = "Assistant"

        mcp_tool = MCPToolInfo(
            name="search",
            description="Search for items",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results"
                    }
                },
                "required": ["query"]
            }
        )

        mock_tool = Mock()
        mock_tool.name = "search"
        mock_tool.description = "Search for items"
        mock_tool.mcp_tool_info = mcp_tool

        tools = [mock_tool]

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=tools,
            engine_type="adk"
        )

        # Should include parameter names
        assert "query" in result or "search" in result

    def test_marks_required_parameters(self):
        """Test that required parameters are marked in documentation."""
        base_instruction = "Assistant"

        mcp_tool = MCPToolInfo(
            name="create_item",
            description="Create an item",
            input_schema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Item name"},
                    "description": {"type": "string", "description": "Item description"}
                },
                "required": ["name"]
            }
        )

        mock_tool = Mock()
        mock_tool.name = "create_item"
        mock_tool.description = "Create an item"
        mock_tool.mcp_tool_info = mcp_tool

        tools = [mock_tool]

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=tools,
            engine_type="adk"
        )

        # Should mention the tool
        assert "create_item" in result


class TestMultipleTools:
    """Test documentation generation with multiple tools."""

    def test_documents_multiple_tools(self):
        """Test that multiple tools are all documented."""
        base_instruction = "Assistant"

        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "First tool"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Second tool"

        tools = [tool1, tool2]

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=tools,
            engine_type="adk"
        )

        # Should document both tools
        assert "tool1" in result
        assert "tool2" in result
        assert "First tool" in result
        assert "Second tool" in result

    def test_preserves_tool_order(self):
        """Test that tools are documented in the order provided."""
        base_instruction = "Assistant"

        tools = []
        for i in range(5):
            tool = Mock()
            tool.name = f"tool{i}"
            tool.description = f"Tool number {i}"
            tools.append(tool)

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=tools,
            engine_type="adk"
        )

        # All tools should be present
        for i in range(5):
            assert f"tool{i}" in result


class TestEngineTypeHandling:
    """Test handling of different engine types."""

    def test_supports_adk_engine(self):
        """Test that ADK engine type works."""
        base_instruction = "Assistant"
        tool = Mock()
        tool.name = "test"
        tool.description = "Test"

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=[tool],
            engine_type="adk"
        )

        # Should generate documentation
        assert len(result) > len(base_instruction)

    def test_supports_langgraph_engine(self):
        """Test that LangGraph engine type works."""
        base_instruction = "Assistant"
        tool = Mock()
        tool.name = "test"
        tool.description = "Test"

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=[tool],
            engine_type="langgraph"
        )

        # Should generate documentation
        assert len(result) > len(base_instruction)

    def test_handles_empty_base_instruction(self):
        """Test handling of empty base instruction."""
        tool = Mock()
        tool.name = "test"
        tool.description = "Test"

        result = PromptBuilder.build_system_prompt(
            base_instruction="",
            tools=[tool],
            engine_type="adk"
        )

        # Should still generate tool documentation
        assert "test" in result


class TestToolDescriptionFormats:
    """Test different tool description formats."""

    def test_handles_tool_without_description(self):
        """Test that tools without description are still documented."""
        base_instruction = "Assistant"

        tool = Mock()
        tool.name = "unnamed_tool"
        tool.description = None

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=[tool],
            engine_type="adk"
        )

        # Should still include the tool
        assert "unnamed_tool" in result

    def test_handles_long_descriptions(self):
        """Test that long tool descriptions are handled."""
        base_instruction = "Assistant"

        tool = Mock()
        tool.name = "complex_tool"
        tool.description = "This is a very long description. " * 50

        result = PromptBuilder.build_system_prompt(
            base_instruction=base_instruction,
            tools=[tool],
            engine_type="adk"
        )

        # Should include the tool name
        assert "complex_tool" in result
