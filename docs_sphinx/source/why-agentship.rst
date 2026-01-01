Why AgentShip?
==============

With frameworks like Google ADK, CrewAI, LangGraph, LangChain, and others available, you might wonder: **Why AgentShip?**

The answer is simple: **AgentShip is the production layer that other frameworks don't provide.**

The Problem
-----------

Most agent frameworks focus on **building** agents, not **shipping** them:

- ✅ **Google ADK**: Great for building agents, but you need to build infrastructure
- ✅ **CrewAI**: Excellent for multi-agent workflows, but requires setup
- ✅ **LangGraph**: Powerful for complex flows, but needs integration work
- ✅ **LangChain**: Comprehensive toolkit, but lots of configuration

**The gap**: These frameworks help you **build** agents, but you still need to:
- Set up a REST API
- Configure session management
- Set up observability
- Handle deployment
- Manage infrastructure
- Write boilerplate code

AgentShip's Role
----------------

AgentShip is **not a replacement** for these frameworks. Instead, it's a **production-ready layer** that sits on top of them.

Think of it this way:

.. code-block:: text

   ┌─────────────────────────────────────┐
   │     Your Application/Agents         │
   ├─────────────────────────────────────┤
   │     AgentShip (Production Layer)    │  ← What AgentShip provides
   ├─────────────────────────────────────┤
   │     Google ADK / LangChain / etc.   │  ← What other frameworks provide
   ├─────────────────────────────────────┤
   │     LLM Providers (OpenAI, etc.)    │
   └─────────────────────────────────────┘

What AgentShip Provides
-----------------------

1. **Zero-Configuration Agent Discovery**
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   **Other frameworks**: Manual registration, import statements, configuration files

   **AgentShip**: Create a directory and two files → Agent is automatically discovered

   .. code-block:: bash

      # Just create these files:
      src/agents/all_agents/my_agent/
      ├── main_agent.yaml
      └── main_agent.py
      
      # That's it! Agent is registered automatically.

2. **Production-Ready REST API**
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   **Other frameworks**: You build the API yourself

   **AgentShip**: REST API with FastAPI, auto-generated docs, type-safe endpoints

   - ``POST /api/agents/chat`` - Chat with any agent
   - ``GET /health`` - Health checks
   - Auto-generated Swagger/ReDoc docs
   - Type-safe request/response models

3. **Automatic Session Management**
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

   **Other frameworks**: You implement session handling

   **AgentShip**: Automatic session management with:
   - PostgreSQL for persistent conversations
   - In-memory for testing
   - Automatic session creation
   - Conversation history tracking

4. **One-Command Setup**
   ~~~~~~~~~~~~~~~~~~~~~~

   **Other frameworks**: Multiple setup steps, configuration files, dependencies

   **AgentShip**: One command gets everything running

   .. code-block:: bash

      make docker-setup
      # ✅ Docker installed
      # ✅ Database configured
      # ✅ API running
      # ✅ Everything ready

5. **Built-in Observability**
   ~~~~~~~~~~~~~~~~~~~~~~~~~~~

   **Other frameworks**: You add observability yourself

   **AgentShip**: Opik integration for:
   - Tracing
   - Metrics
   - Logging
   - Performance monitoring

6. **Deployment Ready**
   ~~~~~~~~~~~~~~~~~~~~

   **Other frameworks**: You figure out deployment

   **AgentShip**: One-command deployment to Heroku

   .. code-block:: bash

      make heroku-deploy
      # ✅ App created
      # ✅ Database set up
      # ✅ Environment configured
      # ✅ Deployed

Comparison with Other Frameworks
---------------------------------

Google ADK
~~~~~~~~~~

**Google ADK**: Low-level agent building framework
- ✅ Excellent for building agents
- ❌ No REST API
- ❌ No session management
- ❌ No deployment scripts
- ❌ Requires infrastructure setup

**AgentShip**: Production layer on top of Google ADK
- ✅ Uses Google ADK for agent logic
- ✅ Adds REST API
- ✅ Adds session management
- ✅ Adds deployment
- ✅ Adds observability

**Use together**: Google ADK for agent logic, AgentShip for production infrastructure.

CrewAI
~~~~~~

**CrewAI**: Multi-agent orchestration framework
- ✅ Great for complex workflows
- ✅ Agent collaboration
- ❌ Requires setup and configuration
- ❌ No built-in API
- ❌ No deployment scripts

**AgentShip**: Can integrate CrewAI agents
- ✅ Use CrewAI for orchestration
- ✅ AgentShip provides API layer
- ✅ AgentShip handles deployment
- ✅ Best of both worlds

LangGraph
~~~~~~~~~

**LangGraph**: State machine for agent workflows
- ✅ Powerful for complex flows
- ✅ Visual workflow design
- ❌ Requires integration work
- ❌ No production infrastructure

**AgentShip**: Production layer for LangGraph
- ✅ Use LangGraph for workflows
- ✅ AgentShip provides API
- ✅ AgentShip handles sessions
- ✅ Production-ready

LangChain
~~~~~~~~~

**LangChain**: Comprehensive LLM toolkit
- ✅ Huge ecosystem
- ✅ Many integrations
- ❌ Lots of configuration
- ❌ Can be complex

**AgentShip**: Simplified production layer
- ✅ Use LangChain components
- ✅ AgentShip simplifies deployment
- ✅ AgentShip provides structure
- ✅ Less boilerplate

When to Use AgentShip
---------------------

Use AgentShip when you want to:

✅ **Ship agents quickly** - Get to production in minutes, not weeks
✅ **Focus on agent logic** - Not infrastructure setup
✅ **Need a REST API** - Expose agents via HTTP
✅ **Want auto-discovery** - No manual registration
✅ **Deploy easily** - One-command deployment
✅ **Monitor agents** - Built-in observability

Don't use AgentShip if you:

❌ **Need custom infrastructure** - You want full control
❌ **Building a library** - Not deploying a service
❌ **Research/experimentation** - Just prototyping
❌ **Already have infrastructure** - You have your own setup

The AgentShip Philosophy
-------------------------

**"Build agents, not infrastructure"**

AgentShip believes:
- You should focus on **agent logic**, not boilerplate
- **Shipping** should be as easy as building
- **Infrastructure** should be invisible
- **Configuration** should be minimal

Real-World Example
------------------

**Without AgentShip** (using just Google ADK):

1. Set up FastAPI
2. Create REST endpoints
3. Implement session management
4. Set up PostgreSQL
5. Configure observability
6. Write deployment scripts
7. Handle errors
8. Test everything

**Time**: 2-3 weeks

**With AgentShip**:

1. Create agent files
2. Run ``make docker-setup``
3. Deploy with ``make heroku-deploy``

**Time**: 30 minutes

The Value Proposition
--------------------

AgentShip doesn't replace other frameworks. It **complements** them by providing:

- **Production infrastructure** they don't include
- **Simplified deployment** they don't provide
- **Auto-discovery** they don't have
- **One-command setup** they don't offer

Think of AgentShip as the **"Heroku for agents"** - it takes care of infrastructure so you can focus on building.

Conclusion
----------

AgentShip fills the gap between **building agents** and **shipping them**. It's the production layer that makes agent frameworks production-ready.

**Use AgentShip when**: You want to ship agents to production quickly
**Use other frameworks when**: You need their specific capabilities (orchestration, workflows, etc.)
**Use both**: AgentShip + other frameworks = Best of both worlds

