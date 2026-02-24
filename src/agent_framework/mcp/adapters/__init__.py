"""MCP tool adapters: convert MCP tools to engine-specific types."""

from src.agent_framework.mcp.adapters.adk import to_adk_tool
from src.agent_framework.mcp.adapters.langgraph import to_langgraph_tool

__all__ = ["to_adk_tool", "to_langgraph_tool"]
