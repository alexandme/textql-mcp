-- Unified edge table
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
    FOREIGN KEY (from_vid) REFERENCES entities (vid),
    FOREIGN KEY (to_vid) REFERENCES entities (vid),
) PRIMARY KEY (from_vid, to_vid, edge_type);

-- Index for entity type queries
CREATE INDEX idx_entities_type ON entities(entity_type);

-- Index for edge type queries
CREATE INDEX idx_edges_type ON edges(edge_type);
