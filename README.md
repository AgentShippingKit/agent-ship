<p align="center">
  <img src="branding/banners/github-banner@3x.png" alt="AgentShip" width="100%">
</p>

<p align="center">
  <strong>Build and deploy AI agents in minutes, not weeks.</strong>
</p>

<p align="center">
  AgentShip is the <strong>production layer</strong> for AI agents. Built on Google ADK and LangGraph, it provides everything you need to ship agents to production: REST API, session management, observability, streaming, MCP integration, and one-command deployment.
</p>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
  </a>
  <a href="https://fastapi.tiangolo.com/">
    <img src="https://img.shields.io/badge/FastAPI-0.119-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
  </a>
  <a href="https://github.com/google/generative-ai-python">
    <img src="https://img.shields.io/badge/Google_ADK-1.15-4285F4?style=flat&logo=google&logoColor=white" alt="Google ADK">
  </a>
  <a href="https://www.langchain.com/">
    <img src="https://img.shields.io/badge/LangGraph-Latest-121212?style=flat&logo=langchain&logoColor=white" alt="LangGraph">
  </a>
  <a href="https://modelcontextprotocol.io/">
    <img src="https://img.shields.io/badge/MCP-Integrated-FF6B35?style=flat" alt="MCP">
  </a>
  <a href="https://www.postgresql.org/">
    <img src="https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white" alt="PostgreSQL">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
</p>

---

## ✨ Key Features

- 🚀 **Dual Execution Engines** - Choose between Google ADK or LangGraph
- 🔌 **MCP Integration** - STDIO and HTTP/OAuth MCP transports for both engines
- 📝 **Auto Tool Documentation** - Tool schemas automatically generate LLM prompts
- 🎯 **YAML Configuration** - Define agents declaratively, `agent_name` drives registry key
- 💾 **Session Management** - PostgreSQL-backed conversation memory
- 📊 **Observability** - Built-in OPIK integration for monitoring
- 🌊 **Streaming Support** - Token-by-token and SSE streaming with Stop button
- 🔧 **Debug UI** - Interactive interface with abort mid-stream support
- 🐳 **Docker Ready** - One-command deployment with hot-reload
- 🧪 **Integration Test Suite** - Comprehensive tests for agents, MCP, and streaming

---

## 🚀 Quick Start

### First Time Setup
```bash
git clone https://github.com/AgentShippingKit/agent-ship.git
cd agent-ship
make docker-setup
```

**That's it!** The script will:
- ✅ Check Docker installation
- ✅ Create `.env` file
- ✅ Prompt for your API key
- ✅ Start everything

**Access your services:**
- 🔌 **API (Swagger)**: http://localhost:7001/swagger
- 📚 **Documentation**: http://localhost:7001/docs
- 🔧 **Debug UI**: http://localhost:7001/debug-ui

### Next Time (After First Setup)
```bash
make docker-up      # Start containers (with hot-reload)
make docker-down    # Stop containers
make docker-logs    # View logs
```

**Hot-reload enabled!** Edit code in `src/` and changes auto-reload.

---

## 🏗️ Architecture

AgentShip's architecture is designed for production-scale AI agent deployment:

<p align="center">
  <img src="branding/Architecture.png" alt="AgentShip Architecture" width="100%">
</p>

The system includes:
- **FastAPI Entrypoint**: HTTP, SSE, and WebSocket support
- **Main Ecosystem**: YAML-based agent configurations, LLM sidecar, observability, and guardrails
- **LLM Tooling Layer**: Utils, tools, and **MCP integration**
- **Auto Tool Documentation**: Automatic prompt generation from tool schemas
- **Memory Layer**: Session memory, external context stores, caching, and file storage
- **Data Ingestion Pipeline**: Processes data from various sources
- **Observability**: OPIK & Langfuse integration for monitoring and evaluation

---

## 📝 Create Your First Agent

### Basic Agent

```bash
# 1. Create directory
mkdir -p src/all_agents/my_agent
cd src/all_agents/my_agent

# 2. Create main_agent.yaml
cat > main_agent.yaml << EOF
agent_name: my_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
execution_engine: adk  # or langgraph
description: My helpful assistant
instruction_template: |
  You are a helpful assistant that answers questions clearly.
EOF

# 3. Create main_agent.py
cat > main_agent.py << EOF
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput
from src.agent_framework.utils.path_utils import resolve_config_path

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            input_schema=TextInput,
            output_schema=TextOutput
        )
EOF
```

Restart server → Agent is automatically discovered!

### Agent with MCP Tools

```yaml
agent_name: database_agent
llm_provider_name: openai
llm_model: gpt-4o-mini
temperature: 0.2
execution_engine: adk  # MCP works with both adk and langgraph!
description: Database agent with MCP PostgreSQL integration
instruction_template: |
  You are a database assistant. Use the available tools to query and analyze data.

mcp:
  servers:
    - postgres  # References server from .mcp.settings.json
```

**Configure MCP servers** in `.mcp.settings.json`:
```json
{
  "servers": {
    "postgres": {
      "transport": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "postgresql://user:password@host:5432/database"
      ],
      "env": {}
    },
    "filesystem": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

**That's it!** The agent automatically:
- ✅ Discovers MCP tools from the server
- ✅ Generates tool documentation for the LLM
- ✅ Injects it into the system prompt
- ✅ Handles event loop management
- ✅ Works with both ADK and LangGraph engines

---

## 🔌 MCP Integration

AgentShip has **production-ready MCP (Model Context Protocol) integration**:

### Features

- ✅ **STDIO Transport** - Connect to local MCP servers via stdin/stdout
- ✅ **HTTP/OAuth Transport** - Connect to remote services (GitHub, Slack, etc.) via OAuth
- ✅ **Auto Tool Discovery** - Tools are discovered automatically from MCP servers
- ✅ **Auto Documentation** - Tool schemas generate LLM-friendly documentation
- ✅ **Dual Engine Support** - Works with both ADK and LangGraph
- ✅ **Per-Agent Client Isolation** - OAuth servers get separate clients per agent
- ✅ **Env Var Resolution** - `${VAR}` tokens in command args resolved at load time
- ✅ **Event Loop Safe** - Automatic reconnection on event loop changes

### Transports

| Transport | Use Case | Auth |
|-----------|----------|------|
| `stdio` | Local servers (`npx`, Python scripts) | None (env vars) |
| `http` / `sse` | Remote APIs (GitHub, Slack, etc.) | OAuth 2.0 |

### Configuration

**Global Config** (`.mcp.settings.json`):
```json
{
  "servers": {
    "postgres": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${AGENT_SESSION_STORE_URI}"]
    },
    "github": {
      "transport": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "auth": {
        "type": "oauth",
        "provider": "github",
        "client_id_env": "GITHUB_OAUTH_CLIENT_ID",
        "client_secret_env": "GITHUB_OAUTH_CLIENT_SECRET",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "token_url": "https://github.com/login/oauth/access_token",
        "scopes": ["repo", "read:org"]
      }
    }
  }
}
```

**Agent YAML**:
```yaml
mcp:
  servers:
    - postgres   # STDIO: shared client
    - github     # HTTP/OAuth: per-agent client
```

### OAuth Setup

```bash
# Connect a user to GitHub MCP (opens browser)
pipenv run agentship mcp connect github --user-id alice

# List active connections
pipenv run agentship mcp list-connections --user-id alice
```

### Example Agents

- `src/all_agents/github_adk_mcp_agent/` — GitHub via HTTP/OAuth, ADK engine
- `src/all_agents/github_langgraph_mcp_agent/` — GitHub via HTTP/OAuth, LangGraph engine

### How It Works

1. **Agent Initialization** - MCP servers configured in YAML
2. **Tool Discovery** - AgentShip connects to MCP servers and fetches tool schemas
3. **Auto Documentation** - `ToolDocumentationGenerator` creates LLM-friendly docs
4. **Prompt Injection** - `PromptBuilder` injects docs into the system prompt
5. **Runtime** - Agent uses tools naturally; AgentShip handles all MCP transport

---

## 🤖 Auto Tool Documentation

AgentShip automatically generates tool documentation for LLMs:

### Features

- ✅ **Single Source of Truth** - Tool schemas define documentation
- ✅ **Always Accurate** - Documentation updates automatically with schema changes
- ✅ **All Tool Types** - Functions, MCP tools, agent tools
- ✅ **Engine Agnostic** - Works with ADK and LangGraph
- ✅ **Zero Maintenance** - No manual documentation needed

### How It Works

```python
# Tool schemas are automatically extracted
{
  "name": "query",
  "description": "Execute SQL query",
  "parameters": {
    "sql": {"type": "string", "required": true}
  }
}

# Converted to LLM-friendly documentation
"""
## Available Tools

### query
**Description:** Execute SQL query
**Parameters:**
- `sql` (string, **required**)

**Example:**
```json
{"sql": "SELECT * FROM table"}
```
"""

# Automatically injected into system prompt
# LLM sees accurate, up-to-date tool documentation!
```

No manual work required - schemas are the single source of truth.

---

## 🔧 Debug UI

AgentShip includes a **Gradio-based Debug UI** for testing agents interactively:

**Access**: http://localhost:7001/debug-ui (same port as API)

Features:
- 💬 Interactive chat with any registered agent
- 📝 Dynamic input forms from Pydantic schemas
- 🔍 Real-time debug logs
- 🔄 Session management (new/clear conversations)
- ⏹ **Stop button** — abort a running stream mid-response
- 🔌 Works with MCP-enabled agents

---

## 🛠️ Commands

### Docker Development (Recommended)
```bash
make docker-setup   # First-time setup (builds + starts)
make docker-up      # Start containers (after first setup)
make docker-down    # Stop containers
make docker-restart # Restart containers
make docker-reload  # Hard reload (rebuild + restart)
make docker-logs    # View logs
```

### Local Development (No Docker)
```bash
make dev            # Start dev server → http://localhost:7001
                    # Debug UI at → http://localhost:7001/debug-ui
```

### Testing
```bash
make test           # Run all tests
make test-cov       # Run tests with coverage

# Integration tests (by scope)
pipenv run pytest tests/unit/ -v                              # Unit tests only
pipenv run pytest tests/integration/ -v                       # All integration tests
pipenv run pytest tests/integration/test_agent_naming.py -v  # Agent naming
pipenv run pytest tests/integration/test_mcp_infrastructure.py -v  # MCP isolation
pipenv run pytest tests/integration/test_streaming.py -v     # Streaming events
```

### Deploy to Heroku
```bash
make heroku-deploy  # Deploy to Heroku (one command)
```

### Other Commands
```bash
make help           # See all commands
make lint           # Run linter
make format         # Format code
```

---

## 🗄️ Database Environments

AgentShip uses PostgreSQL for session storage. Different environments use different databases:

| Environment | Command | Database | Access |
|---|---|---|---|
| **Docker** | `make docker-up` | Docker PostgreSQL (`agentship_session_store`) | `postgres:5432` (inside containers), `localhost:5433` (external) |
| **Local** | `make dev` | Local PostgreSQL (`agentship_session_store`) | `localhost:5432` |
| **Heroku** | Auto-provisioned | Heroku PostgreSQL | `DATABASE_URL` env var |

**Note**: Docker and local development use separate databases. Data does not sync between them.

### Docker Networking

Inside Docker, containers communicate via service names, not `localhost`:
- ✅ `postgres:5432` - Correct (Docker service name)
- ❌ `localhost:5432` - Wrong (refers to container's own network)

The `docker-compose.yml` automatically overrides the database URL for Docker networking.

---

## 📚 Documentation

### Online Docs (When Running)
- **📖 Full Documentation**: http://localhost:7001/docs
- **🚀 API Reference**: http://localhost:7001/swagger
- **🔧 Debug UI**: http://localhost:7001/debug-ui

### Documentation Files
- **📘 CLAUDE.md** - Developer guide for Claude Code
- **📙 Architecture** - See `branding/Architecture.png`

---

## 🎯 Example Agents

AgentShip includes several example patterns:

1. **Single Agent** (`single_agent_pattern/`) - Simple one-agent flow
2. **Orchestrator** (`orchestrator_pattern/`) - Main agent + sub-agents
3. **Tool Pattern** (`tool_pattern/`) - Agent with custom tools
4. **File Analysis** (`file_analysis_agent/`) - PDF/document analysis
5. **PostgreSQL MCP** (`postgres_mcp_agent/`) - STDIO MCP integration example
6. **GitHub ADK MCP** (`github_adk_mcp_agent/`) - HTTP/OAuth MCP with ADK
7. **GitHub LangGraph MCP** (`github_langgraph_mcp_agent/`) - HTTP/OAuth MCP with LangGraph

---

## 🌟 Production Features

- ✅ **Dual Engines** - ADK (Google) and LangGraph
- ✅ **MCP Integration** - STDIO and HTTP/OAuth MCP transports
- ✅ **Per-Agent MCP Isolation** - OAuth clients separated per agent
- ✅ **Env Var Resolution** - `${VAR}` resolved in MCP command args
- ✅ **Auto Tool Docs** - Zero-maintenance tool documentation
- ✅ **Session Memory** - PostgreSQL-backed conversations
- ✅ **Streaming** - Token-by-token and SSE with abort support
- ✅ **Observability** - OPIK integration
- ✅ **Hot Reload** - Development-friendly
- ✅ **Docker Ready** - Production deployment
- ✅ **YAML-Based Naming** - `agent_name` in YAML drives registry key
- ✅ **Event Loop Safe** - Robust async handling
- ✅ **Integration Tests** - Comprehensive test suite for all features

---

## 🤝 Contributing

Contributions welcome! Please check existing issues or create new ones.

---

## 📄 License

**MIT License** | [GitHub](https://github.com/AgentShippingKit/agent-ship)
