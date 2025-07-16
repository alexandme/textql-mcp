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

### Option 1: Using Conda (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/textql-mcp.git
   cd textql-mcp
   ```

2. Create and activate the conda environment:
   ```bash
   conda create -n textql-mcp python=3.11 -y
   conda activate textql-mcp
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-spanner.txt  # For Google Cloud Spanner support
   pip install -e .
   ```

### Option 2: Using pip

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/textql-mcp.git
   cd textql-mcp
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```


## Quick Start

### Running with Google Cloud Spanner:

1. Configure your Google Cloud credentials:
   ```bash
   gcloud auth application-default login
   ```

2. Create a configuration file (e.g., `config/my_config.yaml`):
   ```yaml
   project_id: "my-project-id"
   instance_id: "my-instance"
   database_id: "my-database"
   ```

3. Start the server:
   ```bash
   python spanner_wikidata_server.py --config config/my_config.yaml
   ```

## Running the Server

### For Google Cloud Spanner:

```bash
# Using the wrapper script
./run_mcp_server.sh

# Or directly via command line
python -m textql_mcp --spanner-instance-id=<instance-id> --spanner-database-id=<database-id>
```

The server can be configured using YAML configuration files (e.g., `config/wikidata_poc.yaml`).

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
