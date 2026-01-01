# Configuration

## Environment Variables

### Required

**LLM Provider** (at least one required):

```bash
OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**Database** (required for session management):

```bash
SESSION_STORE_URI=postgresql://user:password@host:port/database
```

### Optional

**Observability**:

```bash
OPIK_API_KEY=your_opik_api_key
OPIK_WORKSPACE=your_workspace
OPIK_PROJECT_NAME=your_project
```

**Agent Discovery**:

```bash
# Defaults to all agents
AGENT_DIRECTORIES=src/agents/all_agents

# For open-source only agents:
AGENT_DIRECTORIES=src/agents/all_agents/orchestrator_pattern,src/agents/all_agents/single_agent_pattern
```

**Logging**:

```bash
LOG_LEVEL=INFO
ENVIRONMENT=development
```

## Agent Configuration

Agent configuration is managed through YAML files. See [Agent Configuration](../building-agents/agent-configuration.md) for details.
