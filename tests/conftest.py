"""
Pytest configuration for the TextQL MCP Server tests.
"""

import os
import sys
import logging
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Disable logging during tests
logging.disable(logging.CRITICAL)


@pytest.fixture
def simple_schema():
    """Fixture for a simple GraphQL schema."""
    return """
    type Employee {
      id: ID!
      name: String!
      position: String!
      department: String!
    }
    
    type Query {
      employees(department: String): [Employee!]!
      employee(id: ID!): Employee
    }
    """


@pytest.fixture
def dummy_query_result():
    """Fixture for a dummy query result."""
    return {
        "result": """
        {
          "employees": [
            {"id": "1", "name": "John Doe", "position": "Sales Manager"},
            {"id": "2", "name": "Jane Smith", "position": "Sales Representative"}
          ]
        }
        """,
        "intermediate_steps": [],
    }
