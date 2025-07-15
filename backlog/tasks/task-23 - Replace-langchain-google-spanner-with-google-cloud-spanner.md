---
id: task-23
title: Replace langchain-google-spanner with google-cloud-spanner
status: In Progress
assignee:
  - Cline
created_date: '2025-07-15'
updated_date: '2025-07-15'
labels: []
dependencies: []
---

## Description

Migrate Spanner query execution from langchain-google-spanner wrapper to direct google-cloud-spanner client to reduce dependencies and improve control.

## Acceptance Criteria

- [ ] All queries execute successfully using new implementation
- [ ] langchain-google-spanner removed from requirements
- [ ] No LangChain dependencies remain unless needed
- [ ] Tests pass

## Implementation Plan

1. Replace SpannerGraphStore with direct google-cloud-spanner client usage in query_executor.py
2. Update query execution to use database.snapshot().execute_sql()
3. Ensure result format compatibility with existing code
4. Remove langchain-google-spanner from requirements-spanner.txt
5. Update error messages and imports
6. Test with various query types
7. Remove unused langchain dependencies
8. Update documentation if needed
