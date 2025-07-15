"""
Query executor implementations for the TextQL MCP Server.

This module provides various implementations of query executors that
can be used with the TextQL MCP Server.
"""

import logging
from typing import Dict, Any, Optional, List, Callable

# Import Spanner-related libraries if SpannerQueryExecutor is used
try:
    from google.cloud import spanner

    SPANNER_AVAILABLE = True
except ImportError:
    SPANNER_AVAILABLE = False

logger = logging.getLogger("textql_mcp.query_executor")


class DummyQueryExecutor:
    """Query executor that returns dummy results for testing and demonstration."""

    def __init__(self):
        """Initialize a DummyQueryExecutor."""
        logger.info("Initialized DummyQueryExecutor")

    def execute_query(self, query: str, agent_type: str = "default") -> Dict[str, Any]:
        """
        Execute a query against the database.

        Args:
            query: The query to execute
            agent_type: The agent type identifier

        Returns:
            Query results as a dictionary
        """
        logger.info(f"Executing dummy query for agent_type={agent_type}")
        return {
            "result": f"This is a dummy result for query: {query[:100]}...",
            "intermediate_steps": [],
        }


class CallbackQueryExecutor:
    """Query executor that uses a callback function to execute queries."""

    def __init__(self, callback: Callable[[str, str], Dict[str, Any]]):
        """
        Initialize a CallbackQueryExecutor.

        Args:
            callback: Function that executes queries and returns results
        """
        self.callback = callback
        logger.info("Initialized CallbackQueryExecutor")

    def execute_query(self, query: str, agent_type: str = "default") -> Dict[str, Any]:
        """
        Execute a query against the database.

        Args:
            query: The query to execute
            agent_type: The agent type identifier

        Returns:
            Query results as a dictionary
        """
        logger.info(f"Executing query via callback for agent_type={agent_type}")
        try:
            result = self.callback(query, agent_type)
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                "result": f"Error executing query: {e}",
                "intermediate_steps": [],
                "error": str(e),
            }


class LLMQueryExecutor:
    """Query executor that uses an LLM to process queries."""

    def __init__(self, get_llm_chain: Callable[[str], Any]):
        """
        Initialize an LLMQueryExecutor.

        Args:
            get_llm_chain: Function that returns an LLM chain for a given agent type
        """
        self.get_llm_chain = get_llm_chain
        logger.info("Initialized LLMQueryExecutor")

    def execute_query(self, query: str, agent_type: str = "default") -> Dict[str, Any]:
        """
        Execute a query using an LLM chain.

        Args:
            query: The query to execute
            agent_type: The agent type identifier

        Returns:
            Query results as a dictionary
        """
        logger.info(f"Executing query via LLM for agent_type={agent_type}")
        try:
            chain = self.get_llm_chain(agent_type)
            result = chain.invoke(query)
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                "result": f"Error executing query: {e}",
                "intermediate_steps": [],
                "error": str(e),
            }


class SpannerQueryExecutor:
    """
    Query executor that executes GQL queries directly against Google Spanner.
    This executor expects valid Spanner GQL queries and executes them without
    any NL processing or translation.
    """

    def __init__(
        self,
        instance_id: str,
        database_id: str,
        project_id: Optional[str] = None,
        spanner_client: Optional[Any] = None,
        graph_name: str = "wikidata_graph",
    ):
        """
        Initialize a SpannerQueryExecutor.

        Args:
            instance_id: The Google Spanner instance ID.
            database_id: The Google Spanner database ID.
            project_id: Google Cloud project ID (optional, defaults to ADC).
            spanner_client: Optional pre-configured Spanner client.
            graph_name: Name of the graph in Spanner.
        """
        if not SPANNER_AVAILABLE:
            raise ImportError(
                "Google Spanner dependencies not available. "
                "Install with: pip install langchain-google-spanner google-cloud-spanner"
            )

        if not instance_id or not database_id:
            raise ValueError("instance_id and database_id are required.")

        self.instance_id = instance_id
        self.database_id = database_id
        self.project_id = project_id
        self.graph_name = graph_name

        # Initialize Google Spanner client
        try:
            self.spanner_client = spanner_client or spanner.Client(
                project=self.project_id
            )
            logger.info(
                f"Initialized SpannerQueryExecutor for instance='{instance_id}', "
                f"database='{database_id}'"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Spanner client: {e}", exc_info=True)
            raise RuntimeError(f"Spanner client initialization failed: {e}") from e

        # Cache for graph stores per agent type to avoid re-initialization
        self._graph_store_cache = {}

    def _get_graph_store(self, agent_type: str = "default") -> Any:
        """Gets or initializes the SpannerGraphStore."""
        if agent_type not in self._graph_store_cache:
            try:
                logger.info(
                    f"Initializing SpannerGraphStore for graph '{self.graph_name}'"
                )

                # Import here to avoid dependency issues if not installed
                from langchain_google_spanner import SpannerGraphStore

                self._graph_store_cache[agent_type] = SpannerGraphStore(
                    instance_id=self.instance_id,
                    database_id=self.database_id,
                    graph_name=self.graph_name,
                    client=self.spanner_client,
                )
            except Exception as e:
                logger.error(
                    f"Failed to initialize SpannerGraphStore: {e}",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"SpannerGraphStore initialization failed: {e}"
                ) from e
        return self._graph_store_cache[agent_type]

    def execute_query(self, query: str, agent_type: str = "default") -> Dict[str, Any]:
        """
        Execute a GQL query directly against the Spanner graph.

        Args:
            query: The GQL query string to execute
            agent_type: The agent type identifier

        Returns:
            Query results as a dictionary containing 'result' and 'error' keys
        """
        logger.info(f"Executing direct Spanner GQL for agent_type='{agent_type}'")
        logger.debug(f"GQL query: {query[:200]}...")

        try:
            # Get the graph store
            graph_store = self._get_graph_store(agent_type)

            # Add LIMIT if not present (for safety)
            query_lower = query.lower()
            if "limit" not in query_lower and "count" not in query_lower:
                query = query.strip()
                if query.endswith(";"):
                    query = query[:-1]
                query += " LIMIT 100"

            # Ensure GRAPH clause is present
            if "graph" not in query_lower:
                query += f" GRAPH {self.graph_name}"

            logger.info(f"Executing GQL: {query}")

            # Execute the GQL query directly
            raw_results = graph_store.query(query)

            # Format results
            import json

            result_data = {
                "result": json.dumps(raw_results, default=str),
                "intermediate_steps": [],
            }

            logger.info(f"Query execution successful for agent_type='{agent_type}'")
            logger.debug(f"Result: {str(result_data)[:200]}...")
            return result_data

        except Exception as e:
            logger.error(
                f"GQL execution failed for agent_type '{agent_type}': {e}",
                exc_info=True,
            )
            return {
                "result": "",
                "intermediate_steps": [],
                "error": str(e),  # Clients use this to iterate/refine GQL
            }
