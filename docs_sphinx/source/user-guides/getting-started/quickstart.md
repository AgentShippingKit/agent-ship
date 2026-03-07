# Quick Start

Get AgentShip running and your first agent in under 5 minutes.

## Step 1: Run AgentShip

```bash
git clone https://github.com/Agent-Ship/agent-ship.git
cd agent-ship
make docker-setup
```

Setup will prompt for your API key, create `.env`, and start the API + PostgreSQL. When ready:

| Service | URL |
|---------|-----|
| AgentShip Studio | http://localhost:7001/studio |
| API / Swagger | http://localhost:7001/swagger |

## Step 2: Chat with a Built-in Agent

Open http://localhost:7001/studio, pick any agent, and start chatting. No extra setup.

## Step 3: Create Your First Agent

Create two files in `src/all_agents/my_agent/`:

**`main_agent.yaml`**

```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
execution_engine: adk   # or langgraph
description: My helpful assistant
instruction_template: |
  You are a helpful assistant that answers questions clearly.
```

**`main_agent.py`**

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

Restart: `make docker-restart`. Your agent is auto-discovered — no registration.

## Next Steps

- [Agent Configuration](../building-agents/agent-configuration.md) — YAML fields, engines, streaming
- [Agent Patterns](../building-agents/patterns/single-agent.md) — single agent, orchestrator, tools
- [MCP Integration](../mcp-integration.md) — PostgreSQL, GitHub, and other MCP servers

## Local Development (No Docker)

```bash
pipenv install
cp .env.example .env   # add your API key
make dev               # http://localhost:7001
```
