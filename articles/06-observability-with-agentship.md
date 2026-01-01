# Observability with AgentShip

## Why Observability Matters

AI agents are non-deterministic. The same input can produce different outputs. They call tools, make decisions, and sometimes fail in unexpected ways.

Without observability, you're flying blind.

**Observability answers:**
- Why did the agent make that decision?
- Which tools were called and what did they return?
- How many tokens were used?
- Where is latency coming from?
- Why did this request fail?

---

## AgentShip's Observability Stack

AgentShip uses **Opik** for observability. Opik provides:

- **Tracing**: End-to-end visibility into agent execution
- **Metrics**: Token usage, latency, success rates
- **Logging**: Structured logs for debugging
- **Callbacks**: Hooks for custom observability

```
┌─────────────────────────────────────────────────────────────────┐
│                      Agent Execution                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Request ─▶ Agent ─▶ Model Call ─▶ Tool Calls ─▶ Response       │
│     │         │          │             │            │            │
│     ▼         ▼          ▼             ▼            ▼            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Opik Tracer                           │   │
│  │                                                          │   │
│  │  Trace: agent-execution-123                              │   │
│  │  ├─ Span: before_agent                                   │   │
│  │  ├─ Span: model_call                                     │   │
│  │  │   └─ Tokens: prompt=150, completion=80                │   │
│  │  ├─ Span: tool_call (fetch_action_items)                 │   │
│  │  │   └─ Duration: 120ms                                  │   │
│  │  ├─ Span: model_call                                     │   │
│  │  └─ Span: after_agent                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│                    ┌──────────────────┐                         │
│                    │  Opik Dashboard  │                         │
│                    └──────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Setting Up Observability

### 1. Configuration

```bash
# .env
OPIK_API_KEY=your-api-key
OPIK_WORKSPACE=your-workspace
OPIK_PROJECT_NAME=agentship
ENVIRONMENT=production
```

### 2. Opik Settings

```python
# src/agents/configs/opik_config.py

class OpikSettings(BaseSettings):
    """Opik observability configuration."""
    
    OPIK_API_KEY: str = os.getenv("OPIK_API_KEY")
    OPIK_WORKSPACE: str = os.getenv("OPIK_WORKSPACE")
    OPIK_PROJECT_NAME: str = os.getenv("OPIK_PROJECT_NAME")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    OPIK_FRAMEWORK: str = "google-adk"
    OPIK_LITTELM_INTEGRATION: str = "true"
    OPIK_TRACING_METHODS: List[str] = ["decorators", "callbacks"]
```

### 3. Automatic Integration

Observability is automatic in AgentShip. When you create an agent, Opik is configured:

```python
# In BaseAgent.__init__
self.observer = create_observer(self.agent_config)
```

---

## The Observer Pattern

AgentShip uses an observer pattern for observability:

```python
# src/agents/observability/base.py

class BaseObserver(abc.ABC):
    """Base class for all observability."""
    
    @abc.abstractmethod
    def setup(self) -> None:
        """Setup the observability."""
    
    @abc.abstractmethod
    def before_agent_callback(self, callback_context: CallbackContext) -> None:
        """Called before agent execution."""
    
    @abc.abstractmethod
    def after_agent_callback(self, callback_context: CallbackContext) -> None:
        """Called after agent execution."""
    
    @abc.abstractmethod
    def before_tool_callback(self, callback_context: CallbackContext) -> None:
        """Called before tool execution."""
    
    @abc.abstractmethod
    def after_tool_callback(self, callback_context: CallbackContext) -> None:
        """Called after tool execution."""
    
    @abc.abstractmethod
    def before_model_callback(self, callback_context: CallbackContext, llm_request: LlmRequest) -> None:
        """Called before model call."""
    
    @abc.abstractmethod
    def after_model_callback(self, callback_context: CallbackContext, llm_response) -> None:
        """Called after model call."""
```

---

## Opik Observer Implementation

```python
# src/agents/observability/opik.py

class OpikObserver(BaseObserver):
    """Opik observability implementation."""
    
    def __init__(self, agent_config: AgentConfig):
        super().__init__(agent_config)
    
    def setup(self) -> None:
        """Configure Opik tracer."""
        self.tracer = OpikTracer(
            name=self.agent_config.agent_name,
            tags=self.agent_config.tags,
            metadata={
                "model": self.agent_config.model.value,
                "environment": opik_settings.ENVIRONMENT,
                "framework": opik_settings.OPIK_FRAMEWORK,
            },
            project_name=opik_settings.OPIK_PROJECT_NAME
        )
    
    def before_agent_callback(self, *args, **kwargs) -> None:
        """Track agent start."""
        if self.tracer:
            self.tracer.before_agent_callback(*args, **kwargs)
    
    def after_agent_callback(self, *args, **kwargs) -> None:
        """Track agent completion."""
        if self.tracer:
            self.tracer.after_agent_callback(*args, **kwargs)
    
    def before_model_callback(self, *args, **kwargs) -> None:
        """Track model call start."""
        if self.tracer:
            self.tracer.before_model_callback(*args, **kwargs)
    
    def after_model_callback(self, *args, **kwargs) -> None:
        """Track model call with token usage."""
        if self.tracer:
            # Extract and format token usage
            if 'llm_response' in kwargs:
                usage_metadata = kwargs['llm_response'].usage_metadata
                if usage_metadata:
                    kwargs['usage'] = {
                        "prompt_token_count": usage_metadata.prompt_token_count,
                        "candidates_token_count": usage_metadata.candidates_token_count,
                        "total_token_count": usage_metadata.total_token_count,
                    }
            self.tracer.after_model_callback(*args, **kwargs)
```

---

## What Gets Traced

### 1. Agent Execution
- Agent name
- Input/output
- Duration
- Success/failure

### 2. Model Calls
- Model used (gpt-4o, gemini, etc.)
- Prompt tokens
- Completion tokens
- Total tokens
- Latency

### 3. Tool Calls
- Tool name
- Input parameters
- Output
- Duration
- Errors

### 4. Session Information
- Session ID
- User ID
- Conversation turn

---

## Viewing Traces in Opik

Once configured, traces appear in your Opik dashboard:

```
Project: agentship
├── Trace: health_assistant_agent (200ms)
│   ├── Span: before_agent
│   ├── Span: model_call (gpt-4o)
│   │   ├── Prompt: 150 tokens
│   │   ├── Completion: 80 tokens
│   │   └── Duration: 120ms
│   ├── Span: tool_call (fetch_action_items_tool)
│   │   ├── Input: {"user_id": "123"}
│   │   ├── Output: [{"id": 1, "text": "..."}]
│   │   └── Duration: 45ms
│   ├── Span: model_call (gpt-4o)
│   │   └── Duration: 35ms
│   └── Span: after_agent
└── Metadata
    ├── Agent: health_assistant_agent
    ├── Model: gpt-4o
    ├── Environment: production
    └── Session: session-456
```

---

## Key Metrics

### Token Usage
```
Total Tokens = Prompt Tokens + Completion Tokens

Cost = (Prompt Tokens × Prompt Price) + (Completion Tokens × Completion Price)
```

Track this to:
- Optimize prompts
- Estimate costs
- Identify inefficient agents

### Latency
```
Total Latency = Model Latency + Tool Latency + Overhead

Breakdown:
- Model calls: Usually 100-500ms each
- Tool calls: Depends on external services
- Overhead: Usually <10ms
```

Track this to:
- Identify bottlenecks
- Optimize tool calls
- Improve user experience

### Success Rate
```
Success Rate = Successful Requests / Total Requests × 100%
```

Track this to:
- Monitor reliability
- Identify failure patterns
- Set alerts

---

## Debugging with Observability

### Scenario 1: Wrong Tool Called

**Symptom**: Agent calls the wrong tool

**Debug Steps**:
1. Find the trace in Opik
2. Look at the model call before the tool call
3. Check what the model "thought" based on the prompt
4. Adjust tool descriptions or instructions

### Scenario 2: High Latency

**Symptom**: Responses are slow

**Debug Steps**:
1. Find the trace in Opik
2. Look at the span durations
3. Identify the slow component (model? tool? database?)
4. Optimize that component

### Scenario 3: Unexpected Output

**Symptom**: Agent gives wrong answer

**Debug Steps**:
1. Find the trace in Opik
2. Look at the full conversation context
3. Check tool outputs (was data correct?)
4. Review the model's reasoning

---

## Custom Observability

You can extend the observer for custom tracking:

```python
class CustomObserver(OpikObserver):
    """Extended observer with custom tracking."""
    
    def after_tool_callback(self, *args, **kwargs):
        """Track custom tool metrics."""
        super().after_tool_callback(*args, **kwargs)
        
        # Custom tracking
        tool_name = kwargs.get('tool_name')
        duration = kwargs.get('duration')
        
        # Send to custom metrics system
        metrics.increment(f"tool.{tool_name}.calls")
        metrics.timing(f"tool.{tool_name}.duration", duration)
```

---

## Best Practices

### 1. Always Enable in Production
Observability is essential for production debugging.

### 2. Use Meaningful Tags
```python
agent_config.tags = ["health", "assistant", "production"]
```

### 3. Set Up Alerts
Monitor for:
- Error rate > 5%
- Latency > 5s
- Token usage spikes

### 4. Regular Reviews
Weekly review of:
- Top errors
- Slowest requests
- Most expensive agents

### 5. Environment Separation
Use different projects for:
- Development
- Staging
- Production

---

## Summary

AgentShip's observability with Opik provides:

1. **Tracing**: Full visibility into agent execution
2. **Metrics**: Token usage, latency, success rates
3. **Debugging**: Understand why agents behave as they do
4. **Optimization**: Identify and fix bottlenecks

Observability is not optional—it's how you maintain production AI systems.

---

*Next: Evals with AgentShip*

