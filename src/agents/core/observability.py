"""Observability helpers (Opik integration)."""

import logging
from typing import Optional

from src.agents.configs.agent_config import AgentConfig
from src.agents.observability.opik import OpikObserver

logger = logging.getLogger(__name__)


def create_observer(agent_config: AgentConfig) -> Optional[OpikObserver]:
    """Create an OpikObserver for the given agent config.

    If observer creation fails (e.g. missing env vars), a warning is logged
    and `None` is returned, allowing the framework to continue without
    observability.
    """

    try:
        return OpikObserver(agent_config=agent_config)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Failed to setup observability: %s", exc)
        return None
