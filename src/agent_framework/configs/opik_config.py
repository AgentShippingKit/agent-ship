import os
import logging
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from typing import Literal, List


load_dotenv()
logger = logging.getLogger(__name__)


class OpikSettings(BaseSettings):
    """Opik observability configuration."""

    OPIK_API_KEY: str = os.getenv("OPIK_API_KEY")
    OPIK_WORKSPACE: str = os.getenv("OPIK_WORKSPACE")
    OPIK_PROJECT_NAME: str = os.getenv("OPIK_PROJECT_NAME")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    OPIK_FRAMEWORK: str = "google-adk"
    OPIK_LITTELM_INTEGRATION: str = "true"
    OPIK_TRACING_METHODS: List[str] = os.getenv("OPIK_TRACING_METHODS", ["decorators", "callbacks"])
    OPIK_FILE_LOGGING_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = os.getenv("OPIK_FILE_LOGGING_LEVEL", "INFO")
    OPIK_LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = os.getenv("OPIK_LOG_LEVEL", "INFO")

opik_settings = OpikSettings()
