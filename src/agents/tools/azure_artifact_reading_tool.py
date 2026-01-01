"""Azure artifact reading tool for PDF files from Azure Blob Storage."""

import json
import logging
import opik
from typing import Dict, Any
from src.agents.tools.base_tool import BaseTool
from src.agents.utils.azure_utils import AzureUtils
from src.agents.utils.pdf_utils import PdfUtils
from google.adk.tools import FunctionTool

logger = logging.getLogger(__name__)


class AzureArtifactTool(BaseTool):
    """Tool for reading PDF files from Azure Blob Storage."""
    
    def __init__(self):
        super().__init__(
            name="azure_artifact_tool",
            description="Reads and extracts text content from PDF files stored in Azure Blob Storage. Provide the Azure blob path (container/blob_name) to read and extract PDF content."
        )
        self.azure_utils = AzureUtils()
        self.pdf_utils = PdfUtils()
    
    @opik.track(name="azure_artifact_tool_run", tags=["azure_artifact_tool"])
    def run(self, input: str) -> str:
        """Run the Azure artifact reading tool with the given input.
        
        Args:
            input: JSON string containing the Azure blob path (container/blob_name)
            
        Returns:
            JSON string containing the extracted PDF content
        """
        try:
            # Handle empty or non-JSON input
            if not input or input.strip() == "":
                return json.dumps({"error": "No input provided. Please provide blob_path in format: container/blob_name"})
            
            # Parse the input
            try:
                params = json.loads(input) if isinstance(input, str) else input
            except json.JSONDecodeError:
                # If input is not JSON, treat it as a direct blob path
                blob_path = input.strip()
            else:
                blob_path = params.get("blob_path") or params.get("input", "")
            
            if not blob_path:
                return json.dumps({"error": "blob_path is required. Format: container/blob_name"})
            
            logger.info(f"Reading Azure artifact: {blob_path}")
            print(f"📄 AZURE ARTIFACT TOOL: Reading PDF from {blob_path}")
            
            # Parse blob path (container/blob_name)
            if "/" not in blob_path:
                return json.dumps({"error": "Invalid blob path format. Use: container/blob_name"})
            
            container_name, blob_name = blob_path.split("/", 1)
            
            # Read PDF from Azure and extract content
            result = self._read_pdf_with_processing(container_name, blob_name)
            
            return json.dumps(result)
                
        except Exception as e:
            logger.error(f"Error in Azure artifact tool: {e}")
            return json.dumps({"error": str(e)})
    
    def _read_pdf_with_processing(self, container_name: str, blob_name: str) -> Dict[str, Any]:
        """Read PDF from Azure and extract text content."""
        # Download blob from Azure
        blob_result = self.azure_utils.download_blob(container_name, blob_name)
        if "error" in blob_result:
            return blob_result
        
        # Extract text using PDF utils
        pdf_result = self.pdf_utils.extract_text_from_bytes(blob_result["data"])
        if "error" in pdf_result:
            return pdf_result
        
        # Return extracted content
        return {
            "blob_path": f"{container_name}/{blob_name}",
            "content": pdf_result["extracted_text"],
            "content_length": pdf_result["text_length"],
            "blob_size": blob_result["size"],
            "status": "success"
        }
    
    @opik.track(name="azure_artifact_tool_to_function_tool", tags=["azure_artifact_tool"])
    def to_function_tool(self) -> FunctionTool:
        """Convert this tool to a Google ADK FunctionTool."""
        # Use the base class implementation which properly handles function metadata
        return super().to_function_tool()
