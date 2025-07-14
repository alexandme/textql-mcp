---
id: task-20
title: Fix MCP Server Path Handling for Cline Integration
status: In Progress
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-14'
updated_date: '2025-07-14'
labels: []
dependencies:
  - task-13
---

## Description

The MCP server fails to start when invoked by Cline/Claude because it uses relative paths that break when the working directory differs from the project directory. This prevents the server from finding its configuration and schema files.

## Acceptance Criteria

- [ ] MCP server starts successfully when invoked by Cline
- [ ] Server finds config/wikidata_poc.yaml regardless of working directory
- [ ] Server finds textql_mcp/schema.graphql regardless of working directory
- [ ] All MCP tools work correctly after path fixes
- [ ] Manual server start still works from project directory
- [ ] Server logs show correct absolute paths being used
