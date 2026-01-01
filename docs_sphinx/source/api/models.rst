Models
======

AgentShip uses Pydantic models for type-safe data validation and serialization. All API requests and responses are validated against these models.

Overview
--------

Models provide:

- **Type safety**: Automatic validation of data types
- **Documentation**: Self-documenting API schemas
- **Serialization**: Automatic JSON conversion
- **Error messages**: Clear validation errors

Core Models
-----------

.. automodule:: src.models.base_models
   :members:
   :undoc-members:
   :show-inheritance:

TextInput / TextOutput
----------------------

Simple text-based input/output for basic agents:

.. code-block:: python

   from src.models.base_models import TextInput, TextOutput
   
   input_data = TextInput(text="Hello!")
   # Used for simple text-based interactions

AgentChatRequest
----------------

Request model for the chat endpoint:

.. code-block:: python

   {
     "agent_name": "my_agent",
     "user_id": "user-123",
     "session_id": "session-456",
     "query": "Hello!",
     "features": []
   }

**Fields**:
- **agent_name** (str, required): Name of the agent to use
- **user_id** (str, required): Unique user identifier
- **session_id** (str, required): Conversation session identifier
- **query** (str/object/array, required): User's input
- **features** (List[FeatureMap], optional): Feature configuration

AgentChatResponse
-----------------

Response model from the chat endpoint:

.. code-block:: python

   {
     "agent_name": "my_agent",
     "user_id": "user-123",
     "session_id": "session-456",
     "sender": "SYSTEM",
     "success": true,
     "agent_response": {...}
   }

**Fields**:
- **agent_name** (str): Name of the agent that responded
- **user_id** (str): User identifier
- **session_id** (str): Session identifier
- **sender** (str): Who sent the response (usually "SYSTEM")
- **success** (bool): Whether the request succeeded
- **agent_response** (any): The agent's response (format depends on agent)

FeatureMap
----------

Configuration for agent features:

.. code-block:: python

   {
     "feature_name": "max_followups",
     "feature_value": 5
   }

**Fields**:
- **feature_name** (str): Name of the feature
- **feature_value** (any): Value for the feature

Artifact
--------

File attachments for agents:

.. code-block:: python

   {
     "artifact_name": "document.pdf",
     "artifact_path": "/path/to/document.pdf"
   }

**Fields**:
- **artifact_name** (str): Name of the artifact
- **artifact_path** (str): Path to the artifact file

Usage Examples
--------------

Creating a Request
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from src.models.base_models import AgentChatRequest, FeatureMap
   
   request = AgentChatRequest(
       agent_name="my_agent",
       user_id="user-123",
       session_id="session-456",
       query="Hello!",
       features=[
           FeatureMap(
               feature_name="max_followups",
               feature_value=5
           )
       ]
   )

Validating Data
~~~~~~~~~~~~~~~

Pydantic automatically validates all data:

.. code-block:: python

   try:
       request = AgentChatRequest(**data)
   except ValidationError as e:
       # Handle validation errors
       print(e.errors())
