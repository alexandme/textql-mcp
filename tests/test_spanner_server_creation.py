"""
Unit tests for the Spanner server creation functionality.

These tests ensure that the create_mcp_server_with_spanner function
works correctly with mocked dependencies.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
import pytest
import logging
import sys
from typing import Dict, Any, Optional

# Import the modules directly to patch them properly
import textql_mcp.main as main_module
from textql_mcp.main import create_mcp_server_with_spanner, SPANNER_AVAILABLE, VERTEXAI_AVAILABLE

# Skip all tests if Spanner dependencies aren't available
pytestmark = pytest.mark.skipif(not SPANNER_AVAILABLE, reason="Google Spanner dependencies not available")


class TestSpannerServerCreation(unittest.TestCase):
    """Test cases for Spanner server creation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock for SpannerQueryExecutor
        self.mock_executor = MagicMock()

        # Create mock for ChatVertexAI
        self.mock_llm = MagicMock()

        # Create mock for create_mcp_server
        self.mock_server = MagicMock()

        # Set up test parameters
        self.instance_id = "test-instance"
        self.database_id = "test-database"
        self.project_id = "test-project"
        self.llm_location = "test-location"
        self.llm_model_name = "test-model"

    @patch('textql_mcp.main.create_mcp_server')
    @patch('textql_mcp.main.SpannerQueryExecutor')
    @patch('textql_mcp.main.ChatVertexAI')
    @patch('textql_mcp.main.VERTEXAI_AVAILABLE', True)
    def test_create_with_default_llm(self, mock_vertex_ai, mock_spanner_executor, mock_create_server):
        """Test creation with default VertexAI LLM."""
        # Set up mocks
        mock_vertex_ai.return_value = self.mock_llm
        mock_spanner_executor.return_value = self.mock_executor
        mock_create_server.return_value = self.mock_server

        # Call the function with test parameters
        server = create_mcp_server_with_spanner(
            instance_id=self.instance_id,
            database_id=self.database_id,
            llm_project_id=self.project_id,
            llm_location=self.llm_location,
            llm_model_name=self.llm_model_name
        )

        # Verify VertexAI was initialized with correct parameters
        mock_vertex_ai.assert_called_once_with(
            project=self.project_id,
            location=self.llm_location,
            model_name=self.llm_model_name
        )

        # Verify SpannerQueryExecutor was created with correct parameters
        mock_spanner_executor.assert_called_once()
        call_args = mock_spanner_executor.call_args[1]
        self.assertEqual(call_args["instance_id"], self.instance_id)
        self.assertEqual(call_args["database_id"], self.database_id)
        self.assertEqual(call_args["project_id"], None)  # Default value
        self.assertTrue(callable(call_args["get_llm_chain"]))

        # Verify create_mcp_server was called with executor
        mock_create_server.assert_called_once()
        self.assertEqual(mock_create_server.call_args[1]["query_executor"], self.mock_executor)

        # Verify the returned server
        self.assertEqual(server, self.mock_server)

    @patch('textql_mcp.main.create_mcp_server')
    @patch('textql_mcp.main.SpannerQueryExecutor')
    @patch('textql_mcp.main.VERTEXAI_AVAILABLE', False)
    def test_create_with_custom_llm(self, mock_spanner_executor, mock_create_server):
        """Test creation with custom LLM instance."""
        # Set up mocks
        mock_spanner_executor.return_value = self.mock_executor
        mock_create_server.return_value = self.mock_server

        # Call the function with test parameters and custom LLM
        server = create_mcp_server_with_spanner(
            instance_id=self.instance_id,
            database_id=self.database_id,
            llm_instance=self.mock_llm
        )

        # Verify SpannerQueryExecutor was created with correct parameters
        mock_spanner_executor.assert_called_once()
        call_args = mock_spanner_executor.call_args[1]
        self.assertEqual(call_args["instance_id"], self.instance_id)
        self.assertEqual(call_args["database_id"], self.database_id)
        self.assertTrue(callable(call_args["get_llm_chain"]))

        # Verify create_mcp_server was called with executor
        mock_create_server.assert_called_once()
        self.assertEqual(mock_create_server.call_args[1]["query_executor"], self.mock_executor)

        # Verify the returned server
        self.assertEqual(server, self.mock_server)

    @patch('textql_mcp.main.VERTEXAI_AVAILABLE', False)
    def test_create_without_llm_instance_or_vertex(self):
        """Test that creation fails when no LLM is available."""
        # Call the function without LLM instance and with VertexAI unavailable
        with self.assertRaises(ImportError):
            create_mcp_server_with_spanner(
                instance_id=self.instance_id,
                database_id=self.database_id
            )

    @patch('textql_mcp.main.create_mcp_server')
    @patch('textql_mcp.main.SpannerQueryExecutor')
    @patch('textql_mcp.main.ChatVertexAI')
    @patch('textql_mcp.main.VERTEXAI_AVAILABLE', True)
    def test_create_with_custom_components(self, mock_vertex_ai, mock_spanner_executor, mock_create_server):
        """Test creation with custom schema provider and ambiguity detector."""
        # Set up mocks
        mock_vertex_ai.return_value = self.mock_llm
        mock_spanner_executor.return_value = self.mock_executor
        mock_create_server.return_value = self.mock_server

        # Create mock components
        mock_schema_provider = MagicMock()
        mock_ambiguity_detector = MagicMock()

        # Call the function with test parameters and custom components
        server = create_mcp_server_with_spanner(
            instance_id=self.instance_id,
            database_id=self.database_id,
            llm_project_id=self.project_id,
            schema_provider=mock_schema_provider,
            ambiguity_detector=mock_ambiguity_detector,
            server_name="Custom-Server-Name"
        )

        # Verify create_mcp_server was called with custom components
        mock_create_server.assert_called_once()
        call_args = mock_create_server.call_args[1]
        self.assertEqual(call_args["schema_provider"], mock_schema_provider)
        self.assertEqual(call_args["ambiguity_detector"], mock_ambiguity_detector)
        self.assertEqual(call_args["server_name"], "Custom-Server-Name")

    @patch('textql_mcp.main.create_mcp_server')
    @patch('textql_mcp.main.SpannerQueryExecutor')
    @patch('textql_mcp.main.ChatVertexAI')
    @patch('textql_mcp.main.VERTEXAI_AVAILABLE', True)
    def test_llm_chain_creation(self, mock_vertex_ai, mock_spanner_executor, mock_create_server):
        """Test the LLM chain creation function."""
        # Set up mocks
        mock_vertex_ai.return_value = self.mock_llm
        mock_spanner_executor.return_value = self.mock_executor
        mock_create_server.return_value = self.mock_server

        # Mock SpannerGraphStore and LLMChain
        mock_graph_store = MagicMock()
        mock_chain = MagicMock()

        with patch('textql_mcp.main.SpannerGraphStore', return_value=mock_graph_store) as mock_spanner_graph_store:
            with patch('textql_mcp.main.LLMChain', return_value=mock_chain) as mock_llm_chain:
                with patch('textql_mcp.main.PromptTemplate') as mock_prompt_template:
                    # Call the function with test parameters
                    server = create_mcp_server_with_spanner(
                        instance_id=self.instance_id,
                        database_id=self.database_id,
                        llm_project_id=self.project_id
                    )

                    # Extract the get_llm_chain function
                    get_llm_chain = mock_spanner_executor.call_args[1]["get_llm_chain"]

                    # Call it with a test agent type
                    chain = get_llm_chain("test_agent")

                    # Verify SpannerGraphStore was initialized
                    mock_spanner_graph_store.assert_called_once()

                    # Verify PromptTemplate was created
                    mock_prompt_template.assert_called_once()

                    # Verify LLMChain was created with correct parameters
                    mock_llm_chain.assert_called_once()
                    self.assertEqual(mock_llm_chain.call_args[1]["llm"], self.mock_llm)

                    # Verify the chain was returned
                    self.assertEqual(chain, mock_chain)

    @patch('textql_mcp.main.create_mcp_server')
    @patch('textql_mcp.main.SpannerQueryExecutor')
    @patch('textql_mcp.main.ChatVertexAI')
    @patch('textql_mcp.main.VERTEXAI_AVAILABLE', True)
    def test_chatvertexai_initialization_error(self, mock_vertex_ai, mock_spanner_executor, mock_create_server):
        """Test error handling when ChatVertexAI initialization fails."""
        # Set up mock to raise an exception
        mock_vertex_ai.side_effect = Exception("VertexAI error")

        # Call the function and check for ValueError
        with self.assertRaises(ValueError):
            create_mcp_server_with_spanner(
                instance_id=self.instance_id,
                database_id=self.database_id,
                llm_project_id=self.project_id
            )


if __name__ == '__main__':
    unittest.main()
