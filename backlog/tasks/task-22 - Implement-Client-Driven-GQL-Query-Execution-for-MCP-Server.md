---
id: task-22
title: Implement Client-Driven GQL Query Execution for MCP Server
status: To Do
assignee: []
created_date: '2025-07-14'
labels: []
dependencies: []
---

## Description

Following MCP best practices, refactor the server to focus on simple tool execution while clients handle complex logic like NL-to-GQL translation. This promotes flexibility, reduces server complexity, and empowers agents to build complex workflows.

## Acceptance Criteria

- [ ] Schema provider returns Spanner schema in client-friendly format
- [ ] Query executor accepts pre-generated GQL queries only
- [ ] Server-side NL handling is removed
- [ ] Error responses enable client-side iteration
- [ ] Direct GQL execution works correctly against Spanner
