from enum import Enum


class AgentType(Enum):
    """Enum for the type of agent.

    This is re-exported via `src.agents.all_agents.base_agent` so that
    agent authors can continue to import it from there.
    """

    LLM_AGENT = "llm_agent"
    PARALLEL_AGENT = "parallel_agent"
    SEQUENTIAL_AGENT = "sequential_agent"
