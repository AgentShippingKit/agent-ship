import os
from typing import List
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

class LLMProviderName(Enum):
    """Name of the LLM provider."""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"

    def __str__(self):
        return self.value

class LLMModel(Enum):
    """Name of the LLM model."""
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_3_5_HAIKU = "claude-3-5-haiku-20241022"
    GEMINI_1_5_PRO = "gemini-1.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"

    def __str__(self):
        return self.value

class ProviderAPIKey(Enum):
    """API key for the LLM provider."""
    OPENAI = os.getenv("OPENAI_API_KEY", "")
    CLAUDE = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI = os.getenv("GOOGLE_API_KEY", "")

    def __str__(self):
        return self.value


class LLMProvider:
    """
    Configuration for a specific LLM provider.
    This configuration is used to configure the LLM provider.
    It is used to configure the name, API key, models, default model, and temperature.
    It is also used to validate that the default model is in the models list.
    """

    def __init__(self, name: LLMProviderName, api_key: ProviderAPIKey, models: List[LLMModel], 
                default_model: LLMModel, temperature: float = 0.7):
        self._name: LLMProviderName = name
        self._api_key: ProviderAPIKey = api_key
        self._models: List[LLMModel] = models
        self._default_model: LLMModel = default_model
        self._temperature = temperature
        
        # Validate that default_model is in the models list
        if default_model not in self._models:
            raise ValueError(f"Default model '{default_model}' not found in available models: {models}")
    
    @property
    def name(self) -> LLMProviderName:
        """Get the provider name."""
        return self._name
    
    @property
    def api_key(self) -> str:
        """Get the provider API key."""
        return self._api_key.value

    @property
    def default_model(self) -> LLMModel:
        """Get the provider default model."""
        return self._default_model

    @property
    def temperature(self) -> float:
        """Get the provider temperature."""
        return self._temperature

    @property
    def models(self) -> List[LLMModel]:
        """Get the provider models."""
        return self._models

    def get_model_string(self, model_name: str) -> str:
        """Get the model string for LiteLLM."""
        return f"{self.name}/{model_name}"
    
    def __str__(self):
        return f"LLMProvider(name={self.name.value}, models={self.models}, default_model={self.default_model.value}, temperature={self.temperature})"


class LLMProviderConfig:
    """Configuration manager for all LLM providers and their models."""
    
    # OpenAI provider
    openai = LLMProvider(
        name=LLMProviderName.OPENAI,
        api_key=ProviderAPIKey.OPENAI,
        models=[LLMModel.GPT_4O, LLMModel.GPT_4O_MINI, LLMModel.GPT_3_5_TURBO],
        default_model=LLMModel.GPT_4O_MINI
    )
    
    # Claude provider
    claude = LLMProvider(
        name=LLMProviderName.CLAUDE,
        api_key=ProviderAPIKey.CLAUDE,
        models=[LLMModel.CLAUDE_3_5_SONNET, LLMModel.CLAUDE_3_5_HAIKU],
        default_model=LLMModel.CLAUDE_3_5_SONNET,
    )

    # Gemini provider
    gemini = LLMProvider(
        name=LLMProviderName.GEMINI,
        api_key=ProviderAPIKey.GEMINI,
        models=[LLMModel.GEMINI_1_5_PRO, LLMModel.GEMINI_1_5_FLASH],
        default_model=LLMModel.GEMINI_1_5_PRO
    )
    
    @staticmethod
    def get_llm_provider(llm_provider_name: LLMProviderName) -> LLMProvider:
        """Get provider configuration by name."""
        if llm_provider_name == LLMProviderName.OPENAI:
            return LLMProviderConfig.openai
        elif llm_provider_name == LLMProviderName.CLAUDE:
            return LLMProviderConfig.claude
        elif llm_provider_name == LLMProviderName.GEMINI:
            return LLMProviderConfig.gemini
        else:
            raise ValueError(f"Unsupported provider: {llm_provider_name}") 
    

if __name__ == "__main__":
    print(LLMProviderConfig.get_llm_provider(LLMProviderName.OPENAI))
    print(LLMProviderConfig.get_llm_provider(LLMProviderName.CLAUDE))
    print(LLMProviderConfig.get_llm_provider(LLMProviderName.GEMINI))