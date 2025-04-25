"""
Integration tests for the Google Spanner integration.

These tests ensure that the full integration with Google Spanner works correctly.
They are designed to be skipped if Spanner dependencies aren't available or
if no Spanner credentials are configured.
"""

import unittest
import pytest
import os
import logging
from unittest.mock import MagicMock, patch
import tempfile
import json
import sys

# Import the modules directly
import textql_mcp.main as main_module
from textql_mcp.main import create_mcp_server_with_spanner, SPANNER_AVAILABLE, VERTEXAI_AVAILABLE
from textql_mcp.utils.query_executor import SpannerQueryExecutor

# Skip all tests if Spanner dependencies aren't available
pytestmark = pytest.mark.skipif(
    not SPANNER_AVAILABLE or not VERTEXAI_AVAILABLE,
    reason="Google Spanner or VertexAI dependencies not available"
)

# Check if we should run real integration tests (requires actual credentials)
SPANNER_INTEGRATION_TESTS = os.environ.get("SPANNER_INTEGRATION_TESTS", "").lower() == "true"
INSTANCE_ID = os.environ.get("SPANNER_TEST_INSTANCE_ID", "")
DATABASE_ID = os.environ.get("SPANNER_TEST_DATABASE_ID", "")
PROJECT_ID = os.environ.get("SPANNER_TEST_PROJECT_ID", "")


@pytest.mark.skipif(
    not SPANNER_INTEGRATION_TESTS or not INSTANCE_ID or not DATABASE_ID,
    reason="Spanner integration tests not enabled or credentials not configured"
)
class TestSpannerIntegration(unittest.TestCase):
    """
    Integration tests for Spanner integration.

    These tests require:
    1. SPANNER_INTEGRATION_TESTS=true environment variable
    2. SPANNER_TEST_INSTANCE_ID, SPANNER_TEST_DATABASE_ID environment variables
    3. Google Cloud credentials configured (via ADC or service account)
    """

    def setUp(self):
        """Set up test fixtures."""
        self.instance_id = INSTANCE_ID
        self.database_id = DATABASE_ID
        self.project_id = PROJECT_ID

    def test_executor_initialization(self):
        """Test that SpannerQueryExecutor initializes with real credentials."""
        try:
            # Create a simple mock for get_llm_chain
            mock_get_llm_chain = MagicMock(return_value=MagicMock())

            # Create executor with real credentials
            executor = SpannerQueryExecutor(
                instance_id=self.instance_id,
                database_id=self.database_id,
                get_llm_chain=mock_get_llm_chain,
                project_id=self.project_id
            )

            # Basic validation
            self.assertEqual(executor.instance_id, self.instance_id)
            self.assertEqual(executor.database_id, self.database_id)

            # Attempt to initialize graph store (will fail if credentials are invalid)
            graph_store = executor._get_graph_store("test_agent")
            self.assertIsNotNone(graph_store)

        except Exception as e:
            self.fail(f"SpannerQueryExecutor initialization failed: {e}")

    @patch('textql_mcp.main.create_mcp_server')
    def test_server_creation(self, mock_create_server):
        """Test server creation with real credentials but mocked server."""
        # Set up mock
        mock_server = MagicMock()
        mock_create_server.return_value = mock_server

        try:
            # Create server with real credentials
            server = create_mcp_server_with_spanner(
                instance_id=self.instance_id,
                database_id=self.database_id,
                llm_project_id=self.project_id
            )

            # Verify server was created
            self.assertEqual(server, mock_server)

            # Verify create_mcp_server was called with SpannerQueryExecutor
            self.assertEqual(mock_create_server.call_count, 1)
            query_executor = mock_create_server.call_args[1]["query_executor"]
            self.assertIsInstance(query_executor, SpannerQueryExecutor)

        except Exception as e:
            self.fail(f"Server creation failed: {e}")


# Mocked integration tests that can always run
class TestMockedSpannerIntegration(unittest.TestCase):
    """
    Mocked integration tests for Spanner integration.

    These tests use mocked Spanner and LLM components to simulate
    the integration without requiring real cloud resources.
    """

    def setUp(self):
        """Set up test fixtures."""
        # Set up test parameters
        self.instance_id = "mock-instance"
        self.database_id = "mock-database"
        self.project_id = "mock-project"

    @patch('textql_mcp.utils.query_executor.spanner.Client')
    @patch('langchain_google_spanner.SpannerGraphStore')
    @patch('textql_mcp.main.ChatVertexAI')
    @patch('textql_mcp.main.create_mcp_server')
    def test_end_to_end_mocked(self, mock_create_server, mock_vertex_ai,
                                mock_spanner_graph_store, mock_spanner_client):
        """Test the entire flow with mocked dependencies."""
        # Set up mocks
        mock_client = MagicMock()
        mock_spanner_client.return_value = mock_client

        mock_graph_store = MagicMock()
        mock_graph_store.query.return_value = {"data": {"entity": {"name": "Test Entity"}}}
        mock_spanner_graph_store.return_value = mock_graph_store

        mock_llm = MagicMock()
        mock_vertex_ai.return_value = mock_llm

        mock_server = MagicMock()
        mock_create_server.return_value = mock_server

        # Create server
        server = create_mcp_server_with_spanner(
            instance_id=self.instance_id,
            database_id=self.database_id,
            llm_project_id=self.project_id
        )

        # Verify server was created
        self.assertEqual(server, mock_server)

        # Extract the query executor
        query_executor = mock_create_server.call_args[1]["query_executor"]
        self.assertIsInstance(query_executor, SpannerQueryExecutor)

        # Mock the LLM chain's invoke method
        llm_chain = MagicMock()
        llm_chain.invoke.return_value = {
            "result": "Query executed successfully",
            "intermediate_steps": [
                {"gql": "{entity(id:\"123\") {name}}"},
                {"data": {"entity": {"name": "Test Entity"}}}
            ]
        }
        query_executor._get_llm_chain = MagicMock(return_value=llm_chain)

        # Execute a query
        result = query_executor.execute_query(
            query="What is the name of entity 123?",
            agent_type="test_agent"
        )

        # Verify the result
        self.assertIn("result", result)
        self.assertEqual(result["result"], "Query executed successfully")
        self.assertIn("intermediate_steps", result)
        self.assertEqual(len(result["intermediate_steps"]), 2)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('textql_mcp.main.create_mcp_server_with_spanner')
    @patch('textql_mcp.main.run_server')
    @patch('textql_mcp.utils.query_executor.SPANNER_AVAILABLE', True)
    def test_command_line_integration(self, mock_run_server, mock_create_spanner_server, mock_parse_args):
        """Test the command-line integration."""
        # Import main module
        import textql_mcp.__main__ as main_module

        # Mock command-line arguments
        args = MagicMock()
        args.use_spanner = True
        args.spanner_instance_id = self.instance_id
        args.spanner_database_id = self.database_id
        args.spanner_project_id = self.project_id
        args.vertex_project_id = self.project_id
        args.vertex_location = "us-central1"
        args.vertex_model = "gemini-pro"
        args.host = "127.0.0.1"
        args.port = 8000
        args.name = "Test-Server"
        args.schema = None
        args.config = None
        args.log_level = "INFO"
        mock_parse_args.return_value = args

        # Mock server
        mock_server = MagicMock()
        mock_create_spanner_server.return_value = mock_server

        # Run main
        main_module.main()

        # Verify create_mcp_server_with_spanner was called with correct arguments
        mock_create_spanner_server.assert_called_once_with(
            instance_id=self.instance_id,
            database_id=self.database_id,
            llm_project_id=self.project_id,
            llm_location="us-central1",
            llm_model_name="gemini-pro",
            schema_provider=None,
            config_path=None,
            server_name="Test-Server",
            spanner_project_id=self.project_id,
        )

        # Verify run_server was called
        mock_run_server.assert_called_once_with(mock_server, "127.0.0.1", 8000)


if __name__ == '__main__':
    unittest.main()
