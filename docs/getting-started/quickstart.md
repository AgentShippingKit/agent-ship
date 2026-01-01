# Quick Start

Get AgentShip running in under 5 minutes.

## Step 1: Clone and Setup

```bash
git clone https://github.com/harshuljain13/ship-ai-agents.git
cd ship-ai-agents/ai/ai-ecosystem
make docker-setup
```

The script will:
- ✅ Check Docker installation
- ✅ Create `.env` file automatically
- ✅ Set up PostgreSQL
- ✅ Build and start everything
- ✅ Wait for services to be ready

**Done!** Open http://localhost:7001/docs

## Step 2: Add Your API Key

Edit `.env` and add at least one LLM API key:

```bash
nano .env
```

Add:
```env
OPENAI_API_KEY=your-actual-key-here
```

Then restart:
```bash
make docker-down
make docker-up
```

## Step 3: Create Your First Agent

### Create the directory

```bash
mkdir -p src/agents/all_agents/my_agent
cd src/agents/all_agents/my_agent
```

### Add configuration (`main_agent.yaml`)

```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: My helpful assistant
instruction_template: |
  You are a helpful assistant that answers questions clearly and concisely.
```

### Add code (`main_agent.py`)

```python
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import TextInput, TextOutput
from src.agents.utils.path_utils import resolve_config_path

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            input_schema=TextInput,
            output_schema=TextOutput
        )
```

### Test it!

Restart the server (if needed), then:

```bash
curl -X POST "http://localhost:7001/api/agents/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "my_agent",
    "user_id": "test-user",
    "session_id": "test-session",
    "query": "Hello, how are you?",
    "features": []
  }'
```

**That's it!** Your agent is automatically discovered and ready to use.

---

## 🐍 Local Development (Alternative)

If you prefer local development without Docker:

```bash
make setup
make dev
```

See [Installation Guide](installation.md) for details.

---

## 📚 Next Steps

- Learn about [Agent Patterns](../building-agents/patterns/single-agent.md)
- Add [Tools](../building-agents/tools.md) to your agent
- Read the [Full Documentation](../index.md)

---

**Questions?** Check the [Full Documentation](../index.md) or [open an issue](https://github.com/harshuljain13/ship-ai-agents/issues).
