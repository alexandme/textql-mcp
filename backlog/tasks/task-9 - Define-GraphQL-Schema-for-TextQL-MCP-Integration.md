---
id: task-9
title: Define GraphQL Schema for TextQL MCP Integration
status: In Progress
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-11'
updated_date: '2025-07-11'
labels: []
dependencies:
  - task-8
---

## Description

Create a GraphQL schema file that matches the Spanner tables to enable querying via TextQL MCP.

## Acceptance Criteria

- [ ] schema.graphql file is created with Query
- [ ] Entity
- [ ] and Relationship types
- [ ] Schema aligns with Spanner entities and edges tables
- [ ] File is validated by loading it in a schema provider test

## Implementation Plan

1. Map Spanner schema fields to GraphQL types\n2. Create schema.graphql file with Query, Entity, and Relationship types\n3. Include scalar JSON for flexible fields\n4. Add relationships field to Entity type for graph traversal\n5. Create or update test to validate schema loading\n6. Run tests to ensure schema is valid
