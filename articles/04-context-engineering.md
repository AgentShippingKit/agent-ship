# Context Engineering with AgentShip

## What is Context Engineering?

**Context Engineering** is the art and science of crafting the right information for your AI agent at the right time. It's the successor to "prompt engineering" but goes far deeper.

While prompt engineering focuses on *how* you write the prompt, context engineering focuses on *what* information goes into the context window and *when*.

---

## The Context Window

Every LLM has a finite context window. Even with 128K+ tokens, you can't fit everything. Context engineering is about making every token count.

```
┌─────────────────────────────────────────────────────┐
│                   Context Window                     │
├─────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────┐  │
│  │  System Prompt (Instructions)                 │  │
│  │  - Role definition                            │  │
│  │  - Behavior guidelines                        │  │
│  │  - Output format                              │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Tools (Available Actions)                    │  │
│  │  - Tool descriptions                          │  │
│  │  - Input/Output schemas                       │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Conversation History (Memory)                │  │
│  │  - Previous messages                          │  │
│  │  - Tool calls and results                     │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Current Query (User Input)                   │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Context Engineering in AgentShip

AgentShip provides structured ways to manage context through configuration.

### 1. System Prompt (instruction_template)

The `instruction_template` in YAML is your primary context engineering tool.

```yaml
agent_name: health_assistant_agent
instruction_template: |
  You are an expert health assistant.
  
  # ROLE
  You help users understand their health data.
  
  # AVAILABLE DATA
  - Conversation insights (past 60 days)
  - Voice notes (past 30 days)
  - Medical reports (past 30 days)
  - Action items
  
  # TOOLS
  - fetch_action_items_tool: Get user's action items
  - create_action_item_tool: Create new action items
  
  # OUTPUT FORMAT
  Respond in JSON matching HealthAssistantOutput:
  - answer: str
  
  # GUIDELINES
  - Be concise but thorough
  - Only answer health-related questions
  - Suggest action items when appropriate
```

### 2. Tool Descriptions

Tools are context. The LLM reads tool descriptions to decide when to use them.

```yaml
tools:
  - type: function
    id: fetch_action_items_tool
    import: src.agents.tools.action_items_tool.ActionItemsTool
    method: run
```

The tool's docstring becomes context:

```python
class ActionItemsTool(BaseTool):
    """
    Fetches action items for a user.
    
    Use this when:
    - User asks about their tasks, to-dos, or action items
    - User asks "what do I need to do?"
    - User asks about pending or completed items
    
    Input:
    - user_id: str (required)
    - status: str (optional: TODO, IN_PROGRESS, DONE, SKIPPED)
    - limit: int (optional, default 20)
    
    Returns: List of action items with status, text, and dates.
    """
    
    def run(self, user_id: str, status: str = None, limit: int = 20) -> str:
        # Implementation
```

### 3. Input/Output Schemas

Schemas constrain the context and response format.

```python
class HealthAssistantInput(BaseModel):
    """Input for health assistant queries."""
    message: str = Field(description="The user's question")
    session_id: str = Field(description="Session for conversation context")
    user_id: str = Field(description="User for data access")

class HealthAssistantOutput(BaseModel):
    """Output from health assistant."""
    answer: str = Field(description="The response to the user")
```

---

## Context Engineering Strategies

### Strategy 1: Layered Instructions

Structure your instructions in layers of priority:

```yaml
instruction_template: |
  # IDENTITY (Who you are)
  You are a professional health assistant.
  
  # CONSTRAINTS (Hard rules)
  - NEVER provide medical diagnoses
  - ALWAYS recommend consulting a doctor for serious concerns
  - ONLY answer health-related questions
  
  # CAPABILITIES (What you can do)
  - Access conversation history
  - Fetch medical reports
  - Create and manage action items
  
  # PREFERENCES (Soft guidelines)
  - Be concise
  - Use markdown for readability
  - Suggest action items when appropriate
  
  # OUTPUT FORMAT (Response structure)
  Respond in JSON:
  - answer: str
```

### Strategy 2: Dynamic Context Injection

Use tools to inject relevant context at runtime:

```yaml
tools:
  # Summary agents provide condensed context
  - type: agent
    id: conversation_insights_summary
    agent_class: ...ConversationInsightsSummaryAgent
  
  # Raw data tools for detailed context when needed
  - type: function
    id: fetch_conversation_insights_tool
    import: ...ConversationInsightsTool
```

The agent can decide:
- Need overview? → Call summary agent
- Need details? → Call raw data tool

### Strategy 3: Context Windowing

For long conversations, manage what stays in context:

```python
class SessionManager:
    async def get_recent_messages(self, session_id: str, limit: int = 10):
        """Get only recent messages to fit context window."""
        messages = await self.get_all_messages(session_id)
        return messages[-limit:]  # Last N messages
```

### Strategy 4: Schema-Driven Context

Use Pydantic schemas to structure both input and output:

```python
# Clear, structured input
class TripPlannerInput(BaseModel):
    source: str = Field(description="Departure city")
    destination: str = Field(description="Destination city")
    travel_dates: str = Field(description="Travel dates")
    preferences: str = Field(description="User preferences")

# This becomes context the LLM can work with
```

---

## Writing Effective Instructions

### DO: Be Specific

```yaml
# ❌ Bad
instruction_template: |
  You are a helpful assistant.

# ✅ Good
instruction_template: |
  You are a health assistant that helps users understand their health data.
  
  You have access to:
  - Conversation history from the past 60 days
  - Voice notes from the past 30 days
  - Medical reports from the past 30 days
  
  Your responses should be:
  - Accurate based on available data
  - Concise but thorough
  - Friendly but professional
```

### DO: Define Output Format

```yaml
# ❌ Bad
instruction_template: |
  Return the answer.

# ✅ Good
instruction_template: |
  Your output should be JSON matching this format:
  {
    "answer": "Your response here",
    "confidence": "high/medium/low",
    "sources_used": ["tool1", "tool2"]
  }
```

### DO: Explain Tool Usage

```yaml
# ❌ Bad
instruction_template: |
  Use the tools available.

# ✅ Good
instruction_template: |
  TOOLS AVAILABLE:
  
  1. fetch_action_items_tool
     - Use when: User asks about tasks, to-dos, pending items
     - Input: {"user_id": "<user_id>"}
     - Returns: List of action items
  
  2. create_action_item_tool
     - Use when: User wants to add a new task
     - Input: {"user_id": "<user_id>", "action_item": "<text>"}
     - Returns: Created action item
  
  Always use the appropriate tool for the user's request.
```

### DO: Handle Edge Cases

```yaml
instruction_template: |
  EDGE CASES:
  
  - If no data is found: Say "I don't have any [data type] on record."
  - If tool fails: Try once more. If still fails, inform user of technical issue.
  - If question is not health-related: Politely decline and explain your scope.
  - If question requires medical advice: Recommend consulting a healthcare provider.
```

---

## Context Engineering for Sub-Agents

Each sub-agent should have focused, relevant context:

### Orchestrator (Broad Context)
```yaml
instruction_template: |
  You coordinate multiple specialists to plan trips.
  
  Available agents:
  1. flight_planner - For flight options
  2. hotel_planner - For accommodation
  3. trip_summary - For final summary
  
  Workflow: Call agents in order, combine outputs.
```

### Sub-Agent (Narrow Context)
```yaml
instruction_template: |
  You are a flight planning specialist.
  
  Given a source and destination, provide:
  - Best flight options
  - Price ranges
  - Duration estimates
  
  Focus ONLY on flights. Other agents handle hotels and summaries.
```

---

## Measuring Context Quality

### Signs of Good Context
- ✅ Agent uses tools appropriately
- ✅ Responses match expected format
- ✅ Agent stays on topic
- ✅ Edge cases are handled gracefully

### Signs of Poor Context
- ❌ Agent hallucinates capabilities
- ❌ Wrong tools are called
- ❌ Responses are off-format
- ❌ Agent goes off-topic

### Debugging Context Issues

1. **Check Observability**: See what the LLM received
2. **Simplify Instructions**: Remove complexity, add back gradually
3. **Test Tool Descriptions**: Ensure they're clear and specific
4. **Validate Schemas**: Confirm input/output match expectations

---

## Advanced: Context Compression

When context grows too large, compress it:

```yaml
tools:
  # Instead of fetching all conversations
  - type: function
    id: fetch_all_conversations
    import: ...
  
  # Use a summary agent that compresses context
  - type: agent
    id: conversation_summary
    agent_class: ...ConversationSummaryAgent
```

The summary agent turns 50 conversations into a concise summary that fits the context window.

---

## Summary

Context engineering in AgentShip involves:

1. **instruction_template**: Clear, layered, specific instructions
2. **Tool Descriptions**: Detailed docstrings that guide tool usage
3. **Schemas**: Structured input/output definitions
4. **Dynamic Injection**: Tools that bring in relevant context at runtime
5. **Compression**: Summary agents for large data sets

The goal: **Right information, right time, right format.**

---

*Next: Memory with AgentShip*

