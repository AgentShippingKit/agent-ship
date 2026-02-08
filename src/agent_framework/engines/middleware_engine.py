"""Middleware-wrapped engine.

This wrapper lets us add memory/RAG/tracing/safety without coupling to any
specific engine (ADK/OpenAI SDK/LangGraph).

Current scope:
- Non-streaming hooks are fully supported.
- Streaming is pass-through for now (future: add streaming hooks + final response capture).
"""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Optional

from pydantic import BaseModel

from src.agent_framework.engines.base import AgentEngine, EngineCapabilities
from src.agent_framework.middleware.base import EngineMiddleware


class MiddlewareEngine(AgentEngine):
    def __init__(
        self,
        *,
        inner: AgentEngine,
        middlewares: List[EngineMiddleware],
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._inner = inner
        self._middlewares = middlewares
        self._meta = meta or {}

    def engine_name(self) -> str:
        # Preserve the underlying engine identity for logging/config.
        return self._inner.engine_name()

    def capabilities(self) -> EngineCapabilities:
        return self._inner.capabilities()

    def rebuild(self) -> None:
        return self._inner.rebuild()

    async def run(self, user_id: str, session_id: str, input_data: BaseModel) -> Any:
        current_input = input_data
        for mw in self._middlewares:
            current_input = await mw.before_run(
                user_id=user_id,
                session_id=session_id,
                input_data=current_input,
                meta=self._meta,
            )

        output = await self._inner.run(user_id=user_id, session_id=session_id, input_data=current_input)

        for mw in reversed(self._middlewares):
            await mw.after_run(
                user_id=user_id,
                session_id=session_id,
                input_data=current_input,
                output_data=output,
                meta=self._meta,
            )

        return output

    async def run_stream(
        self, user_id: str, session_id: str, input_data: BaseModel
    ) -> AsyncGenerator[Dict[str, Any], None]:
        # Pass-through for now (no behavior change).
        async for event in self._inner.run_stream(user_id=user_id, session_id=session_id, input_data=input_data):
            yield event

