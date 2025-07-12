# Task 19: Build Connected Wikidata Subset in BigQuery

## Description
Create a connected subset of Wikidata focused on companies, their executives, industries, and related attributes using BigQuery's public Wikidata dataset. This subset will serve as the data source for ingestion into Spanner Graph.

## Acceptance Criteria
- [ ] BigQuery dataset `wikidata_slice` created with connected subset tables
- [ ] ~1M entities loaded with no dangling edges (all relationships have both endpoints)
- [ ] Views created matching ingestion pipeline format (`v_unified_entities`, `v_extracted_edges`)
- [ ] SQL queries tested and verified for data integrity
- [ ] Documentation updated with setup instructions and assumptions

## Technical Requirements
- **Dataset**: `your-project-id.wikidata_slice`
- **Entity Types**: Companies (Q783794, Q4830453), Executives (Q5), Industries (Q268592), Locations (Q6256, Q515)
- **Relationships**: CEO (P169), Industry (P452), Headquarters (P159), Subsidiary (P355), Owned by (P127), Educated at (P69)
- **Data Size**: ~1M total entities, ~100k seed companies
- **Connectivity**: 2-3 hop recursive expansion from seed companies

## Prerequisites
- Google Cloud project with BigQuery API enabled
- Access to `bigquery-public-data.wikipedia.wikidata`
- Sufficient BigQuery quota for ~1M row queries

## Implementation Steps
1. Create BigQuery dataset `wikidata_slice`
2. Execute seed entity creation query
3. Run recursive expansion to build connected subset
4. Extract edges ensuring no dangling references
5. Create views for ingestion pipeline
6. Verify data integrity and connectivity

## Verification Steps
- Count entities: `SELECT COUNT(*) FROM wikidata_slice.raw_entities`
- Count edges: `SELECT COUNT(*) FROM wikidata_slice.raw_edges`
- Check connectivity: Ensure all edges have valid endpoints
- Validate views: Confirm format matches ingestion requirements

## Next Steps
- Update `config/wikidata_poc.yaml` with new dataset references
- Proceed with Task 12: Execute Wikidata Ingestion into Spanner
