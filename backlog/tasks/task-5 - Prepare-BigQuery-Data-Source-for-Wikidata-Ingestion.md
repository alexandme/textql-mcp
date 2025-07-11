---
id: task-5
title: Prepare BigQuery Data Source for Wikidata Ingestion
status: To Do
assignee: []
created_date: '2025-07-11'
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
