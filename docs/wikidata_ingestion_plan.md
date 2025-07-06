# Simplified BigQuery → Spanner Graph PoC Plan (All Entity Types)

## 1. Create Unified Spanner Graph Schema (Day 1)

### Vertex Tables:
```sql
-- Unified vertex table for all entity types
CREATE TABLE entities (
    vid STRING(36) NOT NULL,
    entity_type STRING(20) NOT NULL,  -- 'Company', 'Person', 'Location', 'Industry', 'Product', 'Event'
    label STRING(MAX),
    description STRING(MAX),
    confidence_score FLOAT64,
    type_specific_attributes JSON,  -- Stores entity-specific fields
    raw_claims JSON,
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (vid);

-- Unified edge table
CREATE TABLE edges (
    from_vid STRING(36) NOT NULL,
    to_vid STRING(36) NOT NULL,
    edge_type STRING(50) NOT NULL,  -- 'EMPLOYED_BY', 'FOUNDER_OF', 'SUBSIDIARY_OF', etc.
    start_date DATE,
    end_date DATE,
    role STRING(MAX),
    rank STRING(20),
    properties JSON,
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (from_vid, to_vid, edge_type),
INTERLEAVE IN PARENT entities ON DELETE CASCADE;
```

## 2. Create Unified BigQuery → Spanner Loader (Day 2-3)

### New file: `textql_mcp/wikidata/unified_loader.py`
```python
class WikidataToSpannerLoader:
    def __init__(self, config):
        self.bq_client = bigquery.Client()
        self.spanner_client = spanner.Client()
        
    def load_entities(self):
        """Load all entity types from unified BigQuery view"""
        # Query: SELECT * FROM `project.wikidata_slice.v_unified_entities` LIMIT 100000
        
    def load_edges(self):
        """Load all relationships from edges view"""
        # Query: SELECT * FROM `project.wikidata_slice.v_extracted_edges` 
        # WHERE FromVid IN (loaded entities) AND ToVid IN (loaded entities)
```

## 3. Configuration for PoC (Day 3)

### New file: `config/wikidata_poc.yaml`
```yaml
bigquery:
  project_id: "your-project"
  dataset: "wikidata_slice"
  unified_entities_view: "v_unified_entities"
  edges_view: "v_extracted_edges"
  
spanner:
  project_id: "your-project"
  instance_id: "your-instance"
  database_id: "wikidata-graph"
  
loader:
  batch_size: 1000
  entity_limits:
    Company: 100000
    Person: 50000
    Location: 20000
    Industry: 5000
    Product: 10000
    Event: 5000
  edge_types_to_load:
    - EMPLOYED_BY
    - FOUNDER_OF
    - SUBSIDIARY_OF
    - HEADQUARTERED_IN
    - PART_OF_INDUSTRY
    - MANUFACTURED_BY
    - OCCURRED_AT
```

## 4. CLI Tool with Progress Tracking (Day 4)

### New file: `textql_mcp/wikidata/cli.py`
```python
@click.command()
@click.option('--config', required=True)
@click.option('--entity-type', help='Load specific entity type only')
@click.option('--dry-run', is_flag=True)
def load(config, entity_type, dry_run):
    """Load Wikidata entities into Spanner Graph"""
    # Show progress bars for each entity type
    # Log statistics at the end
```

## 5. Validation & Testing (Day 5)

### New file: `textql_mcp/wikidata/validator.py`
- Verify entity counts match between BigQuery and Spanner
- Check edge referential integrity
- Test sample GQL queries
- Measure query performance for 3-hop patterns

## Implementation Steps:
1. Create Spanner database with unified schema
2. Implement entity loader with type-based batching
3. Implement edge loader with validation
4. Add progress tracking and logging
5. Create dry-run mode for testing
6. Load sample data (1k entities of each type)
7. Verify data integrity
8. Load full PoC dataset
9. Run performance tests

## Query Examples to Test:
```gql
# Find all subsidiaries of a company
MATCH (c:Company {vid: "Q95"})-[:SUBSIDIARY_OF]->(s:Company)
RETURN s.label, s.country_qid

# Find people who founded companies in tech industry
MATCH (p:Person)-[:FOUNDER_OF]->(c:Company)-[:PART_OF_INDUSTRY]->(i:Industry)
WHERE i.label CONTAINS "technology"
RETURN p.label, c.label

# 3-hop: Person -> Company -> Location -> Companies in same location
MATCH (p:Person)-[:EMPLOYED_BY]->(c1:Company)-[:HEADQUARTERED_IN]->(l:Location)<-[:HEADQUARTERED_IN]-(c2:Company)
WHERE p.vid = "Q12345"
RETURN DISTINCT c2.label
```

## Deliverables:
- Unified loader script supporting all entity types
- Populated Spanner Graph with ~190k entities total
- Performance metrics for different query patterns
- Simple documentation with usage examples

## BigQuery Views Reference

The loader expects these BigQuery views to exist:

### v_unified_entities
Combines all validated entity types with unified schema:
- Vid (STRING)
- EntityType (STRING)
- Label (STRING)
- Description (STRING)
- confidence_score (FLOAT64)
- TypeSpecificAttributes (JSON)
- claims (JSON)

### v_extracted_edges
Extracts relationships between validated entities:
- FromVid (STRING)
- ToVid (STRING)
- EdgeType (STRING)
- StartDate (DATE)
- EndDate (DATE)
- Role (STRING)
- Rank (STRING)
- Qualifiers (JSON)