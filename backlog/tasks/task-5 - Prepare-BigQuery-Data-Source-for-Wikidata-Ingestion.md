---
id: task-5
title: Prepare BigQuery Data Source for Wikidata Ingestion
status: Done
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

- [x] BigQuery dataset (e.g. wikidata_slice) is created
- [x] Views such as v_unified_entities and v_extracted_edges are defined
- [x] Subset of Wikidata (e.g. 50k entities) is loaded
- [x] Verification query counts rows in the views

## Implementation Plan

1. Create and switch to new Git branch spanner-graph-cline-task5
2. Verify project and authentication settings from previous tasks
3. Create BigQuery dataset wikidata_slice for staging Wikidata subset
4. Query public Wikidata dataset to create raw tables with 50,000 entities total
5. Define views v_unified_entities and v_extracted_edges with unified schema
6. Verify data loading with row count queries
7. Update task documentation with implementation notes

## Implementation Notes

- Switched to branch spanner-graph-cline-task5.
- Verified Google Cloud project imperial-ally-429713-v1 from task-2.
- Created BigQuery dataset wikidata_slice.
- Queried bigquery-public-data.wikipedia.wikidata to create raw_entities table with 50,000 entities having labels, descriptions, and instance_of.
- Extracted relationships into raw_edges table, resulting in 549 edges.
- Defined v_unified_entities view with extracted fields like primary_instance_of_id, coordinates, birth/death dates.
- Defined v_extracted_edges view with to_id, edge_label.
- Verified with row counts: 50,000 entities, 549 edges.
- Adjusted entity subset to 50k for manageability, focusing on diverse types.
