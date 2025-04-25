"""
Unit tests for the Spanner CLI argument handling.

These tests ensure that the command-line argument parsing for the Spanner integration works correctly.
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import pytest
import argparse

# Import module directly to patch it
import textql_mcp.__main__ as main_module


class TestSpannerCLIArgs(unittest.TestCase):
    """Test cases for Spanner CLI argument handling."""

    def test_parse_args_includes_spanner_options(self):
        """Test that the argument parser includes Spanner options."""
        with patch('sys.argv', ['textql_mcp', '--help']):
            with patch('argparse.ArgumentParser.parse_args', return_value=None):
                with patch('argparse.ArgumentParser.print_help') as mock_print_help:
                    try:
                        # Call parse_args directly to avoid running main()
                        parser = main_module.parse_args.__func__()
                    except SystemExit:
                        pass

        # Get the parser's argument groups
        parser = main_module.parse_args.__func__()
        spanner_group = None
        vertex_group = None

        for group in parser._action_groups:
            if group.title == 'Google Spanner Configuration':
                spanner_group = group
            elif group.title == 'Google VertexAI Configuration':
                vertex_group = group

        # Verify that Spanner argument group exists
        self.assertIsNotNone(spanner_group, "Spanner argument group not found")

        # Verify that VertexAI argument group exists
        self.assertIsNotNone(vertex_group, "VertexAI argument group not found")

        # Verify specific Spanner arguments
        spanner_arg_names = [action.dest for action in spanner_group._group_actions]
        self.assertIn('use_spanner', spanner_arg_names)
        self.assertIn('spanner_instance_id', spanner_arg_names)
        self.assertIn('spanner_database_id', spanner_arg_names)
        self.assertIn('spanner_project_id', spanner_arg_names)

        # Verify specific VertexAI arguments
        vertex_arg_names = [action.dest for action in vertex_group._group_actions]
        self.assertIn('vertex_project_id', vertex_arg_names)
        self.assertIn('vertex_location', vertex_arg_names)
        self.assertIn('vertex_model', vertex_arg_names)

    @patch('textql_mcp.__main__.create_mcp_server_with_spanner')
    @patch('textql_mcp.utils.query_executor.SPANNER_AVAILABLE', True)
    def test_main_uses_spanner_when_requested(self, mock_create_spanner_server):
        """Test that main() uses Spanner server creation when requested."""
        # Mock command-line arguments
        test_args = argparse.Namespace(
            use_spanner=True,
            spanner_instance_id='test-instance',
            spanner_database_id='test-database',
            spanner_project_id='test-project',
            vertex_project_id='test-vertex-project',
            vertex_location='test-location',
            vertex_model='test-model',
            host='0.0.0.0',
            port=8000,
            schema=None,
            config=None,
            name='Test-Server',
            log_level='INFO'
        )

        # Mock create_mcp_server_with_spanner and run_server
        mock_server = MagicMock()
        mock_create_spanner_server.return_value = mock_server

        with patch('textql_mcp.__main__.parse_args', return_value=test_args):
            with patch('textql_mcp.__main__.run_server') as mock_run_server:
                # Run main
                main_module.main()

        # Verify Spanner server creation was called with correct arguments
        mock_create_spanner_server.assert_called_once_with(
            instance_id='test-instance',
            database_id='test-database',
            llm_project_id='test-vertex-project',
            llm_location='test-location',
            llm_model_name='test-model',
            schema_provider=None,
            config_path=None,
            server_name='Test-Server',
            spanner_project_id='test-project',
        )

    @patch('textql_mcp.__main__.create_simple_server')
    def test_main_uses_simple_server_by_default(self, mock_create_simple_server):
        """Test that main() uses simple server creation by default."""
        # Mock command-line arguments
        test_args = argparse.Namespace(
            use_spanner=False,
            spanner_instance_id=None,
            spanner_database_id=None,
            spanner_project_id=None,
            vertex_project_id=None,
            vertex_location=None,
            vertex_model=None,
            host='0.0.0.0',
            port=8000,
            schema=None,
            config=None,
            name='Test-Server',
            log_level='INFO'
        )

        # Mock create_simple_server and run_server
        mock_server = MagicMock()
        mock_create_simple_server.return_value = mock_server

        with patch('textql_mcp.__main__.parse_args', return_value=test_args):
            with patch('textql_mcp.__main__.run_server') as mock_run_server:
                # Run main
                main_module.main()

        # Verify simple server creation was called
        mock_create_simple_server.assert_called_once()

    @patch('textql_mcp.__main__.logger')
    @patch('textql_mcp.utils.query_executor.SPANNER_AVAILABLE', True)
    def test_missing_spanner_args_validation(self, mock_logger):
        """Test that missing Spanner arguments are properly validated."""
        # Mock command-line arguments with missing required args
        test_args = argparse.Namespace(
            use_spanner=True,
            spanner_instance_id=None,  # Missing required argument
            spanner_database_id='test-database',
            spanner_project_id=None,
            vertex_project_id=None,
            vertex_location=None,
            vertex_model=None,
            host='0.0.0.0',
            port=8000,
            schema=None,
            config=None,
            name='Test-Server',
            log_level='INFO'
        )

        with patch('textql_mcp.__main__.parse_args', return_value=test_args):
            with patch('sys.exit') as mock_exit:
                # Run main - should exit due to missing arguments
                main_module.main()

        # Verify that error was logged and sys.exit was called
        mock_logger.error.assert_called()
        mock_exit.assert_called_once_with(1)

    @patch('textql_mcp.__main__.create_mcp_server_with_spanner')
    @patch('textql_mcp.__main__.logger')
    @patch('textql_mcp.utils.query_executor.SPANNER_AVAILABLE', False)
    def test_spanner_dependency_validation(self, mock_logger, mock_create_spanner_server):
        """Test that Spanner dependency validation works."""
        # Mock command-line arguments
        test_args = argparse.Namespace(
            use_spanner=True,
            spanner_instance_id='test-instance',
            spanner_database_id='test-database',
            spanner_project_id='test-project',
            vertex_project_id='test-project',
            vertex_location='test-location',
            vertex_model='test-model',
            host='0.0.0.0',
            port=8000,
            schema=None,
            config=None,
            name='Test-Server',
            log_level='INFO'
        )

        with patch('textql_mcp.__main__.parse_args', return_value=test_args):
            with patch('sys.exit') as mock_exit:
                # Run main - should exit due to missing dependencies
                main_module.main()

        # Verify that error was logged and sys.exit was called
        mock_logger.error.assert_called()
        mock_exit.assert_called_once_with(1)
        mock_create_spanner_server.assert_not_called()


if __name__ == '__main__':
    unittest.main()
