# Single Agent Pattern

The single agent pattern is for standalone agents that handle focused tasks independently.

## Example: Translation Agent

```python
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput

class TranslationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            input_schema=TextInput,
            output_schema=TextOutput
        )
```

## Configuration

```yaml
agent_name: translation_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: Translates text between languages
instruction_template: |
  You are a translation expert...
```

## Use Cases

- Text translation
- Content summarization
- Question answering
- Simple task automation
