"""Environment-based settings loaded from .env files.

This module contains settings classes that automatically load
configuration from environment variables using pydantic-settings.
"""

from .azure_settings import AzureSettings, azure_settings

__all__ = [
    "AzureSettings",
    "azure_settings",
]
