---
id: task-8
title: Define Schema for Unified Vertex and Edge Tables in Spanner
status: To Do
assignee: []
created_date: '2025-07-11'
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
