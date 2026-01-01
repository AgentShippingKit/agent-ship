# Core Modules API Reference

## Core Package

The `src.agents.core` package contains modular components used by `BaseAgent`.

### `load_agent_config()`

Loads agent configuration from YAML files with automatic path resolution.

```python
from src.agents.core.config import load_agent_config

config = load_agent_config(config_path="main_agent.yaml")
```

### `create_input_from_request()`

Converts `AgentChatRequest` to agent input schema.

```python
from src.agents.core.io import create_input_from_request

input_data = create_input_from_request(TextInput, request)
```

### `parse_agent_response()`

Parses ADK event response to agent output schema.

```python
from src.agents.core.io import parse_agent_response

output = parse_agent_response(TextOutput, adk_event)
```

### `build_tools_from_config()`

Builds tools from YAML configuration.

```python
from src.agents.core.tools import build_tools_from_config

tools = build_tools_from_config(agent_config)
```

### `create_observer()`

Creates Opik observer for observability.

```python
from src.agents.core.observability import create_observer

observer = create_observer(agent_config)
```
