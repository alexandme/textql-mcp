# Task-13: Set Up TextQL MCP Server with Spanner Backend - Action Plan

## Current Status
- ✅ Server implemented (`spanner_wikidata_server.py`)
- ✅ Custom schema provider created (`wikidata_schema_provider.py`)
- ✅ Server running on 0.0.0.0:8000
- ✅ Configuration loaded from `config/wikidata_poc.yaml`
- ✅ Authentication using Application Default Credentials (ADC)
- ✅ Startup script created (`start_server.sh`)
- ⚠️ Basic connectivity verification pending (MCP uses stdio, not HTTP)

## Completed Steps

### 1. Server Implementation ✅
- Created `spanner_wikidata_server.py` using the provided API code from `textql_mcp/core/server.py`
- Integrated custom schema provider (`wikidata_schema_provider.py`) with GraphQL schema
- Server loads configuration from `config/wikidata_poc.yaml`

### 2. Authentication Setup ✅
- Service account key not found (`spanner-graph-sa-key.json`)
- Using Application Default Credentials (configured in task-3)
- Server logs show successful authentication fallback to ADC

### 3. Startup Script ✅
- Created `start_server.sh` with:
  - Conda environment activation
  - Dependency checking
  - Authentication verification
  - Clear server startup messages

## Remaining Steps

### 4. Verify Basic Connectivity (CURRENT)
- [ ] Test authentication with Spanner database
- [ ] Create documentation for MCP client configuration
- [ ] Verify MCP server is accessible to clients
- [ ] Test basic MCP functionality

### 5. Create Usage Documentation
- [ ] Document MCP client configuration (Claude Desktop, etc.)
- [ ] Create example usage scenarios
- [ ] Add troubleshooting guide

### 6. Update Task with Implementation Notes
- [ ] Document all technical decisions
- [ ] List all created/modified files
- [ ] Note any deviations from original plan
- [ ] Mark all acceptance criteria as complete

## Technical Details

### Server Architecture
- MCP server using FastMCP framework
- Spanner integration via custom query executor
- GraphQL schema defined in `textql_mcp/schema.graphql`
- LangChain integration with Vertex AI (gemini-pro)

### Configuration
- Host: 0.0.0.0
- Port: 8000
- Spanner Instance: wikidata-graph-instance
- Spanner Database: wikidata-graph-db
- VertexAI Model: gemini-pro
- VertexAI Location: us-central1

### MCP Tools Available
1. **translate_to_gql**: Converts natural language to GraphQL
2. **query_graph**: Executes GraphQL queries
3. **process_natural_language_query**: End-to-end NL query processing
4. **get_schema_for_query**: Fetches relevant schema information
