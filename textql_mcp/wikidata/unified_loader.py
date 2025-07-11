import logging
import json
from typing import List, Dict
from google.cloud import bigquery
from google.cloud import spanner
import yaml
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedLoader:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.project_id = self.config["gcp"]["project_id"]
        self.spanner_instance = self.config["gcp"]["spanner"]["instance_id"]
        self.spanner_db = self.config["gcp"]["spanner"]["database_id"]
        self.bq_dataset = self.config["gcp"]["bigquery"]["dataset_id"]
        self.bq_entities_view = self.config["gcp"]["bigquery"]["views"]["entities"]
        self.bq_edges_view = self.config["gcp"]["bigquery"]["views"]["edges"]

        self.bq_client = bigquery.Client(project=self.project_id)
        self.spanner_client = spanner.Client(project=self.project_id)
        self.instance = self.spanner_client.instance(self.spanner_instance)
        self.database = self.instance.database(self.spanner_db)

        # Simple mapping for entity types (expand as needed)
        self.entity_type_map = {
            "Q5": "Human",
            "Q43229": "Organization",
            "Q515": "City",
            # Add more from Wikidata ontology
        }

    def _get_entity_type(self, instance_of_id: str) -> str:
        return self.entity_type_map.get(instance_of_id, "Unknown")

    def _transform_entity(self, row: Dict) -> List:
        vid = row["id"]
        entity_type = self._get_entity_type(row.get("primary_instance_of_id", ""))
        label = row.get("label")
        description = row.get("description")
        confidence_score = 1.0  # Default

        # Collect other fields into type_specific_attributes
        type_specific = {
            k: v
            for k, v in row.items()
            if k not in ["id", "primary_instance_of_id", "label", "description"]
        }
        type_specific_json = json.dumps(type_specific) if type_specific else None

        raw_claims_json = json.dumps(row.get("claims", {})) if "claims" in row else None

        return [
            vid,
            entity_type,
            label,
            description,
            confidence_score,
            type_specific_json,
            raw_claims_json,
            spanner.COMMIT_TIMESTAMP,
        ]

    def _transform_edge(self, row: Dict) -> List:
        from_vid = row["from_id"]
        to_vid = row["to_id"]
        edge_type = row.get("edge_label", "RELATED_TO").upper()
        start_date = row.get("start_date")
        end_date = row.get("end_date")
        role = row.get("role")
        rank = row.get("rank")
        properties_json = (
            json.dumps(row.get("properties", {})) if "properties" in row else None
        )

        return [
            from_vid,
            to_vid,
            edge_type,
            start_date,
            end_date,
            role,
            rank,
            properties_json,
            spanner.COMMIT_TIMESTAMP,
        ]

    def load_entities(
        self, batch_size: int = 1000, dry_run: bool = False, limit: int = None
    ) -> int:
        query = f"SELECT * FROM `{self.project_id}.{self.bq_dataset}.{self.bq_entities_view}`"
        if limit:
            query += f" LIMIT {limit}"
        job = self.bq_client.query(query)
        rows = list(job.result())

        loaded = 0
        for i in tqdm(range(0, len(rows), batch_size), desc="Loading entities"):
            batch = rows[i : i + batch_size]

            if dry_run:
                logger.info(f"Dry run: Would insert {len(batch)} entities")
            else:
                try:
                    with self.database.batch() as batch_tx:
                        for row in batch:
                            values = self._transform_entity(row)
                            batch_tx.insert_or_update(
                                "entities",
                                columns=[
                                    "vid",
                                    "entity_type",
                                    "label",
                                    "description",
                                    "confidence_score",
                                    "type_specific_attributes",
                                    "raw_claims",
                                    "created_at",
                                ],
                                values=[values],
                            )
                    loaded += len(batch)
                except Exception as e:
                    logger.error(f"Error inserting batch: {e}")

        return loaded

    def load_edges(
        self, batch_size: int = 1000, dry_run: bool = False, limit: int = None
    ) -> int:
        query = (
            f"SELECT * FROM `{self.project_id}.{self.bq_dataset}.{self.bq_edges_view}`"
        )
        if limit:
            query += f" LIMIT {limit}"
        job = self.bq_client.query(query)
        rows = list(job.result())

        loaded = 0
        for i in tqdm(range(0, len(rows), batch_size), desc="Loading edges"):
            batch = rows[i : i + batch_size]

            if dry_run:
                logger.info(f"Dry run: Would insert {len(batch)} edges")
            else:
                try:
                    with self.database.batch() as batch_tx:
                        for row in batch:
                            values = self._transform_edge(row)
                            batch_tx.insert_or_update(
                                "edges",
                                columns=[
                                    "from_vid",
                                    "to_vid",
                                    "edge_type",
                                    "start_date",
                                    "end_date",
                                    "role",
                                    "rank",
                                    "properties",
                                    "created_at",
                                ],
                                values=[values],
                            )
                    loaded += len(batch)
                except Exception as e:
                    logger.error(f"Error inserting batch: {e}")

        return loaded

    def run(self, dry_run: bool = False, limit: int = None):
        logger.info("Starting entity load")
        entities_loaded = self.load_entities(dry_run=dry_run, limit=limit)
        logger.info(f"Loaded {entities_loaded} entities")

        logger.info("Starting edge load")
        edges_loaded = self.load_edges(dry_run=dry_run, limit=limit)
        logger.info(f"Loaded {edges_loaded} edges")


if __name__ == "__main__":
    loader = UnifiedLoader("config/wikidata_poc.yaml")
    loader.run(dry_run=True, limit=100)  # Test with small dry run
