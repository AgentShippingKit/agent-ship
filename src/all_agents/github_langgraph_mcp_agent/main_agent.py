"""GitHub LangGraph MCP Agent - Demonstrates GitHub integration via MCP OAuth.

This agent showcases:
- OAuth-authenticated GitHub MCP tools via SSE transport
- LangGraph execution engine with streaming
- Real GitHub API access through MCP protocol

Prerequisites:
1. GitHub OAuth app configured (see docs/TESTING_MCP_OAUTH.md)
2. User connected via: agentship mcp connect github --user-id test_user
3. GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET in .env

Example Usage:
    POST /sessions/{session_id}/message
    {
        "message": "Find the most popular Python AI repositories"
    }
"""

from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput


class GitHubLangGraphMCPAgent(BaseAgent):
    """GitHub agent using LangGraph engine with GitHub Copilot MCP tools."""

    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput,
        )
