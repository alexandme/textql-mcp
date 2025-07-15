"""
Schema provider implementations for the TextQL MCP Server.

This module provides various implementations of schema providers that
can be used with the TextQL MCP Server.
"""

import os
import logging
from typing import Dict, Optional

# Import Spanner-related libraries if available
try:
    from google.cloud import spanner

    SPANNER_AVAILABLE = True
except ImportError:
    SPANNER_AVAILABLE = False

logger = logging.getLogger("textql_mcp.schema_provider")

# Import SpannerSchemaProvider if available
try:
    from .schema_provider_spanner import SpannerSchemaProvider

    __all__ = [
        "FileSchemaProvider",
        "StringSchemaProvider",
        "MultiAgentSchemaProvider",
        "SpannerSchemaProvider",
    ]
except ImportError:
    __all__ = ["FileSchemaProvider", "StringSchemaProvider", "MultiAgentSchemaProvider"]
    SpannerSchemaProvider = None


class FileSchemaProvider:
    """Schema provider that reads schema from a file."""

    def __init__(self, schema_file_path: str):
        """
        Initialize a FileSchemaProvider.

        Args:
            schema_file_path: Path to the GraphQL schema file
        """
        self.schema_file_path = schema_file_path
        if not os.path.exists(schema_file_path):
            logger.warning(f"Schema file not found: {schema_file_path}")
        else:
            logger.info(
                f"Initialized FileSchemaProvider with schema file: {schema_file_path}"
            )

    def get_schema(self, query: str, agent_type: str = "default") -> str:
        """
        Get schema information for a query.

        Args:
            query: The query to get schema information for
            agent_type: The agent type identifier

        Returns:
            Schema information as a string
        """
        try:
            logger.info(f"Reading schema from file: {self.schema_file_path}")
            with open(self.schema_file_path, "r") as f:
                schema = f.read()
            return schema
        except Exception as e:
            logger.error(f"Error reading schema file: {e}")
            return f"Error: Could not read schema file: {e}"


class StringSchemaProvider:
    """Schema provider that uses a predefined schema string."""

    def __init__(self, schema: str):
        """
        Initialize a StringSchemaProvider.

        Args:
            schema: The GraphQL schema as a string
        """
        self.schema = schema
        logger.info("Initialized StringSchemaProvider with predefined schema")

    def get_schema(self, query: str, agent_type: str = "default") -> str:
        """
        Get schema information for a query.

        Args:
            query: The query to get schema information for
            agent_type: The agent type identifier

        Returns:
            Schema information as a string
        """
        return self.schema


class MultiAgentSchemaProvider:
    """Schema provider that supports multiple agent types with different schemas."""

    def __init__(self, schemas: Dict[str, str], default_schema: Optional[str] = None):
        """
        Initialize a MultiAgentSchemaProvider.

        Args:
            schemas: Dictionary mapping agent types to schema strings
            default_schema: Default schema to use if agent type not found
        """
        self.schemas = schemas
        self.default_schema = default_schema or next(iter(schemas.values()), "")
        logger.info(
            f"Initialized MultiAgentSchemaProvider with {len(schemas)} agent types"
        )

    def get_schema(self, query: str, agent_type: str = "default") -> str:
        """
        Get schema information for a query.

        Args:
            query: The query to get schema information for
            agent_type: The agent type identifier

        Returns:
            Schema information as a string
        """
        if agent_type in self.schemas:
            return self.schemas[agent_type]
        else:
            logger.warning(f"Unknown agent type: {agent_type}, using default schema")
            return self.default_schema
