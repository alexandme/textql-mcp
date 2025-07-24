"""
MCP Server with GraphQL query tool.

This module provides a modular MCP server implementation that exposes tools
for sending GraphQL queries and translating natural language to GQL.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, AsyncIterator, Protocol
from dataclasses import dataclass
from contextlib import asynccontextmanager
import re

import toml
from mcp.server.fastmcp import FastMCP, Context

from .feature_flags import FeatureFlagManager, FeatureFlag, feature_flag_required

# Set up logging
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("textql_mcp")


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass


class ModuleImportError(Exception):
    """Exception raised when required modules cannot be imported."""

    pass


class SchemaProvider(Protocol):
    """Protocol for schema providers."""

    def get_schema(self, query: str, agent_type: str = "default") -> str:
        """
        Get schema information for a query.

        Args:
            query: The query to get schema information for
            agent_type: The agent type identifier

        Returns:
            Schema information as a string
        """
        ...


class QueryExecutor(Protocol):
    """Protocol for query executors."""

    def execute_query(self, query: str, agent_type: str = "default") -> Dict[str, Any]:
        """
        Execute a query against the database.

        Args:
            query: The query to execute
            agent_type: The agent type identifier

        Returns:
            Query results as a dictionary
        """
        ...


class AmbiguityDetector(Protocol):
    """Protocol for ambiguity detectors."""

    def is_ambiguous(self, query: str) -> bool:
        """
        Check if a query is ambiguous.

        Args:
            query: The query to check

        Returns:
            True if the query is ambiguous, False otherwise
        """
        ...


# Default implementations
class DefaultSchemaProvider:
    """Default schema provider that returns a dummy schema."""

    def get_schema(self, query: str, agent_type: str = "default") -> str:
        """Return a dummy schema for demonstration purposes."""
        return """
        type Query {
            example: String
        }
        """


class DefaultQueryExecutor:
    """Default query executor that returns a dummy result."""

    def execute_query(self, query: str, agent_type: str = "default") -> Dict[str, Any]:
        """Return a dummy result for demonstration purposes."""
        return {"result": f"Dummy result for query: {query}", "intermediate_steps": []}


class DefaultAmbiguityDetector:
    """Default ambiguity detector that always returns False."""

    def is_ambiguous(self, query: str) -> bool:
        """Always return False for demonstration purposes."""
        return False


@dataclass
class AppContext:
    """Application context for lifespan management."""

    config: Dict[str, Any]
    schema_provider: SchemaProvider
    query_executor: QueryExecutor
    ambiguity_detector: AmbiguityDetector
    feature_flags: FeatureFlagManager


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from a TOML file or environment variables.

    Args:
        config_path: Path to the configuration file (optional)

    Returns:
        Configuration dictionary

    Raises:
        ConfigError: If configuration could not be loaded
    """
    logger.info("Loading configuration...")

    if config_path and os.path.exists(config_path):
        try:
            logger.info(f"Loading configuration from {config_path}")
            config_dict = toml.load(config_path)
            return config_dict
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {e}")

    # If no config file or loading failed, use environment variables
    logger.info("Using environment variables for configuration")
    config_dict = {
        "PROJECT_ID": os.environ.get("PROJECT_ID", "default-project"),
        "AGENT_TYPES": os.environ.get("AGENT_TYPES", "default").split(","),
        "PORT": int(os.environ.get("MCP_PORT", "8000")),
        "HOST": os.environ.get("MCP_HOST", "0.0.0.0"),
    }

    return config_dict


def extract_gql_query(text: str) -> str:
    """
    Extract a GraphQL query from text that might contain explanation or other content.

    Args:
        text: The text potentially containing a GraphQL query

    Returns:
        The extracted GraphQL query
    """
    # Try to extract query between GraphQL code blocks
    code_block_pattern = r"```(?:graphql|gql)?\s*([\s\S]+?)\s*```"
    code_match = re.search(code_block_pattern, text)
    if code_match:
        return code_match.group(1).strip()

    # Try to extract query between curly braces if it looks like a GraphQL query
    query_pattern = r"(\{\s*\w+\s*\{[\s\S]+?\}\s*\})"
    query_match = re.search(query_pattern, text)
    if query_match:
        return query_match.group(1).strip()

    # If no clear pattern matches, return the cleaned text
    # Remove explanations, leading/trailing text, etc.
    lines = text.split("\n")
    query_lines = []
    in_query = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("{"):
            in_query = True

        if in_query:
            query_lines.append(line)

        if in_query and stripped.endswith("}"):
            break

    if query_lines:
        return "\n".join(query_lines)

    # Last resort: return the original text, assuming it might be a query or fragment
    return text.strip()


def get_app_context_or_fallback(
    ctx: Context = None, app_context: Optional[AppContext] = None
) -> Dict[str, Any]:
    """
    Get application context from the Context object or fall back to provided context.

    Args:
        ctx: The Context object provided to the tool
        app_context: Fallback application context

    Returns:
        Dict containing the application context elements
    """
    if ctx is None:
        logger.warning("Context object is None, using fallback context")
        if app_context is None:
            logger.error("No fallback context provided")
            raise ValueError("No context available")

        return {
            "config": app_context.config,
            "schema_provider": app_context.schema_provider,
            "query_executor": app_context.query_executor,
            "ambiguity_detector": app_context.ambiguity_detector,
        }

    try:
        if hasattr(ctx, "lifespan_ctx"):
            logger.debug("Using context.lifespan_ctx")
            return {
                "config": ctx.lifespan_ctx.config,
                "schema_provider": ctx.lifespan_ctx.schema_provider,
                "query_executor": ctx.lifespan_ctx.query_executor,
                "ambiguity_detector": ctx.lifespan_ctx.ambiguity_detector,
            }
        else:
            logger.warning(
                "Context object does not have lifespan_ctx attribute, using fallback context"
            )
            if app_context is None:
                logger.error("No fallback context provided")
                raise ValueError("No context available")

            return {
                "config": app_context.config,
                "schema_provider": app_context.schema_provider,
                "query_executor": app_context.query_executor,
                "ambiguity_detector": app_context.ambiguity_detector,
            }
    except Exception as e:
        logger.error(f"Error accessing context: {e}", exc_info=True)
        if app_context is None:
            logger.error("No fallback context provided")
            raise ValueError("No context available")

        return {
            "config": app_context.config,
            "schema_provider": app_context.schema_provider,
            "query_executor": app_context.query_executor,
            "ambiguity_detector": app_context.ambiguity_detector,
        }


def create_mcp_server(
    schema_provider: Optional[SchemaProvider] = None,
    query_executor: Optional[QueryExecutor] = None,
    ambiguity_detector: Optional[AmbiguityDetector] = None,
    config_path: Optional[str] = None,
    server_name: str = "TextQL-MCP-Server",
) -> FastMCP:
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
    # Load configuration
    config = load_config(config_path)

    # Initialize feature flags
    feature_flags = FeatureFlagManager(config)

    # Use provided components or defaults
    _schema_provider = schema_provider or DefaultSchemaProvider()
    _query_executor = query_executor or DefaultQueryExecutor()
    _ambiguity_detector = ambiguity_detector or DefaultAmbiguityDetector()

    # Create application context
    app_context = AppContext(
        config=config,
        schema_provider=_schema_provider,
        query_executor=_query_executor,
        ambiguity_detector=_ambiguity_detector,
        feature_flags=feature_flags,
    )

    # Define lifespan manager
    @asynccontextmanager
    async def app_lifespan(_: FastMCP) -> AsyncIterator[AppContext]:
        """Manage application lifecycle with type-safe context."""
        logger.info("Starting application lifecycle...")
        try:
            # Initialize on startup
            logger.info("Initializing application components")
            yield app_context
        except Exception as e:
            logger.error(f"Error during application initialization: {e}", exc_info=True)
            raise
        finally:
            # Cleanup on shutdown
            logger.info("Application shutting down...")

    # Create MCP server
    logger.info(f"Creating FastMCP server instance: {server_name}")
    mcp = FastMCP(
        server_name,
        lifespan=app_lifespan,
        dependencies=[
            "mcp>=1.6.0",
            "fastapi>=0.95.0",
            "uvicorn>=0.22.0",
            "toml",
        ],
    )

    # Register tools

    # DEPRECATED: translate_to_gql tool is deprecated in favor of client-side GQL generation
    # Clients should use get_schema_for_query to fetch schema and generate GQL themselves
    # @mcp.tool()
    # def translate_to_gql(...) -> Dict[str, Any]:
    #     """[DEPRECATED] Use client-side GQL generation instead."""
    #     pass

    @mcp.tool()
    @feature_flag_required(FeatureFlag.ENABLE_QUERY_GRAPH)
    def query_graph(
        gql_query: str, agent_type: str = "default", ctx: Context = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query against the database and return the results.

        This tool executes a GraphQL query directly against the database without
        additional processing or prompt interpretation. Use this for executing
        queries that have already been formulated.

        Args:
            gql_query: The GraphQL query to execute (not a natural language question)
            agent_type: The agent type identifier (default: "default")
            ctx: MCP context object

        Returns:
            Dict containing the query results and metadata
        """
        logger.info(f"query_graph called with agent_type={agent_type}")
        logger.debug(f"GraphQL query: {gql_query}")

        # Get the app context
        app_ctx = get_app_context_or_fallback(ctx, app_context)

        # Progress reporting
        if ctx:
            try:
                ctx.info("Executing GraphQL query")
                ctx.report_progress(0, 1)
            except Exception as e:
                logger.warning(f"Error reporting progress: {e}")

        # Execute the query directly (no NL processing)
        logger.info("Executing GraphQL query")
        result = app_ctx["query_executor"].execute_query(gql_query, agent_type)

        # Final progress report
        if ctx:
            try:
                ctx.report_progress(1, 1)
            except Exception as e:
                logger.warning(f"Error reporting final progress: {e}")

        logger.info("query_graph completed execution")
        return {
            "gql_query": gql_query,
            "result": result.get("result", ""),
            "intermediate_steps": result.get("intermediate_steps", []),
            "error": result.get("error", ""),  # Key for client refinement
            "agent_type": agent_type,
        }

    # DEPRECATED: process_natural_language_query tool is deprecated in favor of client-side iteration
    # Clients should orchestrate their own query refinement using query_graph and get_schema_for_query
    # @mcp.tool()
    # def process_natural_language_query(...) -> Dict[str, Any]:
    #     """[DEPRECATED] Use client-side orchestration for NL query processing."""
    #     pass

    @mcp.tool()
    @feature_flag_required(FeatureFlag.ENABLE_SCHEMA_FETCH)
    def get_schema_for_query(
        query: str, agent_type: str = "default", ctx: Context = None
    ) -> Dict[str, Any]:
        """
        Fetch schema information relevant to a specific query.

        Args:
            query: The query to fetch schema information for
            agent_type: The agent type identifier (default: "default")
            ctx: MCP context object

        Returns:
            Dict containing schema information relevant to the query
        """
        logger.info(f"get_schema_for_query called with agent_type={agent_type}")
        logger.debug(f"Query: {query}")

        # Safety measure: Remove any triple backticks to prevent parsing issues
        query = query.replace("```", "")

        # Get the app context
        app_ctx = get_app_context_or_fallback(ctx, app_context)

        logger.info(f"Fetching schema information for query: {query}")
        schema_info = app_ctx["schema_provider"].get_schema(query, agent_type)
        logger.debug(
            f"Schema info length: {len(schema_info) if schema_info else 0} characters"
        )

        return {"query": query, "agent_type": agent_type, "schema_info": schema_info}

    # Register endpoints
    @mcp.resource("http://localhost/health")
    def get_health() -> Dict[str, str]:
        """
        Get server health status.

        Returns:
            Dict with status and version information
        """
        logger.debug("Health check requested")
        return {"status": "healthy", "version": "0.1.0"}

    @mcp.resource("http://localhost/schema")
    def get_schema() -> Dict[str, Any]:
        """
        Get database schema information.

        Returns:
            Dict containing schema information
        """
        logger.info("get_schema endpoint called")
        # Access app context
        _app_context = app_context

        # Return complete schema information
        logger.info("Fetching complete schema")
        schema_info = _app_context.schema_provider.get_schema("*", "default")
        logger.debug(
            f"Schema info length: {len(schema_info) if schema_info else 0} characters"
        )

        return {"agent_type": "default", "schema_info": schema_info, "filtered": False}

    @mcp.resource("http://localhost/schema/{agent_type}")
    def get_agent_schema(agent_type: str) -> Dict[str, Any]:
        """
        Get database schema information for a specific agent type.

        Args:
            agent_type: The agent type to get schema information for

        Returns:
            Dict containing schema information for the specified agent type
        """
        logger.info(f"get_agent_schema endpoint called for agent_type={agent_type}")
        # Access app context
        _app_context = app_context

        logger.info(f"Fetching complete schema for agent_type={agent_type}")
        schema_info = _app_context.schema_provider.get_schema("*", agent_type)
        logger.debug(
            f"Schema info length: {len(schema_info) if schema_info else 0} characters"
        )

        return {"agent_type": agent_type, "schema_info": schema_info, "filtered": False}

    return mcp


def result_needs_refinement(result_data: Dict[str, Any]) -> bool:
    """
    Check if query result needs refinement based on content analysis.

    Args:
        result_data: The result data to analyze

    Returns:
        bool: True if the result needs refinement, False otherwise
    """
    logger.debug("Checking if result needs refinement")
    # Check if result contains indicators of failed or insufficient queries
    insufficient_indicators = [
        "no results found",
        "couldn't find",
        "no data available",
        "no information",
        "unable to find",
        "not in our database",
    ]

    result_text = result_data.get("result", "").lower()
    for indicator in insufficient_indicators:
        if indicator in result_text:
            logger.debug(f"Found refinement indicator: '{indicator}'")
            return True

    return False


def run_server(mcp: FastMCP) -> None:
    """
    Run the MCP server.

    Args:
        mcp: The MCP server to run
    """
    try:
        logger.info("Starting MCP server")
        mcp.run()
    except Exception as e:
        logger.error(f"Error starting server: {e}", exc_info=True)
        sys.exit(1)
