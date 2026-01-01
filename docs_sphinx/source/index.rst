.. AgentShip documentation master file

.. raw:: html

   <div style="text-align: center; margin: 2rem 0;">
       <img src="/docs/_static/docs-header.svg" alt="AgentShip Documentation" style="width: 100%; max-width: 960px;" />
   </div>

Welcome to AgentShip's documentation!
=====================================

**Build and deploy AI agents in minutes, not weeks.**

AgentShip is a production-ready framework for building AI agents. No infrastructure complexity. Just focus on building intelligent solutions.

What is AgentShip?
==================

AgentShip is a comprehensive framework that simplifies the development, deployment, and operation of AI agents. Built on top of Google's Agent Development Kit (ADK), it provides:

- **Auto-discovery**: Create agents, they're automatically registered
- **Multiple LLM providers**: OpenAI, Google, Anthropic support
- **Production-ready**: FastAPI, PostgreSQL, observability built-in
- **Three agent patterns**: Orchestrator, single-agent, tool-based
- **Session management**: Persistent conversations with PostgreSQL or in-memory storage
- **Observability**: Built-in tracing, metrics, and logging with Opik

Quick Start
===========

Get started in 2 minutes:

.. code-block:: bash

   git clone https://github.com/harshuljain13/ship-ai-agents.git
   cd ship-ai-agents/ai/ai-ecosystem
   make docker-setup

That's it! Open http://localhost:7001/swagger and you're ready to build.

The setup script will:
- Check Docker installation
- Create `.env` file
- Prompt for your API key
- Start everything (API + PostgreSQL)
- Open the API documentation

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   why-agentship
   user-guides/getting-started/quickstart
   user-guides/getting-started/installation
   user-guides/getting-started/configuration
   user-guides/docker-setup
   user-guides/building-agents/patterns/orchestrator
   user-guides/building-agents/patterns/single-agent
   user-guides/building-agents/patterns/tool-pattern
   user-guides/building-agents/tools
   user-guides/building-agents/agent-configuration
   api/index
   api/base-agent
   api/agent-config
   api/models
   api/modules
   user-guides/deployment/heroku
   user-guides/testing/writing-tests
   testing-with-postman
   contributing

Key Concepts
============

Agents
------

Agents are the core building blocks of AgentShip. Each agent:
- Has a unique name and configuration
- Uses a specific LLM provider (OpenAI, Google, Anthropic)
- Can have custom input/output schemas
- Supports tools for extended functionality
- Maintains conversation sessions

Sessions
--------

Sessions track conversation history:
- **Database sessions**: Persistent storage in PostgreSQL
- **In-memory sessions**: Temporary storage for testing
- Sessions are automatically created on first use
- Each session is scoped to a user_id and session_id

Agent Patterns
--------------

AgentShip supports three patterns:

1. **Single Agent**: Simple, focused agents for specific tasks
2. **Orchestrator**: Coordinate multiple agents for complex workflows
3. **Tool Pattern**: Agents with custom tools for extended capabilities

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
