# BaseAgent API Reference

## Class: `BaseAgent`

Base class for all agents in the framework.

### Constructor

```python
BaseAgent(
    agent_config: Optional[AgentConfig] = None,
    input_schema: Optional[Type[BaseModel]] = None,
    output_schema: Optional[Type[BaseModel]] = None,
    agent_type: Optional[AgentType] = None,
    config_path: Optional[str] = None,
    _caller_file: Optional[str] = None
)
```

**Parameters:**

- `agent_config`: Optional pre-loaded `AgentConfig`. If not provided, loaded from YAML.
- `input_schema`: Pydantic model for input validation. Defaults to `TextInput`.
- `output_schema`: Pydantic model for output validation. Defaults to `TextOutput`.
- `agent_type`: Agent type (`LLM_AGENT`, `PARALLEL_AGENT`, `SEQUENTIAL_AGENT`).
- `config_path`: Explicit path to YAML configuration file.
- `_caller_file`: Internal parameter for automatic path resolution.

### Methods

#### `chat(request: AgentChatRequest) -> AgentChatResponse`

Processes a chat request and returns a response.

**Parameters:**

- `request`: `AgentChatRequest` containing agent name, user ID, session ID, query, and features.

**Returns:**

- `AgentChatResponse` with success status, agent name, and parsed response.

#### `_create_input_from_request(request: AgentChatRequest) -> BaseModel`

Converts an `AgentChatRequest` to the agent's input schema.

**Parameters:**

- `request`: `AgentChatRequest` to convert.

**Returns:**

- Instance of `input_schema` populated from the request.

#### `_get_agent_name() -> str`

Returns the agent's name from configuration.

**Returns:**

- Agent name string.

### Properties

- `agent_config`: `AgentConfig` instance loaded from YAML.
- `input_schema`: Pydantic model class for input validation.
- `output_schema`: Pydantic model class for output validation.
- `agent_type`: Agent type enum value.
- `runner`: Google ADK `Runner` instance for LLM execution.
- `session_manager`: `SessionManager` instance for session handling.
