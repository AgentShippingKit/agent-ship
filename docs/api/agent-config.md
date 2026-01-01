# AgentConfig API Reference

## Class: `AgentConfig`

Configuration class for agents, loaded from YAML files.

### Class Method: `from_yaml(file_path: str) -> AgentConfig`

Loads agent configuration from a YAML file.

**Parameters:**

- `file_path`: Path to the YAML configuration file.

**Returns:**

- `AgentConfig` instance populated from YAML.

### Properties

- `agent_name`: Unique identifier for the agent.
- `llm_provider_name`: LLM provider enum (`OPENAI`, `GOOGLE`, `ANTHROPIC`).
- `llm_model`: Model enum (e.g., `GPT_4O`, `GEMINI_2_0_FLASH_EXP`).
- `temperature`: LLM temperature (default: 0.4).
- `description`: Agent description.
- `instruction_template`: System prompt template.
- `tags`: List of tags for categorization.
- `tools`: List of tool configurations (function or agent tools).

### Example

```python
from src.agents.configs.agent_config import AgentConfig

config = AgentConfig.from_yaml("main_agent.yaml")
print(config.agent_name)  # "translation_agent"
print(config.llm_provider_name)  # LLMProviderName.OPENAI
```
