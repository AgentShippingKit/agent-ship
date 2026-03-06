Run the appropriate AgentShip tests for the current work.

Scope: $ARGUMENTS

Steps:

1. If $ARGUMENTS specifies a scope (e.g. `unit`, `integration`, `mcp`, a filename), run those tests directly.

2. If $ARGUMENTS is empty, look at recently modified files and run the most relevant tests:
   - Changes in `src/agent_framework/mcp/` → run `tests/unit/agent_framework/test_mcp/` and `tests/integration/test_mcp_infrastructure.py`
   - Changes in `src/agent_framework/engines/` → run `tests/unit/agent_framework/` and `tests/integration/test_single_agents.py`
   - Changes in `src/agent_framework/registry/` → run `tests/integration/test_agent_naming.py`
   - Changes in `debug_ui/` → no automated tests; remind to test via http://localhost:7001/studio
   - Changes in `src/service/` → run `tests/integration/test_streaming.py`

3. Always run using `pipenv run pytest`, never bare `pytest`.

4. Use these flags:
   - `-v` for verbose output
   - `-x` to stop on first failure
   - `--tb=short` for compact tracebacks

5. Common test commands for reference:
```bash
# All tests
pipenv run pytest tests/ -v

# Unit only (fast, no external deps)
pipenv run pytest tests/unit/ -v

# Integration (may need Docker postgres running)
pipenv run pytest tests/integration/ -v

# Specific integration suites
pipenv run pytest tests/integration/test_agent_naming.py -v         # no external deps
pipenv run pytest tests/integration/test_mcp_infrastructure.py -v  # no external deps
pipenv run pytest tests/integration/test_mcp_http_agents.py -v     # no external deps
pipenv run pytest tests/integration/test_mcp_stdio_agents.py -v    # needs Docker postgres
pipenv run pytest tests/integration/test_streaming.py -v           # needs LLM key

# Single file
pipenv run pytest tests/unit/agent_framework/test_mcp/test_client_manager.py -v

# With coverage
pipenv run pytest tests/ --cov=src --cov-report=html
```

6. After running:
   - Report which tests passed / failed
   - For failures, show the relevant traceback and suggest a fix if the cause is clear
   - If tests require external deps (postgres, API key) that aren't available, note which were skipped and why

## Test infrastructure notes
- `asyncio_mode = auto` is set in `pytest.ini` — all async tests work without extra decorator
- Integration tests auto-reset MCP singletons via `autouse` fixtures in `tests/integration/conftest.py`
- Tests needing postgres check `AGENT_SESSION_STORE_URI` env var and skip if not set
- Tests needing an LLM key check `OPENAI_API_KEY` and skip if not set
