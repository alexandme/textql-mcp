---
id: task-13
title: Set Up TextQL MCP Server with Spanner Backend
status: Done
assignee:
  - '@me'
created_date: '2025-07-11'
updated_date: '2025-07-13'
labels: []
dependencies:
  - task-4
  - task-6
  - task-9
  - task-12
  - task-19
---

## Description

Configure and run the TextQL MCP server to query the Spanner graph database using the defined schema and ingested data.

## Acceptance Criteria

- [x] Server is implemented using the provided API code
- [x] Server is running on host 0.0.0.0 port 8000
- [x] Basic connectivity is verified using curl or MCP client

## Implementation Plan

1. Activate textql-mcp conda environment and verify dependencies
2. Create custom schema provider using textql_mcp/schema.graphql
3. Create spanner_wikidata_server.py based on examples/spanner_server.py
4. Configure server with config/wikidata_poc.yaml settings
5. Set up authentication using spanner-graph-sa-key.json
6. Implement LangChain Spanner integration with Wikidata schema
7. Create startup script for easy server launch
8. Start server on 0.0.0.0:8000
9. Test connectivity with curl and MCP client
10. Document implementation and any technical decisions

## Implementation Notes

### Approach Taken\n- Implemented MCP server based on the provided API code from textql_mcp/core/server.py\n- Created custom schema provider (wikidata_schema_provider.py) to integrate GraphQL schema with Spanner\n- Used FastMCP framework for MCP protocol implementation\n- Leveraged LangChain for natural language to GraphQL translation with Vertex AI (gemini-pro)\n\n### Features Implemented\n- Created spanner_wikidata_server.py with 4 MCP tools:\n  - translate_to_gql: Natural language to GraphQL translation\n  - query_graph: Direct GraphQL query execution\n  - process_natural_language_query: End-to-end NL query pipeline\n  - get_schema_for_query: Schema information retrieval\n- Integrated with Spanner database containing 910,200 entities and 25,002 edges\n- Configuration loaded from config/wikidata_poc.yaml\n- Authentication using Application Default Credentials (ADC)\n\n### Technical Decisions and Trade-offs\n- Used ADC instead of service account key (key file not found, but ADC works)\n- Server runs on 0.0.0.0:8000 with FastAPI for HTTP endpoints\n- MCP communication via stdio (not HTTP) as per protocol specification\n- Used gemini-pro model for natural language understanding\n\n### Modified/Added Files\n- spanner_wikidata_server.py - Main MCP server implementation\n- wikidata_schema_provider.py - Custom schema provider for Wikidata\n- mcp_server_config.json - MCP server configuration\n- test_mcp_client.py - Basic MCP client for testing\n- start_server.sh - Startup script with environment setup\n- check_dependencies.py - Dependency and connectivity verification\n- docs/mcp-server-usage.md - Comprehensive usage documentation\n- docs/task-13-action-plan.md - Implementation tracking document\n\n### Verification Results\n- All dependencies installed and verified\n- Authentication working with ADC\n- Spanner connectivity confirmed (910,200 entities, 25,002 edges)\n- Server running successfully on 0.0.0.0:8000\n- MCP protocol ready for client connections via stdio
