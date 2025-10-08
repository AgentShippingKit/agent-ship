import abc
import logging
import json
import opik
from enum import Enum
from typing import Any, List, Optional, Type
from pydantic import BaseModel
from src.agents.configs.agent_config import AgentConfig
from src.models.base_models import TextInput, TextOutput, AgentChatRequest, AgentChatResponse
from src.agents.modules import SessionManager, AgentConfigurator, SessionServiceFactory, ResponseParser
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from google.adk import Agent
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv
from src.agents.observability.opik import OpikObserver


load_dotenv()
logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Enum for the type of agent."""
    LLM_AGENT = "llm_agent"
    PARALLEL_AGENT = "parallel_agent"
    SEQUENTIAL_AGENT = "sequential_agent"


class BaseAgent(abc.ABC):
    """Base class for all agents."""

    def __init__(self, agent_config: AgentConfig, 
                 input_schema: Optional[Type[BaseModel]] = None,
                 output_schema: Optional[Type[BaseModel]] = None,
                 agent_type: Optional[AgentType] = None):
        """Initialize the agent."""
        self.agent_config = agent_config
        self.agent_type = agent_type or AgentType.LLM_AGENT
        self.input_schema = input_schema or TextInput
        self.output_schema = output_schema or TextOutput
        logger.info(f"Agent config: {self.agent_config}")
        
        # Initialize modular components
        self.agent_configurator = AgentConfigurator(agent_config)
        self.session_service, self._use_database_sessions = SessionServiceFactory.create_session_service(
            self.agent_configurator.get_agent_name()
        )
        self.session_manager = SessionManager(
            self.session_service, 
            self.agent_configurator.get_agent_name(),
            self._use_database_sessions
        )
        self.response_parser = ResponseParser(self.agent_configurator.get_model())
        # Observability
        self._setup_observability()

        self._setup_agent()
        self._setup_runner()

    def _get_agent_name(self) -> str:
        """Get the name of the agent."""
        return self.agent_configurator.get_agent_name()
    
    def _get_agent_description(self) -> str:
        """Get the description of the agent."""
        return self.agent_configurator.get_agent_description()

    def _get_instruction_template(self) -> str:
        """Get the instruction template of the agent."""
        return self.agent_configurator.get_instruction_template()

    def _get_model(self) -> LiteLlm:
        """Get the model of the agent."""
        return self.agent_configurator.get_model()
    
    def _get_agent_config(self) -> AgentConfig:
        """Get the configuration of the agent."""
        return self.agent_configurator.get_agent_config()

    def _setup_agent(self) -> None:
        """Setup the Google ADK agent with tools."""
        logger.info(f"Setting up agent: {self.agent_config}")
        
        # Get tools from the agent implementation
        tools = self._create_tools()
        logger.info(f"Created {len(tools)} tools for agent: {self._get_agent_name()}")

        sub_agents = self._create_sub_agents()
        logger.info(f"Created {len(sub_agents)} sub-agents for agent: {self._get_agent_name()}")
        
        # Create agent configuration with input/output schemas and tools
        agent_kwargs = {
            "model": self._get_model(),
            "name": self._get_agent_name(),
            "description": self._get_agent_description(),
            "instruction": self._get_instruction_template(),
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "tools": tools,
            "sub_agents": sub_agents,
        }
        
        # Add observability callbacks only if observer is available
        if self.observer:
            agent_kwargs.update({
                "before_agent_callback": self.observer.before_agent_callback,
                "after_agent_callback": self.observer.after_agent_callback,
                "before_model_callback": self.observer.before_model_callback,
                "after_model_callback": self.observer.after_model_callback,
                "before_tool_callback": self.observer.before_tool_callback,
                "after_tool_callback": self.observer.after_tool_callback
            })
        else:
            logger.warning("No observability observer available - tracing will be disabled")
        
        self.agent = self._create_agent_from_type(agent_kwargs)

    def _create_agent_from_type(self, agent_kwargs: dict) -> Agent:
        """Create the agent."""
        if self._get_agent_type() == AgentType.LLM_AGENT:
            return LlmAgent(**agent_kwargs)
        elif self._get_agent_type() == AgentType.PARALLEL_AGENT:
            return ParallelAgent(**agent_kwargs)
        elif self._get_agent_type() == AgentType.SEQUENTIAL_AGENT:
            return SequentialAgent(**agent_kwargs)

        return Agent(**self.agent_kwargs)
    
    def _get_agent_type(self) -> AgentType:
        """Get the type of the agent."""
        return self.agent_type
    
    def _setup_observability(self) -> None:
        """Setup the observability for the agent."""
        logger.info(f"Setting up observer for agent: {self._get_agent_name()}")
        try:
            self.observer = OpikObserver(
                agent_config=self.agent_config
            )
        except Exception as e:
            logger.error(f"Failed to setup observability: {e}")
            # Create a no-op observer to prevent errors
            self.observer = None

    def _setup_runner(self) -> None:
        """Setup the Google ADK runner."""
        logger.info(f"Setting up runner for agent: {self._get_agent_name()}")
        self.runner = Runner(
            agent=self.agent,
            app_name=self._get_agent_name(),
            session_service=self.session_service,
        )


    async def run(self, user_id: str, session_id: str, input_data: BaseModel) -> BaseModel:
        """Run the agent with schema validation handled by ADK."""
        logger.info(f"Running agent: {self._get_agent_name()}")
        logger.debug(f"Using session ID: {session_id}")
        
        # Handle session management based on session service type
        await self.session_manager.ensure_session_exists(user_id, session_id)
        
        # Serialize structured input for the model
        input_text = input_data.model_dump_json()
        
        # Create the proper Google ADK message format
        content = types.Content(
            role='user',
            parts=[types.Part(text=input_text)]
        )
        
        # Run the agent - ADK handles schema validation, output formatting, and session management
        # The runner.run() returns a generator, so we need to consume it
        result_generator = self.runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        )

        # Consume the generator to get the final result
        # The generator yields multiple events: function calls, tool results, final response
        result = None
        for response in result_generator:
            # Look for the final text response (not function calls)
            if (hasattr(response, 'content') and 
                response.content and 
                response.content.parts and 
                response.content.parts[0].text):
                result = response
        
        logger.debug(f"Result: {result}")
        # Parse the result according to output_schema
        return self._parse_agent_response(result)
    
    def _parse_agent_response(self, result) -> BaseModel:
        """Parse the agent response according to the output schema."""
        # Extract the content from the Event object and parse it according to output_schema
        logger.debug(f"Parsing agent response: {result}")
        if result and hasattr(result, 'content') and result.content and result.content.parts:
            # Extract the text content from the event
            content_text = result.content.parts[0].text
            
            # Parse the JSON content according to our output schema
            try:
                logger.debug(f"Parsing agent response: {content_text}")
                parsed_data = json.loads(content_text)
                # Create the output schema instance
                logger.debug(f"Parsed data: {parsed_data}")
                output_instance = self.output_schema(**parsed_data)
                logger.debug(f"Output instance: {output_instance}")
                return output_instance
            except (json.JSONDecodeError, TypeError, ValueError) as e:
                logger.error(f"Failed to parse output: {e}")
                # Fallback: return the raw content
                return content_text
        else:
            logger.error("No valid content found in the response")
            return None
    
    @abc.abstractmethod
    async def chat(self, agent_chat_request: AgentChatRequest) -> AgentChatResponse:
        """Chat with the agent."""
        pass
    
    @abc.abstractmethod
    def _create_tools(self) -> List[FunctionTool]:
        """Create the tools for the agent."""
        pass

    @abc.abstractmethod
    def _create_sub_agents(self) -> List[Agent]:
        """Create the sub-agents for the agent."""
        pass
