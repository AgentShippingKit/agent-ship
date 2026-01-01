# Agent Configuration

Agent configuration is managed through YAML files. The YAML filename must match the Python filename (e.g., `main_agent.yaml` for `main_agent.py`).

## Configuration File Structure

```yaml
agent_name: translation_agent
llm_provider_name: openai
llm_model: gpt-4o
temperature: 0.4
description: Translates text between languages
instruction_template: |
  You are a translation expert...
tags:
  - translation
  - language
tools:
  - type: function
    id: custom_tool
    import: src.agents.tools.my_tool.MyTool
    method: run
  - type: agent
    id: sub_agent
    agent_class: src.agents.all_agents.sub_agent.SubAgent
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
- `tags`: List of tags for categorization
- `tools`: List of tools (function or agent tools)

## Tools Configuration

### Function Tools

```yaml
tools:
  - type: function
    id: my_tool
    import: src.agents.tools.my_tool.MyTool
    method: run
```

### Agent Tools

```yaml
tools:
  - type: agent
    id: sub_agent
    agent_class: src.agents.all_agents.sub_agent.SubAgent
```

Tool order matters and is preserved from the YAML configuration.
