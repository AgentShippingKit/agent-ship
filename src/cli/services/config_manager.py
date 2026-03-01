"""CLI configuration management."""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manage CLI configuration file."""

    DEFAULT_CONFIG_PATH = Path.home() / ".agentship" / "config.yaml"

    DEFAULT_CONFIG = {
        "api_url": "http://localhost:8000",
        "default_user": None,
        "timeout": 300,  # OAuth timeout in seconds
        "log_level": "INFO"
    }

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize config manager.

        Args:
            config_path: Path to config file (uses default if not specified)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self._config: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                self._config = {}
        else:
            self._config = {}

        # Merge with defaults
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self._config:
                self._config[key] = value

    def _save(self):
        """Save configuration to file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error: Could not save config to {self.config_path}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value.

        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
        self._save()

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.

        Returns:
            Dict of all config values
        """
        return self._config.copy()

    def get_api_url(self) -> str:
        """Get API URL.

        Returns:
            API base URL
        """
        return self.get("api_url", "http://localhost:8000")

    def get_default_user(self) -> Optional[str]:
        """Get default user ID.

        Returns:
            Default user ID or None
        """
        return self.get("default_user")

    def get_timeout(self) -> int:
        """Get OAuth timeout in seconds.

        Returns:
            Timeout in seconds
        """
        return self.get("timeout", 300)
