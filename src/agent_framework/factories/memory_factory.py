"""Memory factory for creating memory components.

This factory provides a clean interface for creating different
memory backends (Redis, PostgreSQL, in-memory, etc.) with proper
configuration and error handling.
"""

from typing import Optional
from abc import ABC, abstractmethod

from src.agent_framework.configs.memory_config import MemoryConfig, MemoryBackend


class BaseMemory(ABC):
    """Abstract base class for all memory implementations."""
    
    @abstractmethod
    async def store(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Store a value with optional TTL."""
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[str]:
        """Retrieve a stored value."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a stored value."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all stored values."""
        pass


class InMemoryMemory(BaseMemory):
    """In-memory implementation for testing and development."""
    
    def __init__(self, config: MemoryConfig):
        self._storage = {}
        self._ttl_storage = {}
        self.config = config
    
    async def store(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        self._storage[key] = value
        if ttl:
            import time
            self._ttl_storage[key] = time.time() + ttl
    
    async def retrieve(self, key: str) -> Optional[str]:
        import time
        if key in self._ttl_storage:
            if time.time() > self._ttl_storage[key]:
                await self.delete(key)
                return None
        return self._storage.get(key)
    
    async def delete(self, key: str) -> None:
        self._storage.pop(key, None)
        self._ttl_storage.pop(key, None)
    
    async def clear(self) -> None:
        self._storage.clear()
        self._ttl_storage.clear()


class RedisMemory(BaseMemory):
    """Redis implementation for distributed memory."""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self._client = None
    
    async def _get_client(self):
        if self._client is None:
            try:
                import redis.asyncio as redis
                self._client = redis.from_url(
                    self.config.connection_string,
                    decode_responses=True
                )
            except ImportError:
                raise ImportError("redis package is required for RedisMemory")
        return self._client
    
    async def store(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        client = await self._get_client()
        if ttl:
            await client.setex(key, ttl, value)
        else:
            await client.set(key, value)
    
    async def retrieve(self, key: str) -> Optional[str]:
        client = await self._get_client()
        return await client.get(key)
    
    async def delete(self, key: str) -> None:
        client = await self._get_client()
        await client.delete(key)
    
    async def clear(self) -> None:
        client = await self._get_client()
        await client.flushdb()


class MemoryFactory:
    """Factory for creating memory components.
    
    This factory creates memory instances based on configuration,
    with proper validation and error handling.
    """
    
    @staticmethod
    def create(memory_config: MemoryConfig) -> Optional[BaseMemory]:
        """Create a memory component based on configuration.
        
        Args:
            memory_config: Memory configuration including backend type
            
        Returns:
            Configured memory instance or None if disabled
            
        Raises:
            ValueError: If memory backend is not supported
            ImportError: If required dependencies are missing
        """
        if not memory_config.enabled:
            return None
        
        backend = memory_config.backend
        
        if backend == MemoryBackend.IN_MEMORY:
            return InMemoryMemory(memory_config)
        elif backend == MemoryBackend.REDIS:
            return RedisMemory(memory_config)
        elif backend == MemoryBackend.POSTGRESQL:
            # TODO: Implement PostgreSQL memory backend
            raise NotImplementedError(
                f"Memory backend '{backend.value}' is not yet implemented"
            )
        elif backend == MemoryBackend.VERTEXAI:
            # TODO: Implement VertexAI memory backend
            raise NotImplementedError(
                f"Memory backend '{backend.value}' is not yet implemented"
            )
        else:
            supported_backends = [b.value for b in MemoryBackend]
            raise ValueError(
                f"Unsupported memory backend '{backend.value}'. "
                f"Supported backends: {supported_backends}"
            )
