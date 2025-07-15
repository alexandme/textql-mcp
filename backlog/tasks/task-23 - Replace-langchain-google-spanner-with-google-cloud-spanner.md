---
id: task-23
title: Replace langchain-google-spanner with google-cloud-spanner
status: To Do
assignee: []
created_date: '2025-07-15'
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
