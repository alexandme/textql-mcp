# Google Spanner Integration for TextQL MCP

This document provides information on setting up and using the Google Spanner integration for TextQL MCP.

## Overview

The Google Spanner integration allows TextQL MCP to interact with a Google Spanner database using GraphQL queries. The integration leverages LangChain's Google Spanner integration to provide a seamless experience for querying graph data stored in Spanner.

## Features

- Connect to a Google Spanner database instance
- Use Google VertexAI (Gemini) as the LLM backend
- Translate natural language questions to GraphQL queries
- Execute GraphQL queries against the Spanner database
- Process and refine queries in a conversational manner

## Prerequisites

To use the Google Spanner integration, you'll need:

1. A Google Cloud account with a Spanner instance and database
2. Google Cloud credentials configured (either through Application Default Credentials or service account keys)
3. The necessary Python dependencies installed

## Installation

Install the TextQL MCP package with Spanner dependencies:

```bash
pip install textql-mcp[spanner]
```

Or if you're installing from the repository:

```bash
pip install -e ".[spanner]"
```

Alternatively, you can install the base package and then add the Spanner dependencies separately:

```bash
pip install textql-mcp
pip install -r requirements-spanner.txt
```

## Required Dependencies

The Spanner integration requires the following additional packages:

- `google-auth`: Google authentication library
- `google-cloud-spanner`: Google Cloud Spanner client library
- `langchain-google-spanner`: LangChain integration for Google Spanner
- `langchain-google-vertexai`: LangChain integration for Google VertexAI

## Authentication

The Spanner integration uses Google Cloud's Application Default Credentials (ADC) by default. You can set up ADC in one of the following ways:

1. For local development:
   ```bash
   gcloud auth application-default login
   ```

2. For service accounts:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

3. When running on Google Cloud (GCE, GKE, Cloud Run, etc.), the application will automatically use the service account attached to the resource.

## Usage

### Command Line

You can run the TextQL MCP server with Spanner integration using the command line:

```bash
python -m textql_mcp --use-spanner --spanner-instance-id=my-instance --spanner-database-id=my-database
```

Additional options:
```
--spanner-project-id      Google Cloud project ID for Spanner
--vertex-project-id       Google Cloud project ID for VertexAI
--vertex-location         Google Cloud location for VertexAI (default: us-central1)
--vertex-model            Model name for VertexAI (default: gemini-pro)
--schema                  Path to a GraphQL schema file (optional)
```

### Python API

You can also create a server with Spanner integration programmatically:

```python
from textql_mcp.main import create_mcp_server_with_spanner, run_server

# Create server with Spanner integration
server = create_mcp_server_with_spanner(
    instance_id="my-instance",
    database_id="my-database",
    llm_project_id="my-project",
    llm_location="us-central1",
    llm_model_name="gemini-pro",
    spanner_project_id="my-project",  # Optional, defaults to ADC
)

# Run server
run_server(server, host="0.0.0.0", port=8000)
```

### Example Script

An example script is provided in the `examples` directory:

```bash
python examples/spanner_server.py \
    --instance-id=my-instance \
    --database-id=my-database \
    --project-id=my-project
```

## Configuration

You can customize the Spanner integration using a TOML configuration file. Example configuration:

```toml
[spanner]
instance_id = "my-instance"
database_id = "my-database"
project_id = "my-project"
graph_name_prefix = "mcp_graph"

[vertex_ai]
project_id = "my-project"
location = "us-central1"
model_name = "gemini-pro"

[server]
host = "0.0.0.0"
port = 8000
name = "TextQL-MCP-Spanner-Server"
```

Pass the configuration file path using the `--config` option.

## How It Works

1. When a natural language query is received, the server uses the LLM (VertexAI Gemini) to translate it to GraphQL.
2. The GraphQL query is executed against the Spanner database using the LangChain SpannerGraphStore.
3. Results are processed and returned to the client.
4. If the query is ambiguous or returns no results, the server can refine the query through a conversation with the user.

## Limitations

- The integration is currently in beta and may have limitations in complex query scenarios.
- Performance may vary depending on the complexity of the schema and queries.
- Schema information must be provided manually or through a schema provider; automatic schema extraction from Spanner is planned for future releases.

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure your Google Cloud credentials are correctly configured. Check the `GOOGLE_APPLICATION_CREDENTIALS` environment variable if using a service account.

2. **Missing Dependencies**: Make sure all required dependencies are installed. If you get import errors, try reinstalling with:
   ```bash
   pip install textql-mcp[spanner]
   ```

3. **Connection Issues**: Verify your Spanner instance and database exist and are accessible with your credentials. Try using the Google Cloud Console to check the status.

4. **Schema Errors**: If you're seeing schema-related errors, check that your schema definition matches the actual structure in your Spanner database.

### Logging

To enable more detailed logging, set the log level to DEBUG:

```bash
python -m textql_mcp --use-spanner ... --log-level=DEBUG
```

## Future Enhancements

Planned enhancements for the Spanner integration include:

- Automatic schema extraction from Spanner database
- Improved query optimization
- Support for more complex GraphQL features
- Enhanced result formatting and presentation
- Improved error handling and retry mechanisms

## Contributing

Contributions to improve the Spanner integration are welcome. Please see the main project's contribution guidelines for more information.
