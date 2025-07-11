-- =====================================================================
-- Wikidata Graph Database Schema for Google Cloud Spanner
-- =====================================================================
-- 
-- This DDL file contains the complete schema for the Wikidata graph
-- database implementation in Google Cloud Spanner.
--
-- Design Decisions:
-- - Uses a unified vertex table (entities) and edge table (edges)
-- - Foreign key constraints ensure referential integrity
-- - JSON columns provide flexibility for entity-specific attributes
-- - Indexes on entity_type and edge_type for efficient filtering
-- - Composite primary key on edges prevents duplicate relationships
--
-- Usage:
-- 1. For initial creation: Run this file directly with gcloud
-- 2. For recreation: Uncomment the DROP statements below first
-- 3. Command: gcloud spanner databases ddl update wikidata-graph-db \
--    --instance=wikidata-graph-instance --ddl="$(cat docs/spanner_schema_ddl.sql)"
--
-- =====================================================================

-- Optional: Drop existing schema (uncomment for recreation)
-- WARNING: This will DELETE ALL DATA in these tables!
-- ---------------------------------------------------------------------
-- DROP INDEX idx_edges_type;
-- DROP INDEX idx_entities_type;
-- ALTER TABLE edges DROP FOREIGN KEY fk_edges_from_vid;
-- ALTER TABLE edges DROP FOREIGN KEY fk_edges_to_vid;
-- DROP TABLE edges;
-- DROP TABLE entities;

-- =====================================================================
-- ENTITIES TABLE (Vertices)
-- =====================================================================
-- Unified vertex table for all entity types (Company, Person, Location, etc.)
CREATE TABLE entities (
    vid STRING(36) NOT NULL,                    -- Vertex ID (e.g., 'Q123456')
    entity_type STRING(20) NOT NULL,            -- Type of entity
    label STRING(MAX),                          -- Human-readable label
    description STRING(MAX),                    -- Entity description
    confidence_score FLOAT64,                   -- Data quality score (0.0-1.0)
    type_specific_attributes JSON,              -- Flexible storage for entity-specific data
    raw_claims JSON,                            -- Original Wikidata claims
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
) PRIMARY KEY(vid);

-- =====================================================================
-- EDGES TABLE (Relationships)
-- =====================================================================
-- Unified edge table for all relationship types
CREATE TABLE edges (
    from_vid STRING(36) NOT NULL,               -- Source vertex ID
    to_vid STRING(36) NOT NULL,                 -- Target vertex ID
    edge_type STRING(50) NOT NULL,              -- Relationship type (e.g., 'EMPLOYED_BY')
    start_date DATE,                            -- Optional: When relationship started
    end_date DATE,                              -- Optional: When relationship ended
    role STRING(MAX),                           -- Optional: Role in the relationship
    rank STRING(20),                            -- Optional: Rank/priority of the relationship
    properties JSON,                            -- Flexible storage for edge-specific data
    created_at TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp = true),
    FOREIGN KEY (from_vid) REFERENCES entities (vid),
    FOREIGN KEY (to_vid) REFERENCES entities (vid),
) PRIMARY KEY (from_vid, to_vid, edge_type);

-- =====================================================================
-- INDEXES
-- =====================================================================
-- Index for efficient entity type filtering
CREATE INDEX idx_entities_type ON entities(entity_type);

-- Index for efficient edge type filtering
CREATE INDEX idx_edges_type ON edges(edge_type);

-- =====================================================================
-- NOTES
-- =====================================================================
-- 1. The schema uses foreign keys instead of interleaving because edges
--    reference two different entities, which is not supported by interleaving.
--
-- 2. JSON columns allow storing complex, nested data without requiring
--    schema changes for new entity types or relationship properties.
--
-- 3. The composite primary key on edges (from_vid, to_vid, edge_type)
--    ensures that there can only be one relationship of a specific type
--    between any two entities.
--
-- 4. Timestamps use allow_commit_timestamp for automatic timestamping
--    of when records are inserted.
--
-- 5. Common edge types include:
--    - EMPLOYED_BY, FOUNDER_OF, CEO_OF (for person-company relationships)
--    - SUBSIDIARY_OF, ACQUIRED_BY (for company-company relationships)
--    - LOCATED_IN, HEADQUARTERED_IN (for entity-location relationships)
--    - WORKED_AT, CITIZEN_OF, EDUCATED_AT, MEMBER_OF (from Wikidata)
