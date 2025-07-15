---
id: task-22
title: Implement Client-Driven GQL Query Execution for MCP Server
status: Done
assignee: []
created_date: '2025-07-14'
updated_date: '2025-07-15'
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

## Implementation Plan

1. Enhance SchemaProvider for Spanner Schema Retrieval
   - Add SpannerSchemaProvider to schema_provider.py that formats output as client-parseable string/JSON
   - Instantiate it in main.py with project_id, instance_id, database_id
   - Ensure get_schema_for_query returns formatted schema for client GQL generation

2. Simplify QueryExecutor for Direct GQL Execution Only
   - Remove all NL handling from SpannerQueryExecutor
   - Update execute_query to assume inputs are valid Spanner GQL strings
   - Execute GQL directly via graph_store.query() with proper graph clause
   - Return structured results with error key for client iteration

3. Remove NL Handling from get_spanner_llm_chain
   - Deprecate or simplify the LLM chain factory
   - Focus on direct execution via graph_store in QueryExecutor
   - Remove any NL-to-GQL translation logic

4. Update MCP Tools for Client-Driven Workflow
   - Deprecate/repurpose translate_to_gql tool
   - Update query_graph to execute client-generated GQL only
   - Remove process_natural_language_query tool entirely
   - Keep get_schema_for_query for client schema fetching

5. Implement Error Handling and Optimization
   - Always include error key in responses for client refinement
   - Add query limits (e.g., LIMIT 100) if not specified
   - Leverage Spanner indexes for performance

6. Create Test Workflow
   - Test client fetches schema via get_schema_for_query
   - Test direct GQL execution for counts, entities, relationships
   - Verify error responses enable client iteration

7. Update Documentation
   - Document client-driven workflow
   - Provide example GQL queries for common operations
   - Update server documentation to reflect MCP alignment

## Implementation Notes

Implemented client-driven GQL query execution following MCP best practices. Key changes:

- Created SpannerSchemaProvider in textql_mcp/utils/schema_provider_spanner.py that returns schema in client-parseable JSON format
- Simplified SpannerQueryExecutor to only execute pre-generated GQL queries, removing all NL handling
- Deprecated server-side NL tools (translate_to_gql and process_natural_language_query)
- Updated query_graph tool to execute client-generated GQL directly
- Added error key in all responses to enable client-side iteration
- Created test_client_driven_workflow.py demonstrating the new workflow
- Updated main_spanner.py to integrate the new components

The server now follows MCP principles where clients handle complex logic (NL-to-GQL translation) while the server provides simple, secure tool execution. Clients fetch schema, generate GQL using their LLM, execute queries, and iterate on errors.

Branch: task-22-client-driven-gql
Commit: d22564c
