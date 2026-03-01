Building Agents
===============

This guide covers how to build custom agents in AgentShip, including different agent patterns and best practices.

Agent Patterns
--------------

AgentShip supports three main patterns:

Single Agent Pattern
--------------------

Simple, focused agents for specific tasks. Best for:
- Single-purpose agents
- Straightforward interactions
- Quick prototyping

**Example**: A translation agent that translates text between languages.

Orchestrator Pattern
--------------------

Coordinate multiple agents for complex workflows. Best for:
- Multi-step processes
- Workflows requiring multiple agents
- Complex business logic

**Example**: A trip planner that uses flight, hotel, and activity agents.

Tool Pattern
------------

Agents with custom tools for extended functionality. Best for:
- Agents that need external APIs
- Database interactions
- Custom business logic

**Example**: A database agent that can query and manipulate data.

Creating a Basic Agent
----------------------

1. **Create Directory Structure**:

.. code-block:: bash

   mkdir -p src/all_agents/my_agent
   cd src/all_agents/my_agent

2. **Create Configuration** (``main_agent.yaml``):

.. code-block:: yaml

   agent_name: my_agent
   llm_provider_name: openai
   llm_model: gpt-4o
   temperature: 0.4
   description: My helpful assistant
   instruction_template: |
     You are a helpful assistant that answers questions clearly.
     Be concise and friendly.

3. **Create Agent Class** (``main_agent.py``):

.. code-block:: python

   from src.all_agents.base_agent import BaseAgent
   from src.service.models.base_models import TextInput, TextOutput

   class MyAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               config_path=resolve_config_path(relative_to=__file__),
               input_schema=TextInput,
               output_schema=TextOutput
           )

4. **Restart Server**: The agent is automatically discovered!

Adding Custom Tools
-------------------

Tools extend agent capabilities:

.. code-block:: python

   from google.adk.tools import FunctionTool
   
   def get_weather(city: str) -> str:
       """Get weather for a city."""
       # Your implementation
       return f"Weather in {city}: Sunny, 72°F"
   
   weather_tool = FunctionTool(
       function=get_weather,
       name="get_weather",
       description="Get current weather for a city"
   )
   
   class MyAgent(BaseAgent):
       def __init__(self):
           # ... initialization ...
           # Add tools to the agent
           self.agent.tools = [weather_tool]

Custom Input/Output Schemas
---------------------------

Define structured data for your agent:

.. code-block:: python

   from pydantic import BaseModel, Field
   
   class TripInput(BaseModel):
       source: str = Field(description="Source location")
       destination: str = Field(description="Destination location")
       dates: str = Field(description="Travel dates")
   
   class TripOutput(BaseModel):
       itinerary: str = Field(description="Trip itinerary")
       cost: float = Field(description="Estimated cost")
   
   class TripAgent(BaseAgent):
       def __init__(self):
           # ... use TripInput and TripOutput ...

Best Practices
--------------

1. **Clear Instructions**: Write detailed instruction templates
2. **Appropriate Temperature**: Use lower values (0.2-0.4) for factual tasks, higher (0.7-0.9) for creative tasks
3. **Descriptive Names**: Use clear, descriptive agent names
4. **Error Handling**: Handle errors gracefully in your agent code
5. **Testing**: Test agents thoroughly with various inputs

For detailed guides, see the :doc:`user-guides/building-agents/patterns/single-agent` and :doc:`user-guides/building-agents/patterns/orchestrator` pages.
