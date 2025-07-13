---
id: task-13
title: Set Up TextQL MCP Server with Spanner Backend
status: In Progress
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

- [ ] Server is implemented using the provided API code
- [ ] Server is running on host 0.0.0.0 port 8000
- [ ] Basic connectivity is verified using curl or MCP client

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
