---
id: task-10
title: Implement Unified Loader Script for Wikidata to Spanner
status: In Progress
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-11'
updated_date: '2025-07-11'
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

## Implementation Plan

1. Create and switch to new Git branch spanner-graph-cline-task10\n2. Review dependencies and configuration from previous tasks\n3. Create textql_mcp/wikidata directory if it doesn't exist\n4. Implement UnifiedLoader class in textql_mcp/wikidata/unified_loader.py with:\n   - Config loading from YAML\n   - BigQuery and Spanner client initialization\n   - load_entities() method with batch processing and data transformation\n   - load_edges() method ensuring referential integrity\n   - Error handling and logging\n5. Add dry-run mode for testing with small datasets\n6. Test with 100-row subset to verify functionality\n7. Document implementation notes and mark task as done
