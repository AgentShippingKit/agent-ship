Getting Started
===============

This guide will help you get AgentShip up and running quickly. Choose the setup method that works best for you.

Installation Methods
--------------------

Docker (Recommended)
~~~~~~~~~~~~~~~~~~~~

The easiest way to get started. Docker handles everything automatically.

**Prerequisites**:
- Docker Desktop installed
- Docker Compose available

**Steps**:

1. Clone the repository:

.. code-block:: bash

   git clone https://github.com/harshuljain13/ship-ai-agents.git
   cd ship-ai-agents/ai/ai-ecosystem

2. Run the setup:

.. code-block:: bash

   make docker-setup

The script will:
- Check Docker installation
- Create `.env` file from template
- Prompt for your API key (OpenAI, Google, or Anthropic)
- Build Docker images
- Start containers (API + PostgreSQL)
- Wait for services to be ready

3. Verify installation:

.. code-block:: bash

   curl http://localhost:7001/health

You should see: ``{"status": "running"}``

4. Access the API:

- **Swagger UI**: http://localhost:7001/swagger
- **ReDoc**: http://localhost:7001/redoc
- **Sphinx Docs**: http://localhost:7001/docs (after building)

**Next Steps**:
- Start containers: ``make docker-up``
- Stop containers: ``make docker-down``
- View logs: ``make docker-logs``
- Restart: ``make docker-restart``

Local Development
~~~~~~~~~~~~~~~~~

For development without Docker.

**Prerequisites**:
- Python 3.13+
- PostgreSQL (optional, for persistent sessions)
- pipenv

**Steps**:

1. Clone and navigate:

.. code-block:: bash

   git clone https://github.com/harshuljain13/ship-ai-agents.git
   cd ship-ai-agents/ai/ai-ecosystem

2. Run setup script:

.. code-block:: bash

   make setup

This will:
- Install dependencies
- Create `.env` file
- Optionally set up PostgreSQL

3. Start the server:

.. code-block:: bash

   make dev

The server will start with hot-reload enabled at http://localhost:7001

Configuration
-------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Create a `.env` file (or copy from `env.example`):

**Required** (at least one LLM API key):

.. code-block:: bash

   OPENAI_API_KEY=your_openai_key_here
   # OR
   GOOGLE_API_KEY=your_google_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_key_here

**Optional**:

.. code-block:: bash

   # Session storage (defaults to in-memory if not set)
   AGENT_SESSION_STORE_URI=postgresql://user:password@localhost:5432/dbname
   
   # Logging
   LOG_LEVEL=INFO
   ENVIRONMENT=development
   
   # Observability (optional)
   OPIK_API_KEY=your_opik_key

Create Your First Agent
-----------------------

1. Create the agent directory:

.. code-block:: bash

   mkdir -p src/all_agents/my_agent
   cd src/all_agents/my_agent

2. Create ``main_agent.yaml``:

.. code-block:: yaml

   agent_name: my_agent
   llm_provider_name: openai
   llm_model: gpt-4o
   temperature: 0.4
   description: My helpful assistant
   instruction_template: |
     You are a helpful assistant that answers questions clearly.
     Be concise and friendly in your responses.

3. Create ``main_agent.py``:

.. code-block:: python

   from src.all_agents.base_agent import BaseAgent
   from src.service.models.base_models import TextInput, TextOutput

   class MyAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               _caller_file=__file__,
               input_schema=TextInput,
               output_schema=TextOutput
           )

4. Restart the server:

The agent will be automatically discovered and registered. No manual registration needed!

5. Test your agent:

.. code-block:: bash

   curl -X POST "http://localhost:7001/api/agents/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "agent_name": "my_agent",
       "user_id": "test-user",
       "session_id": "test-session",
       "query": "Hello!",
       "features": []
     }'

Or use Postman (see :doc:`testing-with-postman`).

Understanding the Structure
---------------------------

Agent Directory
~~~~~~~~~~~~~~~

Each agent lives in its own directory:

.. code-block:: text

   src/all_agents/
   └── my_agent/
       ├── main_agent.yaml    # Agent configuration
       └── main_agent.py       # Agent implementation

Configuration File
~~~~~~~~~~~~~~~~~~

The ``main_agent.yaml`` file defines:

- **agent_name**: Unique identifier
- **llm_provider_name**: Which LLM to use (openai, google, anthropic)
- **llm_model**: Specific model (e.g., gpt-4o, gemini-pro)
- **temperature**: Creativity level (0.0 to 1.0)
- **description**: What the agent does
- **instruction_template**: System prompt for the agent

Agent Class
~~~~~~~~~~~

The ``main_agent.py`` file:

- Inherits from ``BaseAgent``
- Loads configuration from YAML
- Defines input/output schemas
- Can add custom tools (optional)

Next Steps
----------

- :doc:`api/index` - Learn about the API
- :doc:`testing-with-postman` - Test your agents
- :doc:`building-agents` - Advanced agent patterns
- :doc:`deployment` - Deploy to production
