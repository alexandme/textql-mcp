---
id: task-8
title: Define Schema for Unified Vertex and Edge Tables in Spanner
status: In Progress
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-11'
updated_date: '2025-07-11'
labels: []
dependencies:
  - task-7
---

## Description

Execute DDL to create tables for entities and edges in the Spanner database to form the graph structure.

## Acceptance Criteria

- [ ] DDL for entities table is executed
- [ ] DDL for edges table (interleaved) is executed
- [ ] Indexes for entity_type and edge_type are created
- [ ] Schema is verified with gcloud spanner databases ddl describe

## Implementation Plan

1. Create and switch to new Git branch spanner-graph-cline-task8
2. Update task file with implementation plan
3. Prepare DDL statements for entities and edges tables based on docs/spanner_graph_creation.md
4. Create DDL file docs/spanner_schema_ddl.sql with:
   - entities table (vertices) with vid, entity_type, label, description, etc.
   - edges table (edges) interleaved in entities for performance
   - Indexes on entity_type and edge_type
5. Execute DDL using gcloud CLI to create tables and indexes
6. Verify schema creation with gcloud spanner databases ddl describe
7. Handle any edge cases or errors
8. Document implementation notes and mark task as done
