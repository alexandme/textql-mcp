---
id: task-12
title: Execute Wikidata Ingestion into Spanner
status: To Do
assignee: []
created_date: '2025-07-11'
labels: []
dependencies:
  - task-11
---

## Description

Run the CLI tool to load data from BigQuery into the Spanner database, ensuring entities and edges are ingested correctly.

## Acceptance Criteria

- [ ] Ingestion is executed using the CLI without dry-run
- [ ] Approximately 190k entities and edges are loaded
- [ ] Process completes without errors
- [ ] Basic count queries in Spanner confirm data presence
