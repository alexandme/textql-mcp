---
id: task-6
title: Gather and Create Configuration for Spanner Wikidata Pipeline
status: Done
assignee: []
created_date: '2025-07-11'
updated_date: '2025-07-11'
labels: []
dependencies: []
---

## Description

Compile necessary configuration details and create a YAML config file to drive the ingestion and server processes.

## Acceptance Criteria

- [x] Spanner instance ID
- [x] database ID
- [x] project ID
- [x] Vertex AI details are noted
- [x] config/wikidata_poc.yaml file is created with the required settings
- [x] Configuration is validated by loading it in a test script

## Implementation Plan

1. Create and switch to new Git branch spanner-graph-cline-task6
2. Gather configuration details from previous tasks (project ID, authentication, BigQuery dataset)
3. Decide on Spanner instance and database names for future tasks
4. Create config/wikidata_poc.yaml with all required settings
5. Write test script tests/test_config.py to validate configuration
6. Run validation script to ensure all keys are present
7. Update task with implementation notes and mark as done

## Implementation Notes

- Created and switched to new Git branch: spanner-graph-cline-task6
- Gathered configuration details from previous tasks:
  - Project ID: imperial-ally-429713-v1 (from task-2)
  - Service account key: spanner-graph-sa-key.json (from task-3)
  - BigQuery dataset: wikidata_slice with views v_unified_entities and v_extracted_edges (from task-5)
  - Conda environment: textql-mcp with Python 3.11 (from task-4)
- Decided on Spanner configuration for future tasks:
  - Instance ID: wikidata-graph-instance
  - Database ID: wikidata-graph-db
- Created comprehensive YAML configuration file at config/wikidata_poc.yaml with:
  - GCP settings (project, Spanner, BigQuery, Vertex AI)
  - Authentication settings referencing service account key
  - Pipeline configuration for ingestion (batch size, workers, entity/edge processing)
  - Server configuration for MCP and GraphQL
  - Monitoring, logging, and data quality settings
- Implemented validation script tests/test_config.py that:
  - Loads and parses the YAML configuration
  - Validates all required sections and keys are present
  - Checks that values match expected configuration from previous tasks
  - Provides detailed error reporting if validation fails
- Successfully ran validation script confirming:
  - All required configuration keys are present
  - All values match expected configuration
  - Configuration is ready to drive the ingestion and server processes
