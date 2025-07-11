---
id: task-5
title: Prepare BigQuery Data Source for Wikidata Ingestion
status: In Progress
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-11'
updated_date: '2025-07-11'
labels: []
dependencies: []
---

## Description

Set up a BigQuery dataset with views for staging a subset of Wikidata to be loaded into Spanner.

## Acceptance Criteria

- [ ] BigQuery dataset (e.g.
- [ ] wikidata_slice) is created
- [ ] Views such as v_unified_entities and v_extracted_edges are defined
- [ ] Subset of Wikidata (e.g.
- [ ] 100k-200k entities) is loaded
- [ ] Verification query counts rows in the views

## Implementation Plan

1. Create and switch to new Git branch spanner-graph-cline-task5
2. Verify project and authentication settings from previous tasks
3. Create BigQuery dataset wikidata_slice for staging Wikidata subset
4. Query public Wikidata dataset to create raw tables with 50,000 entities total
5. Define views v_unified_entities and v_extracted_edges with unified schema
6. Verify data loading with row count queries
7. Update task documentation with implementation notes
