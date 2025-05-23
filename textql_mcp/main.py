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
from .utils.query_executor import (
    DummyQueryExecutor,
    CallbackQueryExecutor,
    LLMQueryExecutor,
    SpannerQueryExecutor,
    SPANNER_AVAILABLE
)
from .utils.ambiguity_detector import SimpleAmbiguityDetector, RegexAmbiguityDetector, CallbackAmbiguityDetector

# Try to import optional dependencies
try:
    from google.cloud import spanner
    from langchain_google_vertexai import ChatVertexAI
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False

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


def create_mcp_server_with_spanner(
    instance_id: str,
    database_id: str,
    # --- LLM Configuration ---
    # Option 1: Pass a pre-configured LLM instance
    llm_instance: Optional[Any] = None,
    # Option 2: Or pass arguments to configure a default LLM (e.g., VertexAI)
    llm_project_id: Optional[str] = None,
    llm_location: Optional[str] = None,
    llm_model_name: str = "gemini-pro",
    # --- Other MCP Components ---
    schema_provider: Optional[SchemaProvider] = None,
    ambiguity_detector: Optional[AmbiguityDetector] = None,
    config_path: Optional[str] = None,
    server_name: str = "TextQL-MCP-Spanner-Server",
    spanner_project_id: Optional[str] = None,
) -> Any:  # Return type is actually FastMCP but avoid import cycles
    """
    Creates an MCP server configured to use Google Spanner as the backend.

    Args:
        instance_id: Google Spanner instance ID.
        database_id: Google Spanner database ID.
        llm_instance: Optional pre-configured LangChain LLM instance.
        llm_project_id: Project ID for the LLM (if using default VertexAI).
        llm_location: Location for the LLM (if using default VertexAI).
        llm_model_name: Model name for the LLM (if using default VertexAI).
        schema_provider: Provider for database schema information.
        ambiguity_detector: Detector for query ambiguities.
        config_path: Path to the configuration file.
        server_name: Name of the MCP server.
        spanner_project_id: Google Cloud project ID for Spanner (defaults to ADC or LLM project).

    Returns:
        Configured FastMCP server instance.
    """
    logger.info(f"Creating MCP server with Spanner integration: {server_name}")

    # Validate dependencies
    if not SPANNER_AVAILABLE:
        raise ImportError(
            "Google Spanner dependencies not available. "
            "Install with: pip install langchain-google-spanner google-cloud-spanner"
        )

    if not VERTEXAI_AVAILABLE and llm_instance is None:
        raise ImportError(
            "Either LangChain VertexAI or a custom LLM instance is required. "
            "Install VertexAI with: pip install langchain-google-vertexai"
        )

    # --- Configure LLM ---
    if llm_instance:
        llm = llm_instance
        logger.info("Using provided LLM instance.")
    else:
        try:
            # Default to VertexAI if no instance provided
            logger.info(f"Initializing default LLM: ChatVertexAI (model: {llm_model_name})")
            llm = ChatVertexAI(
                project=llm_project_id,
                location=llm_location,
                model_name=llm_model_name,
            )
        except Exception as e:
            logger.error(f"Failed to initialize default VertexAI LLM: {e}", exc_info=True)
            raise ValueError(f"LLM initialization failed: {e}") from e

    # --- Define the LLM Chain Provider Function ---
    def get_spanner_llm_chain(agent_type: str) -> Any:
        """Factory function to create a LangChain chain for a given agent type."""
        logger.info(f"Creating LLM chain for agent_type='{agent_type}'")
        try:
            # Import required LangChain components
            from langchain_google_spanner import SpannerGraphStore
            from langchain.chains import LLMChain
            from langchain.prompts import PromptTemplate

            # Initialize the graph store (needed by the chain)
            graph_store = SpannerGraphStore(
                instance_id=instance_id,
                database_id=database_id,
                client=spanner.Client(project=spanner_project_id or llm_project_id),
            )

            # *** Create a custom chain that interacts with Spanner ***
            # This is a simplified placeholder - implement the full chain using actual
            # LangChain components for Spanner interaction
            graph_query_template = """
            You are an AI assistant that helps with answering questions using a Google Spanner database.

            Given the following user query, please do the following:
            1. Convert the natural language query into an appropriate GQL (Graph Query Language) query
            2. Execute that query on the database
            3. Provide a human-readable answer based on the query results

            User query: {query}

            First, write a GQL query that would answer this question, then provide the final answer.
            """

            prompt = PromptTemplate(
                input_variables=["query"],
                template=graph_query_template
            )

            chain = LLMChain(llm=llm, prompt=prompt)

            logger.info(f"Created LLM chain for agent type: {agent_type}")
            return chain

        except Exception as e:
            logger.error(f"Failed to create LLM chain for agent '{agent_type}': {e}", exc_info=True)
            raise RuntimeError(f"Chain creation failed for agent '{agent_type}': {e}") from e

    # --- Initialize Spanner Query Executor ---
    spanner_executor = SpannerQueryExecutor(
        instance_id=instance_id,
        database_id=database_id,
        get_llm_chain=get_spanner_llm_chain,
        project_id=spanner_project_id,
    )

    # --- Create Default Components if Needed ---
    if schema_provider is None:
        # Default schema provider - can be enhanced to fetch from Spanner later
        logger.warning("No schema provider specified, using default string schema.")
        schema_provider = StringSchemaProvider("""
        type Query {
            # This is a placeholder schema
            # The actual schema would be derived from Spanner
            entity(id: ID!): Entity
            search(term: String!): [Entity]
        }

        type Entity {
            id: ID!
            name: String
            description: String
            properties: [Property]
            relationships: [Relationship]
        }

        type Property {
            name: String!
            value: String
        }

        type Relationship {
            type: String!
            target: Entity
        }
        """)

    if ambiguity_detector is None:
        ambiguity_detector = SimpleAmbiguityDetector()

    # --- Create the MCP Server ---
    return create_mcp_server(
        schema_provider=schema_provider,
        query_executor=spanner_executor,
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
