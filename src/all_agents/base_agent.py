"""Public import surface for agents.

Agent authors should import `BaseAgent` and `AgentType` from here.
The actual implementation lives in `src.agent_framework.core.base_agent`.
"""

from src.agent_framework.core.types import AgentType
from src.agent_framework.core.base_agent import BaseAgent

__all__ = ["BaseAgent", "AgentType"]
