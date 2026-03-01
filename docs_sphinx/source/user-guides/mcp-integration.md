# MCP Integration

AgentShip has built-in support for the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/), letting agents connect to any MCP server as a tool source. Works with both ADK and LangGraph engines.

## Transports

| Transport | Use case | Auth |
|-----------|----------|------|
| `stdio` | Local servers (npx, Python scripts) | Env vars |
| `http` / `sse` | Remote APIs (GitHub, Slack, etc.) | OAuth 2.0 |

## Configuration

### 1. Define servers in `.mcp.settings.json`

```json
{
  "servers": {
    "postgres": {
      "transport": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-postgres",
        "${AGENT_SESSION_STORE_URI}"
      ]
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
    },
    "filesystem": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
    }
  }
}
```

`${VAR}` tokens in `args` are resolved from the environment at startup.

### 2. Reference servers in your agent YAML

```yaml
agent_name: database_agent
execution_engine: adk   # or langgraph — both work

mcp:
  servers:
    - postgres   # STDIO: shared client across agents
    - github     # HTTP/OAuth: per-agent client
```

That's it. AgentShip automatically:
- Connects to each MCP server
- Discovers available tools
- Generates documentation for the LLM
- Injects it into the system prompt

## How It Works

```
.mcp.settings.json
    ↓
MCPServerRegistry (loads + resolves env vars)
    ↓
MCPClientManager (one client per server, or per agent for OAuth)
    ↓
StdioMCPClient / SSEMCPClient
    ↓
Tool Discovery → LLM-friendly documentation → System prompt
```

## STDIO Servers (Local)

STDIO servers run as local subprocesses via `npx` or Python. They start when the agent initialises and reconnect automatically if the event loop changes (normal in production ASGI servers).

### Popular STDIO servers

| Server | Package | Provides |
|--------|---------|---------|
| PostgreSQL | `@modelcontextprotocol/server-postgres` | SQL queries |
| Filesystem | `@modelcontextprotocol/server-filesystem` | File read/write |
| Memory | `@modelcontextprotocol/server-memory` | Key-value store |
| Brave Search | `@modelcontextprotocol/server-brave-search` | Web search |

See [MCP Servers](https://github.com/modelcontextprotocol/servers) for the full list.

### Example: PostgreSQL agent

```yaml
agent_name: postgres_agent
execution_engine: adk
instruction_template: |
  You are a database assistant. Use the available tools to query and analyse data.

mcp:
  servers:
    - postgres
```

```json
{
  "servers": {
    "postgres": {
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${AGENT_SESSION_STORE_URI}"]
    }
  }
}
```

## HTTP/OAuth Servers (Remote)

HTTP/SSE servers connect to remote APIs using OAuth 2.0. Each agent gets its own client to prevent token cross-contamination.

**Requirements:** Set `AGENTSHIP_AUTH_DB_URI` in your `.env` — this is where OAuth tokens are stored (encrypted with Fernet).

### Connect a user

```bash
pipenv run agentship mcp connect github --user-id alice
# Opens browser → GitHub OAuth → token stored automatically
```

```bash
pipenv run agentship mcp list-connections --user-id alice
pipenv run agentship mcp disconnect github --user-id alice
```

### Example: GitHub agent

See `src/all_agents/github_adk_mcp_agent/` and `src/all_agents/github_langgraph_mcp_agent/` for complete working examples.

## Auto Tool Documentation

Tools discovered from MCP servers are automatically documented and injected into the agent's system prompt. No manual work needed.

Given this MCP tool schema:

```json
{
  "name": "query",
  "description": "Execute a read-only SQL query",
  "inputSchema": {
    "properties": {
      "sql": {"type": "string", "description": "SQL to run"}
    },
    "required": ["sql"]
  }
}
```

AgentShip generates and injects:

```
## Available Tools

### query
Execute a read-only SQL query

Parameters:
- sql (string, required): SQL to run

Example: {"sql": "SELECT * FROM users LIMIT 10"}
```

## Client Isolation

STDIO clients are shared across agents (safe — no auth state). OAuth clients are isolated per agent:

- STDIO cache key: `"{server_id}"`
- OAuth cache key: `"{server_id}:{agent_name}"`

This ensures users of one agent can't access tokens belonging to another.

## Troubleshooting

**"Event loop changed, reconnecting…"** — Normal in production. STDIO clients auto-reconnect on each request.

**`ValueError: AGENTSHIP_AUTH_DB_URI`** — Required for HTTP/OAuth servers. Add to `.env`.

**Tools not appearing** — Check that the server name in YAML matches the key in `.mcp.settings.json`.

**`npx` not found** — Install Node.js: `brew install node` (macOS) or see [nodejs.org](https://nodejs.org).
