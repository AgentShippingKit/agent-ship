# Testing

## Overview

The framework includes a comprehensive test suite with mocked LLM calls for fast, reliable testing.

## Running Tests

```bash
# Run all tests
pipenv run pytest tests/ -v

# Run agent-specific tests
pipenv run pytest tests/unit/agents/all_agents/ -v

# Run with coverage
pipenv run pytest tests/ --cov=src/agents
```

## Test Structure

- **Unit Tests**: Test individual components (config loading, I/O handling, tool building)
- **Integration Tests**: Test agent discovery and registration
- **Agent Tests**: Test each agent with mocked LLM calls

All tests use mocked LLM responses, so they run fast and don't require API keys.

## Writing Tests

See [Writing Tests](writing-tests.md) for a guide on writing tests for your agents.
