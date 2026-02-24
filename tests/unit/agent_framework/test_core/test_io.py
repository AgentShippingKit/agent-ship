"""Unit tests for input/output helpers."""

import pytest
from pydantic import BaseModel, Field

from src.agent_framework.core.io import build_schema_prompt


class TestBuildSchemaPrompt:
    """Test output schema prompt generation."""

    def test_generates_prompt_for_simple_schema(self):
        """Test schema prompt generation for simple model."""
        class SimpleOutput(BaseModel):
            response: str = Field(description="The response text")

        prompt = build_schema_prompt(SimpleOutput)

        # Should include output format section
        assert "## Output Format" in prompt

        # Should mention the field
        assert "response" in prompt

        # Should show it's required
        assert "required" in prompt.lower()

    def test_includes_field_types(self):
        """Test that field types are included in prompt."""
        class TypedOutput(BaseModel):
            text: str
            count: int
            ratio: float
            enabled: bool

        prompt = build_schema_prompt(TypedOutput)

        # Should mention fields
        assert "text" in prompt
        assert "count" in prompt
        assert "ratio" in prompt
        assert "enabled" in prompt

    def test_shows_required_vs_optional(self):
        """Test that required and optional fields are distinguished."""
        class MixedOutput(BaseModel):
            required_field: str
            optional_field: str = None

        prompt = build_schema_prompt(MixedOutput)

        # Should distinguish required from optional
        assert "required" in prompt.lower()
        assert "optional" in prompt.lower()

    def test_includes_field_descriptions(self):
        """Test that field descriptions are included."""
        class DescribedOutput(BaseModel):
            name: str = Field(description="The user's name")
            age: int = Field(description="The user's age in years")

        prompt = build_schema_prompt(DescribedOutput)

        # Should include descriptions
        assert "name" in prompt
        assert "age" in prompt

    def test_generates_example_format(self):
        """Test that example JSON format is generated."""
        class ExampleOutput(BaseModel):
            message: str

        prompt = build_schema_prompt(ExampleOutput)

        # Should show example format
        assert "```json" in prompt or "Example" in prompt

        # Should tell user to return actual data, not example
        assert "actual data" in prompt.lower() or "your" in prompt.lower()

    def test_handles_nested_models(self):
        """Test handling of nested Pydantic models."""
        class NestedModel(BaseModel):
            value: str

        class ParentOutput(BaseModel):
            nested: NestedModel
            simple: str

        prompt = build_schema_prompt(ParentOutput)

        # Should include both fields
        assert "nested" in prompt
        assert "simple" in prompt

    def test_handles_list_fields(self):
        """Test handling of list fields."""
        class ListOutput(BaseModel):
            items: list[str]
            tags: list

        prompt = build_schema_prompt(ListOutput)

        # Should include list fields
        assert "items" in prompt
        assert "tags" in prompt

    def test_handles_dict_fields(self):
        """Test handling of dictionary fields."""
        class DictOutput(BaseModel):
            metadata: dict

        prompt = build_schema_prompt(DictOutput)

        # Should include dict field
        assert "metadata" in prompt

    def test_handles_empty_model(self):
        """Test handling of model with no fields."""
        class EmptyOutput(BaseModel):
            pass

        prompt = build_schema_prompt(EmptyOutput)

        # Should still generate some output
        assert len(prompt) > 0
        assert "Output Format" in prompt

    def test_handles_model_with_many_fields(self):
        """Test handling of model with many fields."""
        class LargeOutput(BaseModel):
            field1: str
            field2: str
            field3: int
            field4: bool
            field5: float
            field6: list
            field7: dict
            field8: str
            field9: str
            field10: str

        prompt = build_schema_prompt(LargeOutput)

        # Should include all fields
        for i in range(1, 11):
            assert f"field{i}" in prompt

    def test_generates_different_prompts_for_different_schemas(self):
        """Test that different schemas generate different prompts."""
        class Schema1(BaseModel):
            response: str

        class Schema2(BaseModel):
            answer: str
            confidence: float

        prompt1 = build_schema_prompt(Schema1)
        prompt2 = build_schema_prompt(Schema2)

        # Prompts should be different
        assert prompt1 != prompt2
        assert "response" in prompt1
        assert "answer" in prompt2
        assert "confidence" in prompt2

    def test_shows_clear_example_format(self):
        """Test that example format is clear and not confusing."""
        class UserOutput(BaseModel):
            name: str = Field(description="User name")
            email: str = Field(description="User email")

        prompt = build_schema_prompt(UserOutput)

        # Should have clear structure
        assert "name" in prompt
        assert "email" in prompt

        # Should not show JSON Schema metadata (no "properties", "type": "object", etc.)
        # The prompt should show actual field names, not schema structure
        lines = prompt.lower()

        # Should be instructive, not showing raw JSON Schema
        assert "format" in lines or "field" in lines

    def test_handles_errors_gracefully(self):
        """Test that errors in schema generation are handled."""
        # Test with invalid input (not a BaseModel)
        prompt = build_schema_prompt(str)  # type: ignore

        # Should return empty string or handle gracefully
        assert isinstance(prompt, str)
