# Tool Pattern

The tool pattern enables agents with comprehensive tooling capabilities.

## Example: Database Agent

```python
from src.agents.all_agents.base_agent import BaseAgent
from src.agents.utils.path_utils import resolve_config_path

class DatabaseAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__)
        )
```

## Configuration

```yaml
agent_name: database_agent
llm_provider_name: openai
llm_model: gpt-4o
description: Natural language database queries
tools:
  - type: function
    id: database_tool
    import: src.agents.tools.database_tool.DatabaseTool
    method: run
```

## Use Cases

- Database querying
- API integration
- External service interaction
- Complex tool orchestration
