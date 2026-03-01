BaseAgent
=========

The ``BaseAgent`` class is the foundation for all agents in AgentShip. It provides a complete framework for building AI agents with minimal boilerplate.

Overview
--------

``BaseAgent`` handles:

- Agent initialization and configuration
- Session management (automatic)
- LLM integration via Google ADK
- Response parsing and formatting
- Tool support for extended functionality
- Conversation context management

All agents in AgentShip inherit from ``BaseAgent``, which provides the core functionality needed to interact with LLMs and manage conversations.

Class Definition
----------------

.. automodule:: src.agent_framework.core.base_agent
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Key Methods
-----------

``__init__(_caller_file, input_schema, output_schema)``
   Initialize the agent with caller file path and schemas. Config is auto-loaded from the YAML file adjacent to the caller.

``async chat(request: AgentChatRequest) -> AgentChatResponse``
   Main method for chatting with the agent. Handles session management and response formatting.

``async run(user_id, session_id, input_data) -> BaseModel``
   Lower-level method for running the agent with schema validation.

Usage Example
-------------

.. code-block:: python

   from src.all_agents.base_agent import BaseAgent
   from src.service.models.base_models import TextInput, TextOutput
   
   # Create agent — config auto-loads from main_agent.yaml
   class MyAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               config_path=resolve_config_path(relative_to=__file__),
               input_schema=TextInput,
               output_schema=TextOutput
           )
   
   # Use the agent
   agent = MyAgent()
   response = await agent.chat(request)

Session Management
------------------

Sessions are automatically managed by ``BaseAgent``:

- Sessions are created on first use
- Conversation history is maintained
- Supports both database and in-memory storage
- Session IDs are scoped to user_id

Input/Output Schemas
--------------------

Agents can define custom input/output schemas:

- **TextInput/TextOutput**: Simple text-based I/O
- **Custom schemas**: Define structured data for your use case
- **Validation**: Pydantic validates all inputs automatically

Tool Support
------------

Agents can extend functionality with tools:

- Tools are automatically discovered
- Tools are passed to the LLM
- LLM decides when to use tools
- Tool results are included in responses

See :doc:`building-agents` for more on creating agents with tools.
