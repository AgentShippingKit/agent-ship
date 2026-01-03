# Orchestrator Pattern

The orchestrator pattern coordinates multiple sub-agents to complete complex tasks.

## Example: Trip Planner Agent

```python
from src.all_agents.base_agent import BaseAgent

class TripPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            _caller_file=__file__,
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
    agent_class: src.all_agents.orchestrator_pattern.sub_agents.flight_agent.FlightPlannerAgent
  - type: agent
    id: hotel_planner
    agent_class: src.all_agents.orchestrator_pattern.sub_agents.hotel_agent.HotelPlannerAgent
  - type: agent
    id: trip_summary
    agent_class: src.all_agents.orchestrator_pattern.sub_agents.trip_summary_agent.TripSummaryAgent
```

## Use Cases

- Multi-step workflows
- Complex task coordination
- Hierarchical agent systems
