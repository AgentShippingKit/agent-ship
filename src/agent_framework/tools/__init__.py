"""Tool system with clean separation of concerns.

Base tool provides the foundation for all tools.
Domain tools are specific to particular business domains (e.g. Azure).
"""

# Base tool (foundation for all tools)
from .base_tool import BaseTool

# Domain tools (business-specific)
from .domains.azure import AzureArtifactTool

__all__ = [
    # Base tool
    "BaseTool",
    # Azure domain tools
    "AzureArtifactTool",
]
