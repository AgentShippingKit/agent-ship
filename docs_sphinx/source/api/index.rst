API Reference
==============

This section contains automatically generated API documentation from the source code. All classes, methods, and functions are documented with their signatures, parameters, and return types.

Overview
--------

AgentShip's API is built on FastAPI and provides:

- **RESTful endpoints** for agent interactions
- **Auto-generated documentation** via Swagger/ReDoc
- **Type-safe models** using Pydantic
- **Session management** for conversation persistence
- **Error handling** with detailed error messages

Main Endpoints
--------------

**POST** ``/api/agents/chat``
   Chat with any registered agent. This is the primary endpoint for agent interactions.

**GET** ``/health``
   Health check endpoint to verify service status.

**GET** ``/``
   Root endpoint with welcome message.

Core Modules
------------

The following pages document the core API components:

- :doc:`base-agent` - Base agent class
- :doc:`agent-config` - Agent configuration  
- :doc:`models` - Data models
- :doc:`modules` - Supporting modules

.. toctree::
   :hidden:
   :maxdepth: 2

   base-agent
   agent-config
   models
   modules

Base Agent
----------

The ``BaseAgent`` class is the foundation for all agents. It provides:

- Agent initialization and configuration
- Session management
- LLM integration
- Response parsing
- Tool support

See :doc:`base-agent` for complete documentation.

Agent Configuration
-------------------

The ``AgentConfig`` class handles:

- Loading configuration from YAML files
- Validating agent settings
- Managing LLM provider configurations

See :doc:`agent-config` for complete documentation.

Models
------

Pydantic models for type-safe data:

- ``TextInput`` / ``TextOutput``: Basic text I/O
- ``AgentChatRequest`` / ``AgentChatResponse``: API request/response
- ``FeatureMap``: Feature configuration
- ``Artifact``: File attachments

See :doc:`models` for complete documentation.

Modules
-------

Supporting modules for agent functionality:

- ``SessionManager``: Manages conversation sessions
- ``AgentConfigurator``: Handles agent configuration
- ``ResponseParser``: Parses and formats agent responses
- ``SessionServiceFactory``: Creates session services

See :doc:`modules` for complete documentation.

Usage Examples
--------------

Basic Agent Chat
~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.service.models.base_models import AgentChatRequest
   
   request = AgentChatRequest(
       agent_name="my_agent",
       user_id="user-123",
       session_id="session-456",
       query="Hello!",
       features=[]
   )
   
   response = await agent.chat(request)

Creating an Agent
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.all_agents.base_agent import BaseAgent
   from src.agent_framework.configs.agent_config import AgentConfig
   from src.service.models.base_models import TextInput, TextOutput
   
   config = AgentConfig.from_yaml("path/to/config.yaml")
   agent = MyAgent(
       agent_config=config,
       input_schema=TextInput,
       output_schema=TextOutput
   )

Session Management
~~~~~~~~~~~~~~~~~~

Sessions are automatically managed:

- New sessions are created on first use
- Sessions persist conversation history
- Can use PostgreSQL or in-memory storage

Error Handling
--------------

All endpoints return appropriate HTTP status codes:

- **200**: Success
- **404**: Agent not found
- **422**: Validation error
- **500**: Internal server error

Error responses include detailed messages:

.. code-block:: json

   {
     "detail": "Agent 'invalid_agent' not found. Available agents: ['my_agent', 'other_agent']"
   }
