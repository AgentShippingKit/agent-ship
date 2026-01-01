"""Core implementation of `BaseAgent`.

This is the primary class that agent authors build on, but the heavy
lifting is delegated to small helper modules in this `core` package so
that the code is easier to read and extend.
"""

import abc
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional, Type

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.genai import types
from pydantic import BaseModel

from src.agents.configs.agent_config import AgentConfig
from src.agents.core.config import load_agent_config
from src.agents.core.io import create_input_from_request, parse_agent_response
from src.agents.core.observability import create_observer
from src.agents.core.tools import build_tools_from_config
from src.agents.core.types import AgentType
from src.agents.modules import (
    AgentConfigurator,
    ResponseParser,
    SessionManager,
    SessionServiceFactory,
)
from src.models.base_models import AgentChatRequest, AgentChatResponse, TextInput, TextOutput


load_dotenv()
logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """Base class for all agents.

    Responsibilities (high-level):
    - Load `AgentConfig` from YAML (via `load_agent_config`).
    - Wire up session services and the Google ADK `Runner`.
    - Build tools from YAML configuration.
    - Provide a default `chat()` implementation.

    Subclasses typically only need to:
    - Provide `input_schema` / `output_schema` via `super().__init__`.
    - Optionally override `_create_input_from_request` for custom input
      mapping.
    """

    def __init__(
        self,
        agent_config: Optional[AgentConfig] = None,
        input_schema: Optional[Type[BaseModel]] = None,
        output_schema: Optional[Type[BaseModel]] = None,
        agent_type: Optional[AgentType] = None,
        config_path: Optional[str] = None,
        _caller_file: Optional[str] = None,
    ) -> None:
        # 1) Load configuration
        self.agent_config: AgentConfig = load_agent_config(
            agent_config=agent_config,
            config_path=config_path,
            caller_file=_caller_file,
        )
        logger.info("Agent config: %s", self.agent_config)

        # 2) Basic properties
        self.agent_type: Optional[AgentType] = agent_type
        self.input_schema: Type[BaseModel] = input_schema or TextInput
        self.output_schema: Type[BaseModel] = output_schema or TextOutput

        # 3) Modular components for configuration & sessions
        self.agent_configurator = AgentConfigurator(self.agent_config)
        self.session_service, self._use_database_sessions = SessionServiceFactory.create_session_service(
            self.agent_configurator.get_agent_name()
        )
        self.session_manager = SessionManager(
            self.session_service,
            self.agent_configurator.get_agent_name(),
            self._use_database_sessions,
        )
        self.response_parser = ResponseParser(self.agent_configurator.get_model())

        # 4) Observability (Opik)
        self.observer = create_observer(self.agent_config)

        # 5) Create underlying ADK agent and runner
        self._setup_agent()
        self._setup_runner()

    # ------------------------------------------------------------------
    # Small helper accessors
    # ------------------------------------------------------------------

    def _get_agent_name(self) -> str:
        return self.agent_configurator.get_agent_name()

    def _get_agent_description(self) -> str:
        return self.agent_configurator.get_agent_description()

    def _get_instruction_template(self) -> str:
        return self.agent_configurator.get_instruction_template()

    def _get_model(self) -> LiteLlm:
        return self.agent_configurator.get_model()

    def _get_agent_config(self) -> AgentConfig:
        return self.agent_configurator.get_agent_config()

    # ------------------------------------------------------------------
    # Agent + runner construction
    # ------------------------------------------------------------------

    def _setup_agent(self) -> None:
        """Setup the Google ADK agent with tools."""

        logger.info("Setting up agent: %s", self.agent_config)

        tools = self._create_tools()
        logger.info("Created %d tools for agent: %s", len(tools), self._get_agent_name())

        sub_agents = self._create_sub_agents()
        logger.info("Created %d sub-agents for agent: %s", len(sub_agents), self._get_agent_name())

        agent_kwargs: dict[str, Any] = {
            "model": self._get_model(),
            "name": self._get_agent_name(),
            "description": self._get_agent_description(),
            "instruction": self._get_instruction_template(),
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "tools": tools,
            "sub_agents": sub_agents,
        }

        # Attach observability callbacks if available
        if self.observer:
            agent_kwargs.update(
                {
                    "before_agent_callback": self.observer.before_agent_callback,
                    "after_agent_callback": self.observer.after_agent_callback,
                    "before_model_callback": self.observer.before_model_callback,
                    "after_model_callback": self.observer.after_model_callback,
                    "before_tool_callback": self.observer.before_tool_callback,
                    "after_tool_callback": self.observer.after_tool_callback,
                }
            )
        else:
            logger.warning("No observability observer available - tracing will be disabled")

        self.agent: Agent = self._create_agent_from_type(agent_kwargs)

    def _create_agent_from_type(self, agent_kwargs: dict[str, Any]) -> Agent:
        """Instantiate the concrete ADK agent based on `agent_type`."""

        if self._get_agent_type() == AgentType.LLM_AGENT:
            return LlmAgent(**agent_kwargs)
        if self._get_agent_type() == AgentType.PARALLEL_AGENT:
            return ParallelAgent(**agent_kwargs)
        if self._get_agent_type() == AgentType.SEQUENTIAL_AGENT:
            return SequentialAgent(**agent_kwargs)
        return Agent(**agent_kwargs)

    def _get_agent_type(self) -> Optional[AgentType]:
        return self.agent_type

    def _setup_runner(self) -> None:
        """Setup the Google ADK runner."""

        logger.info("Setting up runner for agent: %s", self._get_agent_name())
        self.runner = Runner(
            agent=self.agent,
            app_name=self._get_agent_name(),
            session_service=self.session_service,
        )

    # ------------------------------------------------------------------
    # Public run + chat API
    # ------------------------------------------------------------------

    async def run(self, user_id: str, session_id: str, input_data: BaseModel) -> BaseModel:
        """Run the agent with schema validation handled by ADK."""

        logger.info("Running agent: %s", self._get_agent_name())
        logger.debug("Using session ID: %s", session_id)

        await self.session_manager.ensure_session_exists(user_id, session_id)

        input_text = input_data.model_dump_json()
        content = types.Content(role="user", parts=[types.Part(text=input_text)])

        result_generator = self.runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        )

        result = None
        for response in result_generator:
            if (
                hasattr(response, "content")
                and response.content
                and response.content.parts
                and response.content.parts[0].text
            ):
                result = response

        logger.debug("Result: %s", result)
        return self._parse_agent_response(result)

    def _parse_agent_response(self, result) -> BaseModel:
        """Parse the agent response according to the output schema."""

        return parse_agent_response(self.output_schema, result)

    # ------------------------------------------------------------------
    # Overridable hooks
    # ------------------------------------------------------------------

    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Create input schema instance from `AgentChatRequest`.

        Subclasses may override this for custom input transformation. The
        default implementation delegates to `core.io.create_input_from_request`.
        """

        return create_input_from_request(self.input_schema, request)

    async def chat(self, request: AgentChatRequest) -> AgentChatResponse:
        """Default chat implementation.

        Steps:
        1. Build input schema from the request.
        2. Run the agent.
        3. Wrap the result in `AgentChatResponse` with basic error handling.
        """

        logger.debug("Chatting with the agent: %s", self._get_agent_name())

        try:
            input_data = self._create_input_from_request(request)

            result = await self.run(
                request.user_id,
                request.session_id,
                input_data,
            )

            logger.info("Result from %s: %s", self._get_agent_name(), result)

            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=True,
                agent_response=result,
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("Error in %s: %s", self._get_agent_name(), exc, exc_info=True)
            return AgentChatResponse(
                agent_name=self._get_agent_name(),
                user_id=request.user_id,
                session_id=request.session_id,
                success=False,
                agent_response=f"Error: {str(exc)}",
            )

    def _create_tools(self) -> List[Any]:
        """Create tools for the agent.

        By default this reads from the agent's YAML configuration via
        `build_tools_from_config`. Subclasses can override this for very
        custom behaviour.
        """

        return build_tools_from_config(self.agent_config)

    def _create_sub_agents(self) -> List[Agent]:
        """Create sub-agents for the agent.

        The default implementation returns an empty list; subclasses can
        override this to supply explicit sub-agents if needed.
        """

        return []

    # ------------------------------------------------------------------
    # Streaming API
    # ------------------------------------------------------------------

    async def run_stream(
        self, user_id: str, session_id: str, input_data: BaseModel
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Run the agent with streaming - yields events as they happen.

        Events yielded:
        - {"type": "thinking", "agent": "...", "message": "..."}
        - {"type": "tool_call", "agent": "...", "tool_name": "...", "arguments": {...}}
        - {"type": "tool_result", "agent": "...", "tool_name": "...", "result": "..."}
        - {"type": "content", "agent": "...", "text": "..."}
        - {"type": "done"}
        """
        logger.info("Starting streaming run for agent: %s", self._get_agent_name())

        await self.session_manager.ensure_session_exists(user_id, session_id)

        input_text = input_data.model_dump_json()
        content = types.Content(role="user", parts=[types.Part(text=input_text)])

        # Emit "thinking" event to indicate processing started
        yield {
            "type": "thinking",
            "agent": self._get_agent_name(),
            "message": "Processing your request...",
        }

        # ADK Runner.run() returns a generator with events
        try:
            result_generator = self.runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=content,
            )
            logger.info("Runner.run() returned generator, starting to iterate...")
        except Exception as e:
            logger.error(f"Failed to create runner generator: {e}", exc_info=True)
            yield {
                "type": "error",
                "agent": self._get_agent_name(),
                "message": f"Failed to start agent: {str(e)}",
            }
            return

        # Track the last content event for final response
        last_content_event = None
        event_count = 0

        # Iterate through all events from the runner
        try:
            for event in result_generator:
                event_count += 1
                logger.info(f"Received event #{event_count} from runner: {type(event).__name__}")
                
                stream_events = self._format_stream_event(event)
                logger.info(f"Formatted {len(stream_events)} stream events from event #{event_count}")
                
                if not stream_events:
                    # If no stream events were generated, log why
                    if not hasattr(event, "content"):
                        logger.warning(f"Event #{event_count} has no 'content' attribute. Event type: {type(event)}, dir: {[a for a in dir(event) if not a.startswith('_')][:10]}")
                    elif not event.content:
                        logger.warning(f"Event #{event_count} has empty 'content'")
                    elif not hasattr(event.content, "parts") or not event.content.parts:
                        logger.warning(f"Event #{event_count} has content but no parts")
                    else:
                        logger.warning(f"Event #{event_count} has {len(event.content.parts)} parts but none were processed")
                
                for stream_event in stream_events:
                    if stream_event["type"] == "content":
                        last_content_event = stream_event
                        content_text = stream_event.get("text", "")
                        logger.info(f"Yielding content event: text_length={len(str(content_text))}, preview={str(content_text)[:100] if content_text else 'EMPTY'}")
                    yield stream_event

            logger.info(f"Finished processing {event_count} events from runner")
        except Exception as e:
            logger.error(f"Error while processing runner events: {e}", exc_info=True)
            yield {
                "type": "error",
                "agent": self._get_agent_name(),
                "message": f"Error processing events: {str(e)}",
            }
        
        yield {"type": "done"}

    def _format_stream_event(self, event) -> List[Dict[str, Any]]:
        """Convert ADK event to streamable format with tool call visibility.

        Returns a list of events (an ADK event may contain multiple parts).
        """
        events = []

        if not hasattr(event, "content") or not event.content:
            logger.debug(f"Event has no content: {type(event)}, attributes: {dir(event) if hasattr(event, '__dict__') else 'N/A'}")
            return events

        author = getattr(event, "author", self._get_agent_name())

        # Check each part of the content
        for part in event.content.parts if event.content.parts else []:
            # Function/Tool Call (the model is requesting to call a tool)
            if hasattr(part, "function_call") and part.function_call:
                fc = part.function_call
                events.append({
                    "type": "tool_call",
                    "agent": author,
                    "tool_name": fc.name if hasattr(fc, "name") else str(fc),
                    "arguments": dict(fc.args) if hasattr(fc, "args") and fc.args else {},
                })

            # Function/Tool Response (result from a tool call)
            elif hasattr(part, "function_response") and part.function_response:
                fr = part.function_response
                result_str = ""
                if hasattr(fr, "response"):
                    result_str = str(fr.response)[:500]  # Truncate long results
                events.append({
                    "type": "tool_result",
                    "agent": author,
                    "tool_name": fr.name if hasattr(fr, "name") else "unknown",
                    "result": result_str,
                })

            # Text content
            elif hasattr(part, "text"):
                text_value = part.text if part.text else ""
                logger.info(f"Found text part: has_text={bool(part.text)}, text_length={len(str(text_value))}, preview={str(text_value)[:100] if text_value else 'EMPTY'}")
                if text_value:
                    events.append({
                        "type": "content",
                        "agent": author,
                        "text": text_value,
                    })
                else:
                    logger.warning(f"Text part exists but is empty or None")

        return events

    async def chat_stream(
        self, request: AgentChatRequest
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Streaming chat - yields events for SSE.

        This is the streaming equivalent of chat(). Use this for real-time
        updates showing tool calls, thinking states, and progressive responses.
        """
        logger.debug("Starting streaming chat with agent: %s", self._get_agent_name())

        try:
            input_data = self._create_input_from_request(request)

            async for event in self.run_stream(
                request.user_id,
                request.session_id,
                input_data,
            ):
                yield event

        except Exception as exc:
            logger.error("Streaming chat error: %s", exc, exc_info=True)
            yield {
                "type": "error",
                "agent": self._get_agent_name(),
                "message": str(exc),
            }
