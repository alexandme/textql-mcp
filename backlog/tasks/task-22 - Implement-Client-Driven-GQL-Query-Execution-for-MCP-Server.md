---
id: task-22
title: Implement Client-Driven GQL Query Execution for MCP Server
status: In Progress
assignee: []
created_date: '2025-07-14'
updated_date: '2025-07-14'
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

1. Enhance SchemaProvider for Spanner Schema Retrieval\n   - Add SpannerSchemaProvider to schema_provider.py that formats output as client-parseable string/JSON\n   - Instantiate it in main.py with project_id, instance_id, database_id\n   - Ensure get_schema_for_query returns formatted schema for client GQL generation\n\n2. Simplify QueryExecutor for Direct GQL Execution Only\n   - Remove all NL handling from SpannerQueryExecutor\n   - Update execute_query to assume inputs are valid Spanner GQL strings\n   - Execute GQL directly via graph_store.query() with proper graph clause\n   - Return structured results with error key for client iteration\n\n3. Remove NL Handling from get_spanner_llm_chain\n   - Deprecate or simplify the LLM chain factory\n   - Focus on direct execution via graph_store in QueryExecutor\n   - Remove any NL-to-GQL translation logic\n\n4. Update MCP Tools for Client-Driven Workflow\n   - Deprecate/repurpose translate_to_gql tool\n   - Update query_graph to execute client-generated GQL only\n   - Remove process_natural_language_query tool entirely\n   - Keep get_schema_for_query for client schema fetching\n\n5. Implement Error Handling and Optimization\n   - Always include error key in responses for client refinement\n   - Add query limits (e.g., LIMIT 100) if not specified\n   - Leverage Spanner indexes for performance\n\n6. Create Test Workflow\n   - Test client fetches schema via get_schema_for_query\n   - Test direct GQL execution for counts, entities, relationships\n   - Verify error responses enable client iteration\n\n7. Update Documentation\n   - Document client-driven workflow\n   - Provide example GQL queries for common operations\n   - Update server documentation to reflect MCP alignment
