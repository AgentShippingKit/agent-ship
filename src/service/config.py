import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Agent Discovery Configuration
    # Comma-separated list of directories to discover agents from
    # Default: all agents (for development/testing)
    # For open-source: set to "src/agents/all_agents/orchestrator_pattern,src/agents/all_agents/single_agent_pattern,src/agents/all_agents/tool_pattern"
    AGENT_DIRECTORIES: str = os.getenv(
        "AGENT_DIRECTORIES", 
        "src/agents/all_agents"
    )
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_alpha(self) -> bool:
        return self.ENVIRONMENT.lower() == "alpha"
    
    @property
    def agent_directories(self) -> List[str]:
        """Get list of agent directories from configuration."""
        if not self.AGENT_DIRECTORIES:
            return ["src/agents/all_agents"]
        
        # Split by comma and strip whitespace
        directories = [d.strip() for d in self.AGENT_DIRECTORIES.split(",")]
        # Filter out empty strings
        return [d for d in directories if d]

settings = Settings()


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# List of paths that don't require authentication
PUBLIC_PATHS = [
    "/",
    "/docs",      # Framework documentation (MkDocs)
    "/swagger",   # Swagger UI (API docs)
    "/redoc",     # ReDoc (API docs)
    "/health",
]
