"""
Command-line entry point for the TextQL MCP Server.

This module allows running the TextQL MCP Server from the command line.
"""

import os
import sys
import argparse
import logging

from .core.server import run_server
from .main_spanner import create_mcp_server_with_spanner
from .utils.schema_provider import FileSchemaProvider
from .utils.query_executor import SPANNER_AVAILABLE

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("textql_mcp")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="TextQL MCP Server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--schema",
        type=str,
        help="Path to GraphQL schema file",
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="TextQL-MCP-Server",
        help="Name of the MCP server",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    # Add Spanner-specific arguments
    spanner_group = parser.add_argument_group("Google Spanner Configuration")
    spanner_group.add_argument(
        "--spanner-instance-id",
        type=str,
        help="Google Spanner instance ID",
    )
    spanner_group.add_argument(
        "--spanner-database-id",
        type=str,
        help="Google Spanner database ID",
    )
    spanner_group.add_argument(
        "--spanner-project-id",
        type=str,
        help="Google Cloud project ID for Spanner (defaults to ADC)",
    )

    return parser.parse_args()


def main():
    """Main entry point for the command-line interface."""
    # Parse command-line arguments
    args = parse_args()

    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Set environment variables for host and port
    os.environ["MCP_HOST"] = args.host
    os.environ["MCP_PORT"] = str(args.port)

    # Create schema provider if specified
    schema_provider = None
    if args.schema:
        schema_provider = FileSchemaProvider(args.schema)

    # Validate required Spanner arguments
    if not SPANNER_AVAILABLE:
        logger.error(
            "Google Spanner dependencies not available. Install with: pip install google-cloud-spanner"
        )
        sys.exit(1)

    if not args.spanner_instance_id or not args.spanner_database_id:
        logger.error("Spanner instance ID and database ID are required")
        sys.exit(1)

    try:
        # Create MCP server with Spanner backend
        logger.info(
            f"Creating TextQL MCP Server with Spanner backend: instance={args.spanner_instance_id}, database={args.spanner_database_id}"
        )
        server = create_mcp_server_with_spanner(
            instance_id=args.spanner_instance_id,
            database_id=args.spanner_database_id,
            schema_provider=schema_provider,
            config_path=args.config,
            server_name=args.name,
            spanner_project_id=args.spanner_project_id,
        )
    except Exception as e:
        logger.error(
            f"Failed to create server with Spanner backend: {e}", exc_info=True
        )
        sys.exit(1)

    # Run server
    logger.info(f"Starting TextQL MCP Server on {args.host}:{args.port}")
    run_server(server, args.host, args.port)


if __name__ == "__main__":
    main()
