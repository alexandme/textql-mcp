# TextQL MCP Server

A standalone Model Context Protocol (MCP) server implementation that exposes tools for translating natural language to `*` Query Language (`*`QL) and executing `*`QL queries.

## Overview

This library provides a standardized interface for AI models and agents to interact with SQL/Graph databases using the Model Context Protocol. The server exposes tools for sending `*`QL queries and retrieving structured responses.

## Features

- **Natural Language to `*`hQL Translation**: Convert natural language questions to SQL/GraphQL queries
- **Query Execution**: Execute SQL/GraphQL queries against your database
- **Schema Support**: Automatically fetch and use relevant schema information for query refinement
- **Extensible Design**: Easily integrate with your own database and schema providers
- **MCP Standard**: Built on the Model Context Protocol for seamless integration with AI agents

## Installation

```bash
pip install textql-mcp
```

## Quick Start

```python
import asyncio
from textql_mcp import create_mcp_server
from textql_mcp.schemas import SimpleSchemaProvider

# Create a schema provider
schema_provider = SimpleSchemaProvider("path/to/schema.sql")

# Create and start the MCP server
server = create_mcp_server(
    schema_provider=schema_provider,
    port=8000
)

server.run()
```

## Advanced Usage

See the `examples/` directory for complete examples of how to use the TextQL MCP Server with different database backends.

## Customization

You can customize the server by implementing these interfaces:

- `SchemaProvider`: Provides schema information for queries
- `QueryExecutor`: Executes queries against your database
- `AmbiguityDetector`: Detects ambiguities in natural language queries

## API Reference

### Tools

#### `translate_to_gql`

Translate a natural language query into a GraphQL query.

**Parameters:**
- `natural_language_query` (str): The natural language question to translate
- `agent_type` (str, optional): The agent type identifier (default: "default")

**Returns:**
- Dictionary containing the generated GraphQL query and related metadata

#### `query_graph`

Execute a query against the database.

**Parameters:**
- `gql_query` (str): The query to execute
- `agent_type` (str, optional): The agent type identifier (default: "default")

**Returns:**
- Dictionary containing the query results and metadata

#### `process_natural_language_query`

Process a natural language query by translating it to `*`QL and executing it.

**Parameters:**
- `natural_language_query` (str): The natural language question to process
- `agent_type` (str, optional): The agent type identifier (default: "default")
- `max_attempts` (int, optional): Maximum number of query refinement attempts (default: 3)

**Returns:**
- Dictionary containing the final results and execution history

## License

Apache 2.0 License
