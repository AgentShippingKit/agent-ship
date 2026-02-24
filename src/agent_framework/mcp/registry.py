"""Global MCP server registry.

Loads server definitions from a config file and provides lookup by ID.
Singleton: use MCPServerRegistry.get_instance().
"""

import json
import logging
import os
from typing import Dict, List, Optional

import yaml

from src.agent_framework.mcp.models import MCPServerConfig

logger = logging.getLogger(__name__)


class MCPServerRegistry:
    """Manages global MCP server configurations.

    Config file discovery order:
    1. MCP_SERVERS_CONFIG (env var)
    2. .mcp.settings.json (project root)
    3. mcp_servers.yaml (project root)
    4. mcp_servers.json (project root)
    """

    _instance: Optional["MCPServerRegistry"] = None

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize registry from config file.

        Args:
            config_path: Optional path to config file. If None, discovery is used.
        """
        self._servers: Dict[str, MCPServerConfig] = {}
        path = config_path or self._find_config_file()
        if path and os.path.exists(path):
            self._load_config(path)
        else:
            if config_path and not os.path.exists(config_path):
                logger.warning("MCP config path does not exist: %s", config_path)
            else:
                logger.debug("No MCP config file found; registry empty")

    def _find_config_file(self) -> Optional[str]:
        """Return path to first existing config file in standard locations.

        Priority order (AgentShip-only):
        1. MCP_SERVERS_CONFIG env var (explicit override)
        2. .mcp.settings.json (AgentShip project config) ← PRIMARY
        3. mcp_servers.yaml (AgentShip YAML format)
        4. mcp_servers.json (AgentShip JSON format)
        """
        locations: List[str] = []

        # 1. Explicit env var override
        env_path = os.getenv("MCP_SERVERS_CONFIG")
        if env_path:
            locations.append(env_path)

        cwd = os.getcwd()

        # 2-4. AgentShip-native locations
        locations.extend([
            os.path.join(cwd, ".mcp.settings.json"),  # Primary config
            os.path.join(cwd, "mcp_servers.yaml"),
            os.path.join(cwd, "mcp_servers.json"),
        ])

        for path in locations:
            if path and os.path.exists(path):
                logger.info("Found MCP config file: %s", path)
                return path
        return None

    def _load_config(self, config_path: str) -> None:
        """Load server configurations from file. Overwrites current _servers.

        Supports flexible root keys: "servers" (preferred) or "mcpServers" (alternate).
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            logger.error("Invalid MCP config file %s: %s", config_path, e)
            raise

        if not isinstance(data, dict):
            logger.error("MCP config root must be a dict; got %s", type(data).__name__)
            raise ValueError("MCP config root must be a dict")

        # Support both "servers" (preferred) and "mcpServers" (alternate root key)
        servers = data.get("servers") or data.get("mcpServers", {})
        if not isinstance(servers, dict):
            logger.error("MCP config 'servers' or 'mcpServers' must be a dict; got %s", type(servers).__name__)
            raise ValueError("MCP config must contain 'servers' or 'mcpServers' dict")

        self._servers = {}
        for server_id, raw in servers.items():
            if not isinstance(raw, dict):
                logger.warning("Skipping invalid server entry '%s': not a dict", server_id)
                continue
            try:
                # Normalize server config to standard format
                normalized = self._normalize_server_config(server_id, raw)
                config = MCPServerConfig(**normalized)
                self._servers[server_id] = config
            except Exception as e:
                logger.warning("Skipping server '%s': %s", server_id, e)

        logger.info("Loaded %d MCP server(s) from %s", len(self._servers), config_path)

    def get_server(self, server_id: str) -> Optional[MCPServerConfig]:
        """Return server config by ID, or None if not found."""
        return self._servers.get(server_id)

    def get_servers(self, server_ids: List[str]) -> List[MCPServerConfig]:
        """Return configs for the given IDs; skips missing IDs (no error)."""
        return [self._servers[sid] for sid in server_ids if sid in self._servers]

    def list_server_ids(self) -> List[str]:
        """Return all registered server IDs."""
        return list(self._servers.keys())

    @classmethod
    def get_instance(cls, config_path: Optional[str] = None) -> "MCPServerRegistry":
        """Return singleton instance. First call may pass config_path; later calls ignore it."""
        if cls._instance is None:
            cls._instance = cls(config_path=config_path)
        return cls._instance

    def _normalize_server_config(self, server_id: str, raw: Dict) -> Dict:
        """Normalize server config to standard format.

        Handles flexible input formats:
        - Compact: { "command": "npx", "args": [...], "env": {...} }
        - Explicit: { "transport": "stdio", "command": [...], ... }
        - Mixed: { "transport": "stdio", "command": "npx", "args": [...] }
        """
        normalized = {"id": server_id}

        # Copy or auto-detect transport
        if "transport" in raw:
            normalized["transport"] = raw["transport"]
        elif "url" in raw:
            normalized["transport"] = "http"  # Model will refine based on URL
            normalized["url"] = raw["url"]
        elif "command" in raw:
            normalized["transport"] = "stdio"

        # Handle command field (always normalize command + args if present)
        if "command" in raw:
            command = raw["command"]
            args = raw.get("args", [])

            # Command can be string or list
            # String + args → combine into single list
            if isinstance(command, str):
                normalized["command"] = [command] + (args if isinstance(args, list) else [])
            elif isinstance(command, list):
                normalized["command"] = command
            else:
                logger.warning("Server '%s': invalid command type %s", server_id, type(command).__name__)
                normalized["command"] = [str(command)]

        # Copy URL for HTTP/SSE transports
        if "url" in raw:
            normalized["url"] = raw["url"]

        # Copy environment variables
        if "env" in raw:
            normalized["env"] = raw["env"]

        # Copy other optional fields
        for key in ["timeout", "max_retries", "auth", "tools"]:
            if key in raw:
                normalized[key] = raw[key]

        return normalized

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for tests)."""
        cls._instance = None
