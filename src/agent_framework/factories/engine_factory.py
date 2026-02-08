"""Engine factory for creating execution engines.

This factory provides a clean interface for creating different
execution engines (ADK, LangGraph, etc.) with proper validation
and error handling.
"""

from typing import Optional, Type
from pydantic import BaseModel

from src.agent_framework.configs.agent_config import AgentConfig, ExecutionEngine
from src.agent_framework.core.types import AgentType
from src.agent_framework.engines.base import AgentEngine
from src.agent_framework.engines.adk.engine import AdkEngine
from src.agent_framework.engines.langgraph.engine import LangGraphEngine


class EngineFactory:
    """Factory for creating agent execution engines.
    
    This factory encapsulates the logic for creating different types
    of engines and validates that the requested configuration is
    compatible with the selected engine.
    """
    
    @staticmethod
    def create(
        agent_config: AgentConfig,
        input_schema: Type[BaseModel],
        output_schema: Type[BaseModel],
        agent_type: Optional[AgentType] = None,
    ) -> AgentEngine:
        """Create an execution engine based on agent configuration.
        
        Args:
            agent_config: Agent configuration containing engine settings
            input_schema: Pydantic model for agent input
            output_schema: Pydantic model for agent output
            agent_type: Optional agent type specification
            
        Returns:
            Configured engine instance
            
        Raises:
            ValueError: If engine type is not supported
            ConfigurationError: If configuration is invalid
        """
        engine_name = agent_config.execution_engine.value
        
        if engine_name == ExecutionEngine.ADK.value:
            engine = AdkEngine(
                agent_config=agent_config,
                input_schema=input_schema,
                output_schema=output_schema,
                agent_type=agent_type,
            )
        elif engine_name == ExecutionEngine.LANGGRAPH.value:
            engine = LangGraphEngine(
                agent_config=agent_config,
                input_schema=input_schema,
                output_schema=output_schema,
                agent_type=agent_type,
            )
        else:
            valid_engines = [e.value for e in ExecutionEngine]
            raise ValueError(
                f"Unsupported execution_engine '{engine_name}'. "
                f"Expected one of: {valid_engines}"
            )
        
        # Validate engine capabilities
        EngineFactory._validate_engine_capabilities(agent_config, engine)
        
        return engine
    
    @staticmethod
    def _validate_engine_capabilities(agent_config: AgentConfig, engine: AgentEngine) -> None:
        """Validate that the engine can support the agent configuration.
        
        Args:
            agent_config: Agent configuration to validate
            engine: Engine instance to check capabilities
            
        Raises:
            ValueError: If configuration is not supported by engine
        """
        capabilities = engine.capabilities()
        provider_name = agent_config.model_provider.name.value.lower()
        
        if provider_name and provider_name not in capabilities.supported_providers:
            raise ValueError(
                f"Unsupported configuration: "
                f"agent='{agent_config.agent_name}' execution_engine='{engine.engine_name()}' "
                f"does not support provider='{provider_name}'. "
                f"Supported providers for this engine: {sorted(capabilities.supported_providers)}. "
                f"{f'Notes: {capabilities.notes}' if capabilities.notes else ''}"
            )
