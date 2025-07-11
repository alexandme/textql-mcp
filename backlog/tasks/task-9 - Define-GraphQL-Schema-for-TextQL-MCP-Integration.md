---
id: task-9
title: Define GraphQL Schema for TextQL MCP Integration
status: Done
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

- [x] schema.graphql file is created with Query
- [x] Entity
- [x] and Relationship types
- [x] Schema aligns with Spanner entities and edges tables
- [x] File is validated by loading it in a schema provider test

## Implementation Plan

1. Map Spanner schema fields to GraphQL types\n2. Create schema.graphql file with Query, Entity, and Relationship types\n3. Include scalar JSON for flexible fields\n4. Add relationships field to Entity type for graph traversal\n5. Create or update test to validate schema loading\n6. Run tests to ensure schema is valid

## Implementation Notes

- Created GraphQL schema at `textql_mcp/schema.graphql` aligned with Spanner DDL from task-8
- Defined scalar JSON type to support flexible fields (type_specific_attributes, raw_claims, properties)
- Mapped Spanner fields to GraphQL types:
  - Entity: vid (ID!), entity_type (String!), label (String), description (String), confidence_score (Float), type_specific_attributes (JSON), raw_claims (JSON), created_at (String), relationships ([Relationship])
  - Relationship: edge_type (String!), target (Entity), start_date (String), end_date (String), role (String), rank (String), properties (JSON), created_at (String)
- Added Query type with three operations: entity(vid), entitiesByType(entity_type), search(term)
- Added test case `test_wikidata_spanner_schema` to `tests/test_schema_provider.py` to validate schema loading and structure
- Test validates presence of all required types, fields, and the JSON scalar
- All tests passing with `mcp` package installed in conda environment
