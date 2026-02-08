"""Engine interface for agent execution.

This is the seam where we isolate framework specifics:
- ADK runner execution
- (future) OpenAI Agents SDK execution
- (future) LangGraph execution
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, FrozenSet, Optional

from pydantic import BaseModel


@dataclass(frozen=True)
class EngineCapabilities:
    """Capabilities contract for an execution engine.

    This is used to fail-fast when an agent is configured with an engine
    that cannot support its requested model/provider/features.
    """

    supported_providers: FrozenSet[str]
    supports_sse_streaming: bool = True
    supports_tool_calling: bool = True
    supports_bidi_streaming: bool = False
    supports_multimodal: bool = False
    notes: Optional[str] = None


class AgentEngine(abc.ABC):
    """Abstract engine for executing an agent."""

    @abc.abstractmethod
    def engine_name(self) -> str:
        """Human-readable engine name (e.g. 'adk', 'openai_sdk')."""

    @abc.abstractmethod
    def capabilities(self) -> EngineCapabilities:
        """Return the engine capability contract."""

    @abc.abstractmethod
    async def run(self, user_id: str, session_id: str, input_data: BaseModel) -> BaseModel:
        """Run the agent (non-streaming)."""

    @abc.abstractmethod
    async def run_stream(
        self, user_id: str, session_id: str, input_data: BaseModel
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run the agent and yield standardized stream events."""

    def rebuild(self) -> None:
        """Optional hook to rebuild underlying engine state."""

        return None

