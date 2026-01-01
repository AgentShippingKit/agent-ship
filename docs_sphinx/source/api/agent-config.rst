AgentConfig
===========

The ``AgentConfig`` class manages agent configuration, loading settings from YAML files and providing access to agent parameters.

Overview
--------

``AgentConfig`` handles:

- Loading configuration from YAML files
- Validating configuration settings
- Managing LLM provider configurations
- Providing access to agent metadata

Configuration Structure
-----------------------

Agent configuration is defined in YAML files (typically ``main_agent.yaml``):

.. code-block:: yaml

   agent_name: my_agent
   llm_provider_name: openai
   llm_model: gpt-4o
   temperature: 0.4
   description: My helpful assistant
   instruction_template: |
     You are a helpful assistant.

Class Definition
----------------

.. automodule:: src.agents.configs.agent_config
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Key Methods
-----------

``from_yaml(path: str) -> AgentConfig``
   Load configuration from a YAML file. This is the primary way to create an ``AgentConfig`` instance.

Configuration Fields
--------------------

- **agent_name**: Unique identifier for the agent
- **llm_provider_name**: LLM provider (openai, google, anthropic)
- **llm_model**: Specific model to use
- **temperature**: Creativity level (0.0-1.0)
- **description**: What the agent does
- **instruction_template**: System prompt for the agent

Usage Example
-------------

.. code-block:: python

   from src.agents.configs.agent_config import AgentConfig
   
   # Load from YAML
   config = AgentConfig.from_yaml("my_agent.yaml")
   
   # Access configuration
   print(config.agent_name)  # "my_agent"
   print(config.llm_provider_name)  # "openai"
   print(config.temperature)  # 0.4
