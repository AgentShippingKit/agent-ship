"""Configuration loading helpers.

This wraps the logic for loading `AgentConfig` from YAML, including the
`_caller_file` and stack-based auto-detection.
"""

import inspect
from typing import Optional

from src.agent_framework.configs.agent_config import AgentConfig
from src.agent_framework.utils.path_utils import resolve_config_path


def load_agent_config(
    agent_config: Optional[AgentConfig] = None,
    config_path: Optional[str] = None,
    caller_file: Optional[str] = None,
) -> AgentConfig:
    """Load or resolve an `AgentConfig`.

    Priority:
    1. If `agent_config` is provided, return it as-is.
    2. Else, resolve `config_path`.
       - If `config_path` is None but `caller_file` is provided, derive YAML
         path from that.
       - Else, fall back to stack inspection to find the calling module's
         `__file__`.
    """

    if agent_config is not None:
        return agent_config

    # Resolve config path if not explicitly provided
    if config_path is None:
        if caller_file:
            config_path = resolve_config_path(relative_to=caller_file)
        else:
            # Fallback: attempt to infer from the call stack
            try:
                frame = inspect.currentframe()
                caller_frame = frame.f_back if frame else None
                if caller_frame:
                    caller_file_stack = caller_frame.f_globals.get("__file__")
                    if caller_file_stack:
                        config_path = resolve_config_path(relative_to=caller_file_stack)
                    else:
                        raise ValueError(
                            "Cannot auto-detect config file. Please provide one of: "
                            "agent_config, config_path, or _caller_file=__file__"
                        )
                if frame is not None:
                    del frame
            except Exception as e:  # pragma: no cover - defensive
                raise ValueError(
                    f"Cannot auto-detect config file: {e}. "
                    "Please provide one of: agent_config, config_path, or _caller_file=__file__"
                )

    if not config_path:
        raise ValueError("Config path could not be resolved.")

    # AgentConfig.from_yaml already normalises and validates the path
    return AgentConfig.from_yaml(config_path)
