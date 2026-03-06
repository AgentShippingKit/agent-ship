Help the user work with AgentShip Studio — the browser-based agent testing interface.

Query: $ARGUMENTS

AgentShip Studio is at http://localhost:7001/studio (legacy /debug-ui redirects here).

## Common tasks

### Open Studio
```bash
open http://localhost:7001/studio
```
Make sure the server is running first: `make docker-up`

### Check which agents are available
```bash
curl -s http://localhost:7001/api/debug/agents | python3 -m json.tool
```

### Check an agent's engine/model config
```bash
curl -s http://localhost:7001/api/debug/agents/<agent_name>/config
# Returns: {"engine": "adk"|"langgraph", "model": "...", "provider": "...", "streaming_mode": "..."}
```

### Get an agent's input schema (to know what fields to fill in)
```bash
curl -s http://localhost:7001/api/debug/agents/<agent_name>/schema
```

### Test an agent via API (equivalent to Studio chat)
```bash
curl -X POST http://localhost:7001/api/debug/chat \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "<agent_name>",
    "message": "your message here",
    "session_id": "test-session",
    "user_id": "test-user"
  }'
```

### Stream a response (SSE)
```bash
curl -X POST http://localhost:7001/api/debug/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "<agent_name>", "message": "hello", "session_id": "s1", "user_id": "u1"}'
```
Events streamed: `thinking`, `content` (token), `tool_call`, `tool_result`, `error`, `done`

## Studio UI features

| Feature | How to use |
|---------|------------|
| Select agent | Click agent name in left sidebar |
| Engine badge | Header shows ADK (green) or LangGraph (purple) + model name |
| Send message | Type in textarea → Enter or Send button |
| Stop streaming | Click red Stop button while response is generating |
| New conversation | Click "New chat" button |
| Previous conversations | Click saved sessions under each agent in sidebar |
| Feedback | Hover over assistant message → 👍 👎 buttons appear |
| Observability | Right panel → Activity tab for tool calls + latency |
| Schema | Right panel → Schema tab for input/output field docs |
| Dark/light mode | Toggle button in top-right corner |

## Troubleshooting

**Agent not appearing in sidebar**
- Agent directory exists in `src/all_agents/`?
- `main_agent.yaml` has valid `agent_name`?
- Run `make docker-restart` to trigger auto-discovery

**Engine badge shows "unknown"**
- The `/api/debug/agents/<name>/config` endpoint failed
- Check that `agent.agent_config.execution_engine` is set in YAML

**Tools not showing in obs panel**
- Only MCP and function tool calls appear
- Make sure the agent is configured with `mcp.servers` in YAML

**"Event loop changed, reconnecting…" in logs**
- Normal for STDIO MCP clients in ASGI servers — auto-reconnects each request
