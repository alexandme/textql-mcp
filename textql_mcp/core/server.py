"""
MCP Server with GraphQL query tool.

This module provides a modular MCP server implementation that exposes tools
for sending GraphQL queries and translating natural language to GQL.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List, AsyncIterator, Type, Protocol, Callable
from dataclasses import dataclass
from contextlib import asynccontextmanager
import re

import toml
from mcp.server.fastmcp import FastMCP, Context

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
        return {
            "result": f"Dummy result for query: {query}",
            "intermediate_steps": []
        }


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


def get_app_context_or_fallback(ctx: Context = None, app_context: Optional[AppContext] = None) -> Dict[str, Any]:
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
    
    @mcp.tool()
    def translate_to_gql(
        natural_language_query: str, agent_type: str = "default", ctx: Context = None
    ) -> Dict[str, Any]:
        """
        Translate a natural language query into a GraphQL query based on the database schema.

        This tool helps bridge the gap between natural language questions and database queries
        by analyzing the question and generating an appropriate GraphQL query.

        Args:
            natural_language_query: The natural language question to translate
            agent_type: The agent type identifier (default: "default")
            ctx: MCP context object

        Returns:
            Dict containing the generated GraphQL query and related metadata
        """
        logger.info(f"translate_to_gql called with agent_type={agent_type}")
        logger.debug(f"Natural language query: {natural_language_query}")

        # Get the app context
        app_ctx = get_app_context_or_fallback(ctx, app_context)

        # Fetch relevant schema information
        logger.info("Fetching schema information for query translation")
        schema_info = app_ctx["schema_provider"].get_schema(natural_language_query, agent_type)
        logger.debug(
            f"Schema info length: {len(schema_info) if schema_info else 0} characters"
        )

        # Check if the query is ambiguous
        is_ambiguous = app_ctx["ambiguity_detector"].is_ambiguous(natural_language_query)

        # Construct a prompt for translation
        translation_prompt = f"""I need to translate the following natural language question into a GraphQL query:

QUESTION: {natural_language_query}

To help with this translation, here is the relevant part of our database schema:

{schema_info}

Please generate a valid GraphQL query that will retrieve the information needed to answer this question.
Follow these guidelines:
1. Structure the query using proper GraphQL syntax with curly braces, fields, and arguments
2. Include only fields that are present in the schema
3. Use precise entity names as they appear in the schema
4. Use appropriate filters and conditions based on the question
5. If entity names mentioned in the question don't match exactly what's in the schema, use LIKE with wildcards
6. Return only the fields necessary to answer the question
7. Format the query neatly with proper indentation

Your response should ONLY contain the GraphQL query, no explanations or additional text.
"""

        # Execute the translation
        result = app_ctx["query_executor"].execute_query(translation_prompt, agent_type)
        
        # Extract the GraphQL query from the result
        gql_query = extract_gql_query(result.get("result", ""))

        return {
            "natural_language_query": natural_language_query,
            "gql_query": gql_query,
            "schema_info": schema_info,
            "is_ambiguous": is_ambiguous,
            "agent_type": agent_type,
        }

    @mcp.tool()
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
                ctx.info(f"Executing GraphQL query")
                ctx.report_progress(0, 1)
            except Exception as e:
                logger.warning(f"Error reporting progress: {e}")

        # Construct an execution prompt
        execution_prompt = f"""
        Please execute the following GraphQL query and return the results:
        
        ```graphql
        {gql_query}
        ```
        
        Execute this query exactly as provided without modifications.
        """

        # Execute the query
        logger.info("Executing GraphQL query")
        result = app_ctx["query_executor"].execute_query(execution_prompt, agent_type)

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
            "agent_type": agent_type,
        }

    @mcp.tool()
    def process_natural_language_query(
        natural_language_query: str,
        agent_type: str = "default",
        max_attempts: int = 3,
        ctx: Context = None,
    ) -> Dict[str, Any]:
        """
        Process a natural language query by translating it to GQL and executing it.

        This tool provides a complete end-to-end pipeline for handling natural language
        queries by translating them to GraphQL and executing them with automatic
        refinement if needed.

        Args:
            natural_language_query: The natural language question to process
            agent_type: The agent type identifier (default: "default")
            max_attempts: Maximum number of query refinement attempts (default: 3)
            ctx: MCP context object

        Returns:
            Dict containing the final results and execution history
        """
        logger.info(
            f"process_natural_language_query called with agent_type={agent_type}, max_attempts={max_attempts}"
        )
        logger.debug(f"Natural language query: {natural_language_query}")

        # Get the app context
        app_ctx = get_app_context_or_fallback(ctx, app_context)

        # Initialize tracking for attempts
        attempts = []
        current_query = natural_language_query

        for attempt in range(max_attempts):
            logger.info(f"Processing attempt {attempt+1}/{max_attempts}")

            # Progress reporting
            if ctx:
                try:
                    ctx.info(f"Attempt {attempt+1}: Processing query")
                    ctx.report_progress(attempt, max_attempts)
                except Exception as e:
                    logger.warning(f"Error reporting progress: {e}")

            # Get relevant schema information
            schema_info = app_ctx["schema_provider"].get_schema(current_query, agent_type)

            # Construct a prompt with information from previous attempts if available
            context_from_prev = ""
            if attempts:
                last_attempt = attempts[-1]
                context_from_prev = f"""
                Previous attempt information:
                - GQL Query: {last_attempt.get('gql_query', 'N/A')}
                - Result: {last_attempt.get('result', {}).get('result', 'N/A')}
                
                If the previous attempt did not yield satisfactory results, please refine the query to better address the question.
                """

            # Combined prompt for translating and executing in one step
            combined_prompt = f"""I need to answer the following question: {natural_language_query}
            
            {context_from_prev}
            
            Here is the relevant part of our database schema:
            
            {schema_info}
            
            Please follow these steps to help me answer this question:
            1. Analyze the question carefully
            2. Create a GraphQL query based on the schema that will retrieve the necessary information
            3. Execute the query and provide the results
            4. If the query does not yield useful results, refine it and try again
            
            When creating the GraphQL query, please follow these best practices:
            - Structure the query using proper GraphQL syntax with curly braces, fields, and arguments
            - Include only fields that are present in the schema
            - Use precise entity names as they appear in the schema
            - Use appropriate filters and conditions based on the question
            - If entity names mentioned in the question don't match exactly what's in the schema, use LIKE with wildcards
            - Return only the fields necessary to answer the question
            
            Please answer the original question based on the query results.
            """

            # Execute the combined prompt
            logger.info("Executing combined translation and execution")
            result = app_ctx["query_executor"].execute_query(combined_prompt, agent_type)

            # Extract the executed GQL query from intermediate steps if available
            gql_query = "Unknown - not found in response"
            for step in result.get("intermediate_steps", []):
                if isinstance(step, dict) and "gql" in step and isinstance(step["gql"], str) and step["gql"].strip():
                    gql_query = step["gql"]
                    break

            # Record this attempt
            attempt_info = {
                "attempt_number": attempt + 1,
                "query_input": current_query,
                "gql_query": gql_query,
                "result": result,
                "schema_info": schema_info,
            }
            attempts.append(attempt_info)

            # Check if results seem sufficient to stop refinement
            if not result_needs_refinement(result):
                logger.info(
                    f"Attempt {attempt+1} provided satisfactory results. Stopping refinement."
                )
                break

            # Update the query for the next attempt to include refinement instructions
            if attempt < max_attempts - 1:
                current_query = f"""
                The original question was: {natural_language_query}
                
                The previous query attempt was: {gql_query}
                
                This did not yield satisfactory results. Please refine the query to better address the original question.
                Consider:
                - Using different table or field names from the schema
                - Adjusting filters or conditions
                - Using LIKE with wildcards for fuzzy matching
                - Exploring alternative relationships in the schema
                """
                logger.info("Query updated for refinement in next attempt")

        # Final progress report
        if ctx:
            try:
                ctx.report_progress(min(len(attempts), max_attempts), max_attempts)
            except Exception as e:
                logger.warning(f"Error reporting final progress: {e}")

        # Prepare the final response
        final_result = (
            attempts[-1]["result"] if attempts else {"result": "No attempts were made"}
        )
        final_result["all_attempts"] = attempts
        final_result["original_query"] = natural_language_query
        final_result["agent_type"] = agent_type

        logger.info(
            f"process_natural_language_query completed with {len(attempts)} attempts"
        )
        return final_result

    @mcp.tool()
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
