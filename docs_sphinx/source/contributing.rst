Contributing
============

Contributions welcome. The most valuable contributions are new implementations of the four pluggable layers:

- **New engines** — OpenAI Agents SDK, CrewAI, Autogen adapters
- **New memory backends** — Zep, Pinecone, custom vector stores
- **New observability backends** — LangFuse, custom tracing integrations
- **New MCP transports** — additional protocol implementations

Getting Started
---------------

1. Read ``CLAUDE.md`` in the repository root — it has the full developer guide
2. Check ``good first issue`` labels on GitHub
3. Run tests before submitting:

.. code-block:: bash

   make test && make lint

All PRs require passing integration tests.

Reporting Issues
----------------

Open an issue at https://github.com/Agent-Ship/agent-ship/issues

Please include:

- AgentShip version or commit hash
- Python version
- Execution engine (ADK or LangGraph)
- Minimal reproduction steps
- Relevant logs (``make docker-logs`` or ``dev_app.log``)
