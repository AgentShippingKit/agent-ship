"""Tool construction helpers for BaseAgent.

This module takes the `tools` configuration from `AgentConfig` and
constructs the appropriate Google ADK `FunctionTool` / `AgentTool`
instances.
"""

import importlib
import logging
from typing import Any, List

from google.adk.tools import FunctionTool, AgentTool

from src.agents.configs.agent_config import AgentConfig

logger = logging.getLogger(__name__)


def _import_string(dotted_path: str) -> Any:
    """Import a symbol from a dotted module path.

    Example: ``"src.agents.tools.conversation_insights_tool.ConversationInsightsTool"``
    """

    try:
        module_path, attr_name = dotted_path.rsplit(".", 1)
    except ValueError as exc:
        raise ImportError(f"Error parsing import path '{dotted_path}': {exc}") from exc

    module = importlib.import_module(module_path)
    try:
        return getattr(module, attr_name)
    except AttributeError as exc:  # pragma: no cover - defensive
        raise ImportError(f"Module '{module_path}' has no attribute '{attr_name}'") from exc


def build_tools_from_config(agent_config: AgentConfig) -> List[FunctionTool]:
    """Build tools for an agent from its YAML configuration.

    Expected schema (per-tool):

    - ``type: "function"``
      - ``import``: dotted path to a callable or a class
      - ``method``: optional method name on the class (e.g. ``"run"``)
    - ``type: "agent"``
      - ``agent_class``: dotted path to a ``BaseAgent`` subclass

    The order of tools in the returned list matches the order in the
    YAML config.
    """

    tools_config = getattr(agent_config, "tools", None)
    if not tools_config:
        return []

    tools: List[FunctionTool] = []

    for cfg in tools_config:
        try:
            cfg_type = cfg.get("type")

            if cfg_type == "function":
                import_path = cfg.get("import")
                method_name = cfg.get("method")
                if not import_path:
                    logger.warning(
                        "Skipping function tool without 'import' path in agent '%s': %s",
                        agent_config.agent_name,
                        cfg,
                    )
                    continue

                target = _import_string(import_path)

                if method_name:
                    target_obj = target()
                    func = getattr(target_obj, method_name, None)
                    if func is None:
                        logger.warning(
                            "Method '%s' not found on '%s' for agent '%s', skipping tool.",
                            method_name,
                            import_path,
                            agent_config.agent_name,
                        )
                        continue
                    # If the object has to_function_tool method, use it to get proper name/description
                    if hasattr(target_obj, 'to_function_tool') and callable(getattr(target_obj, 'to_function_tool')):
                        tool = target_obj.to_function_tool()
                        logger.info(f"Registered tool '{target_obj.tool_name}' with description: {target_obj.tool_description[:100]}...")
                        tools.append(tool)
                    else:
                        tools.append(FunctionTool(func))
                else:
                    if not callable(target):
                        logger.warning(
                            "Imported object '%s' is not callable for agent '%s', skipping tool.",
                            import_path,
                            agent_config.agent_name,
                        )
                        continue
                    tools.append(FunctionTool(target))

            elif cfg_type == "agent":
                agent_class_path = cfg.get("agent_class")
                if not agent_class_path:
                    logger.warning(
                        "Skipping agent tool without 'agent_class' in agent '%s': %s",
                        agent_config.agent_name,
                        cfg,
                    )
                    continue

                agent_cls = _import_string(agent_class_path)
                agent_instance = agent_cls()
                tools.append(AgentTool(agent_instance.agent))

            else:
                logger.warning(
                    "Unsupported tool type '%s' in agent '%s': %s",
                    cfg_type,
                    agent_config.agent_name,
                    cfg,
                )

        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(
                "Failed to create tool from config %s for agent '%s': %s",
                cfg,
                agent_config.agent_name,
                exc,
                exc_info=True,
            )

    return tools
