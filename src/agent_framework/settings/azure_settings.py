"""Re-export Azure settings from azure_config for backward compatibility."""

from .azure_config import AzureSettings, azure_settings

__all__ = ["AzureSettings", "azure_settings"]
