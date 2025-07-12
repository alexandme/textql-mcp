# BigQuery Wikidata Connected Subset Creation

## Overview
This document describes the creation of a connected Wikidata subset in BigQuery that addresses the connectivity issues found in random sampling approaches. The solution builds a graph-focused subset centered around companies and their relationships.

## Problem Statement
The initial approach (task-5) used a random sample of 50k entities which resulted in:
- Only ~5% connectivity between entities
- Most edges pointing to entities outside the sample
- A highly disconnected graph unsuitable for demonstrating graph database capabilities

## Solution Approach
Instead of random sampling, we built a connected subset by:
1. Starting with diverse entity types (companies, people, educational institutions, locations, industries)
2. Selecting entities that have known relationships with each other
3. Ensuring all edges have both endpoints within our entity set

## Implementation Details

### Dataset
- **Project**: `imperial-ally-429713-v1`
- **Dataset**: `wikidata_slice`
- **Tables**:
  - `raw_entities`: 1,000,000 entities
  - `raw_edges`: 636,556 edges
  - `v_unified_entities`: View for entity ingestion
  - `v_extracted_edges`: View for edge ingestion

### Entity Categories
1. **Companies/Organizations** (~800k limit):
   - Companies (Q783794)
   - Businesses (Q4830453)
   - Organizations (Q891723, Q43229)
   - Non-profits (Q163740)
   - Private companies (Q15265221)
   - Enterprises (Q6881511)
   - Political organizations (Q1048835)
   - Various specialized companies

2. **People** (~500k limit):
   - Humans (Q5) with English labels

3. **Educational Institutions** (~100k limit):
   - Universities (Q3918)
   - Schools (Q3914)
   - Educational institutions (Q2385804)
   - Research institutes (Q31855)

4. **Locations** (~150k limit):
   - Countries (Q6256)
   - Cities (Q515)
   - States (Q35657)
   - Administrative units

5. **Industries/Occupations** (~150k limit):
   - Industries (Q268592)
   - Professions (Q28640)
   - Occupations (Q12737077)
   - Academic disciplines

### Relationship Types
- Industry (P452)
- Country (P17)
- Member of (P463)
- Educated at (P69)
- Worked at (P108)
- Country of citizenship (P27)
- Occupation (P106)
- Place of birth (P19)
- Subclass of (P279)
- Instance of (P31)

### Results
- **Total Entities**: 1,000,000 (exactly)
- **Total Edges**: 636,556
- **Connectivity**: ~43.79% of entities have at least one edge
- **Average Degree**: ~1.28 edges per entity
- **Data Integrity**: 0 dangling edges (all edges have valid endpoints)

## Query Examples

### Entity Creation Query
```sql
CREATE OR REPLACE TABLE `imperial-ally-429713-v1.wikidata_slice.raw_entities` AS
WITH 
-- Get ALL companies/organizations
all_companies AS (
  SELECT DISTINCT w.id, w.numeric_id
  FROM `bigquery-public-data.wikipedia.wikidata` w
  CROSS JOIN UNNEST(w.instance_of) AS io
  WHERE w.type = 'item' 
  AND io.numeric_id IN (783794, 4830453, 891723, 43229, 163740, 15265221, 6881511, 1048835, 7094, 11032, 1002697, 732577)
  AND w.en_label IS NOT NULL
  LIMIT 800000
),
-- Similar CTEs for other entity types...
```

### Edge Creation Query
```sql
CREATE OR REPLACE TABLE `imperial-ally-429713-v1.wikidata_slice.raw_edges` AS
WITH entity_ids AS (
  SELECT id, numeric_id FROM `imperial-ally-429713-v1.wikidata_slice.raw_entities`
)
SELECT * FROM (
  -- Various relationship types with INNER JOINs to ensure both endpoints exist
  ...
)
```

## Benefits Over Random Sampling
1. **Higher Connectivity**: 43.79% vs 5% in random sample
2. **Meaningful Relationships**: Entities are related through real-world connections
3. **No Dangling Edges**: All relationships have both endpoints in the dataset
4. **Diverse Entity Types**: Covers multiple domains for richer graph analysis
5. **Scalable Approach**: Can be expanded by adjusting category limits

## Usage
The created views (`v_unified_entities` and `v_extracted_edges`) match the format expected by the Wikidata ingestion pipeline, allowing seamless integration with the existing Spanner ingestion tools.
