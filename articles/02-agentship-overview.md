# AgentShip: High-Level Overview

## What is AgentShip?

AgentShip is a **production-ready framework** for building, deploying, and operating AI agents. Built on top of Google's Agent Development Kit (ADK), it provides everything you need to go from idea to production in minutes.

---

## Core Principles

### 1. Convention Over Configuration
Create files in the right place, they work automatically. No manual registration, no complex setup.

### 2. YAML + Python
Configuration in YAML (human-readable), logic in Python (developer-friendly). Best of both worlds.

### 3. Batteries Included
REST API, session management, observability, deployment—all built-in. Focus on agent logic.

### 4. Progressive Complexity
Start simple, add complexity as needed. Don't pay for features you don't use.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│                    Your Agents                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Agent A   │  │   Agent B   │  │   Agent C   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────┤
│                  AgentShip Core                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ Registry │  │ Sessions │  │Observability│         │
│  └──────────┘  └──────────┘  └──────────┘           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ REST API │  │  Config  │  │  Tools   │           │
│  └──────────┘  └──────────┘  └──────────┘           │
├──────────────────────────────────────────────────────┤
│                  Google ADK                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Agent   │  │  Runner  │  │ LiteLLM  │           │
│  └──────────┘  └──────────┘  └──────────┘           │
├──────────────────────────────────────────────────────┤
│                 LLM Providers                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  OpenAI  │  │  Google  │  │ Anthropic│           │
│  └──────────┘  └──────────┘  └──────────┘           │
└──────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. BaseAgent
The foundation of every agent. Handles:
- Configuration loading
- Session management
- LLM integration
- Response parsing
- Tool management

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput
        )
```

### 2. AgentConfig (YAML)
Declarative agent configuration:

```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: What this agent does
instruction_template: |
  The system prompt for the agent.
tools:
  - type: function
    id: my_tool
    import: src.agents.tools.my_tool.MyTool
```

### 3. Agent Registry
Automatic agent discovery and management:

```python
from src.agents.registry import discover_agents, get_agent_instance

# Agents are discovered automatically at startup
# Get an agent by name
agent = get_agent_instance("my_agent")
```

### 4. Session Management
Automatic conversation persistence:

- **PostgreSQL**: Production, persistent storage
- **In-memory**: Development, testing

```python
# Sessions are managed automatically
# Just use session_id in requests
response = await agent.chat(AgentChatRequest(
    query="Hello",
    session_id="user-123-session-1",
    user_id="user-123"
))
```

### 5. REST API
FastAPI-based API with:
- `/api/agents/chat` - Chat with agents
- `/swagger` - Interactive API docs
- `/health` - Health checks
- `/redoc` - Alternative API docs

---

## Directory Structure

```
ai-ecosystem/
├── src/
│   ├── agents/
│   │   ├── all_agents/           # Your agents go here
│   │   │   ├── my_agent/
│   │   │   │   ├── main_agent.yaml
│   │   │   │   └── main_agent.py
│   │   │   └── another_agent/
│   │   ├── core/                 # Core abstractions
│   │   ├── configs/              # Configuration classes
│   │   ├── modules/              # Reusable modules
│   │   ├── registry/             # Auto-discovery
│   │   ├── tools/                # Shared tools
│   │   └── observability/        # Opik integration
│   ├── models/                   # Pydantic models
│   └── service/                  # FastAPI service
├── Makefile                      # Commands
├── docker-compose.yml            # Docker setup
└── Pipfile                       # Dependencies
```

---

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/harshuljain13/ship-ai-agents.git
cd ship-ai-agents/ai/ai-ecosystem
make docker-setup
```

### 2. Create an Agent

```bash
mkdir -p src/agents/all_agents/my_agent
```

**main_agent.yaml**:
```yaml
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: My helpful assistant
instruction_template: |
  You are a helpful assistant.
```

**main_agent.py**:
```python
from src.agents.all_agents.base_agent import BaseAgent
from src.models.base_models import TextInput, TextOutput

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput
        )
```

### 3. Restart and Test

```bash
make docker-restart
# Open http://localhost:7001/swagger
```

---

## Agent Patterns

AgentShip supports three main patterns:

### 1. Single Agent
Simple, focused agents for specific tasks.

```
User → Agent → Response
```

### 2. Orchestrator (Multi-Agent)
Coordinate multiple agents for complex workflows.

```
User → Orchestrator → [Agent A, Agent B, Agent C] → Combined Response
```

### 3. Tool-Based
Agents with custom tools for extended functionality.

```
User → Agent → [Tool 1, Tool 2, Database] → Response
```

---

## Built-in Features

| Feature | Description |
|---------|-------------|
| **Auto-Discovery** | Create agent files → automatically registered |
| **Multi-Provider** | OpenAI, Google, Anthropic support |
| **Session Management** | PostgreSQL or in-memory |
| **Observability** | Opik tracing, metrics, logging |
| **REST API** | FastAPI with Swagger docs |
| **Docker Support** | One-command setup and deployment |
| **Hot Reload** | Edit code → automatic restart |
| **Heroku Deployment** | One-command cloud deployment |

---

## Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...            # Or GOOGLE_API_KEY, ANTHROPIC_API_KEY

# Optional - Session Storage
AGENT_SHORT_TERM_MEMORY=Database
AGENT_SESSION_STORE_URI=postgresql://user:pass@host:5432/db

# Optional - Observability
OPIK_API_KEY=your-key
OPIK_WORKSPACE=your-workspace
OPIK_PROJECT_NAME=your-project
```

---

## Commands

```bash
# Setup
make docker-setup      # First-time setup

# Development
make docker-up         # Start containers
make docker-down       # Stop containers
make docker-restart    # Restart containers
make docker-logs       # View logs

# Testing
make test              # Run tests

# Deployment
make heroku-deploy     # Deploy to Heroku

# Help
make help              # See all commands
```

---

## What's Next?

Explore these guides:
1. **Agentic Design Patterns** - Different agent architectures
2. **Context Engineering** - Crafting effective prompts
3. **Memory Management** - Short-term, long-term, RAG
4. **Observability** - Tracing and monitoring
5. **Evals** - Testing and evaluation

---

*AgentShip: Build agents, not infrastructure.*

