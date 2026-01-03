"""Agent execution engines.

This package defines the seam where we isolate *agent execution runtimes*:
- Google ADK execution
- (future) OpenAI Agents SDK execution
- (future) LangGraph execution

We use the term "engine" because these modules are responsible for executing
an agent using a particular runtime/framework.
"""

from src.agent_framework.engines.base import AgentEngine, EngineCapabilities
from src.agent_framework.factories.engine_factory import EngineFactory

# For backward compatibility, create_engine function
def create_engine(agent_config, input_schema, output_schema, observer=None):
    """Create an engine using the EngineFactory."""
    return EngineFactory.create(agent_config, input_schema, output_schema, observer)

__all__ = ["AgentEngine", "EngineCapabilities", "create_engine", "EngineFactory"]

