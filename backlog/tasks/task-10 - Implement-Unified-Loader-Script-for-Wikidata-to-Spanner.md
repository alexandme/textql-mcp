---
id: task-10
title: Implement Unified Loader Script for Wikidata to Spanner
status: To Do
assignee: []
created_date: '2025-07-11'
labels: []
dependencies:
  - task-4
  - task-5
  - task-6
  - task-8
---

## Description

Develop a Python script to load entities and edges from BigQuery into Spanner using batch inserts.

## Acceptance Criteria

- [ ] textql_mcp/wikidata/unified_loader.py file is created with loading logic
- [ ] Batch inserts are used for efficiency
- [ ] Script transforms data and ensures entities are loaded before edges
- [ ] Basic functionality is tested with a small dataset
