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
    Query executor that uses Google Spanner, potentially via LangChain integrations.
    It expects the 'query' input to be the final instruction or GQL query
    as prepared by the calling MCP tool.
    """

    def __init__(
        self,
        instance_id: str,
        database_id: str,
        # Use a more specific type hint if possible (e.g., Chain from langchain)
        # This function should return a configured LangChain chain instance ready to invoke
        get_llm_chain: Callable[[str], Any],
        project_id: Optional[str] = None,
        spanner_client: Optional[Any] = None,
        graph_name_prefix: str = "mcp_graph",
    ):
        """
        Initialize a SpannerQueryExecutor.

        Args:
            instance_id: The Google Spanner instance ID.
            database_id: The Google Spanner database ID.
            get_llm_chain: A callable that takes an agent_type (str) and returns
                           a configured LangChain chain instance capable of processing
                           the input query against the Spanner graph.
            project_id: Google Cloud project ID (optional, defaults to ADC).
            spanner_client: Optional pre-configured Spanner client.
            graph_name_prefix: Prefix for naming graphs in Spanner (e.g., per agent).
        """
        if not SPANNER_AVAILABLE:
            raise ImportError(
                "Google Spanner dependencies not available. "
                "Install with: pip install langchain-google-spanner google-cloud-spanner"
            )

        if not instance_id or not database_id:
            raise ValueError("instance_id and database_id are required.")
        if not callable(get_llm_chain):
             raise TypeError("get_llm_chain must be a callable function.")

        self.instance_id = instance_id
        self.database_id = database_id
        self.project_id = project_id
        self._get_llm_chain = get_llm_chain
        self.graph_name_prefix = graph_name_prefix

        # Initialize Google Spanner client
        try:
            self.spanner_client = spanner_client or spanner.Client(project=self.project_id)
            logger.info(
                f"Initialized SpannerQueryExecutor for instance='{instance_id}', "
                f"database='{database_id}'"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Spanner client: {e}", exc_info=True)
            raise RuntimeError(f"Spanner client initialization failed: {e}") from e

        # Cache for graph stores per agent type to avoid re-initialization
        self._graph_store_cache = {}

    def _get_graph_store(self, agent_type: str) -> Any:
        """Gets or initializes the SpannerGraphStore for a given agent type."""
        if agent_type not in self._graph_store_cache:
            try:
                # Construct a unique graph name per agent if needed
                graph_name = f"{self.graph_name_prefix}_{agent_type}"
                logger.info(f"Initializing SpannerGraphStore for agent '{agent_type}' with graph name '{graph_name}'")

                # Import here to avoid dependency issues if not installed
                from langchain_google_spanner import SpannerGraphStore

                self._graph_store_cache[agent_type] = SpannerGraphStore(
                    instance_id=self.instance_id,
                    database_id=self.database_id,
                    # graph_name=graph_name, # Include if supported/needed
                    client=self.spanner_client,
                )
            except Exception as e:
                logger.error(f"Failed to initialize SpannerGraphStore for agent '{agent_type}': {e}", exc_info=True)
                raise RuntimeError(f"SpannerGraphStore initialization failed for agent '{agent_type}': {e}") from e
        return self._graph_store_cache[agent_type]

    def execute_query(self, query: str, agent_type: str = "default") -> Dict[str, Any]:
        """
        Executes a query (which could be a natural language prompt intended for an LLM
        chain or a direct GQL query string) using the configured LangChain chain
        associated with the agent_type, interacting with Google Spanner.

        Args:
            query: The query/prompt string provided by the MCP tool.
            agent_type: The agent type identifier, used to select the appropriate
                        LLM chain and potentially graph configuration.

        Returns:
            Query results as a dictionary, expected to contain at least 'result'
            and optionally 'intermediate_steps' or 'error'.
        """
        logger.info(f"Executing Spanner query/prompt for agent_type='{agent_type}'")
        logger.debug(f"Input query/prompt: {query[:200]}...") # Log truncated query

        try:
            # 1. Get the appropriate LangChain chain for this agent type
            # This chain should be pre-configured (e.g., in the factory function)
            # to use the SpannerGraphStore and the LLM.
            chain = self._get_llm_chain(agent_type)
            if not chain:
                 raise ValueError(f"No LLM chain configured for agent_type '{agent_type}'")

            # Optional: Get/ensure the graph store is initialized (needed if chain doesn't handle it)
            # graph_store = self._get_graph_store(agent_type) # May not be needed if chain uses it internally

            # 2. Execute the query/prompt using the LangChain chain
            # The chain is responsible for NL->GQL translation (if needed),
            # query execution against SpannerGraphStore, and result formatting.
            # The specific input format (e.g., {'query': query}) depends on the chain type.
            logger.info(f"Invoking LLM chain for agent_type '{agent_type}'")
            # Example invocation, adjust based on the actual chain's expected input
            result_data = chain.invoke({"query": query})

            # 3. Format the result
            # Ensure the output conforms to the expected dictionary structure
            if isinstance(result_data, dict):
                # If the chain already returns the desired dict format
                 if 'result' not in result_data:
                      # Adapt if result is under a different key
                      result_data = {'result': str(result_data), 'intermediate_steps': result_data.get('intermediate_steps', [])}
            else:
                # If the chain returns a simple string or other type
                result_data = {"result": str(result_data), "intermediate_steps": []}

            logger.info(f"Query execution successful for agent_type='{agent_type}'")
            logger.debug(f"Result: {str(result_data)[:200]}...")
            return result_data

        except Exception as e:
            logger.error(f"Error executing query via chain for agent_type '{agent_type}': {e}", exc_info=True)
            return {
                "result": f"Error during Spanner query execution: {e}",
                "intermediate_steps": [],
                "error": str(e),
            }
