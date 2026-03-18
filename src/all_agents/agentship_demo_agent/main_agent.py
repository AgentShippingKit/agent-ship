"""AgentShip Demo Agent — answers questions about the AgentShip framework.

Combines two live knowledge sources:
- GitHub: Agent-Ship/agent-ship repo (source code, issues, PRs, docs)
- Notion: AgentShip Team space (internal docs, roadmap, design decisions)

Prerequisites:
  1. NOTION_API_KEY in .env (internal Notion integration token)
  2. GitHub OAuth connected: agentship mcp connect github --user-id <your-user-id>
  3. GITHUB_OAUTH_CLIENT_ID and GITHUB_OAUTH_CLIENT_SECRET in .env
"""

from src.all_agents.base_agent import BaseAgent
from src.service.models.base_models import TextInput, TextOutput


class AgentShipDemoAgent(BaseAgent):
    """Knowledge agent for the AgentShip framework using GitHub + Notion MCP tools."""

    def __init__(self):
        super().__init__(
            _caller_file=__file__,
            input_schema=TextInput,
            output_schema=TextOutput,
        )
