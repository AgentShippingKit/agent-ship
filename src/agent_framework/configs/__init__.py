"""Configuration system for AI-Ecosystem.

This module contains agent configurations and utility loaders.

Structure:
- agent_config.py: Agent behavior and capabilities configuration
- memory_config.py: Memory backend configuration  
- loader.py: Utility methods to load configurations
- llm/: LLM provider configurations and enums
"""

from .agent_config import AgentConfig, ExecutionEngine, StreamingMode
from .memory_config import MemoryConfig, MemoryBackend
from .loader import load_agent_config

__all__ = [
    "AgentConfig",
    "ExecutionEngine", 
    "StreamingMode",
    "MemoryConfig",
    "MemoryBackend",
    "load_agent_config",
]