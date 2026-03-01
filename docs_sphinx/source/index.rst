.. AgentShip documentation master file

.. raw:: html

   <div style="text-align: center; margin: 2rem 0;">
       <img src="/docs/_static/docs-header@3x.png" alt="AgentShip Documentation" style="width: 100%; max-width: 960px;" />
   </div>

AgentShip
=========

**Build and deploy AI agents in minutes, not weeks.**

AgentShip is an open-source production framework for AI agents. It sits on top of Google ADK and LangGraph — giving you the REST API, session memory, observability, streaming, and MCP tool integration that these engines don't provide on their own.

Drop in a YAML file and a Python class. AgentShip does the rest.

.. code-block:: bash

   git clone https://github.com/Agent-Ship/agent-ship.git
   cd agent-ship
   make docker-setup
   # ✅  API ready at http://localhost:7001

----

What You Get
============

- **Auto-discovery** — agents register themselves from YAML, no manual wiring
- **Dual engines** — Google ADK or LangGraph, configured per agent in YAML
- **MCP integration** — STDIO and HTTP/OAuth transports for any MCP server
- **Token-by-token streaming** — real SSE streaming with LangGraph + LiteLLM
- **Session memory** — PostgreSQL-backed conversations, zero config
- **Observability** — Opik tracing and metrics out of the box
- **Debug UI** — browser-based chat interface at ``/debug-ui`` with stop button
- **One-command Docker setup** — ``make docker-setup`` starts everything

----

Quick Start
===========

.. code-block:: bash

   # 1. Clone and start
   git clone https://github.com/Agent-Ship/agent-ship.git
   cd agent-ship
   make docker-setup

   # 2. Add your LLM key to .env
   echo "OPENAI_API_KEY=sk-..." >> .env
   make docker-restart

   # 3. Open the Debug UI and start chatting
   open http://localhost:7001/debug-ui

Your first agent is included — talk to it immediately. To create your own, see :doc:`user-guides/getting-started/quickstart`.

----

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   why-agentship
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
