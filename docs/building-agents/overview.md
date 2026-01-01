# Building Agents

## Overview

Agents in this framework are built by extending `BaseAgent` and providing configuration through YAML files. The framework handles all the infrastructure—you focus on defining your agent's behavior.

## Agent Lifecycle

1. **Discovery**: Agents are automatically discovered from the filesystem
2. **Registration**: Agents register themselves with the `AgentRegistry` on startup
3. **Configuration**: Configuration is loaded from YAML files
4. **Initialization**: `BaseAgent` handles LLM setup, tool creation, and observability
5. **Execution**: Agents process requests through the `chat()` method

## Agent Patterns

The framework supports three proven patterns:

- **[Single Agent](patterns/single-agent.md)**: Standalone agents for focused tasks
- **[Orchestrator](patterns/orchestrator.md)**: Coordinate multiple sub-agents
- **[Tool Pattern](patterns/tool-pattern.md)**: Agents with comprehensive tooling

## Key Concepts

**BaseAgent**: The base class all agents extend. Handles configuration, session management, and LLM setup.

**AgentConfig**: YAML-based configuration for agent behavior, LLM settings, and tools.

**Tools**: Function tools or agent tools that extend agent capabilities.

**Session Management**: Automatic session creation and persistence for conversation history.

See the [API Reference](../api/base-agent.md) for complete details.
