# BaseAgent

The `BaseAgent` class is the foundation for all agents in the framework. It handles configuration loading, session management, LLM setup, tool creation, and observability initialization.

## Usage

```python
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            input_schema=TextInput,
            output_schema=TextOutput
        )
```

## Responsibilities

`BaseAgent` handles:

- **Configuration Loading**: Loads `AgentConfig` from YAML files
- **Session Management**: Wires up session services and manages conversation history
- **LLM Setup**: Configures the Google ADK `Runner` with your LLM provider
- **Tool Creation**: Builds tools from YAML configuration
- **Observability**: Initializes Opik tracing and metrics

## Subclass Requirements

Subclasses typically only need to:

- Provide `input_schema` and `output_schema` via `super().__init__`
- Optionally override `_create_input_from_request` for custom input mapping

## Methods

### `chat(request: AgentChatRequest) -> AgentChatResponse`

Processes a chat request and returns a response. Handles session management, input parsing, LLM execution, and response parsing automatically.

### `_create_input_from_request(request: AgentChatRequest) -> BaseModel`

Converts an `AgentChatRequest` to your agent's input schema. Override this for custom input mapping.

### `_get_agent_name() -> str`

Returns the agent's name from configuration.

See the [API Reference](../api/base-agent.md) for complete method documentation.
