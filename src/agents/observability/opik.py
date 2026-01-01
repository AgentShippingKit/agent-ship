from src.agents.observability.base import BaseObserver
from opik.integrations.adk import OpikTracer
import opik
import logging
from src.agents.configs.opik_config import opik_settings
from src.agents.configs.agent_config import AgentConfig
from dotenv import load_dotenv


load_dotenv()
logger = logging.getLogger(__name__)


# print(f"Opik configured with api_key={opik_config.api_key}, workspace={opik_config.workspace}")
opik.configure(
    api_key=opik_settings.OPIK_API_KEY,
    workspace=opik_settings.OPIK_WORKSPACE,
    use_local=False,
    force=True,
)

class OpikObserver(BaseObserver):
    """Opik observability."""
    def __init__(self, agent_config: AgentConfig):
        super().__init__(agent_config)

    def setup(self) -> None:
        """Setup the observability."""
        try:
            # Configure OPIK tracer with LiteLLM-specific settings
            # Try to use OpenAI provider type to handle LiteLLM token format
            self.tracer = OpikTracer(
                name=self.agent_config.agent_name,
                tags=self.agent_config.tags,
                metadata={
                    "model": self.agent_config.model.value,
                    "environment": opik_settings.ENVIRONMENT,
                    "framework": opik_settings.OPIK_FRAMEWORK,
                    "tracing_methods": opik_settings.OPIK_TRACING_METHODS,
                    "litellm_integration": opik_settings.OPIK_LITTELM_INTEGRATION
                },
                project_name= opik_settings.OPIK_PROJECT_NAME
            )

            logger.info(f"Opik tracing initialized for agent: {self.agent_config.agent_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Opik tracing: {e}")
            self.tracer = None
    
    def before_agent_callback(self, *args, **kwargs) -> None:
        """Before agent callback."""
        if self.tracer is None:
            logger.debug("Opik tracer not initialized, skipping before_agent_callback")
            return
        try:
            self.tracer.before_agent_callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in before_agent_callback: {e}")
    
    def after_agent_callback(self, *args, **kwargs) -> None:
        """After agent callback."""
        if self.tracer is None:
            logger.debug("Opik tracer not initialized, skipping after_agent_callback")
            return
        try:
            self.tracer.after_agent_callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in after_agent_callback: {e}")

    def before_model_callback(self, *args, **kwargs) -> None:
        """Before model callback."""
        if self.tracer is None:
            logger.debug("Opik tracer not initialized, skipping before_model_callback")
            return
        try:
            self.tracer.before_model_callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in before_model_callback: {e}")
    
    def after_model_callback(self, *args, **kwargs) -> None:
        """After model callback."""
        if self.tracer is None:
            logger.debug("Opik tracer not initialized, skipping after_model_callback")
            return
        try:
            # The correct token data is nested inside the 'llm_response'.
            # We must extract it and create the 'usage' dictionary that Opik expects.
            if 'llm_response' in kwargs and hasattr(kwargs['llm_response'], 'usage_metadata'):
                usage_metadata = kwargs['llm_response'].usage_metadata
                
                if usage_metadata:
                    logger.info(f"Found usage_metadata object: {usage_metadata}")
                    
                    # Create the 'usage' dictionary from the metadata object's attributes.
                    # Use the original Google field names that Opik expects for Google Gemini
                    usage_dict = {
                        "candidates_token_count": usage_metadata.candidates_token_count,
                        "prompt_token_count": usage_metadata.prompt_token_count,
                        "total_token_count": usage_metadata.total_token_count,
                    }
                    
                    # Add this correctly formatted dictionary to kwargs.
                    # Opik will now find and use it successfully.
                    kwargs['usage'] = usage_dict
                    logger.info(f"Successfully injected 'usage' dictionary into kwargs: {kwargs['usage']}")

            self.tracer.after_model_callback(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error in after_model_callback: {e}", exc_info=True)


    def before_tool_callback(self, *args, **kwargs) -> None:
        """Before tool callback."""
        if self.tracer is None:
            logger.debug("Opik tracer not initialized, skipping before_tool_callback")
            return
        try:
            self.tracer.before_tool_callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in before_tool_callback: {e}")
    
    def after_tool_callback(self, *args, **kwargs) -> None:
        """After tool callback."""
        if self.tracer is None:
            logger.debug("Opik tracer not initialized, skipping after_tool_callback")
            return
        try:
            self.tracer.after_tool_callback(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in after_tool_callback: {e}")
        