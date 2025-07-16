"""
Tests for the schema provider implementations.
"""

import os
import tempfile

from textql_mcp.utils.schema_provider import (
    FileSchemaProvider,
    StringSchemaProvider,
    MultiAgentSchemaProvider,
)


def test_string_schema_provider(simple_schema):
    """Test the StringSchemaProvider."""
    # Create provider
    provider = StringSchemaProvider(simple_schema)

    # Check schema
    schema = provider.get_schema("Get all employees", "default")
    assert "type Employee" in schema
    assert "type Query" in schema


def test_file_schema_provider(simple_schema):
    """Test the FileSchemaProvider."""
    # Create a temporary schema file
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(simple_schema)
        file_path = f.name

    try:
        # Create provider
        provider = FileSchemaProvider(file_path)

        # Check schema
        schema = provider.get_schema("Get all employees", "default")
        assert "type Employee" in schema
        assert "type Query" in schema
    finally:
        # Clean up
        if os.path.exists(file_path):
            os.unlink(file_path)


def test_multi_agent_schema_provider():
    """Test the MultiAgentSchemaProvider."""
    # Create schemas for different agent types
    cne_schema = """
    type Company {
      id: ID!
      name: String!
    }
    
    type Query {
      companies: [Company!]!
    }
    """

    rnc_schema = """
    type News {
      id: ID!
      title: String!
    }
    
    type Query {
      news: [News!]!
    }
    """

    # Create provider
    provider = MultiAgentSchemaProvider(
        schemas={"CNE": cne_schema, "RNC": rnc_schema},
        default_schema=cne_schema,
    )

    # Check schemas
    cne_result = provider.get_schema("Get all companies", "CNE")
    assert "type Company" in cne_result

    rnc_result = provider.get_schema("Get all news", "RNC")
    assert "type News" in rnc_result

    # Check default schema for unknown agent type
    default_result = provider.get_schema("Get all data", "UNKNOWN")
    assert "type Company" in default_result
