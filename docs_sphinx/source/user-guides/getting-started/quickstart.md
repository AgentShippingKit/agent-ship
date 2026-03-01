# Quick Start

Get AgentShip running and your first agent deployed in under 5 minutes.

## Step 1: Clone and Start

```bash
git clone https://github.com/Agent-Ship/agent-ship.git
cd agent-ship
make docker-setup
```

The setup script will:
- ✅ Check Docker installation
- ✅ Create a `.env` file and prompt for your API key
- ✅ Start the API server and PostgreSQL
- ✅ Print service URLs when ready

**Services available at:**
- **API / Swagger**: http://localhost:7001/swagger
- **Debug UI**: http://localhost:7001/debug-ui

## Step 2: Chat with a Built-In Agent

Open the Debug UI at http://localhost:7001/debug-ui, pick any agent, and start chatting. No extra setup needed.

Or use curl:

```bash
curl -X POST http://localhost:7001/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "translation_agent",
    "user_id": "demo",
    "session_id": "demo-session",
    "query": {"text": "Hello!", "from_language": "English", "to_language": "Spanish"},
    "features": []
  }'
```

## Step 3: Create Your First Agent

### 1. Create the directory

```bash
mkdir -p src/all_agents/my_agent
```

### 2. Add `main_agent.yaml`

```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
execution_engine: adk   # or langgraph
description: My helpful assistant
instruction_template: |
  You are a helpful assistant that answers questions clearly and concisely.
```

### 3. Add `main_agent.py`

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

### 4. Restart and test

```bash
make docker-restart
```

Your agent is automatically discovered — no registration needed.

```bash
curl -X POST http://localhost:7001/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "my_agent",
    "user_id": "demo",
    "session_id": "s1",
    "query": {"text": "Hello!"},
    "features": []
  }'
```

---

## Local Development (No Docker)

```bash
pipenv install
cp .env.example .env   # add your API key
make dev               # starts on http://localhost:7001
```

---

## Next Steps

- [Agent Configuration](../building-agents/agent-configuration.md) — YAML fields, engines, streaming modes
- [Agent Patterns](../building-agents/patterns/single-agent.md) — single agent, orchestrator, tool pattern
- [MCP Integration](../mcp-integration.md) — connect PostgreSQL, GitHub, and other MCP servers

---

**Questions?** [Open an issue](https://github.com/Agent-Ship/agent-ship/issues) on GitHub.
