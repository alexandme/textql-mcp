Below is a **comprehensive and detailed step-by-step plan** for creating a graph database in Google Spanner. This plan is derived from the provided files (`spanner_integration.md` and `wikidata_ingestion_plan.md`). It focuses on setting up Spanner as a graph database, defining a unified schema (inspired by the Wikidata ingestion plan), ingesting data (e.g., from Wikidata via BigQuery), and integrating it with TextQL MCP for query translation and execution. The plan assumes you're building a proof-of-concept (PoC) graph database, such as one populated with Wikidata entities (companies, people, locations, etc.) and their relationships.

The plan is structured into phases for clarity: **Preparation**, **Schema Creation**, **Data Ingestion**, **Integration with TextQL MCP**, **Validation and Testing**, and **Optimization and Maintenance**. Each step includes prerequisites, actions, rationale, potential commands/scripts, and troubleshooting tips based on the files.

---

### **Phase 1: Preparation (Setup Environment and Prerequisites)**
This phase ensures you have the necessary tools, credentials, and dependencies.

1. **Set Up Google Cloud Account and Project**:
   - Create or select a Google Cloud project with billing enabled.
   - Enable the Spanner API in the Google Cloud Console (APIs & Services > Enable APIs > Search for "Cloud Spanner API").
   - Rationale: Spanner requires an active project and enabled APIs.
   - Troubleshooting: If you encounter permission issues, ensure your IAM role includes `roles/spanner.admin` or equivalent.

2. **Configure Authentication (Application Default Credentials - ADC)**:
   - Install the Google Cloud CLI (`gcloud`) if not already installed.
   - Run: `gcloud auth application-default login` for local development.
   - Alternatively, for service accounts: Download a service account key JSON from IAM & Admin > Service Accounts, then set `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`.
   - Rationale: Spanner uses ADC for authentication, as noted in `spanner_integration.md`.
   - Troubleshooting: Test with `gcloud auth list`. If running in GCP (e.g., Cloud Run), it auto-uses the attached service account.

3. **Install Dependencies**:
   - Install Python 3.8+ and pip.
   - Clone the TextQL MCP repository: `git clone https://github.com/your-username/textql-mcp.git && cd textql-mcp`.
   - Install base package: `pip install textql-mcp`.
   - Install Spanner extras: `pip install textql-mcp[spanner]` (or `pip install -r requirements-spanner.txt` for explicit dependencies like `google-cloud-spanner`, `langchain-google-spanner`, `langchain-google-vertexai`, `google-auth`).
   - Rationale: These are required for Spanner integration, as per `spanner_integration.md`.
   - Troubleshooting: If imports fail (e.g., `ImportError: No module named 'langchain_google_spanner'`), reinstall with extras and verify with `pip list`.

4. **Prepare Data Source (e.g., BigQuery with Wikidata Slice)**:
   - Set up a BigQuery dataset (e.g., `wikidata_slice`) with views like `v_unified_entities` and `v_extracted_edges` as described in `wikidata_ingestion_plan.md`.
   - If using Wikidata: Load a subset (e.g., 100k-200k entities) into BigQuery using public datasets or custom extraction.
   - Rationale: The ingestion plan assumes data is staged in BigQuery for loading into Spanner.
   - Troubleshooting: Query BigQuery to verify views: `bq query --nouse_legacy_sql "SELECT COUNT(*) FROM your-project.wikidata_slice.v_unified_entities"`.

5. **Gather Configuration Details**:
   - Note your Spanner instance ID (create one if needed via `gcloud spanner instances create my-instance --config=regional-us-central1 --description="Wikidata Graph" --nodes=1`).
   - Note database ID (e.g., `wikidata-graph`).
   - Note project ID, Vertex AI details (project ID, location: `us-central1`, model: `gemini-pro`).
   - Create a config file (e.g., `config/wikidata_poc.yaml`) as shown in `wikidata_ingestion_plan.md`.
   - Rationale: Configurations drive the loader and server.

---

### **Phase 2: Schema Creation (Define Graph Structure in Spanner)**
Create a Spanner database with a unified graph schema for vertices (entities) and edges (relationships).

1. **Create Spanner Instance and Database**:
   - Use Google Cloud Console or CLI: `gcloud spanner databases create wikidata-graph --instance=my-instance`.
   - Rationale: Spanner organizes data into instances and databases.
   - Troubleshooting: If creation fails, check quota limits or IAM permissions.

2. **Define Unified Vertex and Edge Tables**:
   - Use the schema from `wikidata_ingestion_plan.md` as a base.
   - Execute DDL statements via the Spanner client library or Console SQL editor:
     ```sql
     -- Unified vertex table for all entity types
     CREATE TABLE entities (
         vid STRING(36) NOT NULL,
         entity_type STRING(20) NOT NULL,  -- e.g., 'Company', 'Person', 'Location', 'Industry', 'Product', 'Event'
         label STRING(MAX),
         description STRING(MAX),
         confidence_score FLOAT64,
         type_specific_attributes JSON,  -- Stores entity-specific fields as JSON
         raw_claims JSON,
         created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
     ) PRIMARY KEY (vid);

     -- Unified edge table (interleaved for performance)
     CREATE TABLE edges (
         from_vid STRING(36) NOT NULL,
         to_vid STRING(36) NOT NULL,
         edge_type STRING(50) NOT NULL,  -- e.g., 'EMPLOYED_BY', 'FOUNDER_OF', 'SUBSIDIARY_OF'
         start_date DATE,
         end_date DATE,
         role STRING(MAX),
         rank STRING(20),
         properties JSON,
         created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
     ) PRIMARY KEY (from_vid, to_vid, edge_type),
     INTERLEAVE IN PARENT entities ON DELETE CASCADE;
     ```
   - Add indexes for common queries: `CREATE INDEX idx_entities_type ON entities(entity_type); CREATE INDEX idx_edges_type ON edges(edge_type);`.
   - Rationale: This unified schema supports multiple entity types (as per Wikidata plan) while allowing graph traversals. Interleaving optimizes joins.
   - Troubleshooting: Use `gcloud spanner databases ddl describe wikidata-graph --instance=my-instance` to verify schema.

3. **Define GraphQL Schema (for TextQL MCP Integration)**:
   - Create a GraphQL schema file (e.g., `schema.graphql`) matching the Spanner tables, as hinted in `spanner_integration.md`:
     ```
     type Query {
         entity(vid: ID!): Entity
         search(term: String!): [Entity]
     }

     type Entity {
         vid: ID!
         entity_type: String!
         label: String
         description: String
         confidence_score: Float
         type_specific_attributes: JSON
         raw_claims: JSON
         relationships: [Relationship]
     }

     type Relationship {
         edge_type: String!
         target: Entity
         start_date: String
         end_date: String
         role: String
         rank: String
         properties: JSON
     }
     ```
   - Rationale: TextQL MCP translates natural language to GraphQL, which maps to Spanner queries.

---

### **Phase 3: Data Ingestion (Load Data into Spanner)**
Ingest data from BigQuery into Spanner using a custom loader.

1. **Implement Unified Loader Script**:
   - Based on `wikidata_ingestion_plan.md`, create `textql_mcp/wikidata/unified_loader.py` with classes for loading entities and edges (see file excerpt).
   - Use batch inserts for efficiency (batch size: 1000).
   - Limit entities per type (e.g., 100k companies) as per config.

2. **Implement CLI Tool for Loading**:
   - Create `textql_mcp/wikidata/cli.py` with Click for commands (see file excerpt).
   - Run: `python -m textql_mcp.wikidata.cli --config config/wikidata_poc.yaml --dry-run` (for testing), then without `--dry-run`.
   - Include progress bars (e.g., via `tqdm`) and logging.
   - Rationale: Loads ~190k entities and edges in batches.

3. **Execute Ingestion**:
   - Query BigQuery views, transform data (e.g., JSON fields), and insert into Spanner.
   - Load entities first, then edges (ensuring referential integrity).
   - Rationale: Ensures graph connectivity.
   - Troubleshooting: Monitor for timeouts; increase batch size or use transactions.

---

### **Phase 4: Integration with TextQL MCP (Enable Querying)**
Set up TextQL MCP to query the Spanner graph.

1. **Create TextQL MCP Server with Spanner Backend**:
   - Use the API from `spanner_integration.md`:
     ```python
     from textql_mcp.main import create_mcp_server_with_spanner, run_server
     from textql_mcp.utils.schema_provider import FileSchemaProvider

     schema_provider = FileSchemaProvider("schema.graphql")
     server = create_mcp_server_with_spanner(
         instance_id="my-instance",
         database_id="wikidata-graph",
         llm_project_id="your-project",
         llm_location="us-central1",
         llm_model_name="gemini-pro",
         schema_provider=schema_provider,
         spanner_project_id="your-project"
     )
     run_server(server, host="0.0.0.0", port=8000)
     ```
   - Or via CLI: `python -m textql_mcp --use-spanner --spanner-instance-id=my-instance --spanner-database-id=wikidata-graph --schema=schema.graphql`.

2. **Test Basic Queries**:
   - Use MCP client or curl to test tools like `translate_to_gql` and `query_graph`.
   - Rationale: Enables natural language to GraphQL translation, executed via LangChain on Spanner.

---

### **Phase 5: Validation and Testing**
Verify the graph database.

1. **Data Integrity Checks**:
   - Use `textql_mcp/wikidata/validator.py` to compare counts between BigQuery and Spanner.
   - Check edges for dangling references.

2. **Query Testing**:
   - Run sample GQL queries from `wikidata_ingestion_plan.md` (e.g., subsidiaries, founders).
   - Test via TextQL MCP: Natural language like "Find subsidiaries of Google".

3. **Performance Metrics**:
   - Measure query latency for 1-3 hop traversals.
   - Rationale: Ensures the graph is queryable and performant.
   - Troubleshooting: Enable DEBUG logging (`--log-level=DEBUG`).

---

### **Phase 6: Optimization and Maintenance**
1. **Optimize Schema and Queries**: Add more indexes based on query patterns.
2. **Scale Spanner**: Increase nodes if needed (`gcloud spanner instances update my-instance --nodes=3`).
3. **Backup and Monitoring**: Set up Spanner backups and Cloud Monitoring.
4. **Future Enhancements**: Auto-schema extraction, as noted in `spanner_integration.md`.
5. **Cleanup**: Delete test data/instances to avoid costs.

**Estimated Timeline**: 5-7 days for a PoC, assuming familiarity with GCP.
**Total Cost Estimate**: Low (Spanner starts at ~$0.90/hour per node; use 1 node for PoC).
**Risks**: Authentication issues, data volume exceeding quotas—start small.

This plan creates a functional graph database in Spanner, ready for AI-driven querying via TextQL MCP. If you need code snippets or modifications, let me know!