"""Memory configuration for agents.

Simple abstraction over different memory solutions:
- Session memory: conversation-level, short-term
- Persistence memory: cross-session, long-term

Supported backends:
- Mem0: External memory service
- VertexAI: Google ADK-based memory (only works with google_adk runtime)
"""

import os
from enum import Enum
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings


load_dotenv()


class MemoryBackend(str, Enum):
    """Supported memory backend types."""
    MEM0 = "mem0"
    VERTEXAI = "vertexai"


class MemoryConfig(BaseModel):
    """Memory configuration for an agent.
    
    Example YAML:
        memory:
          enabled: true
          backend: "mem0"
    """
    
    enabled: bool = Field(
        default=False,
        description="Enable memory for this agent"
    )
    backend: Optional[MemoryBackend] = Field(
        default=None,
        description="Memory backend: 'mem0' or 'vertexai'. Required if enabled=true"
    )
    
    @model_validator(mode='after')
    def validate_backend_when_enabled(self) -> 'MemoryConfig':
        """Ensure backend is specified when memory is enabled."""
        if self.enabled and self.backend is None:
            raise ValueError("backend must be specified when memory is enabled")
        return self


class Mem0Settings(BaseSettings):
    """Mem0 memory backend configuration settings.
    
    Environment variables:
    - MEM0_API_KEY: Mem0 API key (required for Mem0 Platform)
    - MEM0_API_URL: Mem0 API URL (optional, defaults to platform URL)
    """
    
    MEM0_API_KEY: Optional[str] = os.getenv("MEM0_API_KEY")
    MEM0_API_URL: Optional[str] = os.getenv("MEM0_API_URL")


# Create a global instance
mem0_settings = Mem0Settings()
