Why AgentShip?
==============

The Origin
----------

   *"I spent two days building an agent. It worked perfectly. Then I tried to ship it. Two weeks later — after writing FastAPI endpoints, setting up PostgreSQL sessions, wiring observability, writing Docker configs — the agent still did the exact same thing it did on day two. I'd spent 12 days wrapping it in plumbing. This happened three times. By the third agent, I stopped and built it once."*

   — Harshul Jain, Creator of AgentShip

Two Problems
------------

**Problem 1: Production plumbing**

Every team building AI agents re-builds the same infrastructure from scratch:

- REST API + request validation
- Session storage (PostgreSQL or Redis)
- Observability & tracing
- MCP tool integration
- Docker + deployment config
- Streaming with error handling

Result: ~2,000 lines of infrastructure code and two weeks of work per agent. Zero product value shipped.

**Problem 2: Framework lock-in**

50+ AI agent frameworks exist. Teams pick one, build deep, then hit limits:

- Need a different LLM? Framework may not support it.
- Framework B has the feature you need? 3–6 month rewrite.
- Scaling limits, missing MCP support, observability gaps.

Result: Architecture decisions made on day one become impossible to change. Every new requirement compounds the lock-in tax.

.. code-block:: text

   Without AgentShip:       Your Agent Logic
                                 ↕  tightly coupled
                            LangGraph / ADK / CrewAI
                                 ↕  tightly coupled
                           Memory · Observability · Tools

   With AgentShip:          Your Agent Logic (unchanged)
                                 ↕  talks to abstraction
                              AgentShip Interface
                                 ↕  pluggable
                      ADK  |  LangGraph  |  Future Engines
                                 ↕  config-driven
                      Memory  ·  Observability  ·  MCP Tools

The One-Line Definition
-----------------------

**AgentShip is LiteLLM for agent runtimes.**

LiteLLM unified LLM provider APIs behind a single ``completion()`` call — swap OpenAI for Anthropic with one config change. AgentShip does the same at the agent runtime layer: ``BaseAgent`` is the unified interface, and swapping ADK for LangGraph is one YAML line. But AgentShip goes further — it includes the full production stack that LiteLLM never needed to build.

The Engine Swap
---------------

The whole value proposition in one diff:

.. code-block:: diff

   # main_agent.yaml — the entire change required
   - execution_engine: adk
   + execution_engine: langgraph

**Your Python class is unchanged. Your tools are unchanged. Your prompts are unchanged.**

Impact
------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Metric
     - Without AgentShip
     - With AgentShip
   * - Time to production (per agent)
     - 2 weeks
     - **1 hour**
   * - Infrastructure code
     - ~2,000 lines
     - **~50 lines** (agent logic only)
   * - Observability setup
     - 2–3 days
     - **0** (built-in)
   * - Session management
     - 2–3 days
     - **0** (built-in)
   * - Engine migration
     - 3–6 months, 50–80% rewrite
     - **One line in YAML**
   * - MCP tool integration
     - Manual per-framework
     - **Config declaration, auto-discovered**

Competitive Position
--------------------

AgentShip's unique position: the only open-source, Python-native, production-deployed framework where the **same agent class runs on ADK or LangGraph without modification** — with REST API, PostgreSQL sessions, streaming, MCP (STDIO + HTTP/OAuth), and observability included.

Google, Microsoft, and LangChain all have competing incentives to *not* build true portability. Their businesses depend on lock-in. Open source with no vendor allegiance is the moat.

.. list-table::
   :header-rows: 1
   :widths: 25 30 20 25

   * - Product
     - Thesis
     - Status
     - Limitation
   * - Oracle Agent Spec (arxiv Oct 2025)
     - Declarative YAML portability spec
     - Research only
     - No production runtime shipped
   * - LangServe / LangGraph Platform
     - Deployment layer for LangGraph
     - Production
     - LangChain-locked, no ADK support
   * - Google ADK built-in server
     - Serve ADK agents
     - Production
     - ADK-only, no sessions, no MCP
   * - CrewAI
     - "Works with any LLM"
     - Production
     - No runtime portability, 50–80% rewrite to migrate
   * - **AgentShip**
     - Runtime-agnostic production layer
     - **Production ✓**
     - —

Why Now
-------

Three converging trends make 2026 the right moment:

1. **Protocol standardisation** — MCP (tools), A2A (agent-to-agent), A2UI (agent-to-interface) are all landing in 2025–2026. AgentShip sits above the execution engine but below the protocol layer — the exact position that needs to exist.
2. **Production pressure** — 57% of developers now have agents in production. 95% of enterprise AI pilots are delivering zero measurable ROI. The "make it work in a notebook" phase is over.
3. **No incumbent** — The Oracle Agent Spec paper (arxiv, Oct 2025) explicitly states the industry lacks a unified abstraction for AI agents. No production-deployed answer exists.
