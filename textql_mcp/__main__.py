"""
Command-line entry point for the TextQL MCP Server.

This module allows running the TextQL MCP Server from the command line.
"""

import os
import sys
import argparse
import logging
from typing import Dict, Any

from .main import create_simple_server, run_server
from .utils.schema_provider import FileSchemaProvider, StringSchemaProvider
from .utils.query_executor import DummyQueryExecutor

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
    
    # Create schema provider
    if args.schema:
        schema_provider = FileSchemaProvider(args.schema)
    else:
        # Use default schema
        schema_provider = StringSchemaProvider("""
        type Query {
            example: String
        }
        """)
    
    # Create MCP server
    server = create_simple_server(
        schema_file_path=args.schema,
        config_path=args.config,
        server_name=args.name,
    )
    
    # Run server
    logger.info(f"Starting TextQL MCP Server on {args.host}:{args.port}")
    run_server(server, args.host, args.port)


if __name__ == "__main__":
    main()
