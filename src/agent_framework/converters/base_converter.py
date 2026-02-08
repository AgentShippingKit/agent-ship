"""Base converter interface for all data format conversions.

This module provides the abstract base class that all converters should
inherit from, ensuring consistent interface and behavior across all
converter implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic

T = TypeVar('T')
U = TypeVar('U')


class BaseConverter(ABC, Generic[T, U]):
    """Abstract base class for all data converters.
    
    This class defines the interface that all converters must implement,
    providing a consistent way to convert data between different formats.
    """
    
    @abstractmethod
    def convert(self, data: T) -> U:
        """Convert data from source format to target format.
        
        Args:
            data: The data to convert
            
        Returns:
            Converted data in target format
            
        Raises:
            ConversionError: If conversion fails
        """
        pass
    
    @abstractmethod
    def can_convert(self, data: Any) -> bool:
        """Check if this converter can handle the given data.
        
        Args:
            data: The data to check
            
        Returns:
            True if this converter can handle the data, False otherwise
        """
        pass


class ConversionError(Exception):
    """Exception raised when data conversion fails."""
    pass
