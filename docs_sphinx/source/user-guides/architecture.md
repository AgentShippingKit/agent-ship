# Architecture

AgentShip is the production layer above execution engines (ADK, LangGraph) and below protocol layers (MCP, A2A). Your agent code talks to AgentShip's abstractions — never to the engines directly.

## Four Pluggable Layers

| Layer | Abstracts | Implementations | How to swap |
|---|---|---|---|
| **Engine** | Execution runtime | Google ADK, LangGraph + LiteLLM | `execution_engine:` in YAML |
| **Memory** | Short + long-term storage | mem0, Supermemory, in-memory | `memory_backend:` in YAML |
| **Observability** | Tracing & monitoring | Opik (LangFuse planned) | `observability:` in YAML |
| **Tools** | Discovery & invocation | MCP — STDIO and HTTP/OAuth | `mcp.servers:` in YAML |

## System Diagram

![AgentShip Architecture](/docs/_static/Architecture.png)

```text
┌────────────────────────────────────────────────┐
│          Your Application / API Clients        │
├────────────────────────────────────────────────┤
│       FastAPI REST + SSE Layer                  │
│   /api/agents/chat · /health · /swagger         │
├────────────────────────────────────────────────┤
│              AgentShip Core                    │
│  Registry · Session · Observability · MCP       │
├────────────────────────────────────────────────┤
│          Execution Engines                     │
│    Google ADK          LangGraph + LiteLLM      │
├────────────────────────────────────────────────┤
│          LLM Providers                         │
│  OpenAI · Anthropic · Google · any LiteLLM     │
└────────────────────────────────────────────────┘
```

## Key Design Decisions

- **ADK and LangGraph are dependencies, not competitors** — they are the engines under the hood, not what AgentShip competes with
- **Config-first, not code-first** — every infrastructure decision lives in YAML; agent logic is pure Python
- **Event loop safe** — MCP STDIO clients auto-reconnect when asyncio event loops change between requests (standard ASGI production pattern)
- **Per-agent client isolation** — HTTP/OAuth MCP servers get isolated clients per agent to prevent token cross-contamination

## Components

### FastAPI Entrypoint
- HTTP and SSE support
- Auto-generated Swagger at `/swagger`
- Health check at `/health`
- AgentShip Studio at `/studio`

### Agent Registry
- Scans `src/all_agents/` on startup
- Discovers `BaseAgent` subclasses from YAML + Python pairs
- `agent_name` in YAML is the registry key — no manual registration

### Execution Engines

| Engine | Config value | Streaming | LLM access |
|--------|-------------|-----------|-----------|
| Google ADK | `adk` | Event-based | ADK runner |
| LangGraph + LiteLLM | `langgraph` | Token-by-token | Any LiteLLM provider |

Set `execution_engine` per agent in YAML. Default is `adk`.

### Session Memory
- PostgreSQL-backed via `AsyncPostgresSaver` (LangGraph) or ADK session service
- In-memory fallback for development (`AGENT_SHORT_TERM_MEMORY=InMemory`)
- Keyed by `user_id:session_id` thread

### MCP Integration
- STDIO transport: spawns local `npx` / Python subprocesses
- HTTP/OAuth transport: connects to remote APIs (GitHub, Slack, etc.)
- Tools auto-discovered from server schemas and documented for the LLM
- See [MCP Integration](mcp-integration.md) for full details

### Auto Tool Documentation
- Tool schemas from MCP or function definitions → LLM-readable markdown
- Injected into the system prompt automatically
- Zero maintenance — schemas are the single source of truth

### Observability
- Opik tracing for both ADK and LangGraph engines
- AgentShip Studio right panel shows live tool call timeline and latency

## Directory Structure

```
src/
├── agent_framework/      # Core framework
│   ├── engines/          # ADK and LangGraph execution engines
│   ├── mcp/              # MCP client manager, registry, adapters
│   ├── registry/         # Agent auto-discovery
│   ├── session/          # Session storage adapters
│   ├── tools/            # Tool system
│   ├── prompts/          # Auto tool documentation generator
│   └── observability/    # Opik integration
├── all_agents/           # Your agents (auto-discovered)
└── service/              # FastAPI REST layer

studio/                   # AgentShip Studio (browser UI at /studio)
docs_sphinx/              # This documentation
```

## Data Flow

```
HTTP Request → FastAPI → AgentRegistry.get_agent()
    ↓
BaseAgent.chat() / BaseAgent.stream()
    ↓
ToolManager → MCPClientManager → MCP Server (tools)
    ↓
ExecutionEngine (ADK or LangGraph)
    ↓
LLM (via ADK runner or LiteLLM)
    ↓
SSE stream → Client
```
