# Task 23: Replace langchain-google-spanner with google-cloud-spanner - Implementation Plan

## Overview
This document outlines the comprehensive plan for migrating from langchain-google-spanner to direct google-cloud-spanner usage in the TextQL MCP project.

## Current State Analysis

### Dependencies
- **langchain-google-spanner**: Currently used as a wrapper for Spanner operations
- **langchain-google-vertexai**: Listed in requirements but may not be needed
- **google-cloud-spanner**: Already present, will be used directly

### Code Usage
The main usage is in `textql_mcp/utils/query_executor.py`:
- `SpannerQueryExecutor` class uses `langchain_google_spanner.SpannerGraphStore`
- The `SpannerGraphStore.query()` method executes SQL queries
- Graph store is cached per agent type

## Implementation Plan

### Phase 1: Understand Current Implementation
1. **Analyze SpannerGraphStore behavior**
   - Review how queries are executed
   - Understand result format
   - Check any special processing done by the wrapper

2. **Identify all langchain dependencies**
   - Check for any other imports beyond SpannerGraphStore
   - Verify if langchain-google-vertexai is used anywhere

### Phase 2: Design New Implementation
1. **Direct Spanner Query Execution**
   - Use `google.cloud.spanner` client directly
   - Create database instance and snapshot for queries
   - Handle result formatting to match current output

2. **Maintain Interface Compatibility**
   - Keep the same `execute_query` method signature
   - Return results in the same format
   - Preserve error handling behavior

### Phase 3: Implementation Steps

#### Step 1: Update SpannerQueryExecutor
```python
# Remove:
from langchain_google_spanner import SpannerGraphStore

# Use direct Spanner operations:
instance = self.spanner_client.instance(self.instance_id)
database = instance.database(self.database_id)
```

#### Step 2: Replace query execution
Instead of:
```python
graph_store = SpannerGraphStore(...)
raw_results = graph_store.query(query)
```

Use:
```python
with database.snapshot() as snapshot:
    results = snapshot.execute_sql(query)
    raw_results = [dict(row) for row in results]
```

#### Step 3: Handle result formatting
- Ensure results are JSON-serializable
- Maintain the same structure as before

### Phase 4: Testing Plan
1. **Unit Tests**
   - Mock Spanner client for isolated testing
   - Test query execution with various queries
   - Test error handling scenarios

2. **Integration Tests**
   - Use test_client_driven_workflow.py
   - Verify queries work with actual Spanner instance
   - Compare results with current implementation

3. **Regression Testing**
   - Run all existing tests
   - Verify MCP server still works correctly
   - Test with various query types

### Phase 5: Cleanup
1. **Remove unused dependencies**
   - Remove langchain-google-spanner from requirements-spanner.txt
   - Remove langchain-google-vertexai if unused
   - Clean up any other langchain imports

2. **Update documentation**
   - Update architecture-overview.md
   - Update any setup instructions
   - Document the direct Spanner usage

## Risk Mitigation

### Potential Issues
1. **Query Format Differences**
   - SpannerGraphStore might handle SQL differently
   - Solution: Test thoroughly with various query types

2. **Result Format Changes**
   - Direct Spanner results might have different structure
   - Solution: Add result transformation layer if needed

3. **Connection Management**
   - Need to handle database connections properly
   - Solution: Use context managers and proper cleanup

### Rollback Plan
- Keep the old implementation commented out initially
- Can quickly revert by uncommenting and re-adding dependency
- Tag the commit before making changes

## Success Criteria
- All existing queries work without modification
- No langchain dependencies remain (unless explicitly needed elsewhere)
- Tests pass without changes
- Performance is same or better
- Code is cleaner and more maintainable

## Timeline Estimate
- Phase 1: 30 minutes (analysis)
- Phase 2: 30 minutes (design)
- Phase 3: 2 hours (implementation)
- Phase 4: 1 hour (testing)
- Phase 5: 30 minutes (cleanup)

Total: ~4.5 hours

## Next Steps
1. Review this plan and get approval
2. Create a backup/checkpoint of current code
3. Begin implementation following the phases
4. Test thoroughly at each step
5. Document any deviations from the plan
