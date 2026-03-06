Create a new AgentShip agent using the standard 2-file pattern.

Agent details: $ARGUMENTS

Follow these steps:

1. Ask the user for any missing details if $ARGUMENTS is empty or incomplete. You need:
   - `agent_name` (snake_case, e.g. `weather_agent`)
   - `execution_engine` — `adk` or `langgraph` (default: `adk`)
   - `llm_model` — e.g. `gpt-4o`, `claude-sonnet-4-6` (default: `gpt-4o`)
   - `description` — one sentence describing what the agent does
   - `instruction_template` — system prompt for the agent
   - Whether MCP servers are needed (optional)

2. Create the directory: `src/all_agents/<agent_name>/`

3. Create `src/all_agents/<agent_name>/main_agent.yaml`:
```yaml
agent_name: <agent_name>
llm_provider_name: openai        # or anthropic / google
llm_model: <llm_model>
temperature: 0.4
execution_engine: <engine>       # adk or langgraph
streaming_mode: token_based      # token_based (langgraph) or event_based (adk)
description: <description>
instruction_template: |
  <instruction_template>
# Optional — add if MCP tools needed:
# mcp:
#   servers:
#     - postgres
```

4. Create `src/all_agents/<agent_name>/main_agent.py`:
```python
from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput
from src.agent_framework.utils.path_utils import resolve_config_path


class <PascalCaseName>Agent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            input_schema=TextInput,
            output_schema=TextOutput,
        )
```

5. Tell the user:
   - Files created at `src/all_agents/<agent_name>/`
   - Run `make docker-restart` to auto-discover the agent
   - Test at http://localhost:7001/studio — pick `<agent_name>` from the sidebar
   - Or curl: `curl -X POST http://localhost:7001/api/agents/chat -H "Content-Type: application/json" -d '{"agent_name": "<agent_name>", "user_id": "test", "session_id": "s1", "query": {"text": "hello"}, "features": []}'`

Rules:
- `agent_name` in YAML must be snake_case and match the directory name
- Class name must be PascalCase + "Agent"
- Do NOT create `__init__.py` — not needed
- If the user wants custom input fields beyond `text`, define a custom Pydantic model and use it for `input_schema`
