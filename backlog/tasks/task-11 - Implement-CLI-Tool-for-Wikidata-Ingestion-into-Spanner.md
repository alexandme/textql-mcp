---
id: task-11
title: Implement CLI Tool for Wikidata Ingestion into Spanner
status: In Progress
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-11'
updated_date: '2025-07-11'
labels: []
dependencies:
  - task-10
---

## Description

Develop a CLI interface to orchestrate the data loading process using the unified loader script.

## Acceptance Criteria

- [ ] textql_mcp/wikidata/cli.py file is created with Click commands
- [ ] Supports configuration loading and dry-run mode
- [ ] Includes progress tracking and logging
- [ ] CLI functionality is verified by running help and a dry-run command
