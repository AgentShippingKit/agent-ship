# Tools

Tools extend agent capabilities by providing access to functions or other agents.

## Function Tools

Function tools import any Python class and method as a tool:

```yaml
tools:
  - type: function
    id: my_tool
    import: src.agents.tools.my_tool.MyTool
    method: run
```

## Agent Tools

Agent tools use other agents as tools, enabling agent composition:

```yaml
tools:
  - type: agent
    id: sub_agent
    agent_class: src.agents.all_agents.sub_agent.SubAgent
```

## Tool Ordering

Tool order matters and is preserved from the YAML configuration. The framework will present tools to the LLM in the order specified.

## Creating Custom Tools

Create a tool class:

```python
class MyTool:
    def run(self, input: str) -> str:
        # Tool logic here
        return result
```

Then reference it in your agent's YAML configuration.
