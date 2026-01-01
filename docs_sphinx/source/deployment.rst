Deployment
==========

This guide covers deploying AgentShip to production environments.

Heroku Deployment
----------------

Deploy to Heroku with one command:

.. code-block:: bash

   make heroku-deploy

This command will:
- Create Heroku app (if needed)
- Set up PostgreSQL addon
- Configure environment variables
- Deploy your code
- Verify deployment

**Prerequisites**:
- Heroku CLI installed
- Heroku account
- Git repository initialized

**Manual Steps**:

1. **Create Heroku App**:

.. code-block:: bash

   heroku create your-app-name

2. **Add PostgreSQL**:

.. code-block:: bash

   heroku addons:create heroku-postgresql:essential-0

3. **Set Environment Variables**:

.. code-block:: bash

   heroku config:set OPENAI_API_KEY=your_key
   heroku config:set AGENT_SESSION_STORE_URI=$(heroku config:get DATABASE_URL)

4. **Deploy**:

.. code-block:: bash

   git push heroku main

Docker Deployment
-----------------

Deploy using Docker:

1. **Build Image**:

.. code-block:: bash

   docker build -t agentship:latest .

2. **Run Container**:

.. code-block:: bash

   docker run -d \
     -p 7001:7001 \
     -e OPENAI_API_KEY=your_key \
     -e AGENT_SESSION_STORE_URI=postgresql://... \
     agentship:latest

Or use docker-compose:

.. code-block:: bash

   docker-compose up -d

Environment Variables
---------------------

Required for production:

- At least one LLM API key (OPENAI_API_KEY, GOOGLE_API_KEY, or ANTHROPIC_API_KEY)
- AGENT_SESSION_STORE_URI (for persistent sessions)

Optional:

- LOG_LEVEL (default: INFO)
- ENVIRONMENT (default: production)
- OPIK_API_KEY (for observability)

Post-Deployment
---------------

After deployment:

1. **Verify Health**:

.. code-block:: bash

   curl https://your-app.herokuapp.com/health

2. **Check Logs**:

.. code-block:: bash

   heroku logs --tail

3. **Access API Docs**:

- Swagger: https://your-app.herokuapp.com/swagger
- ReDoc: https://your-app.herokuapp.com/redoc

For detailed deployment guides, see the `user documentation <https://harshuljain13.github.io/ship-ai-agents/>`_.
