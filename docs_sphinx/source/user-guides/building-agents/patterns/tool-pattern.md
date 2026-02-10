# Tool Pattern

The tool pattern enables agents with comprehensive tooling capabilities.

## Example: Database Agent

```python
from src.all_agents.base_agent import BaseAgent

class DatabaseAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            _caller_file=__file__,
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
    import: src.agent_framework.tools.database_tool.DatabaseTool
    method: run
```

## Use Cases

- Database querying
- API integration
- External service interaction
- Complex tool orchestration
