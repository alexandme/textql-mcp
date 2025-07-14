# TextQL MCP Server Usage Guide

## Overview

The TextQL MCP Server provides natural language to SQL translation capabilities for querying the Wikidata graph database stored in Google Cloud Spanner. The server uses the Model Context Protocol (MCP) for communication.

## Server Details

- **Name**: TextQL-MCP-Wikidata-Spanner
- **Protocol**: MCP (Model Context Protocol) via stdio
- **Host**: 0.0.0.0
- **Port**: 8000 (for FastAPI/HTTP endpoints, not MCP)

## Available MCP Tools

### 1. translate_to_gql
Translates natural language queries into GraphQL queries based on the database schema.

**Parameters:**
- `natural_language_query` (string, required): The natural language question to translate
- `agent_type` (string, optional): Agent type identifier (default: "default")

**Example:**
```json
{
  "natural_language_query": "Show me all companies founded by Elon Musk"
}
```

### 2. query_graph
Executes a GraphQL query directly against the database.

**Parameters:**
- `gql_query` (string, required): The GraphQL query to execute
- `agent_type` (string, optional): Agent type identifier (default: "default")

**Example:**
```json
{
  "gql_query": "{ entitiesByType(entity_type: \"Q783794\") { vid label description } }"
}
```

### 3. process_natural_language_query
End-to-end pipeline that translates and executes natural language queries with automatic refinement.

**Parameters:**
- `natural_language_query` (string, required): The natural language question to process
- `agent_type` (string, optional): Agent type identifier (default: "default")
- `max_attempts` (integer, optional): Maximum query refinement attempts (default: 3)

### 4. get_schema_for_query
Fetches relevant schema information for a specific query.

**Parameters:**
- `query` (string, required): The query to fetch schema information for
- `agent_type` (string, optional): Agent type identifier (default: "default")

## MCP Client Configuration

### For Claude Desktop

Add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "textql-wikidata-spanner": {
      "command": "python",
      "args": ["/path/to/textql-mcp/spanner_wikidata_server.py"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/service-account-key.json"
      }
    }
  }
}
```

Note: If using Application Default Credentials (ADC), you can omit the `GOOGLE_APPLICATION_CREDENTIALS` environment variable.

### Starting the Server

1. **Using the startup script:**
   ```bash
   ./start_server.sh
   ```

2. **Manually:**
   ```bash
   conda activate textql-mcp
   python spanner_wikidata_server.py
   ```

## Example Queries

### Natural Language Examples
- "Show me all companies in the technology industry"
- "Find universities founded before 1900"
- "List people who are CEOs of multiple companies"
- "What companies is Stanford University affiliated with?"

### GraphQL Query Examples

```graphql
# Get entities by type
{
  entitiesByType(entity_type: "Q783794") {
    vid
    label
    description
    relationships {
      edge_type
      target {
        label
        entity_type
      }
    }
  }
}

# Search for entities
{
  search(term: "Stanford") {
    vid
    label
    entity_type
    description
  }
}

# Get specific entity with relationships
{
  entity(vid: "Q95") {
    label
    description
    relationships {
      edge_type
      target {
        label
      }
      properties
    }
  }
}
```

## Troubleshooting

### Server Won't Start
1. Check conda environment: `conda activate textql-mcp`
2. Verify dependencies: `python check_dependencies.py`
3. Check authentication: `gcloud auth application-default print-access-token`

### Connection Issues
- MCP servers communicate via stdio, not HTTP
- The server must be configured in your MCP client
- Check server logs for authentication or connection errors

### Query Errors
- Ensure entity types match Wikidata identifiers (e.g., Q783794 for companies)
- Use the `get_schema_for_query` tool to understand available fields
- Check server logs for detailed error messages

## Database Schema

The Spanner database contains:
- **entities** table: 910,200 Wikidata entities
- **edges** table: 25,002 relationships between entities

Entity types include:
- Q783794, Q4830453: Companies/Organizations
- Q5: People
- Q3918: Educational Institutions
- Q6256, Q515: Locations
- Q268592, Q28640: Industries/Occupations

Relationship types include:
- P169: CEO/Chief Executive Officer
- P452: Industry
- P159: Headquarters location
- P355: Subsidiary
- P127: Owned by
- P69: Educated at
