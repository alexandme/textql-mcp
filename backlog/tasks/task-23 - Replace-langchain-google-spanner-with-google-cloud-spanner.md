---
id: task-23
title: Replace langchain-google-spanner with google-cloud-spanner
status: Done
assignee:
  - Cline
created_date: '2025-07-15'
updated_date: '2025-07-15'
labels: []
dependencies: []
---

## Description

Migrate Spanner query execution from langchain-google-spanner wrapper to direct google-cloud-spanner client to reduce dependencies and improve control.

## Acceptance Criteria

- [x] All queries execute successfully using new implementation
- [x] langchain-google-spanner removed from requirements
- [x] No LangChain dependencies remain unless needed
- [x] Tests pass

## Implementation Plan

1. Replace SpannerGraphStore with direct google-cloud-spanner client usage in query_executor.py
2. Update query execution to use database.snapshot().execute_sql()
3. Ensure result format compatibility with existing code
4. Remove langchain-google-spanner from requirements-spanner.txt
5. Update error messages and imports
6. Test with various query types
7. Remove unused langchain dependencies
8. Update documentation if needed

## Implementation Notes

Successfully migrated from langchain-google-spanner to direct google-cloud-spanner client usage:

### Changes Made:

1. **Modified `textql_mcp/utils/query_executor.py`**:
   - Replaced `SpannerGraphStore` from langchain with direct Spanner database access
   - Changed `_get_graph_store()` to `_get_database()` which returns a Spanner database instance
   - Updated `execute_query()` to use `database.snapshot().execute_sql()` for query execution
   - Maintained JSON-serializable result format for compatibility
   - Updated error messages to remove langchain references

2. **Updated dependencies**:
   - Removed `langchain-google-spanner` and `langchain-google-vertexai` from `requirements-spanner.txt`
   - Updated `setup.py` to remove langchain dependencies from the fallback list

3. **Fixed imports**:
   - Updated `textql_mcp/__main__.py` to import `create_mcp_server_with_spanner` from `main_spanner.py` instead of `main.py`
   - Updated `examples/spanner_server.py` similarly
   - Removed llm-related parameters that were no longer needed

4. **Technical Details**:
   - Used `database.snapshot()` for read-only query execution
   - Converted Spanner Row objects to dictionaries to maintain JSON serialization
   - Preserved the automatic LIMIT 100 safety feature
   - Kept the database caching strategy per agent type

### Files Modified:
- `textql_mcp/utils/query_executor.py`
- `requirements-spanner.txt`
- `setup.py`
- `textql_mcp/__main__.py`
- `examples/spanner_server.py`

### Notes:
- The `main.py` file still contains langchain references but is not used in production (production uses `main_spanner.py`)
- All existing tests pass without modification
- The MCP server interface remains unchanged, ensuring client compatibility
