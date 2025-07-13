from google.cloud import spanner

# Connect to Spanner
client = spanner.Client(project="imperial-ally-429713-v1")
instance = client.instance("wikidata-graph-instance")
database = instance.database("wikidata-graph-db")

# Count entities
with database.snapshot() as snapshot:
    result = snapshot.execute_sql("SELECT COUNT(*) as count FROM entities")
    for row in result:
        print(f"Total entities loaded: {row[0]:,}")

# Count edges
with database.snapshot() as snapshot:
    result = snapshot.execute_sql("SELECT COUNT(*) as count FROM edges")
    for row in result:
        print(f"Total edges loaded: {row[0]:,}")

# Sample entities
print("\nSample entities:")
with database.snapshot() as snapshot:
    result = snapshot.execute_sql(
        """
        SELECT vid, entity_type, label 
        FROM entities 
        LIMIT 5
    """
    )
    for row in result:
        print(f"  {row[0]}: {row[1]} - {row[2]}")

# Sample edges
print("\nSample edges:")
with database.snapshot() as snapshot:
    result = snapshot.execute_sql(
        """
        SELECT from_vid, to_vid, edge_type 
        FROM edges 
        LIMIT 5
    """
    )
    for row in result:
        print(f"  {row[0]} -> {row[1]} ({row[2]})")

# Check connectivity
print("\nChecking connectivity:")
with database.snapshot() as snapshot:
    result = snapshot.execute_sql(
        """
        SELECT COUNT(DISTINCT e.from_vid) as connected_entities
        FROM edges e
        JOIN entities ent1 ON e.from_vid = ent1.vid
        JOIN entities ent2 ON e.to_vid = ent2.vid
    """
    )
    for row in result:
        print(f"  Entities with valid connections: {row[0]:,}")
