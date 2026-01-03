"""Azure utilities for Azure Blob Storage operations."""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class AzureUtils:
    """Utilities for Azure Blob Storage operations."""
    
    def __init__(self):
        """Initialize Azure utilities."""
        self._blob_service_client = None
        self._client_initialized = False
    
    def _setup_azure_client(self) -> None:
        """Setup Azure Blob Storage client (lazy import)."""
        if self._client_initialized:
            return
            
        try:
            # Lazy import to avoid loading Azure libraries if not used
            from azure.storage.blob import BlobServiceClient
            from src.agent_framework.settings.azure_settings import azure_settings
            
            # Get Azure credentials from configuration
            connection_string = azure_settings.AZURE_STORAGE_CONNECTION_STRING
            account_name = azure_settings.AZURE_STORAGE_ACCOUNT_NAME
            account_key = azure_settings.AZURE_STORAGE_ACCOUNT_KEY
            
            if connection_string:
                self._blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            elif account_name and account_key:
                self._blob_service_client = BlobServiceClient(
                    account_url=f"https://{account_name}.blob.core.windows.net",
                    credential=account_key
                )
            else:
                logger.warning("Azure storage credentials not found. Utils will use mock data.")
                self._blob_service_client = None
                
        except ImportError:
            logger.warning("Azure libraries not installed. AzureUtils will not function.")
            self._blob_service_client = None
        except Exception as e:
            logger.error(f"Failed to setup Azure client: {e}")
            self._blob_service_client = None
        finally:
            self._client_initialized = True
    
    @property
    def blob_service_client(self):
        """Lazy initialization of blob service client."""
        if not self._client_initialized:
            self._setup_azure_client()
        return self._blob_service_client
    
    def download_blob(self, container_name: str, blob_name: str) -> Dict[str, Any]:
        """Download a blob from Azure Blob Storage."""
        if not container_name or not blob_name:
            return {"error": "container_name and blob_name are required"}
        
        try:
            if not self.blob_service_client:
                return self._get_mock_blob_data(blob_name)
            
            # Download the blob
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            # Download blob content
            blob_data = blob_client.download_blob().readall()
            
            return {
                "container_name": container_name,
                "blob_name": blob_name,
                "data": blob_data,
                "size": len(blob_data),
                "status": "success"
            }
            
        except Exception as e:
            error_type = type(e).__name__
            if "Azure" in error_type or "azure" in str(type(e)):
                logger.error(f"Azure error downloading blob: {e}")
                return {"error": f"Azure error: {str(e)}"}
            logger.error(f"Error downloading blob: {e}")
            return {"error": str(e)}
    
    def list_blobs(self, container_name: str, file_extension: Optional[str] = None) -> Dict[str, Any]:
        """List blobs in a container, optionally filtered by file extension."""
        if not container_name:
            return {"error": "container_name is required"}
        
        try:
            if not self.blob_service_client:
                return self._get_mock_blob_list(file_extension)
            
            container_client = self.blob_service_client.get_container_client(container_name)
            blobs = []
            
            for blob in container_client.list_blobs():
                # Filter by file extension if specified
                if file_extension and not blob.name.lower().endswith(file_extension.lower()):
                    continue
                    
                blobs.append({
                    "name": blob.name,
                    "size": blob.size,
                    "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                    "content_type": blob.content_settings.content_type if blob.content_settings else None,
                    "etag": blob.etag
                })
            
            return {
                "container_name": container_name,
                "blobs": blobs,
                "count": len(blobs),
                "filter": file_extension
            }
            
        except Exception as e:
            error_type = type(e).__name__
            if "Azure" in error_type or "azure" in str(type(e)):
                logger.error(f"Azure error listing blobs: {e}")
                return {"error": f"Azure error: {str(e)}"}
            logger.error(f"Error listing blobs: {e}")
            return {"error": str(e)}
    
    def get_blob_metadata(self, container_name: str, blob_name: str) -> Dict[str, Any]:
        """Get metadata for a blob."""
        if not container_name or not blob_name:
            return {"error": "container_name and blob_name are required"}
        
        try:
            if not self.blob_service_client:
                return self._get_mock_blob_metadata(blob_name)
            
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            # Get blob properties
            properties = blob_client.get_blob_properties()
            
            return {
                "container_name": container_name,
                "blob_name": blob_name,
                "size": properties.size,
                "content_type": properties.content_settings.content_type if properties.content_settings else None,
                "last_modified": properties.last_modified.isoformat() if properties.last_modified else None,
                "etag": properties.etag,
                "status": "success"
            }
            
        except Exception as e:
            error_type = type(e).__name__
            if "Azure" in error_type or "azure" in str(type(e)):
                logger.error(f"Azure error getting blob metadata: {e}")
                return {"error": f"Azure error: {str(e)}"}
            logger.error(f"Error getting blob metadata: {e}")
            return {"error": str(e)}
    
    def blob_exists(self, container_name: str, blob_name: str) -> Dict[str, Any]:
        """Check if a blob exists."""
        if not container_name or not blob_name:
            return {"error": "container_name and blob_name are required"}
        
        try:
            if not self.blob_service_client:
                return {"exists": True, "status": "mock"}
            
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name, 
                blob=blob_name
            )
            
            exists = blob_client.exists()
            
            return {
                "container_name": container_name,
                "blob_name": blob_name,
                "exists": exists,
                "status": "success"
            }
            
        except Exception as e:
            error_type = type(e).__name__
            if "Azure" in error_type or "azure" in str(type(e)):
                logger.error(f"Azure error checking blob existence: {e}")
                return {"error": f"Azure error: {str(e)}"}
            logger.error(f"Error checking blob existence: {e}")
            return {"error": str(e)}
    
    def search_blobs_by_name(self, container_name: str, search_pattern: str) -> Dict[str, Any]:
        """Search for blobs by name pattern."""
        if not container_name or not search_pattern:
            return {"error": "container_name and search_pattern are required"}
        
        try:
            if not self.blob_service_client:
                return self._get_mock_search_results(search_pattern)
            
            container_client = self.blob_service_client.get_container_client(container_name)
            matching_blobs = []
            
            for blob in container_client.list_blobs():
                if search_pattern.lower() in blob.name.lower():
                    matching_blobs.append({
                        "name": blob.name,
                        "size": blob.size,
                        "last_modified": blob.last_modified.isoformat() if blob.last_modified else None,
                        "content_type": blob.content_settings.content_type if blob.content_settings else None
                    })
            
            return {
                "container_name": container_name,
                "search_pattern": search_pattern,
                "matching_blobs": matching_blobs,
                "count": len(matching_blobs)
            }
            
        except Exception as e:
            error_type = type(e).__name__
            if "Azure" in error_type or "azure" in str(type(e)):
                logger.error(f"Azure error searching blobs: {e}")
                return {"error": f"Azure error: {str(e)}"}
            logger.error(f"Error searching blobs: {e}")
            return {"error": str(e)}
    
    # Mock data methods for testing when Azure credentials are not available
    def _get_mock_blob_data(self, blob_name: str) -> Dict[str, Any]:
        """Get mock blob data for testing."""
        mock_data = b"This is mock binary data for blob: " + blob_name.encode()
        
        return {
            "container_name": "mock-container",
            "blob_name": blob_name,
            "data": mock_data,
            "size": len(mock_data),
            "status": "success (mock data)"
        }
    
    def _get_mock_blob_list(self, file_extension: Optional[str] = None) -> Dict[str, Any]:
        """Get mock blob list for testing."""
        mock_blobs = [
            {
                "name": "patient_report_001.pdf",
                "size": 245760,
                "last_modified": "2024-01-15T10:30:00Z",
                "content_type": "application/pdf",
                "etag": "0x8D1234567890ABCD"
            },
            {
                "name": "lab_results_002.pdf",
                "size": 189440,
                "last_modified": "2024-01-14T14:20:00Z",
                "content_type": "application/pdf",
                "etag": "0x8D1234567890ABCD"
            },
            {
                "name": "treatment_plan_003.pdf",
                "size": 312320,
                "last_modified": "2024-01-13T09:15:00Z",
                "content_type": "application/pdf",
                "etag": "0x8D1234567890ABCD"
            },
            {
                "name": "image_001.jpg",
                "size": 156789,
                "last_modified": "2024-01-12T16:45:00Z",
                "content_type": "image/jpeg",
                "etag": "0x8D1234567890ABCD"
            }
        ]
        
        # Filter by file extension if specified
        if file_extension:
            mock_blobs = [blob for blob in mock_blobs if blob["name"].lower().endswith(file_extension.lower())]
        
        return {
            "container_name": "mock-container",
            "blobs": mock_blobs,
            "count": len(mock_blobs),
            "filter": file_extension
        }
    
    def _get_mock_blob_metadata(self, blob_name: str) -> Dict[str, Any]:
        """Get mock blob metadata for testing."""
        return {
            "container_name": "mock-container",
            "blob_name": blob_name,
            "size": 245760,
            "content_type": "application/pdf",
            "last_modified": "2024-01-15T10:30:00Z",
            "etag": "0x8D1234567890ABCD",
            "status": "success (mock data)"
        }
    
    def _get_mock_search_results(self, search_pattern: str) -> Dict[str, Any]:
        """Get mock search results for testing."""
        mock_results = [
            {
                "name": "patient_report_001.pdf",
                "size": 245760,
                "last_modified": "2024-01-15T10:30:00Z",
                "content_type": "application/pdf"
            },
            {
                "name": "patient_notes_002.pdf",
                "size": 189440,
                "last_modified": "2024-01-14T14:20:00Z",
                "content_type": "application/pdf"
            }
        ]
        
        return {
            "container_name": "mock-container",
            "search_pattern": search_pattern,
            "matching_blobs": mock_results,
            "count": len(mock_results)
        }
