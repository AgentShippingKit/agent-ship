"""Universal Parameter Mapper - Core Infrastructure

This module provides the automatic parameter mapping functionality that eliminates
the need for manual _create_input_from_request methods in agents.

The mapper handles:
- Automatic flattening of AgentChatRequest (query + features + user_id + session_id)
- Type conversion and validation
- Schema-driven parameter mapping
- Zero-boilerplate agent development
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Type, Union, get_type_hints
from pydantic import BaseModel, ValidationError

from src.service.models.base_models import AgentChatRequest, FeatureMap

logger = logging.getLogger(__name__)


class ParameterMapper:
    """Universal parameter mapper for automatic request-to-schema conversion.
    
    This class provides the core functionality for automatically mapping
    AgentChatRequest objects to agent-specific input schemas without
    requiring manual _create_input_from_request methods.
    """
    
    @staticmethod
    def map_request_to_schema(
        request: AgentChatRequest, 
        schema_class: Type[BaseModel]
    ) -> BaseModel:
        """Map AgentChatRequest to the target schema automatically.
        
        Args:
            request: The incoming AgentChatRequest
            schema_class: The target Pydantic schema class
            
        Returns:
            Instance of the target schema with mapped data
            
        Raises:
            ValidationError: If the mapped data doesn't match the schema
        """
        try:
            # Step 1: Flatten all data sources
            flattened_data = ParameterMapper._flatten_request_data(request)
            
            # Step 2: Filter to only fields that exist in the target schema
            filtered_data = ParameterMapper._filter_to_schema_fields(
                flattened_data, schema_class
            )
            
            # Step 3: Convert types to match schema expectations
            converted_data = ParameterMapper._convert_types(
                filtered_data, schema_class
            )
            
            # Step 4: Create and validate the schema instance
            return schema_class(**converted_data)
            
        except Exception as e:
            logger.error(f"Failed to map request to {schema_class.__name__}: {e}")
            raise ValidationError(f"Parameter mapping failed: {e}")
    
    @staticmethod
    def _flatten_request_data(request: AgentChatRequest) -> Dict[str, Any]:
        """Flatten all data sources from AgentChatRequest into a single dict.
        
        This method consolidates:
        - request.query (dict or string)
        - request.features (list of FeatureMap)
        - request.user_id
        - request.session_id
        - request.agent_name
        - request.sender
        
        Returns:
            Dictionary with all available data
        """
        flattened = {}
        
        # Add direct fields
        if request.user_id:
            flattened['user_id'] = request.user_id
        if request.session_id:
            flattened['session_id'] = request.session_id
        if request.agent_name:
            flattened['agent_name'] = request.agent_name
        if request.sender:
            flattened['sender'] = request.sender
        
        # Handle query field (can be dict, string, or other)
        if request.query is not None:
            if isinstance(request.query, dict):
                # Query is already a dict - merge it
                flattened.update(request.query)
            elif isinstance(request.query, str):
                # Try to parse as JSON first
                try:
                    parsed = json.loads(request.query)
                    if isinstance(parsed, dict):
                        flattened.update(parsed)
                    else:
                        flattened['query'] = request.query
                except json.JSONDecodeError:
                    # Not JSON, treat as string query
                    flattened['query'] = request.query
            else:
                # Other types, store as query
                flattened['query'] = request.query
        
        # Convert features list to dict
        if request.features:
            feature_dict = {}
            for feature in request.features:
                if isinstance(feature, FeatureMap):
                    feature_dict[feature.feature_name] = feature.feature_value
                else:
                    # Handle legacy format
                    if isinstance(feature, dict) and 'feature_name' in feature:
                        feature_dict[feature['feature_name']] = feature.get('feature_value')
            flattened.update(feature_dict)
        
        logger.debug(f"Flattened request data: {flattened}")
        return flattened
    
    @staticmethod
    def _filter_to_schema_fields(
        data: Dict[str, Any], 
        schema_class: Type[BaseModel]
    ) -> Dict[str, Any]:
        """Filter data to only include fields that exist in the target schema.
        
        Args:
            data: The flattened data dictionary
            schema_class: The target Pydantic schema class
            
        Returns:
            Filtered dictionary with only relevant fields
        """
        if not hasattr(schema_class, 'model_fields'):
            return data
        
        schema_fields = set(schema_class.model_fields.keys())
        filtered = {k: v for k, v in data.items() if k in schema_fields}
        
        logger.debug(f"Filtered data for {schema_class.__name__}: {filtered}")
        return filtered
    
    @staticmethod
    def _convert_types(
        data: Dict[str, Any], 
        schema_class: Type[BaseModel]
    ) -> Dict[str, Any]:
        """Convert data types to match the target schema expectations.
        
        Args:
            data: The filtered data dictionary
            schema_class: The target Pydantic schema class
            
        Returns:
            Dictionary with converted types
        """
        if not hasattr(schema_class, 'model_fields'):
            return data
        
        converted = {}
        schema_fields = schema_class.model_fields
        
        for field_name, field_value in data.items():
            if field_name not in schema_fields:
                continue
                
            field_info = schema_fields[field_name]
            target_type = field_info.annotation
            
            try:
                converted[field_name] = ParameterMapper._convert_single_type(
                    field_value, target_type
                )
            except Exception as e:
                logger.warning(f"Failed to convert {field_name}={field_value} to {target_type}: {e}")
                # Keep original value if conversion fails
                converted[field_name] = field_value
        
        logger.debug(f"Converted data for {schema_class.__name__}: {converted}")
        return converted
    
    @staticmethod
    def _convert_single_type(value: Any, target_type: Type) -> Any:
        """Convert a single value to the target type.
        
        Args:
            value: The value to convert
            target_type: The target type
            
        Returns:
            Converted value
        """
        if value is None:
            return None
        
        # Handle Union types (Optional[T] becomes Union[T, None])
        if hasattr(target_type, '__origin__') and target_type.__origin__ is Union:
            # Get the non-None type from Union
            args = [arg for arg in target_type.__args__ if arg is not type(None)]
            if args:
                target_type = args[0]
        
        # Direct type match
        if isinstance(value, target_type):
            return value
        
        # String conversions
        if target_type is str:
            return str(value)
        
        # Integer conversions
        if target_type is int:
            if isinstance(value, str):
                return int(value)
            elif isinstance(value, float):
                return int(value)
            elif isinstance(value, bool):
                return int(value)
        
        # Float conversions
        if target_type is float:
            if isinstance(value, str):
                return float(value)
            elif isinstance(value, int):
                return float(value)
        
        # Boolean conversions
        if target_type is bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            elif isinstance(value, (int, float)):
                return bool(value)
        
        # List conversions
        if hasattr(target_type, '__origin__') and target_type.__origin__ is list:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return [value]
            elif not isinstance(value, list):
                return [value]
            return value
        
        # Dict conversions
        if hasattr(target_type, '__origin__') and target_type.__origin__ is dict:
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return {}
            elif not isinstance(value, dict):
                return {'value': value}
            return value
        
        # If we can't convert, return as-is
        return value


def auto_map_parameters(cls):
    """Decorator that adds automatic parameter mapping to agent classes.
    
    This decorator eliminates the need for manual _create_input_from_request
    methods by automatically mapping AgentChatRequest to the agent's input_schema.
    
    Usage:
        @auto_map_parameters
        class MyAgent(BaseAgent):
            input_schema = MyInputSchema
            output_schema = MyOutputSchema
            
            # No _create_input_from_request needed!
    """
    if not hasattr(cls, 'input_schema'):
        raise ValueError(f"Class {cls.__name__} must have an 'input_schema' attribute to use @auto_map_parameters")
    
    def _create_input_from_request(self, request: AgentChatRequest) -> BaseModel:
        """Automatic parameter mapping implementation."""
        return ParameterMapper.map_request_to_schema(request, self.input_schema)
    
    # Replace the method if it exists, or add it if it doesn't
    setattr(cls, '_create_input_from_request', _create_input_from_request)
    
    logger.info(f"Applied @auto_map_parameters to {cls.__name__}")
    return cls
