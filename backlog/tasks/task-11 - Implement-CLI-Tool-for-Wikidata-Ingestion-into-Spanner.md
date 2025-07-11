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

## Implementation Plan

1. Create new Git branch spanner-graph-cline-task11 from spanner-graph-cline-task10\n2. Verify Click is installed (already available in environment)\n3. Create textql_mcp/wikidata/cli.py with Click CLI implementation\n4. Define main command with options: --config, --dry-run, --limit, --verbose\n5. Implement command function that initializes UnifiedLoader and calls run method\n6. Add user-friendly output with progress tracking and status messages\n7. Test CLI with --help and --dry-run commands to verify functionality
