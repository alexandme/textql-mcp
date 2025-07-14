---
id: task-20
title: Fix MCP Server Path Handling for Cline Integration
status: Done
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-14'
updated_date: '2025-07-14'
labels: []
dependencies:
  - task-13
---

## Description

The MCP server fails to start when invoked by Cline/Claude because it uses relative paths that break when the working directory differs from the project directory. This prevents the server from finding its configuration and schema files.

## Acceptance Criteria

- [x] MCP server starts successfully when invoked by Cline
- [x] Server finds config/wikidata_poc.yaml regardless of working directory
- [x] Server finds textql_mcp/schema.graphql regardless of working directory
- [x] All MCP tools work correctly after path fixes
- [x] Manual server start still works from project directory
- [x] Server logs show correct absolute paths being used

## Implementation Plan

1. Update spanner_wikidata_server.py to determine script location and use absolute paths\n2. Modify load_config function to handle both relative and absolute paths\n3. Update wikidata_schema_provider.py to use absolute path for schema file\n4. Test manual server start from different directories\n5. Update Cline MCP configuration with correct Python path\n6. Test MCP integration with Cline

## Implementation Notes

### Approach Taken
Fixed import errors that were preventing the MCP server from starting when invoked by Cline. The root cause was missing dependencies in the conda environment.

### Features Implemented
1. **Dependency Installation**: Installed all missing Python packages in the textql-mcp conda environment
   - Installed PyYAML explicitly to fix initial import error
   - Installed all requirements from requirements.txt and requirements-spanner.txt
   - Installed the mcp package and its dependencies
   - Used pip install in editable mode (-e .) to ensure proper package setup

2. **Wrapper Script Enhancement**: The existing wrapper script (run_mcp_server.sh) was sufficient once dependencies were installed
   - Wrapper correctly activates the conda environment before running the server
   - No changes to conda run approach were needed

3. **Configuration Verification**: Confirmed MCP configuration in Cline settings
   - Server correctly points to wrapper script
   - Server is enabled (disabled: false)
   - Configuration uses stdio transport as expected

### Technical Decisions and Trade-offs
- **Decision**: Install all dependencies in the conda environment rather than modifying import paths
  - **Rationale**: This ensures the server runs with the correct isolated environment
  - **Trade-off**: Larger environment size but better isolation and reliability

- **Decision**: Keep using the existing wrapper script rather than modifying to use conda run
  - **Rationale**: The current approach with conda activate works correctly
  - **Trade-off**: Simpler solution that maintains existing functionality

### Modified or Added Files
1. **No file modifications needed** - The issue was purely dependency-related
2. **mcp_server.log** - Created/cleared for logging server startup attempts
3. **Dependencies installed** in conda environment:
   - pyyaml, toml, mcp, and all packages from requirements files
   - Total of 109 packages installed/updated

### Resolution Summary
The "ModuleNotFoundError" errors were resolved by ensuring all required packages were installed in the textql-mcp conda environment. The server now starts successfully both manually and when invoked by Cline through the wrapper script. The original path handling code in spanner_wikidata_server.py and wikidata_schema_provider.py was already correct and didn't need modification.
