# Orchestrator Pattern

The orchestrator pattern coordinates multiple sub-agents to complete complex tasks.

## Example: Trip Planner Agent

```python
from src.agents.all_agents.base_agent import BaseAgent
from src.agents.utils.path_utils import resolve_config_path

class TripPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            config_path=resolve_config_path(relative_to=__file__),
            agent_type=AgentType.SEQUENTIAL_AGENT
        )
```

## Configuration

```yaml
agent_name: trip_planner
llm_provider_name: openai
llm_model: gpt-4o
description: Coordinates trip planning with flight and hotel agents
tools:
  - type: agent
    id: flight_planner
    agent_class: src.agents.all_agents.orchestrator_pattern.sub_agents.flight_agent.FlightPlannerAgent
  - type: agent
    id: hotel_planner
    agent_class: src.agents.all_agents.orchestrator_pattern.sub_agents.hotel_agent.HotelPlannerAgent
  - type: agent
    id: trip_summary
    agent_class: src.agents.all_agents.orchestrator_pattern.sub_agents.trip_summary_agent.TripSummaryAgent
```

## Use Cases

- Multi-step workflows
- Complex task coordination
- Hierarchical agent systems
