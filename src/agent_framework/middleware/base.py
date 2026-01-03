"""Middleware protocol for engines.

This is intentionally minimal for the first refactor pass.
We can expand it later to include richer streaming hooks and standardized
context objects.
"""

from __future__ import annotations

import abc
from typing import Any, Dict, Optional

from pydantic import BaseModel


class EngineMiddleware(abc.ABC):
    """Engine-agnostic middleware.

    A middleware can:
    - inspect/transform the input before the engine runs
    - observe the output after the engine runs (for writeback/telemetry)
    """

    @abc.abstractmethod
    async def before_run(
        self,
        *,
        user_id: str,
        session_id: str,
        input_data: BaseModel,
        meta: Optional[Dict[str, Any]] = None,
    ) -> BaseModel:
        """Return the (possibly transformed) input_data."""

    @abc.abstractmethod
    async def after_run(
        self,
        *,
        user_id: str,
        session_id: str,
        input_data: BaseModel,
        output_data: Any,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Observe the result (no return)."""

