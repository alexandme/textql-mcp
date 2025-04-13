"""
Main module for the TextQL MCP Server.

This module provides helper functions for creating and running the server.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

from .core.server import create_mcp_server, SchemaProvider, QueryExecutor, AmbiguityDetector
from .utils.schema_provider import FileSchemaProvider, StringSchemaProvider, MultiAgentSchemaProvider
from .utils.query_executor import DummyQueryExecutor, CallbackQueryExecutor, LLMQueryExecutor
from .utils.ambiguity_detector import SimpleAmbiguityDetector, RegexAmbiguityDetector, CallbackAmbiguityDetector

# Set up logging
logger = logging.getLogger("textql_mcp")


def create_server(
    schema_provider: Optional[SchemaProvider] = None,
    query_executor: Optional[QueryExecutor] = None,
    ambiguity_detector: Optional[AmbiguityDetector] = None,
    config_path: Optional[str] = None,
    server_name: str = "TextQL-MCP-Server",
):
    """
    Create an MCP server with GraphQL query tools.
    
    Args:
        schema_provider: Provider for database schema information
        query_executor: Executor for GraphQL queries
        ambiguity_detector: Detector for query ambiguities
        config_path: Path to the configuration file
        server_name: Name of the MCP server
        
    Returns:
        FastMCP: Configured MCP server
    """
    return create_mcp_server(
        schema_provider=schema_provider,
        query_executor=query_executor,
        ambiguity_detector=ambiguity_detector,
        config_path=config_path,
        server_name=server_name,
    )


def create_simple_server(
    schema_file_path: Optional[str] = None,
    schema_string: Optional[str] = None,
    query_executor_callback: Optional[callable] = None,
    config_path: Optional[str] = None,
    server_name: str = "TextQL-MCP-Server",
):
    """
    Create a simple MCP server with basic components.
    
    Args:
        schema_file_path: Path to the GraphQL schema file
        schema_string: GraphQL schema as a string
        query_executor_callback: Callback function for executing queries
        config_path: Path to the configuration file
        server_name: Name of the MCP server
        
    Returns:
        FastMCP: Configured MCP server
    """
    # Create schema provider
    if schema_file_path is not None:
        schema_provider = FileSchemaProvider(schema_file_path)
    elif schema_string is not None:
        schema_provider = StringSchemaProvider(schema_string)
    else:
        schema_provider = StringSchemaProvider("""
        type Query {
            example: String
        }
        """)
    
    # Create query executor
    if query_executor_callback is not None:
        query_executor = CallbackQueryExecutor(query_executor_callback)
    else:
        query_executor = DummyQueryExecutor()
    
    # Create ambiguity detector
    ambiguity_detector = SimpleAmbiguityDetector()
    
    # Create and return server
    return create_server(
        schema_provider=schema_provider,
        query_executor=query_executor,
        ambiguity_detector=ambiguity_detector,
        config_path=config_path,
        server_name=server_name,
    )


def run_server(server, host: str = "0.0.0.0", port: int = 8000):
    """
    Run the MCP server.
    
    Args:
        server: The MCP server to run
        host: Host to bind to
        port: Port to bind to
    """
    # Set environment variables for host and port
    os.environ["MCP_HOST"] = host
    os.environ["MCP_PORT"] = str(port)
    
    try:
        logger.info(f"Starting MCP server on {host}:{port}")
        server.run()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)
