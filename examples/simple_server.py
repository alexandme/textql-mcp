"""
Simple server example for the TextQL MCP Server.

This module demonstrates how to create and run a simple TextQL MCP server.
"""

import os
import sys
import logging
from typing import Dict, Any

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from textql_mcp.main import create_simple_server, run_server
from textql_mcp.utils.schema_provider import StringSchemaProvider
from textql_mcp.utils.query_executor import DummyQueryExecutor
from textql_mcp.utils.ambiguity_detector import SimpleAmbiguityDetector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("simple_server")


def dummy_query_executor(query: str, agent_type: str) -> Dict[str, Any]:
    """
    Dummy query executor function for demonstration purposes.
    
    Args:
        query: The query to execute
        agent_type: The agent type identifier
        
    Returns:
        Dict containing the query results
    """
    if "employees" in query and "Sales" in query:
        return {
            "result": """
            {
              "employees": [
                {"id": "1", "name": "John Doe", "position": "Sales Manager"},
                {"id": "2", "name": "Jane Smith", "position": "Sales Representative"},
                {"id": "3", "name": "Bob Johnson", "position": "Sales Associate"}
              ]
            }
            """,
            "intermediate_steps": [
                {"type": "query_translation", "gql": "{ employees(department: \"Sales\") { id, name, position } }"},
                {"type": "execution", "status": "success"}
            ],
        }
    else:
        return {
            "result": "No data found for the given query",
            "intermediate_steps": [
                {"type": "query_translation", "gql": query},
                {"type": "execution", "status": "no_results"}
            ],
        }


def main():
    """Main function to create and run the MCP server."""
    # Define a simple schema
    schema = """
    type Employee {
      id: ID!
      name: String!
      position: String!
      department: String!
      salary: Float
      startDate: String
    }
    
    type Department {
      id: ID!
      name: String!
      manager: Employee
      employees: [Employee!]!
    }
    
    type Query {
      employees(department: String): [Employee!]!
      employee(id: ID!): Employee
      departments: [Department!]!
      department(id: ID!): Department
    }
    """
    
    # Create schema provider
    schema_provider = StringSchemaProvider(schema)
    
    # Create query executor
    query_executor = DummyQueryExecutor()
    
    # Create ambiguity detector
    ambiguity_detector = SimpleAmbiguityDetector()
    
    # Create MCP server
    server = create_simple_server(
        schema_string=schema,
        query_executor_callback=dummy_query_executor,
        server_name="Simple-TextQL-MCP-Server"
    )
    
    # Run server
    host = os.environ.get("MCP_HOST", "0.0.0.0")
    port = int(os.environ.get("MCP_PORT", "8000"))
    run_server(server, host, port)


if __name__ == "__main__":
    main()
