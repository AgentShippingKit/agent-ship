# Building Agents

Two files. That's an agent.

AgentShip auto-discovers all agents in `src/all_agents/` at startup. No registration step, no routing config — just a YAML and a Python class.

## The Two Files

**`main_agent.yaml`** — everything infrastructure:

```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
execution_engine: adk        # or langgraph — Python class is unchanged either way
description: A helpful assistant
instruction_template: |
  You are a helpful assistant that answers questions clearly.
```

**`main_agent.py`** — your agent logic:

```python
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput
from src.agent_framework.utils.path_utils import resolve_config_path

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            input_schema=TextInput,
            output_schema=TextOutput,
        )
```

Restart the server — the agent appears in Studio and the API. No other step.

## How Discovery Works

1. AgentShip scans `src/all_agents/` for `main_agent.yaml` files at startup
2. Each YAML's `agent_name` becomes the registry key
3. The corresponding Python class is imported and instantiated
4. The agent is registered and available immediately at `/api/agents/chat`

The registry key is always `agent_name` from YAML — not the class name, not the directory name.

## Execution Engines

Set `execution_engine` in YAML. Your Python class never changes.

| Engine | Config value | Streaming | When to use |
|--------|-------------|-----------|-------------|
| Google ADK | `adk` | Event-based | Default; most agents |
| LangGraph + LiteLLM | `langgraph` | Token-by-token | When you need real streaming |

Swap engines by changing one line:

```diff
- execution_engine: adk
+ execution_engine: langgraph
```

## Agent Patterns

Three proven patterns are included as working examples:

- **[Single Agent](patterns/single-agent.md)** — standalone agent for a focused task
- **[Orchestrator](patterns/orchestrator.md)** — main agent that delegates to sub-agents
- **[Tool Pattern](patterns/tool-pattern.md)** — agent with custom Python function tools

## Agent Lifecycle

1. **Discovery** — `src/all_agents/` scanned on startup
2. **Instantiation** — Python class loaded, YAML config parsed
3. **Tool setup** — function tools and MCP connections established
4. **Prompt build** — tool documentation injected into system prompt
5. **Request** — `chat()` or `stream()` dispatches to the engine
6. **Session** — conversation history persisted to PostgreSQL

See [Agent Configuration](agent-configuration.md) for all YAML fields, and [Tools](tools.md) for adding function tools and MCP servers.
