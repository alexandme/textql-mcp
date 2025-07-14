---
id: task-21
title: Implement Proper GraphQL-to-Spanner Query Translation
status: To Do
assignee: []
created_date: '2025-07-14'
updated_date: '2025-07-14'
labels: []
dependencies:
  - task-20
---

## Description

The current implementation uses a placeholder LLM chain that doesn't actually translate GraphQL queries to Spanner SQL queries. We need to implement proper query translation to enable natural language queries against the Wikidata graph database in Spanner.

## Acceptance Criteria

- [ ] GraphQL queries are properly translated to Spanner SQL
- [ ] Entity count queries work correctly
- [ ] Relationship queries return proper results
- [ ] Error handling provides meaningful feedback
- [ ] Performance is optimized for large datasets

## Implementation Notes

After analysis, we determined that the initial approach of server-side NL-to-GQL translation doesn't align with MCP best practices. MCP emphasizes a client-server model where clients handle orchestration and complex logic (like NL processing), while servers focus on secure, standardized execution of tools. This separation promotes flexibility, reduces server complexity, and empowers agents to build complex workflows. The actual implementation has been moved to task-22, which follows the client-driven approach where clients generate GQL queries using their own LLM capabilities and the server simply executes them.
