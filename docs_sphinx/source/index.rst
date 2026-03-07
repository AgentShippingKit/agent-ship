.. AgentShip documentation master file

.. raw:: html

   <div style="text-align: center; margin: 2rem 0;">
       <img src="_static/docs-header@3x.png" alt="AgentShip Documentation" style="width: 100%; max-width: 960px; border-radius: 8px;" />
   </div>

AgentShip
=========

**The runtime-agnostic production layer for AI agents.**

AgentShip is **LiteLLM for agent runtimes** — one interface to run your agents on Google ADK, LangGraph, or any future engine, plus the production stack (API, sessions, streaming, observability, MCP) that those engines do not ship with.

Write your agent once. Swap runtimes with one YAML line. Ship in an hour, not two weeks.

Fast path (3 commands)
======================

.. code-block:: bash

   git clone https://github.com/Agent-Ship/agent-ship.git
   cd agent-ship
   make docker-setup   # API + PostgreSQL + Studio at http://localhost:7001

Then open ``http://localhost:7001/studio`` and start chatting with the built-in agent.

Where to start
==============

- **Just trying it out** → :doc:`Quick Start <user-guides/getting-started/quickstart>`
- **Deciding if AgentShip fits** → :doc:`Why AgentShip? <why-agentship>`
- **About to build an agent** → :doc:`Building Agents Overview <user-guides/building-agents/overview>`
- **Integrating MCP tools** → :doc:`MCP Integration <user-guides/mcp-integration>`

Concepts in one screen
======================

- **Engines** — ADK or LangGraph + LiteLLM; set ``execution_engine:`` per agent in YAML.
- **Agents** — two files per agent (YAML + Python) in ``src/all_agents/``; auto-discovered at startup.
- **Sessions** — PostgreSQL-backed conversation history keyed by ``user_id:session_id``.
- **MCP tools** — STDIO and HTTP/OAuth transports; tools auto-documented for the LLM.
- **Observability** — Opik tracing out of the box.
- **Studio** — browser UI at ``/studio`` for chatting, inspecting traces, and stopping runs.

----

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   why-agentship
   user-guides/architecture
   user-guides/getting-started/quickstart
   user-guides/getting-started/installation
   user-guides/getting-started/configuration
   user-guides/docker-setup

.. toctree::
   :maxdepth: 1
   :caption: Building Agents

   user-guides/building-agents/overview
   user-guides/building-agents/agent-configuration
   user-guides/building-agents/base-agent
   user-guides/building-agents/tools
   user-guides/building-agents/patterns/single-agent
   user-guides/building-agents/patterns/orchestrator
   user-guides/building-agents/patterns/tool-pattern

.. toctree::
   :maxdepth: 1
   :caption: MCP Integration

   user-guides/mcp-integration

.. toctree::
   :maxdepth: 1
   :caption: Deployment

   user-guides/deployment/overview
   user-guides/deployment/heroku

.. toctree::
   :maxdepth: 1
   :caption: Testing

   user-guides/testing/overview
   user-guides/testing/writing-tests

.. toctree::
   :maxdepth: 1
   :caption: Reference

   api/index
   contributing
