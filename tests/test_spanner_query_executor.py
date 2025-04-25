"""
Unit tests for the SpannerQueryExecutor class.

These tests ensure that the SpannerQueryExecutor works correctly
with mocked dependencies.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import pytest
import logging
import sys
from typing import Dict, Any

# Import the module directly to patch it properly
import textql_mcp.utils.query_executor as query_executor_module
from textql_mcp.utils.query_executor import SpannerQueryExecutor, SPANNER_AVAILABLE

# Skip all tests if Spanner dependencies aren't available
pytestmark = pytest.mark.skipif(not SPANNER_AVAILABLE, reason="Google Spanner dependencies not available")


class TestSpannerQueryExecutor(unittest.TestCase):
    """Test cases for the SpannerQueryExecutor class."""

    @patch('textql_mcp.utils.query_executor.spanner.Client')
    def setUp(self, mock_spanner_client):
        """Set up test fixtures."""
        # Create mock for Spanner client
        self.mock_client = MagicMock()
        mock_spanner_client.return_value = self.mock_client

        # Create mock for LLM chain
        self.mock_llm_chain = MagicMock()
        self.mock_llm_chain.invoke.return_value = {
            "result": "Mock query result",
            "intermediate_steps": ["Step 1", "Step 2"]
        }

        # Create mock get_llm_chain function
        self.mock_get_llm_chain = MagicMock(return_value=self.mock_llm_chain)

        # Create instance with test parameters
        self.instance_id = "test-instance"
        self.database_id = "test-database"
        self.project_id = "test-project"

        # Create executor with mocks
        self.executor = SpannerQueryExecutor(
            instance_id=self.instance_id,
            database_id=self.database_id,
            get_llm_chain=self.mock_get_llm_chain,
            project_id=self.project_id
        )

    def test_initialization(self):
        """Test that SpannerQueryExecutor initializes correctly."""
        # Basic initialization checks
        self.assertEqual(self.executor.instance_id, self.instance_id)
        self.assertEqual(self.executor.database_id, self.database_id)
        self.assertEqual(self.executor.project_id, self.project_id)
        self.assertEqual(self.executor._get_llm_chain, self.mock_get_llm_chain)

        # Check that client was initialized correctly
        self.assertIsNotNone(self.executor.spanner_client)

    def test_initialization_errors(self):
        """Test that initialization errors are handled correctly."""
        # Test missing instance_id
        with self.assertRaises(ValueError):
            SpannerQueryExecutor(
                instance_id="",
                database_id=self.database_id,
                get_llm_chain=self.mock_get_llm_chain
            )

        # Test missing database_id
        with self.assertRaises(ValueError):
            SpannerQueryExecutor(
                instance_id=self.instance_id,
                database_id="",
                get_llm_chain=self.mock_get_llm_chain
            )

        # Test invalid get_llm_chain
        with self.assertRaises(TypeError):
            SpannerQueryExecutor(
                instance_id=self.instance_id,
                database_id=self.database_id,
                get_llm_chain="not_a_callable"
            )

    @patch('langchain_google_spanner.SpannerGraphStore')
    def test_get_graph_store(self, mock_spanner_graph_store):
        """Test that _get_graph_store initializes and caches graph stores."""
        # Setup mock
        mock_graph_store = MagicMock()
        mock_spanner_graph_store.return_value = mock_graph_store

        # First call should create a new graph store
        agent_type = "test_agent"
        graph_store = self.executor._get_graph_store(agent_type)

        # Check that SpannerGraphStore was created with correct parameters
        mock_spanner_graph_store.assert_called_once_with(
            instance_id=self.instance_id,
            database_id=self.database_id,
            client=self.executor.spanner_client
        )

        # Check that result is the mock graph store
        self.assertEqual(graph_store, mock_graph_store)

        # Check that it was cached
        self.assertEqual(len(self.executor._graph_store_cache), 1)
        self.assertEqual(self.executor._graph_store_cache[agent_type], mock_graph_store)

        # Second call should use the cached version
        mock_spanner_graph_store.reset_mock()
        graph_store_2 = self.executor._get_graph_store(agent_type)
        mock_spanner_graph_store.assert_not_called()
        self.assertEqual(graph_store_2, mock_graph_store)

    def test_execute_query(self):
        """Test that execute_query calls the LLM chain correctly."""
        # Execute a test query
        query = "test query"
        agent_type = "test_agent"
        result = self.executor.execute_query(query, agent_type)

        # Check that get_llm_chain was called with the agent_type
        self.mock_get_llm_chain.assert_called_once_with(agent_type)

        # Check that the chain's invoke method was called with the query
        self.mock_llm_chain.invoke.assert_called_once_with({"query": query})

        # Check that the result is what we expect
        self.assertEqual(result, {
            "result": "Mock query result",
            "intermediate_steps": ["Step 1", "Step 2"]
        })

    def test_execute_query_dict_without_result(self):
        """Test that execute_query handles dictionaries without 'result' key."""
        # Set up mock to return a dict without 'result' key
        self.mock_llm_chain.invoke.return_value = {
            "output": "Output without result key",
            "steps": ["Step A", "Step B"]
        }

        # Execute a test query
        result = self.executor.execute_query("test", "agent")

        # Check that the result was reformatted correctly
        self.assertIn("result", result)
        self.assertEqual(result["intermediate_steps"], [])

    def test_execute_query_non_dict_result(self):
        """Test that execute_query handles non-dict results."""
        # Set up mock to return a string
        self.mock_llm_chain.invoke.return_value = "Simple string result"

        # Execute a test query
        result = self.executor.execute_query("test", "agent")

        # Check that the result was reformatted correctly
        self.assertIn("result", result)
        self.assertEqual(result["result"], "Simple string result")
        self.assertEqual(result["intermediate_steps"], [])

    def test_execute_query_error(self):
        """Test that execute_query handles errors correctly."""
        # Set up mock to raise an exception
        self.mock_llm_chain.invoke.side_effect = Exception("Test error")

        # Execute a test query
        result = self.executor.execute_query("test", "agent")

        # Check that error is captured in the result
        self.assertIn("error", result)
        self.assertIn("Test error", result["error"])
        self.assertIn("Error during Spanner", result["result"])

    def test_execute_query_no_chain(self):
        """Test that execute_query handles case when no chain is returned."""
        # Set up mock to return None
        self.mock_get_llm_chain.return_value = None

        # Execute a test query and check for ValueError
        with self.assertRaises(ValueError):
            self.executor.execute_query("test", "agent")

    @patch('langchain_google_spanner.SpannerGraphStore')
    def test_graph_store_initialization_error(self, mock_spanner_graph_store):
        """Test error handling when graph store initialization fails."""
        # Set up mock to raise an exception
        mock_spanner_graph_store.side_effect = Exception("Graph store error")

        # Attempt to get a graph store and check for RuntimeError
        with self.assertRaises(RuntimeError):
            self.executor._get_graph_store("test_agent")


if __name__ == '__main__':
    unittest.main()
