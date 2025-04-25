"""
Pytest configuration for the TextQL MCP Server tests.
"""

import os
import sys
import logging
import pytest
from unittest.mock import MagicMock

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


@pytest.fixture
def spanner_schema():
    """Fixture for a Spanner Graph schema."""
    return """
    type Entity {
      id: ID!
      name: String!
      description: String
      type: String!
      properties: [Property!]
      relationships: [Relationship!]
    }

    type Property {
      id: ID!
      name: String!
      value: String!
      type: String
    }

    type Relationship {
      id: ID!
      type: String!
      source: Entity!
      target: Entity!
      properties: [Property!]
    }

    type Query {
      entity(id: ID!): Entity
      entities(type: String): [Entity!]!
      search(term: String!): [Entity!]
      findByProperty(name: String!, value: String!): [Entity!]
    }
    """


@pytest.fixture
def mock_spanner_client():
    """Fixture for a mocked Spanner client."""
    client = MagicMock()
    instance = MagicMock()
    database = MagicMock()
    client.instance.return_value = instance
    instance.database.return_value = database
    return client


@pytest.fixture
def mock_vertex_ai_llm():
    """Fixture for a mocked VertexAI LLM."""
    llm = MagicMock()
    llm.invoke.return_value = "Mock LLM response"
    return llm


@pytest.fixture
def mock_llm_chain():
    """Fixture for a mocked LLM chain."""
    chain = MagicMock()
    chain.invoke.return_value = {
        "result": "Mock chain result",
        "intermediate_steps": [
            {"step": "translating", "output": "Translating query..."},
            {"gql": "{entity(id:\"123\") {name}}"},
            {"step": "executing", "output": "Executing query..."},
            {"data": {"entity": {"name": "Test Entity"}}}
        ]
    }
    return chain
