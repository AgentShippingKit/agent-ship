Add an MCP server to this AgentShip project and wire it to an agent.

Details: $ARGUMENTS

Follow these steps:

1. If $ARGUMENTS is empty, ask the user:
   - MCP server name (e.g. `postgres`, `github`, `filesystem`, `brave-search`)
   - Transport type: `stdio` (local npx/Python process) or `http` (remote OAuth API)
   - Which agent(s) should use it (or create a new agent)

2. Read the current `.mcp.settings.json` to understand existing servers.

3. Add the new server entry to `.mcp.settings.json`:

**STDIO example (local npx server):**
```json
"<server_name>": {
  "transport": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-<name>", "${RELEVANT_ENV_VAR}"]
}
```

**HTTP/OAuth example (remote API):**
```json
"<server_name>": {
  "transport": "http",
  "url": "<mcp_endpoint_url>",
  "auth": {
    "type": "oauth",
    "provider": "<provider_name>",
    "client_id_env": "<CLIENT_ID_ENV_VAR>",
    "client_secret_env": "<CLIENT_SECRET_ENV_VAR>",
    "authorize_url": "<oauth_authorize_url>",
    "token_url": "<oauth_token_url>",
    "scopes": ["<scope1>"]
  }
}
```

4. Add the server to the target agent's `main_agent.yaml`:
```yaml
mcp:
  servers:
    - <server_name>
```

5. If the server uses env vars (`${VAR}`), remind the user to add them to `.env`.

6. If it's an HTTP/OAuth server, explain the connect flow:
```bash
pipenv run agentship mcp connect <server_name> --user-id <user_id>
# Opens browser for OAuth, stores token encrypted in DB
```
Note: HTTP/OAuth servers require `AGENTSHIP_AUTH_DB_URI` in `.env`.

7. Tell the user to run `make docker-restart` to reload, then test via AgentShip Studio at http://localhost:7001/studio.

## Popular STDIO servers

| Server | Package | Env var needed |
|--------|---------|----------------|
| PostgreSQL | `@modelcontextprotocol/server-postgres` | `AGENT_SESSION_STORE_URI` |
| Filesystem | `@modelcontextprotocol/server-filesystem` | path as arg, no env var |
| Memory | `@modelcontextprotocol/server-memory` | none |
| Brave Search | `@modelcontextprotocol/server-brave-search` | `BRAVE_API_KEY` |

## Key rules
- `${VAR}` tokens in `args` are resolved from the environment at startup
- STDIO clients are shared across agents (safe — no auth state)
- HTTP/OAuth clients are isolated per-agent to prevent token cross-contamination
- Node.js must be installed for `npx` servers (`brew install node` on macOS)
