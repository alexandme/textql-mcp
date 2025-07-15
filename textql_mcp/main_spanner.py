"""
Spanner-specific MCP server creation function.
"""

import logging
from typing import Optional, Any

from .core.server import (
    create_mcp_server,
    SchemaProvider,
    AmbiguityDetector,
)
from .utils.schema_provider import SpannerSchemaProvider
from .utils.query_executor import SpannerQueryExecutor
from .utils.ambiguity_detector import SimpleAmbiguityDetector

logger = logging.getLogger("textql_mcp")


def create_mcp_server_with_spanner(
    instance_id: str,
    database_id: str,
    schema_provider: Optional[SchemaProvider] = None,
    ambiguity_detector: Optional[AmbiguityDetector] = None,
    config_path: Optional[str] = None,
    server_name: str = "TextQL-MCP-Spanner-Server",
    spanner_project_id: Optional[str] = None,
    graph_name: str = "wikidata_graph",
) -> Any:  # Return type is actually FastMCP but avoid import cycles
    """
    Creates an MCP server configured to use Google Spanner as the backend.
    This server expects clients to generate GQL queries directly.

    Args:
        instance_id: Google Spanner instance ID.
        database_id: Google Spanner database ID.
        schema_provider: Provider for database schema information.
        ambiguity_detector: Detector for query ambiguities.
        config_path: Path to the configuration file.
        server_name: Name of the MCP server.
        spanner_project_id: Google Cloud project ID for Spanner (defaults to ADC).
        graph_name: Name of the graph in Spanner.

    Returns:
        Configured FastMCP server instance.
    """
    logger.info(f"Creating MCP server with Spanner integration: {server_name}")

    # Initialize Spanner Query Executor
    spanner_executor = SpannerQueryExecutor(
        instance_id=instance_id,
        database_id=database_id,
        project_id=spanner_project_id,
        graph_name=graph_name,
    )

    # Create Default Components if Needed
    if schema_provider is None:
        # Use SpannerSchemaProvider to fetch schema from Spanner
        logger.info("No schema provider specified, creating SpannerSchemaProvider.")
        schema_provider = SpannerSchemaProvider(
            instance_id=instance_id,
            database_id=database_id,
            project_id=spanner_project_id,
            graph_name=graph_name,
        )

    if ambiguity_detector is None:
        ambiguity_detector = SimpleAmbiguityDetector()

    # Create the MCP Server
    return create_mcp_server(
        schema_provider=schema_provider,
        query_executor=spanner_executor,
        ambiguity_detector=ambiguity_detector,
        config_path=config_path,
        server_name=server_name,
    )
