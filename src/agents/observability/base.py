import logging
import abc
from src.agents.configs.agent_config import AgentConfig
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest

logger = logging.getLogger(__name__)

class BaseObserver(abc.ABC):
    """Base class for all observability."""

    def __init__(self, agent_config: AgentConfig):
        self.agent_config = agent_config
        self.agent_name = self.agent_config.agent_name

        self.tracer = None

        self.setup()

    @abc.abstractmethod
    def setup(self) -> None:
        """Setup the observability."""
    
    @abc.abstractmethod
    def before_agent_callback(self, callback_context: CallbackContext) -> None:
        """Before agent callback."""
    
    @abc.abstractmethod
    def after_agent_callback(self, callback_context: CallbackContext) -> None:
        """After agent callback."""
    
    @abc.abstractmethod
    def before_tool_callback(self, callback_context: CallbackContext) -> None:
        """Before tool callback."""

    @abc.abstractmethod
    def after_tool_callback(self, callback_context: CallbackContext) -> None:
        """After tool callback."""
    
    @abc.abstractmethod
    def before_model_callback(self, callback_context: CallbackContext, llm_request: LlmRequest) -> None:
        """Before model callback."""
    
    @abc.abstractmethod
    def after_model_callback(self, callback_context: CallbackContext, llm_response) -> None:
        """After model callback."""