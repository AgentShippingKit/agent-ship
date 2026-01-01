"""Database information fetching tool."""

import json
import logging
from typing import Dict, Any, List, Optional
import opik
from src.agents.tools.base_tool import BaseTool
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)


class DatabaseInfoTool(BaseTool):
    """Tool for fetching database information and performing queries."""
    
    def __init__(self):
        super().__init__(
            name="database_info_tool",
            description="Fetches database information, table schemas, and performs basic queries"
        )
        self.sample_data = {
            "users": [
                {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
                {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35}
            ],
            "products": [
                {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
                {"id": 2, "name": "Book", "price": 19.99, "category": "Education"},
                {"id": 3, "name": "Coffee", "price": 4.99, "category": "Food"}
            ],
            "orders": [
                {"id": 1, "user_id": 1, "product_id": 1, "quantity": 1, "total": 999.99},
                {"id": 2, "user_id": 2, "product_id": 2, "quantity": 2, "total": 39.98},
                {"id": 3, "user_id": 1, "product_id": 3, "quantity": 3, "total": 14.97}
            ]
        }
    
    @opik.track(name="database_tool_run", tags=["database_tool"])
    def run(self, input: str) -> str:
        """Run the database tool with the given input.
        
        Args:
            input: JSON string containing the operation and parameters
            
        Returns:
            JSON string containing the result
        """
        try:
            # Parse the input
            params = json.loads(input) if isinstance(input, str) else input
            operation = params.get("operation", "list_tables")
            
            logger.info(f"Executing database operation: {operation}")
            print(f"🔧 DATABASE TOOL: Executing operation: {operation}")
            
            if operation == "list_tables":
                return self._list_tables()
            elif operation == "get_table_schema":
                table_name = params.get("table_name")
                return self._get_table_schema(table_name)
            elif operation == "query_table":
                table_name = params.get("table_name")
                limit = params.get("limit", 10)
                return self._query_table(table_name, limit)
            elif operation == "search_records":
                table_name = params.get("table_name")
                search_field = params.get("search_field")
                search_value = params.get("search_value")
                return self._search_records(table_name, search_field, search_value)
            elif operation == "get_table_stats":
                table_name = params.get("table_name")
                return self._get_table_stats(table_name)
            else:
                return json.dumps({
                    "error": f"Unknown operation: {operation}",
                    "available_operations": [
                        "list_tables",
                        "get_table_schema", 
                        "query_table",
                        "search_records",
                        "get_table_stats"
                    ]
                })
                
        except Exception as e:
            logger.error(f"Error in database tool: {e}")
            return json.dumps({"error": str(e)})
    
    @opik.track(name="database_tool_list_tables", tags=["database_tool"])
    def _list_tables(self) -> str:
        """List all available tables."""
        tables = list(self.sample_data.keys())
        return json.dumps({
            "tables": tables,
            "count": len(tables)
        })
    
    @opik.track(name="database_tool_get_table_schema", tags=["database_tool"])
    def _get_table_schema(self, table_name: str) -> str:
        """Get the schema of a specific table."""
        if not table_name:
            return json.dumps({"error": "table_name is required"})
            
        if table_name not in self.sample_data:
            return json.dumps({"error": f"Table '{table_name}' not found"})
        
        # Get sample record to determine schema
        sample_record = self.sample_data[table_name][0] if self.sample_data[table_name] else {}
        schema = {
            "table_name": table_name,
            "columns": list(sample_record.keys()),
            "column_types": {k: type(v).__name__ for k, v in sample_record.items()},
            "record_count": len(self.sample_data[table_name])
        }
        
        return json.dumps(schema)
    
    @opik.track(name="database_tool_query_table", tags=["database_tool"])
    def _query_table(self, table_name: str, limit: int = 10) -> str:
        """Query a table with a limit."""
        if not table_name:
            return json.dumps({"error": "table_name is required"})
            
        if table_name not in self.sample_data:
            return json.dumps({"error": f"Table '{table_name}' not found"})
        
        records = self.sample_data[table_name][:limit]
        return json.dumps({
            "table_name": table_name,
            "records": records,
            "count": len(records),
            "total_available": len(self.sample_data[table_name])
        })
    
    @opik.track(name="database_tool_search_records", tags=["database_tool"])
    def _search_records(self, table_name: str, search_field: str, search_value: str) -> str:
        """Search for records in a table."""
        if not all([table_name, search_field, search_value]):
            return json.dumps({"error": "table_name, search_field, and search_value are required"})
            
        if table_name not in self.sample_data:
            return json.dumps({"error": f"Table '{table_name}' not found"})
        
        # Simple search - in a real implementation, this would use SQL
        matching_records = []
        for record in self.sample_data[table_name]:
            if search_field in record and str(record[search_field]).lower() == str(search_value).lower():
                matching_records.append(record)
        
        return json.dumps({
            "table_name": table_name,
            "search_field": search_field,
            "search_value": search_value,
            "matching_records": matching_records,
            "count": len(matching_records)
        })
    
    @opik.track(name="database_tool_get_table_stats", tags=["database_tool"])
    def _get_table_stats(self, table_name: str) -> str:
        """Get statistics for a table."""
        if not table_name:
            return json.dumps({"error": "table_name is required"})
            
        if table_name not in self.sample_data:
            return json.dumps({"error": f"Table '{table_name}' not found"})
        
        records = self.sample_data[table_name]
        if not records:
            return json.dumps({
                "table_name": table_name,
                "record_count": 0,
                "message": "No records found"
            })
        
        # Calculate basic stats
        stats = {
            "table_name": table_name,
            "record_count": len(records),
            "columns": list(records[0].keys()),
            "column_stats": {}
        }
        
        # Calculate stats for each column
        for column in records[0].keys():
            values = [record[column] for record in records if column in record]
            if values:
                if isinstance(values[0], (int, float)):
                    stats["column_stats"][column] = {
                        "type": "numeric",
                        "min": min(values),
                        "max": max(values),
                        "avg": sum(values) / len(values)
                    }
                else:
                    stats["column_stats"][column] = {
                        "type": "text",
                        "unique_values": len(set(str(v) for v in values)),
                        "sample_values": list(set(str(v) for v in values))[:5]
                    }
        
        return json.dumps(stats)
    
    @opik.track(name="database_tool_to_function_tool", tags=["database_tool"])
    def to_function_tool(self) -> FunctionTool:
        """Convert this tool to a Google ADK FunctionTool."""
        # Use the base class implementation which properly handles function metadata
        return super().to_function_tool()
