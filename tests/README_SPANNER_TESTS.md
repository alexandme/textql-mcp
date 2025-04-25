# Testing the Google Spanner Integration

This document provides information on how to run the tests for the Google Spanner integration in TextQL MCP.

## Overview

The tests for the Google Spanner integration are divided into several categories:

1. **Unit tests**: Test individual components with mocked dependencies
2. **Integration tests**: Test the full integration flow (with both real and mocked dependencies)
3. **CLI argument tests**: Test the command-line interface for Spanner options

## Running the Tests

### Prerequisites

To run all tests, you'll need:

1. Python 3.10 or higher
2. pytest installed (`pip install pytest`)
3. The TextQL MCP package installed with test dependencies (`pip install -e ".[dev]"`)

### Running Unit Tests

Unit tests can be run without any special configuration:

```bash
# Run all tests
python -m pytest tests/

# Run specific Spanner-related tests
python -m pytest tests/test_spanner_query_executor.py
python -m pytest tests/test_spanner_server_creation.py
python -m pytest tests/test_spanner_cli_args.py
```

These tests use mocked dependencies and don't require real Google Cloud credentials.

### Running Integration Tests

For integration tests, there are two options:

#### 1. Mocked Integration Tests

These tests simulate the integration without requiring real cloud resources:

```bash
python -m pytest tests/test_spanner_integration.py::TestMockedSpannerIntegration
```

#### 2. Real Integration Tests

These tests connect to a real Google Spanner instance and require valid credentials:

```bash
# Set environment variables for real Spanner instance
export SPANNER_INTEGRATION_TESTS=true
export SPANNER_TEST_INSTANCE_ID=your-instance-id
export SPANNER_TEST_DATABASE_ID=your-database-id
export SPANNER_TEST_PROJECT_ID=your-project-id

# Ensure Google Cloud authentication is set up
gcloud auth application-default login

# Run integration tests
python -m pytest tests/test_spanner_integration.py::TestSpannerIntegration
```

**Note**: Real integration tests are skipped by default to avoid requiring cloud resources.

## Test Coverage

The test suite covers the following aspects of the Spanner integration:

- **SpannerQueryExecutor**: Initialization, query execution, error handling, graph store caching
- **create_mcp_server_with_spanner**: Server creation, LLM integration, component configuration
- **Command-line integration**: Argument parsing, validation, server startup
- **End-to-end flow**: The full process of translating and executing queries (mocked)

## Adding New Tests

When adding new tests:

1. Follow the existing patterns for mocking dependencies
2. Ensure tests can run without external dependencies by default
3. Use pytest fixtures from `conftest.py` for common test data and mocks
4. Make integration tests conditional with appropriate skipping logic

## Continuous Integration

In CI environments, only the unit tests and mocked integration tests will run automatically. To run real integration tests in CI, provide the necessary environment variables and credentials.
