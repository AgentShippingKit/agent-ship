"""Azure environment settings.

This module contains Azure-specific settings that are loaded
from environment variables using pydantic-settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class AzureSettings(BaseSettings):
    """Azure configuration settings loaded from environment variables."""
    
    # Azure Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING: str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    AZURE_STORAGE_ACCOUNT_NAME: str = os.getenv('AZURE_STORAGE_ACCOUNT_NAME')
    AZURE_STORAGE_ACCOUNT_KEY: str = os.getenv('AZURE_STORAGE_ACCOUNT_KEY')
    
    # Default container for operations
    AZURE_DEFAULT_CONTAINER: str = "documents"
    
    # PDF processing settings
    PDF_MAX_FILE_SIZE_MB: int = 50
    PDF_TEXT_EXTRACTION_METHOD: str = "pymupdf"  # or "pypdf2"
    PDF_SEARCH_CONTEXT_LENGTH: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create a global instance
azure_settings = AzureSettings()