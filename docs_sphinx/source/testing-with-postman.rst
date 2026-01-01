Testing with Postman
====================

AgentShip includes comprehensive Postman collections for testing all API endpoints. This guide will help you set up and use Postman to test your agents.

Prerequisites
-------------

1. **AgentShip running**: Make sure your service is running locally or deployed
2. **Postman installed**: Download from https://www.postman.com/downloads/
3. **API keys configured**: Ensure your `.env` file has at least one LLM API key

Importing the Collection
-------------------------

1. **Open Postman** and click the "Import" button (top left)

2. **Import Collection**:
   - Navigate to ``postman/AgentsAPI.postman_collection.json``
   - Click "Import"

3. **Import Environment**:
   - Navigate to ``postman/AgentAPI.postman_environment.json``
   - Click "Import"

4. **Select Environment**:
   - Click the environment dropdown (top right)
   - Select "AgentShip Environment"

Available Endpoints
-------------------

Health Check
~~~~~~~~~~~~

**GET** ``/health``

Check if the service is running.

**Request**:
.. code-block:: http

   GET http://localhost:7001/health

**Response**:
.. code-block:: json

   {
     "status": "running"
   }

Agent Chat
~~~~~~~~~~

**POST** ``/api/agents/chat``

Chat with any registered agent. This is the main endpoint for interacting with agents.

**Request Body**:
.. code-block:: json

   {
     "agent_name": "medical_followup_agent",
     "user_id": "user-123",
     "session_id": "session-456",
     "query": "I have chest pain",
     "features": []
   }

**Response**:
.. code-block:: json

   {
     "agent_name": "medical_followup_agent",
     "user_id": "user-123",
     "session_id": "session-456",
     "sender": "SYSTEM",
     "success": true,
     "agent_response": {
       "followup_questions": [
         "Can you describe the pain?",
         "When did it start?",
         "Are you experiencing any other symptoms?"
       ]
     }
   }

**Parameters**:

- **agent_name** (required): Name of the agent to use
- **user_id** (required): Unique identifier for the user
- **session_id** (required): Unique identifier for the conversation session
- **query** (required): The user's input (can be string, object, or array)
- **features** (optional): Array of feature maps for agent configuration

Testing Different Agents
-------------------------

Medical Followup Agent
~~~~~~~~~~~~~~~~~~~~~~

Tests medical conversation scenarios:

.. code-block:: json

   {
     "agent_name": "medical_followup_agent",
     "user_id": "user-123",
     "session_id": "medical-session-1",
     "query": [
       {
         "speaker": "Patient",
         "text": "I have chest pain"
       },
       {
         "speaker": "Doctor",
         "text": "Can you describe it?"
       }
     ],
     "features": [
       {
         "feature_name": "max_followups",
         "feature_value": 5
       }
     ]
   }

Trip Planner Agent
~~~~~~~~~~~~~~~~~~

Tests trip planning with structured input:

.. code-block:: json

   {
     "agent_name": "trip_planner_agent",
     "user_id": "user-123",
     "session_id": "trip-session-1",
     "query": {
       "source": "New York",
       "destination": "Paris",
       "dates": "2025-06-01 to 2025-06-10"
     },
     "features": []
   }

Database Agent
~~~~~~~~~~~~~~

Tests database query capabilities:

.. code-block:: json

   {
     "agent_name": "database",
     "user_id": "user-123",
     "session_id": "db-session-1",
     "query": "What tables are available in the database?",
     "features": []
   }

Common Testing Scenarios
------------------------

New Session
~~~~~~~~~~~

1. Use a new ``session_id`` (e.g., "session-new-123")
2. Send your first query
3. Agent will create a new session and respond

Continuing a Conversation
~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Use the same ``session_id`` from a previous request
2. Send follow-up queries
3. Agent maintains conversation context

Error Testing
~~~~~~~~~~~~~

Test error handling:

**Invalid Agent**:
.. code-block:: json

   {
     "agent_name": "nonexistent_agent",
     "user_id": "user-123",
     "session_id": "session-456",
     "query": "Hello",
     "features": []
   }

**Response**: 404 with error message listing available agents

**Missing Fields**:
.. code-block:: json

   {
     "agent_name": "medical_followup_agent",
     "user_id": "user-123"
   }
   
**Response**: 422 validation error

Environment Variables
----------------------

The Postman environment includes:

- **base_url**: Local development URL (default: ``http://localhost:7001``)
- **base_url_production**: Production URL (update with your deployment URL)
- **user_id**: Test user ID (default: "user-123")
- **session_id**: Test session ID (default: "session-456")

Troubleshooting
---------------

Connection Refused
~~~~~~~~~~~~~~~~~~

- Verify service is running: ``curl http://localhost:7001/health``
- Check port 7001 is available
- Ensure Docker containers are running (if using Docker)

404 Not Found
~~~~~~~~~~~~~

- Verify endpoint URL is correct
- Check agent name is registered (see available agents in error message)
- Ensure service is deployed properly

500 Internal Server Error
~~~~~~~~~~~~~~~~~~~~~~~~~

- Check service logs for detailed errors
- Verify API keys are set correctly in `.env`
- Check database connection if using persistent sessions
- Ensure LLM provider credentials are valid

Authentication Issues
~~~~~~~~~~~~~~~~~~~~~

- Verify API keys are valid and have sufficient credits
- Check environment variables are loaded correctly
- Ensure `.env` file exists and is properly formatted

Best Practices
--------------

1. **Use unique session IDs**: Each test scenario should use a different session_id
2. **Test error cases**: Include invalid inputs, missing fields, and edge cases
3. **Verify responses**: Check that agent responses match expected formats
4. **Test session continuity**: Verify conversations maintain context across requests
5. **Monitor logs**: Check service logs for debugging information

Related Documentation
---------------------

- :doc:`getting-started` - Setup and installation
- :doc:`api/index` - Complete API reference
- :doc:`building-agents` - Creating custom agents

