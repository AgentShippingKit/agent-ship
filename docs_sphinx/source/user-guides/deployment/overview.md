# Deployment

AgentShip is designed for production from day one — the same `make docker-setup` you use locally produces a production-ready container with PostgreSQL sessions, observability, and health checks included.

## Supported Platforms

- **[Docker](../../user-guides/docker-setup.md)** — `make docker-setup`, runs anywhere
- **[Heroku](heroku.md)** — `make heroku-deploy`, one command with PostgreSQL addon
- **Cloud Run / AWS ECS** — coming soon (the Docker image works today)

## Deployment Checklist

- [ ] Set at least one LLM API key (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GOOGLE_API_KEY`)
- [ ] Set `AGENT_SESSION_STORE_URI` (PostgreSQL connection string)
- [ ] Set `AGENT_SHORT_TERM_MEMORY=Database` for persistent sessions
- [ ] Set `LOG_LEVEL=INFO` and `ENVIRONMENT=production`
- [ ] Verify health check: `GET /health`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | One of these | LLM provider key |
| `ANTHROPIC_API_KEY` | One of these | LLM provider key |
| `GOOGLE_API_KEY` | One of these | LLM provider key |
| `AGENT_SESSION_STORE_URI` | Yes (production) | PostgreSQL URI |
| `AGENT_SHORT_TERM_MEMORY` | No | `Database` or `InMemory` |
| `AGENTSHIP_AUTH_DB_URI` | For OAuth MCP | PostgreSQL URI for OAuth tokens |

See [Configuration](../getting-started/configuration.md) for the full list.

## Health Check

```bash
curl http://your-deployment-url/health
```

Returns memory usage and status. Target: under 512 MB.

## Observability

Opik tracing is built in — enable it with environment variables. No code changes needed:

- Request/response tracing for every agent call
- Tool call timeline and latency (visible in AgentShip Studio)
- Token usage tracking per request

## Ports

| Service | Port |
|---------|------|
| API / Swagger / Studio | 7001 |
| PostgreSQL (Docker host) | 5433 |
| PostgreSQL (container internal) | 5432 |
