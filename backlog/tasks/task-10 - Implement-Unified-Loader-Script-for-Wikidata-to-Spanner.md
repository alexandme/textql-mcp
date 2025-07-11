---
id: task-10
title: Implement Unified Loader Script for Wikidata to Spanner
status: Done
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

1. Review dependencies and configuration from previous tasks.\n2. Create the file textql_mcp/wikidata/unified_loader.py.\n3. Import necessary libraries: google.cloud.bigquery, google.cloud.spanner, yaml, tqdm.\n4. Define UnifiedLoader class with init, load_entities, load_edges, and run methods.\n5. Implement data transformation and batch inserts for entities and edges.\n6. Add logging, error handling, and test mode.\n7. Test with small dataset.

## Implementation Notes

Successfully implemented UnifiedLoader class with BigQuery to Spanner data pipeline. Fixed Spanner API usage by replacing InsertMutation with proper batch.insert_or_update calls. Added comprehensive data transformation, error handling, and dry run testing. Script tested with 100 entities/edges and ready for production use.
