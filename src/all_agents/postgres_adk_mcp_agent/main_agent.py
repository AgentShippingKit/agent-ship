"""PostgreSQL ADK MCP agent: query AgentShip database using ADK engine with MCP tools."""

from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput


class PostgresAdkMcpAgent(BaseAgent):
    """Agent that uses PostgreSQL MCP tools with ADK execution engine.

    This agent demonstrates MCP database integration with the ADK engine by
    connecting to the PostgreSQL database and using MCP tools.

    The agent has read-only access to the agentship_session_store database and can:
    - List all tables
    - Describe table schemas
    - Execute SELECT queries
    - Analyze session data
    """

    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput,
        )
