"""
Custom schema provider for Wikidata graph database.
This provider uses the GraphQL schema defined for the Wikidata-to-Spanner pipeline.
"""

import os
import logging
from typing import Dict, Any, Optional

from textql_mcp.utils.schema_provider import FileSchemaProvider

logger = logging.getLogger("wikidata_schema_provider")


class WikidataSchemaProvider:
    """Schema provider that uses the Wikidata GraphQL schema."""

    def __init__(self, schema_file_path: str = "textql_mcp/schema.graphql"):
        """
        Initialize the Wikidata schema provider.

        Args:
            schema_file_path: Path to the GraphQL schema file
        """
        self.schema_file_path = schema_file_path
        self._file_provider = FileSchemaProvider(schema_file_path)

        # Check if schema file exists
        if not os.path.exists(schema_file_path):
            logger.error(f"Schema file not found: {schema_file_path}")
            raise FileNotFoundError(f"Schema file not found: {schema_file_path}")

        logger.info(
            f"Initialized WikidataSchemaProvider with schema: {schema_file_path}"
        )

    def get_schema(self, query: str, agent_type: str = "default") -> str:
        """
        Get schema information for a query.

        For the Wikidata graph, we return the full schema as it's relatively
        concise and contains all entity and relationship types.

        Args:
            query: The query to get schema information for
            agent_type: The agent type identifier

        Returns:
            Schema information as a string
        """
        logger.debug(
            f"Getting schema for query: {query[:100]}... (agent_type: {agent_type})"
        )

        # For now, return the full schema
        # In the future, we could implement filtering based on the query
        return self._file_provider.get_schema(query, agent_type)

    def get_entity_types(self) -> list:
        """Get list of available entity types from the schema."""
        # These are extracted from the schema and Spanner tables
        return [
            "Company",
            "Person",
            "Location",
            "Organization",
            "Educational Institution",
        ]

    def get_relationship_types(self) -> list:
        """Get list of available relationship types from the schema."""
        # From the config and schema
        return [
            "WORKED_AT",
            "CITIZEN_OF",
            "EDUCATED_AT",
            "MEMBER_OF",
            "FOUNDER_OF",
            "SUBSIDIARY_OF",
            "EMPLOYED_BY",
        ]
