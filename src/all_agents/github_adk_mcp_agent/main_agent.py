"""GitHub ADK MCP Agent - Demonstrates GitHub integration via MCP OAuth.

This agent showcases:
- OAuth-authenticated GitHub MCP tools via SSE transport
- ADK execution engine with streaming
- Real GitHub API access through MCP protocol

Prerequisites:
1. GitHub OAuth app configured (see docs/TESTING_MCP_OAUTH.md)
2. User connected via: agentship mcp connect github --user-id test_user
3. GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET in .env

Example Usage:
    POST /sessions/{session_id}/message
    {
        "message": "Search for Python repositories with more than 1000 stars"
    }
"""

from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput


class GitHubADKMCPAgent(BaseAgent):
    """GitHub agent using ADK engine with GitHub Copilot MCP tools."""

    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput,
        )
