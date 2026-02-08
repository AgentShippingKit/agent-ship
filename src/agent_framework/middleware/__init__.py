"""Engine-agnostic middleware.

Middleware wraps an `AgentEngine` to add cross-cutting concerns (memory, RAG,
tracing, safety) without coupling those concerns to any specific engine/SDK.
"""

from src.agent_framework.middleware.base import EngineMiddleware

__all__ = ["EngineMiddleware"]

