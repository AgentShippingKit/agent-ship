"""Example usage of the simplified Azure Artifact Reading Tool."""

import json
import logging
from src.agent_framework.tools.domains.azure.azure_artifact_reading_tool import AzureArtifactTool

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_simplified_tool():
    """Test the simplified Azure artifact reading tool."""
    print("\n=== Simplified Azure Artifact Reading Tool ===")
    
    # Initialize the tool
    tool = AzureArtifactTool()
    
    # Test 1: Read PDF with blob path
    print("\n1. Reading PDF from Azure blob path:")
    input_data = json.dumps({
        "blob_path": "documents/patient_report_001.pdf"
    })
    result = tool.run(input_data)
    print(f"Result: {result}")
    
    # Test 2: Read PDF with alternative input format
    print("\n2. Reading PDF with alternative input format:")
    input_data = json.dumps({
        "input": "medical-reports/lab_results_002.pdf"
    })
    result = tool.run(input_data)
    print(f"Result: {result}")
    
    # Test 3: Error handling - invalid path
    print("\n3. Error handling - invalid blob path:")
    input_data = json.dumps({
        "blob_path": "invalid_path_without_slash"
    })
    result = tool.run(input_data)
    print(f"Result: {result}")
    
    # Test 4: Error handling - missing path
    print("\n4. Error handling - missing blob path:")
    input_data = json.dumps({})
    result = tool.run(input_data)
    print(f"Result: {result}")


def demonstrate_simplified_workflow():
    """Demonstrate the simplified workflow."""
    print("\n=== Simplified Workflow ===")
    
    print("✅ Input: Azure blob path (container/blob_name)")
    print("   Example: 'documents/patient_report_001.pdf'")
    
    print("\n✅ Process:")
    print("   1. Parse blob path to get container and blob name")
    print("   2. Use Azure Utils to download blob from Azure")
    print("   3. Use PDF Utils to extract text from PDF bytes")
    print("   4. Return extracted content")
    
    print("\n✅ Output: JSON with extracted PDF content")
    print("   - blob_path: Original path")
    print("   - content: Extracted text")
    print("   - content_length: Text length")
    print("   - blob_size: File size")
    print("   - status: Success/error")


def show_usage_examples():
    """Show usage examples."""
    print("\n=== Usage Examples ===")
    
    print("1. Basic usage:")
    print('   tool.run(\'{"blob_path": "documents/report.pdf"}\')')
    
    print("\n2. Alternative input format:")
    print('   tool.run(\'{"input": "medical-reports/lab_results.pdf"}\')')
    
    print("\n3. With error handling:")
    print('   tool.run(\'{"blob_path": "invalid_path"}\')  # Returns error')


if __name__ == "__main__":
    print("Simplified Azure Artifact Reading Tool")
    print("=" * 50)
    
    # Show simplified workflow
    demonstrate_simplified_workflow()
    
    # Show usage examples
    show_usage_examples()
    
    # Test the tool
    test_simplified_tool()
    
    print("\n✅ Tool simplified! Single purpose: Read PDF from Azure blob path")
    print("✅ Input: Azure blob path (container/blob_name)")
    print("✅ Output: Extracted PDF content")
    print("✅ Clean and focused functionality")
