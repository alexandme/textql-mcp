# BigQuery Wikidata Subset Creation Guide

This guide provides step-by-step instructions for creating a connected subset of Wikidata focused on companies, executives, industries, and related attributes using BigQuery's public Wikidata dataset.

## Overview

This process creates a ~1M entity connected graph from Wikidata, specifically designed for ingestion into Spanner Graph. The subset focuses on companies and their relationships to executives, industries, and locations.

## Prerequisites

- Google Cloud project with BigQuery API enabled
- Access to `bigquery-public-data.wikipedia.wikidata`
- Sufficient BigQuery quota for ~1M row queries
- Replace `your-project-id` with your actual project ID in all queries

## Step 1: Create BigQuery Dataset

```bash
bq mk --dataset your-project-id:wikidata_slice
```

## Step 2: Create Seed Entities (Starting Companies)

Start with ~100k companies (instance_of Q783794 or Q4830453) to seed the graph.

```sql
CREATE OR REPLACE TABLE `your-project-id.wikidata_slice.raw_seeds` AS
SELECT 
  id,
  CAST(SUBSTR(id, 2) AS INT64) AS numeric_id,
  (SELECT value FROM UNNEST(labels) WHERE language = 'en' LIMIT 1) AS label,
  (SELECT value FROM UNNEST(descriptions) WHERE language = 'en' LIMIT 1) AS description,
  ARRAY_AGG(DISTINCT io) AS instance_of,
  (SELECT AS STRUCT
     (SELECT value FROM UNNEST(statements) WHERE property = 'P571' LIMIT 1) AS founding_date,  -- Inception
     (SELECT CAST(value AS FLOAT64) FROM UNNEST(statements) WHERE property = 'P2139' LIMIT 1) AS revenue,  -- Revenue
     (SELECT value FROM UNNEST(statements) WHERE property = 'P1128' LIMIT 1) AS num_employees  -- Employees
   ) AS attributes  -- JSON-like struct for type_specific_attributes
FROM `bigquery-public-data.wikipedia.wikidata`
CROSS JOIN UNNEST(instance_of) AS io
WHERE type = 'item' 
  AND io IN ('Q783794', 'Q4830453')  -- Company or business
  AND RAND() < 0.001  -- Random sample for ~100k (adjust for size)
GROUP BY id, numeric_id, label, description
LIMIT 100000;
```

**Verification:**
```sql
SELECT COUNT(*) FROM `your-project-id.wikidata_slice.raw_seeds`;
-- Expected: ~100k companies
```

## Step 3: Recursively Expand to Connected Entities

Expand from seeds via key properties (executives, industries, locations). Limit to 2 hops for ~1M total.

```sql
CREATE OR REPLACE TABLE `your-project-id.wikidata_slice.raw_entities` AS
WITH recursive_expansion AS (
  -- Base: Seeds
  SELECT id FROM `your-project-id.wikidata_slice.raw_seeds`
  UNION ALL
  -- Hop 1: Add connected entities (executives, industries, locations)
  SELECT statements.value AS id
  FROM `bigquery-public-data.wikipedia.wikidata`,
       UNNEST(statements) AS statements
  INNER JOIN recursive_expansion ON statements.subject = recursive_expansion.id
  WHERE statements.property IN (
    'P169',  -- Chief executive officer (to executives Q5)
    'P452',  -- Industry (to industries Q268592)
    'P159',  -- Headquarters location (to locations Q6256/Q515)
    'P355',  -- Subsidiary (to other companies)
    'P127'   -- Owned by (to investors/parent companies)
  )
    AND statements.value LIKE 'Q%'  -- Entity link
  UNION ALL
  -- Hop 2: One more level for depth (e.g., executive's education)
  SELECT statements.value AS id
  FROM `bigquery-public-data.wikipedia.wikidata`,
       UNNEST(statements) AS statements
  INNER JOIN recursive_expansion ON statements.subject = recursive_expansion.id
  WHERE statements.property IN (
    'P69',   -- Educated at (for executives to universities)
    'P279'   -- Subclass of (for industry hierarchies)
  )
    AND statements.value LIKE 'Q%'
)
-- Final: Get full details for all unique IDs, up to 1M
SELECT DISTINCT 
  w.id,
  CAST(SUBSTR(w.id, 2) AS INT64) AS numeric_id,
  (SELECT value FROM UNNEST(w.labels) WHERE language = 'en' LIMIT 1) AS label,
  (SELECT value FROM UNNEST(w.descriptions) WHERE language = 'en' LIMIT 1) AS description,
  ARRAY_AGG(DISTINCT io) AS instance_of,
  (SELECT AS STRUCT
     (SELECT value FROM UNNEST(w.statements) WHERE property = 'P571' LIMIT 1) AS founding_date,  -- For companies
     (SELECT CAST(value AS FLOAT64) FROM UNNEST(w.statements) WHERE property = 'P2139' LIMIT 1) AS revenue,
     (SELECT value FROM UNNEST(w.statements) WHERE property = 'P1128' LIMIT 1) AS num_employees,
     (SELECT value FROM UNNEST(w.statements) WHERE property = 'P569' LIMIT 1) AS birth_date,  -- For executives
     (SELECT CAST(value AS FLOAT64) FROM UNNEST(w.statements) WHERE property = 'P2218' LIMIT 1) AS net_worth  -- For executives
   ) AS attributes  -- Struct for type_specific_attributes (convert to JSON in loader if needed)
FROM `bigquery-public-data.wikipedia.wikidata` w
INNER JOIN recursive_expansion ON w.id = recursive_expansion.id
WHERE w.type = 'item'
GROUP BY w.id, numeric_id, label, description
LIMIT 1000000;
```

**Verification:**
```sql
SELECT COUNT(*) FROM `your-project-id.wikidata_slice.raw_entities`;
-- Expected: up to 1M entities
```

## Step 4: Extract Edges (Only Within the Subset)

Pull relationships as edges, ensuring no dangling references.

```sql
CREATE OR REPLACE TABLE `your-project-id.wikidata_slice.raw_edges` AS
SELECT 
  statements.subject AS from_id,
  CAST(SUBSTR(statements.subject, 2) AS INT64) AS from_numeric_id,
  statements.value AS to_id,
  CAST(SUBSTR(statements.value, 2) AS INT64) AS to_numeric_id,
  statements.property AS edge_type,  -- e.g., 'P169'
  (SELECT (SELECT value FROM UNNEST(labels) WHERE language = 'en' LIMIT 1) 
   FROM `bigquery-public-data.wikipedia.wikidata` WHERE id = statements.property LIMIT 1) AS edge_label  -- e.g., 'chief executive officer'
FROM `bigquery-public-data.wikipedia.wikidata`,
     UNNEST(statements) AS statements
WHERE statements.property IN (
  'P169',  -- CEO (company -> executive)
  'P452',  -- Industry (company -> industry)
  'P159',  -- Headquarters (company -> location)
  'P355',  -- Subsidiary (company -> company)
  'P127',  -- Owned by (company -> company/investor)
  'P69'    -- Educated at (executive -> university; add university entities if needed)
)
  AND statements.value LIKE 'Q%'
  AND statements.subject IN (SELECT id FROM `your-project-id.wikidata_slice.raw_entities`)
  AND statements.value IN (SELECT id FROM `your-project-id.wikidata_slice.raw_entities`);  -- Ensures closed subset
```

**Verification:**
```sql
SELECT COUNT(*) FROM `your-project-id.wikidata_slice.raw_edges`;
-- Expected: 1M+ edges if dense
```

## Step 5: Create Views for Ingestion Pipeline

These match `v_unified_entities` and `v_extracted_edges` in your config.

```sql
CREATE OR REPLACE VIEW `your-project-id.wikidata_slice.v_unified_entities` AS
SELECT 
  id,
  numeric_id,
  label,
  description,
  instance_of,
  TO_JSON(attributes) AS type_specific_attributes  -- Convert struct to JSON for Spanner
FROM `your-project-id.wikidata_slice.raw_entities`;

CREATE OR REPLACE VIEW `your-project-id.wikidata_slice.v_extracted_edges` AS
SELECT * FROM `your-project-id.wikidata_slice.raw_edges`;
```

## Schema Details

### Entity Types
- **Companies**: Q783794 (company), Q4830453 (business)
- **Executives**: Q5 (human)
- **Industries**: Q268592 (industry)
- **Locations**: Q6256 (country), Q515 (city)

### Relationship Types
- **P169**: Chief executive officer (company → executive)
- **P452**: Industry (company → industry)
- **P159**: Headquarters location (company → location)
- **P355**: Subsidiary (company → company)
- **P127**: Owned by (company → company/investor)
- **P69**: Educated at (executive → university)

### Data Attributes
- **Companies**: founding_date (P571), revenue (P2139), num_employees (P1128)
- **Executives**: birth_date (P569), net_worth (P2218)

## Verification and Testing

### Data Integrity Checks
```sql
-- Check for dangling edges
SELECT COUNT(*) 
FROM `your-project-id.wikidata_slice.raw_edges` e
LEFT JOIN `your-project-id.wikidata_slice.raw_entities` f ON e.from_id = f.id
LEFT JOIN `your-project-id.wikidata_slice.raw_entities` t ON e.to_id = t.id
WHERE f.id IS NULL OR t.id IS NULL;

-- Should return 0

-- Check entity type distribution
SELECT 
  io AS entity_type,
  COUNT(*) as count
FROM `your-project-id.wikidata_slice.raw_entities`,
     UNNEST(instance_of) as io
GROUP BY io
ORDER BY count DESC
LIMIT 10;
```

### Performance Optimization
- Adjust seed size by modifying `RAND() < 0.001` threshold
- Add country filters: `AND ARRAY_CONTAINS(statements, STRUCT('P159', 'Q30'))` for USA companies
- Limit recursion depth by removing the second UNION ALL if needed

## Next Steps

1. **Update Configuration**: Modify `config/wikidata_poc.yaml` to use the new dataset
   ```yaml
   bigquery:
     project_id: your-project-id
     dataset: wikidata_slice
     entities_view: v_unified_entities
     edges_view: v_extracted_edges
   ```

2. **Proceed with Ingestion**: Use Task 12 to execute the ingestion into Spanner

3. **Monitor Costs**: BigQuery queries are cheap, but monitor usage for large datasets

## Troubleshooting

- **Query Timeout**: Reduce seed size or recursion depth
- **Memory Issues**: Add more specific filters (e.g., country, date ranges)
- **Schema Issues**: Verify Wikidata property IDs match your requirements
- **Connectivity Issues**: Ensure all edges have valid endpoints in the subset

## Key Assumptions

- English labels preferred (`language = 'en'`)
- Entity IDs follow Wikidata format (Q-prefixed)
- Relationships are bidirectional for graph purposes
- Data freshness depends on BigQuery public dataset updates
