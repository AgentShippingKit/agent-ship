"""Unit tests for LLM provider config — model strings, aliases, and LiteLLM prefixes.

These tests are pure logic (no mocks, no network) and run without any API keys.
They exist to catch regressions like:
  - Wrong LiteLLM prefix (e.g. "claude/" instead of "anthropic/")
  - Deprecated model IDs passed raw to the API (e.g. "gemini-1.5-pro" without -002)
  - New model added to enum but missing from provider models list
  - Alias map out of sync with the enum
"""

import pytest

from src.agent_framework.configs.llm.llm_provider_config import (
    LLMModel,
    LLMProviderConfig,
    LLMProviderName,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def model_string(provider_name: str, model_name: str) -> str:
    """Resolve a provider + model name to the LiteLLM model string."""
    provider = LLMProviderConfig.get_llm_provider(LLMProviderName(provider_name))
    return provider.get_model_string(model_name)


# ---------------------------------------------------------------------------
# LiteLLM prefix correctness
# ---------------------------------------------------------------------------

class TestLiteLLMPrefixes:
    """The prefix in the model string must match what LiteLLM expects."""

    def test_openai_prefix(self):
        assert model_string("openai", "gpt-4o").startswith("openai/")

    def test_claude_uses_anthropic_prefix_not_claude(self):
        # Critical: LiteLLM routes on "anthropic/", not "claude/"
        result = model_string("claude", "claude-3-5-sonnet")
        assert result.startswith("anthropic/"), (
            f"Expected 'anthropic/' prefix but got '{result}'. "
            "LiteLLM will fail to route Claude calls with any other prefix."
        )
        assert not result.startswith("claude/")

    def test_gemini_prefix(self):
        assert model_string("gemini", "gemini-2.0-flash").startswith("gemini/")


# ---------------------------------------------------------------------------
# Model alias resolution
# ---------------------------------------------------------------------------

class TestModelAliases:
    """Aliases map user-friendly names to versioned API model IDs."""

    # Gemini — 1.5 models were shut down Sep 2025; aliases forward to 2.5
    def test_gemini_1_5_pro_forwards_to_current(self):
        result = model_string("gemini", "gemini-1.5-pro")
        assert result == "gemini/gemini-2.5-pro", (
            "gemini-1.5-pro is shut down — must alias to a live model"
        )

    def test_gemini_1_5_flash_forwards_to_current(self):
        result = model_string("gemini", "gemini-1.5-flash")
        assert result == "gemini/gemini-2.5-flash"

    def test_gemini_2_0_flash_no_alias_needed(self):
        assert model_string("gemini", "gemini-2.0-flash") == "gemini/gemini-2.0-flash"

    def test_gemini_2_5_flash_no_alias(self):
        # 2.5 models are stable GA — no alias needed
        assert model_string("gemini", "gemini-2.5-flash") == "gemini/gemini-2.5-flash"

    def test_gemini_2_5_pro_no_alias(self):
        assert model_string("gemini", "gemini-2.5-pro") == "gemini/gemini-2.5-pro"

    # Claude
    def test_claude_3_5_sonnet_resolves_to_dated(self):
        result = model_string("claude", "claude-3-5-sonnet")
        assert result == "anthropic/claude-3-5-sonnet-20241022"

    def test_claude_3_5_haiku_resolves_to_dated(self):
        result = model_string("claude", "claude-3-5-haiku")
        assert result == "anthropic/claude-3-5-haiku-20241022"

    def test_claude_3_7_sonnet_resolves_to_dated(self):
        result = model_string("claude", "claude-3-7-sonnet")
        assert result == "anthropic/claude-3-7-sonnet-20250219"

    def test_claude_opus_4_resolves_to_dated(self):
        result = model_string("claude", "claude-opus-4")
        assert result == "anthropic/claude-opus-4-20250514"

    def test_claude_sonnet_4_resolves_to_dated(self):
        result = model_string("claude", "claude-sonnet-4")
        assert result == "anthropic/claude-sonnet-4-20250514"

    # GPT-5 — released August 2025; no aliases needed, IDs are stable
    def test_gpt5_no_alias_needed(self):
        assert model_string("openai", "gpt-5") == "openai/gpt-5"

    def test_gpt5_mini_no_alias_needed(self):
        assert model_string("openai", "gpt-5-mini") == "openai/gpt-5-mini"

    def test_gpt5_nano_no_alias_needed(self):
        assert model_string("openai", "gpt-5-nano") == "openai/gpt-5-nano"

    def test_unknown_model_passthrough(self):
        # A model not in aliases should pass through unchanged (LiteLLM may know it)
        result = model_string("openai", "gpt-99-turbo")
        assert result == "openai/gpt-99-turbo"


# ---------------------------------------------------------------------------
# Model enum ↔ provider list consistency
# ---------------------------------------------------------------------------

class TestProviderModelListConsistency:
    """Every model in a provider's models list must exist in LLMModel enum,
    and the enum value must round-trip through get_model_string without error."""

    @pytest.mark.parametrize("provider_name", ["openai", "claude", "gemini"])
    def test_all_provider_models_are_valid_enum_values(self, provider_name):
        provider = LLMProviderConfig.get_llm_provider(LLMProviderName(provider_name))
        for model in provider.models:
            # Each model must be a valid LLMModel enum member
            assert model in LLMModel, f"{model} in {provider_name} models list is not a valid LLMModel"
            # And get_model_string must not raise
            result = provider.get_model_string(model.value)
            assert result  # non-empty string

    def test_openai_models_list_is_not_empty(self):
        assert len(LLMProviderConfig.openai.models) > 0

    def test_claude_models_list_is_not_empty(self):
        assert len(LLMProviderConfig.claude.models) > 0

    def test_gemini_models_list_is_not_empty(self):
        assert len(LLMProviderConfig.gemini.models) > 0


# ---------------------------------------------------------------------------
# Default models
# ---------------------------------------------------------------------------

class TestDefaultModels:
    def test_openai_default_in_model_list(self):
        p = LLMProviderConfig.openai
        assert p.default_model in p.models

    def test_claude_default_in_model_list(self):
        p = LLMProviderConfig.claude
        assert p.default_model in p.models

    def test_gemini_default_in_model_list(self):
        p = LLMProviderConfig.gemini
        assert p.default_model in p.models

    def test_gemini_default_is_not_deprecated(self):
        # All 1.5 and 2.0 models are deprecated/shut down — default must be 2.5+
        deprecated = {"gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"}
        assert LLMProviderConfig.gemini.default_model.value not in deprecated


# ---------------------------------------------------------------------------
# Full model string format
# ---------------------------------------------------------------------------

class TestModelStringFormat:
    """Model strings must be in 'prefix/model-id' format for LiteLLM."""

    @pytest.mark.parametrize("provider_name,model_name,expected", [
        ("openai", "gpt-5",            "openai/gpt-5"),
        ("openai", "gpt-5-mini",       "openai/gpt-5-mini"),
        ("openai", "gpt-5-nano",       "openai/gpt-5-nano"),
        ("openai", "gpt-4o",           "openai/gpt-4o"),
        ("openai", "gpt-4o-mini",      "openai/gpt-4o-mini"),
        ("openai", "o3",               "openai/o3"),
        ("openai", "o3-mini",          "openai/o3-mini"),
        ("claude", "claude-3-5-sonnet","anthropic/claude-3-5-sonnet-20241022"),
        ("claude", "claude-sonnet-4",  "anthropic/claude-sonnet-4-20250514"),
        ("gemini", "gemini-2.0-flash", "gemini/gemini-2.0-flash"),
        ("gemini", "gemini-1.5-pro",   "gemini/gemini-2.5-pro"),
    ])
    def test_model_string(self, provider_name, model_name, expected):
        assert model_string(provider_name, model_name) == expected

    @pytest.mark.parametrize("provider_name", ["openai", "claude", "gemini"])
    def test_model_string_contains_slash(self, provider_name):
        provider = LLMProviderConfig.get_llm_provider(LLMProviderName(provider_name))
        for model in provider.models:
            result = provider.get_model_string(model.value)
            assert "/" in result, f"Model string '{result}' missing provider/model separator"
            prefix, _, model_id = result.partition("/")
            assert prefix, "prefix must not be empty"
            assert model_id, "model id must not be empty"
