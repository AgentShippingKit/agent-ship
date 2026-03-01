# Agent Configuration

Agent configuration is managed through YAML files. The YAML filename must match the Python filename (e.g., `main_agent.yaml` for `main_agent.py`).

## Configuration File Structure

```yaml
agent_name: translation_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
execution_engine: langgraph  # or "adk"
streaming_mode: token_based  # or "event_based", "none"
description: Translates text between languages
instruction_template: |
  You are a translation expert...
tags:
  - translation
  - language
tools:
  - type: function
    id: custom_tool
    import: src.agent_framework.tools.my_tool.MyTool
    method: run
  - type: agent
    id: sub_agent
    agent_class: src.all_agents.sub_agent.SubAgent
memory:
  enabled: true
  backend: database
```

## Configuration Fields

### Required Fields

- `agent_name`: Unique identifier for the agent
- `llm_provider_name`: LLM provider (`openai`, `google`, `anthropic`)
- `llm_model`: Model name (e.g., `gpt-4o`, `gemini-2.0-flash-exp`)
- `description`: Agent description
- `instruction_template`: System prompt for the agent

### Optional Fields

- `temperature`: LLM temperature (default: 0.4)
- `execution_engine`: Execution engine to use (default: `adk`)
- `streaming_mode`: Streaming behavior (default: `chunk`)
- `tags`: List of tags for categorization
- `tools`: List of tools (function or agent tools)
- `memory`: Memory configuration (see below)

## Execution Engines

AgentShip supports multiple execution engines for running agents:

| Engine | Description | Best For |
|--------|-------------|----------|
| `adk` | Google ADK-based engine | Tool calling, sub-agents, Google AI integration |
| `langgraph` | LangGraph + LiteLLM engine | True token streaming, multi-provider support |

### ADK Engine (Default)

```yaml
execution_engine: adk
```

- Built on Google's Agent Development Kit
- Supports tool calling and sub-agents
- Event-based streaming only
- Session management via ADK's built-in session service

### LangGraph Engine

```yaml
execution_engine: langgraph
```

- Built on LangGraph + LiteLLM
- Supports true token-by-token streaming
- Works with OpenAI, Claude, Gemini, and other LiteLLM-supported providers
- In-memory conversation history (per session)

## Streaming Modes

Configure how agent responses are streamed to clients.

### Streaming Mode Values

| Mode | YAML Value | Description |
|------|------------|-------------|
| **No Streaming** | `none` | Return complete response only (no intermediate events) |
| **Event-Based** | `event_based` or `chunk` | Stream response in chunks/events |
| **Token-Based** | `token_based` or `token` | Stream individual tokens as they arrive |

### Engine Support Matrix

| Streaming Mode | ADK Engine | LangGraph Engine |
|----------------|------------|------------------|
| `none` | Not supported (always streams) | Supported |
| `event_based` / `chunk` | Supported | Supported |
| `token_based` / `token` | **Not truly supported** - same as event_based | **Fully supported** - real token streaming |

### Example Configuration

```yaml
# For real token-by-token streaming (ChatGPT-like effect)
execution_engine: langgraph
streaming_mode: token_based

# For chunk-based streaming
execution_engine: adk
streaming_mode: chunk
```

> **Note**: If you need true token-by-token streaming (word-by-word animation in UI), use `langgraph` engine with `token_based` mode. ADK does not support real token streaming due to LiteLLM integration limitations.

## Tools Configuration

### Function Tools

```yaml
tools:
  - type: function
    id: my_tool
    import: src.agent_framework.tools.my_tool.MyTool
    method: run
```

### Agent Tools

```yaml
tools:
  - type: agent
    id: sub_agent
    agent_class: src.all_agents.sub_agent.SubAgent
```

Tool order matters and is preserved from the YAML configuration.

### MCP Tools

Reference any MCP server defined in `.mcp.settings.json`:

```yaml
mcp:
  servers:
    - postgres      # STDIO: shared client
    - github        # HTTP/OAuth: per-agent client
```

See [MCP Integration](../mcp-integration.md) for setup details.

> **Note**: Custom function/agent tools are supported in the ADK engine. Both engines support MCP tools — see [MCP Integration](../mcp-integration.md).

## Memory Configuration

Configure session memory for agents. Memory allows agents to maintain conversation context across requests.

### Memory Options

```yaml
memory:
  enabled: true
  backend: database  # or "vertexai", "in_memory"
```

### Memory Backends

| Backend | Description | Engine Support |
|---------|-------------|----------------|
| `database` | PostgreSQL-backed session storage | ADK, LangGraph |
| `vertexai` | Google Vertex AI session storage | ADK only |
| `in_memory` | In-memory storage (lost on restart) | ADK, LangGraph |

### Engine-Specific Behavior

**ADK Engine:**
- Uses ADK's built-in session service
- Database backend stores sessions in PostgreSQL
- Full session state persistence

**LangGraph Engine:**
- Uses LangGraph's native checkpointer for conversation history
- `AsyncPostgresSaver`: Database-backed persistence (when `AGENT_SHORT_TERM_MEMORY=Database`)
- `InMemorySaver`: In-memory storage for development/testing
- History is maintained per `user_id:session_id` thread
- Follows [LangGraph Memory Pattern](https://docs.langchain.com/oss/python/langgraph/add-memory)

### Example: Enable Memory

```yaml
agent_name: my_agent
execution_engine: langgraph
streaming_mode: token_based
memory:
  enabled: true
  backend: database
```

## Complete Example

Here's a complete agent configuration using LangGraph with token streaming:

```yaml
agent_name: health_assistant
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
execution_engine: langgraph
streaming_mode: token_based
description: A health assistant that provides helpful information
instruction_template: |
  You are a knowledgeable health assistant. Provide accurate, 
  helpful information about health topics. Always recommend 
  consulting a healthcare professional for medical advice.
tags:
  - health
  - assistant
memory:
  enabled: true
  backend: database
```
