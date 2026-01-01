"""Public import surface for agents.

Agent authors should import `BaseAgent` and `AgentType` from here.
The actual implementation lives in `src.agents.core.base_agent`.
"""

from src.agents.core.types import AgentType
from src.agents.core.base_agent import BaseAgent

__all__ = ["BaseAgent", "AgentType"]
