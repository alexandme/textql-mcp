# Documentation: Implementation of Client-Driven GQL Query Execution for TextQL MCP Server (Task-22)

## 1. Introduction

### Feature Overview
The feature implemented in Task-22 refactors the TextQL MCP (Model Context Protocol) server to support **client-driven GQL (Graph Query Language) query execution**. This shifts the responsibility of natural language (NL) processing and GQL generation from the server to the client, aligning with MCP best practices. The server now acts as a lightweight executor of pre-generated GQL queries against a Google Cloud Spanner backend (specifically, a Wikidata graph database), while providing schema information to enable clients to generate valid GQL queries.

Key goals:
- Empower clients (e.g., AI agents like Claude Desktop) to handle complex logic, such as NL-to-GQL translation, query refinement, and iteration on errors.
- Reduce server complexity by removing embedded NL processing, making it more interoperable and modular.
- Maintain secure, standardized tool execution per MCP principles.

This implementation builds on an existing Spanner-backed MCP server setup, enhancing tools like `query_graph` and `get_schema_for_query` while deprecating NL-centric tools.

### Background and Context
The original server implementation included server-side NL handling (e.g., via LLM chains for translating NL queries to GQL). Based on research into MCP principles (from sources like modelcontextprotocol.io, zencoder.ai, and deepset.ai), MCP emphasizes a client-server model where:
- **Clients** (LLM hosts/applications) manage orchestration, logic, and iteration (e.g., generating GQL from NL using client-side LLMs, handling errors by regenerating queries).
- **Servers** focus on simple, secure execution of tools/resources (e.g., executing GQL against data sources like Spanner) without embedding client logic like NL processing.

This refactor promotes flexibility, reduces tight coupling, and enables agentic workflows on the client side.

## 2. Decisions Made and Why

### Key Decisions
1. **Shift NL-to-GQL Generation to Client**:
   - **Why**: Aligns with MCP's client-server architecture. Clients are better suited for dynamic iteration (e.g., "If error, regenerate GQL and retry") using their own LLM capabilities. Servers should remain lightweight to avoid over-engineering (e.g., no need for server-side QA chains or NL refinement).
   - **Research Basis**: MCP documentation (e.g., core architecture on modelcontextprotocol.io) stresses that hosts (clients) initiate connections and handle logic, while servers provide standardized interfaces. This reduces server bloat and enhances interoperability.

2. **Retain and Enhance Schema Provisioning**:
   - **Why**: Clients need schema details to generate accurate GQL. Providing a formatted schema (e.g., JSON listing tables/columns) enables clients to prompt their LLMs effectively (e.g., "Generate GQL for [NL query] using schema: [schema]").
   - **Format Choice**: JSON or string for easy parsing, ensuring client-friendliness.

3. **Simplify Query Execution to Direct GQL Only**:
   - **Why**: Assumes inputs are pre-generated GQL, eliminating server-side assumptions about input types. This keeps the server focused on execution, per MCP's tool executor role.
   - **Error Handling**: Always return an "error" key in responses to allow client-side refinement, promoting iterative workflows.

4. **Deprecate NL-Specific Tools and Chains**:
   - **Why**: Tools like `process_natural_language_query` and `translate_to_gql` embed server-side NL logic, violating MCP's separation of concerns. Deprecating them enforces client-driven orchestration.
   - **Alternative**: Clients use `get_schema_for_query` first, then generate GQL, and call `query_graph`.

5. **Minimal Changes to Existing Code**:
   - **Why**: Builds on current setup (e.g., `langchain-google-spanner` integration) to minimize disruption. No new dependencies; leverage existing SpannerGraphStore for execution.

6. **Optimization and Safety Additions**:
   - **Why**: Add defaults like `LIMIT 100` to prevent resource-intensive queries. Use Spanner indexes for performance, ensuring scalability.

### Trade-offs Considered
- **Legacy Support**: Kept minimal chains for potential legacy use but deprecated NL features to encourage migration.
- **Performance**: Client-side generation adds latency but enables more sophisticated agentic behaviors (e.g., multi-step reasoning).
- **Security**: Relies on MCP's authorization specs; no changes needed as server executes validated GQL.

## 3. What Has Been Changed

Changes were implemented step-by-step based on the provided plan. Below is a summary of modifications to key files/modules:

### Step 1: Update Dependencies (No Changes)
- No updates needed; existing `langchain-google-spanner` and `google-cloud-spanner` suffice.

### Step 2: Enhance `SchemaProvider` for Spanner Schema Retrieval
- **File**: `textql_mcp/utils/schema_provider.py`
  - Added `SpannerSchemaProvider` class to fetch and format Spanner schema (tables, columns, types) as JSON/string.
- **File**: `spanner_wikidata_server.py` or `textql_mcp/main.py`
  - Instantiated `SpannerSchemaProvider` with project/instance/database IDs.
- **Tool Integration**: `get_schema_for_query` in `textql_mcp/core/server.py` now returns formatted schema for client use.

### Step 3: Simplify `QueryExecutor` for Direct GQL Execution Only
- **File**: `textql_mcp/utils/query_executor.py` (in `SpannerQueryExecutor`)
  - Removed NL handling; `execute_query` assumes input is valid GQL.
  - Executes via `graph_store.query(query + " GRAPH wikidata_graph")`.
  - Returns dict with "result", "intermediate_steps", and "error" keys.
  - Added post-processing for counts/relationships if needed.
  - Handles exceptions by returning error details for client iteration.

### Step 4: Remove NL Handling from `get_spanner_llm_chain`
- **File**: `textql_mcp/main.py`
  - Simplified/deprecated the chain factory; no longer handles NL-to-GQL.
  - Focused on direct execution wrappers.

### Step 5: Update MCP Tools in `textql_mcp/core/server.py`
- Deprecated `translate_to_gql` (repurposed to return schema only if kept).
- Updated `query_graph`: Assumes `gql_query` is client-generated; executes and returns results/errors.
- Deprecated/removed `process_natural_language_query` entirely.
- Kept `get_schema_for_query` unchanged for schema fetching.

### Step 6: Error Handling, Optimization, and Testing
- Added "error" key in all responses.
- In `execute_query`, append `LIMIT 100` if absent.
- Testing: Simulated client workflow in `examples/simple_client.py` (fetch schema, generate GQL, execute, handle errors).
  - Examples: Counts (e.g., `MATCH (n:entities {entity_type: 'Company'}) RETURN count(n)`), relationships.

### Step 7: Deployment and MCP Alignment Check
- Restarted server post-changes.
- Verified alignment: Server is now a simple executor, empowering client-side logic.
- No session support added yet (potential future enhancement).

## 4. Current Status
- **Completed**: All acceptance criteria met (schema provisioning, direct GQL execution, NL removal, error handling, testing).
- **Status**: "Done" (based on successful test queries in logs, e.g., counting 48,883 organizations).
- **Branch**: A new branch (e.g., `feature/task-22-client-driven-gql`) was created from the current branch for these changes.
- **Known Issues**: None major; monitor for performance on large queries. Legacy NL code is deprecated but not fully removed.
- **Deployment**: Server restarts apply changes; tested with `simple_client.py`.

## 5. How to Use the Feature

### Workflow for Clients
1. **Fetch Schema**: Call `get_schema_for_query` with a query description to get formatted schema.
2. **Generate GQL**: Use client-side LLM to generate GQL (e.g., prompt: "Generate Spanner GQL for: [NL query] using schema: [schema]").
3. **Execute Query**: Call `query_graph` with the generated `gql_query`.
4. **Handle Errors/Iteration**: If "error" in response, refine GQL and retry.

### Example Usage (via `simple_client.py` or similar)
- **Fetch Schema**:
  ```python
  result = client.call_tool("get_schema_for_query", {"query": "Count organizations"})
  schema = result["schema"]
  ```
- **Generate GQL (Client-Side)**:
  ```python
  # Pseudo-code using LLM
  gql = llm.prompt(f"Generate GQL: Count organizations using schema: {schema}")
  # Example output: "MATCH (n:entities {entity_type: 'Organization'}) RETURN count(n) AS count"
  ```
- **Execute**:
  ```python
  result = client.call_tool("query_graph", {"gql_query": gql})
  print(result["result"])  # e.g., [{"count": 48883}]
  ```
- **Error Handling**:
  If `result["error"]`, regenerate GQL and retry.

### Common GQL Examples for Wikidata Graph
- Count: `MATCH (n:entities {entity_type: 'Company'}) RETURN count(n) AS count`
- Entities: `MATCH (n:entities) RETURN n LIMIT 5`
- Relationships: `MATCH (source:entities {vid: 'Q123'})-[r:edges]->(target:entities) RETURN source, r, target`

## 6. Testing and Validation
- **Unit Tests**: Added to `tests/` for schema fetching and direct GQL execution.
- **Integration Tests**: Simulated client workflow; verified error responses trigger retries.
- **Performance**: Queries use indexes; tested with limits to avoid scans.
- **MCP Alignment**: Confirmed via manual checks against MCP specs (e.g., no server-side orchestration).

## 7. Future Enhancements
- Add session caching for stateful client interactions.
- Support advanced GQL features (e.g., full-text search).
- Fully remove deprecated code after migration.

This implementation enhances the server's adherence to MCP, making it more robust for agentic AI workflows. For questions, refer to task-22 in the backlog.