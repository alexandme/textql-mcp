"""
Query executor implementations for the TextQL MCP Server.

This module provides various implementations of query executors that
can be used with the TextQL MCP Server.
"""

import logging
from typing import Dict, Any, Optional, List, Callable

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
