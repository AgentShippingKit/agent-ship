# Agentic Design Patterns with AgentShip

## Introduction

Not all agents are built the same. Different problems require different architectures. AgentShip supports multiple **agentic design patterns** that help you choose the right approach for your use case.

This guide covers the three main patterns and when to use each.

---

## Pattern 1: Single Agent

### What It Is
A single agent handling one task. The simplest pattern.

```
┌─────────┐      ┌─────────┐      ┌─────────┐
│  User   │ ───▶ │  Agent  │ ───▶ │ Response│
└─────────┘      └─────────┘      └─────────┘
```

### When to Use
- ✅ Single, focused tasks
- ✅ Simple Q&A
- ✅ Translations
- ✅ Summarization
- ✅ Code generation
- ✅ Quick prototyping

### When NOT to Use
- ❌ Complex multi-step workflows
- ❌ Tasks requiring multiple specialized skills
- ❌ When you need parallel processing

### Implementation

**main_agent.yaml**:
```yaml
agent_name: translation_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.3
description: Translates text between languages
instruction_template: |
  You are a professional translator.
  
  Input format:
  - text: The text to translate
  - source_language: Source language
  - target_language: Target language
  
  Output format:
  - translated_text: The translated text
  
  Be accurate and preserve meaning, tone, and style.
```

**main_agent.py**:
```python
from src.agents.all_agents.base_agent import BaseAgent
from pydantic import BaseModel, Field

class TranslationInput(BaseModel):
    text: str = Field(description="Text to translate")
    source_language: str = Field(description="Source language")
    target_language: str = Field(description="Target language")

class TranslationOutput(BaseModel):
    translated_text: str = Field(description="Translated text")

class TranslationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TranslationInput,
            output_schema=TranslationOutput
        )
```

### Key Characteristics
- **Focused**: One agent, one responsibility
- **Fast**: No coordination overhead
- **Simple**: Easy to build, test, and maintain

---

## Pattern 2: Orchestrator (Multi-Agent)

### What It Is
A main agent that coordinates multiple specialized sub-agents. The orchestrator decides which agent to use and combines their outputs.

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │   Agent A   │   │   Agent B   │   │   Agent C   │
    │  (Flights)  │   │  (Hotels)   │   │  (Summary)  │
    └─────────────┘   └─────────────┘   └─────────────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Combined Result │
                    └─────────────────┘
```

### When to Use
- ✅ Complex workflows requiring multiple skills
- ✅ Multi-step processes
- ✅ Tasks that can be decomposed
- ✅ When you need specialized expertise per sub-task

### When NOT to Use
- ❌ Simple, single-purpose tasks
- ❌ When latency is critical (more agents = more time)
- ❌ When tasks can't be cleanly separated

### Implementation

**Orchestrator (main_agent.yaml)**:
```yaml
agent_name: trip_planner_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: Plans complete trips by coordinating multiple agents
instruction_template: |
  You are a trip planner that coordinates multiple specialists.
  
  Use these tools in order:
  1. flight_planner - Get flight options
  2. hotel_planner - Get hotel options  
  3. trip_summary - Create final summary
  
  Input: source, destination
  Output: flight_plan, hotel_plan, summary

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

**Orchestrator (main_agent.py)**:
```python
from src.agents.all_agents.base_agent import BaseAgent
from pydantic import BaseModel, Field

class TripPlannerInput(BaseModel):
    source: str = Field(description="Departure city")
    destination: str = Field(description="Destination city")

class TripPlannerOutput(BaseModel):
    flight_plan: str = Field(description="Flight details")
    hotel_plan: str = Field(description="Hotel details")
    summary: str = Field(description="Trip summary")

class TripPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TripPlannerInput,
            output_schema=TripPlannerOutput
        )
```

**Sub-Agent (flight_agent.yaml)**:
```yaml
agent_name: flight_planner_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: Plans flight routes
instruction_template: |
  You are a flight planning specialist.
  Given source and destination, provide flight options.
```

### Key Characteristics
- **Modular**: Each sub-agent has one job
- **Reusable**: Sub-agents can be used by other orchestrators
- **Scalable**: Add more sub-agents as needed
- **Maintainable**: Fix one sub-agent without touching others

---

## Pattern 3: Tool-Based Agent

### What It Is
An agent that uses external tools (functions, APIs, databases) to accomplish tasks. The agent decides when and how to use each tool.

```
                    ┌─────────────┐
                    │    Agent    │
                    └──────┬──────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
  ┌───────────┐     ┌───────────┐     ┌───────────┐
  │  Tool A   │     │  Tool B   │     │  Tool C   │
  │(Database) │     │  (API)    │     │(Calculate)│
  └───────────┘     └───────────┘     └───────────┘
```

### When to Use
- ✅ Need to fetch external data
- ✅ Database queries
- ✅ API integrations
- ✅ Calculations
- ✅ File operations
- ✅ When agent needs "hands"

### When NOT to Use
- ❌ Pure reasoning tasks
- ❌ When tools would be overkill
- ❌ Security-sensitive operations without safeguards

### Implementation

**main_agent.yaml**:
```yaml
agent_name: health_assistant_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: Health assistant with access to user data
instruction_template: |
  You are a health assistant with access to user health data.
  
  Available tools:
  - fetch_conversation_insights_tool: Get past conversations
  - fetch_voice_notes_tool: Get voice notes
  - fetch_medical_reports_tool: Get medical reports
  - fetch_action_items_tool: Get action items
  - create_action_item_tool: Create new action items
  
  Use the appropriate tool based on what the user asks.

tools:
  - type: function
    id: fetch_conversation_insights_tool
    import: src.agents.tools.conversation_insights_tool.ConversationInsightsTool
    method: run
  
  - type: function
    id: fetch_action_items_tool
    import: src.agents.tools.action_items_tool.ActionItemsTool
    method: run
  
  - type: function
    id: create_action_item_tool
    import: src.agents.tools.action_items_creation_tool.ActionItemsCreationTool
    method: run
```

**Custom Tool (conversation_insights_tool.py)**:
```python
from src.agents.tools.base_tool import BaseTool
from pydantic import BaseModel, Field

class ConversationInsightsInput(BaseModel):
    user_id: str = Field(description="User ID")
    limit: int = Field(default=10, description="Number of items")

class ConversationInsightsTool(BaseTool):
    """Fetches conversation insights from the database."""
    
    def run(self, user_id: str, limit: int = 10) -> str:
        # Fetch from database
        insights = self.database.query(
            "SELECT * FROM conversations WHERE user_id = %s LIMIT %s",
            (user_id, limit)
        )
        return json.dumps(insights)
```

### Key Characteristics
- **Extensible**: Add tools as needed
- **Grounded**: Tools provide real data
- **Powerful**: Agent + tools > agent alone
- **Safe**: Tools can have built-in safeguards

---

## Pattern 4: Hybrid (Orchestrator + Tools)

### What It Is
Combining orchestrator and tool patterns. Sub-agents that also have tools.

```
                    ┌─────────────────┐
                    │   Orchestrator  │
                    └────────┬────────┘
           ┌─────────────────┼─────────────────┐
           ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │   Agent A   │   │   Agent B   │   │   Agent C   │
    │   + Tools   │   │   + Tools   │   │   + Tools   │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           ▼                 ▼                 ▼
       [DB, API]        [Calculator]      [Storage]
```

### Example: Health Assistant

The health assistant orchestrates multiple sub-agents, each with their own tools:

```yaml
# Orchestrator with sub-agents and tools
tools:
  # Sub-agents for summarization
  - type: agent
    id: conversation_insights_summary
    agent_class: ...ConversationInsightsSummaryAgent
  
  - type: agent
    id: voice_notes_summary
    agent_class: ...VoiceNotesSummaryAgent
  
  # Direct tools for raw data
  - type: function
    id: fetch_action_items_tool
    import: ...ActionItemsTool
  
  # Sub-agent with its own logic
  - type: agent
    id: action_items_creation
    agent_class: ...ActionItemsCreationAgent
```

---

## Choosing the Right Pattern

| Pattern | Complexity | Latency | Use Case |
|---------|------------|---------|----------|
| **Single** | Low | Fast | Simple tasks, Q&A |
| **Orchestrator** | Medium | Medium | Multi-step workflows |
| **Tool-Based** | Medium | Varies | External data, APIs |
| **Hybrid** | High | Slower | Complex real-world apps |

### Decision Tree

```
Is the task simple and focused?
├── YES → Single Agent
└── NO → Does it need external data?
    ├── YES → Tool-Based Agent
    └── NO → Does it need multiple specialized skills?
        ├── YES → Orchestrator Pattern
        └── NO → Single Agent (reconsider task breakdown)
```

---

## Best Practices

### 1. Start Simple
Begin with a single agent. Add complexity only when needed.

### 2. Single Responsibility
Each agent/tool should do one thing well.

### 3. Clear Interfaces
Define input/output schemas explicitly.

### 4. Tool Descriptions Matter
LLMs use tool descriptions to decide when to call them. Be specific.

### 5. Test Sub-Agents Independently
Before integrating, ensure each sub-agent works correctly.

### 6. Monitor Agent Interactions
Use observability to see which agents/tools are called and when.

---

## Summary

AgentShip supports multiple patterns:

1. **Single Agent**: Simple, fast, focused
2. **Orchestrator**: Coordinate multiple agents
3. **Tool-Based**: External data and actions
4. **Hybrid**: Combine patterns as needed

Choose based on your use case. Start simple, evolve as needed.

---

*Next: Context Engineering with AgentShip*

