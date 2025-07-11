#!/usr/bin/env python3
"""
Test script to validate the wikidata_poc.yaml configuration file.
This script loads the YAML file and verifies all required keys are present.
"""

import os
import sys
import yaml
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def load_config(config_path: str) -> Dict[str, Any]:
    """Load and parse the YAML configuration file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate the configuration structure and required keys.
    Returns a list of validation errors, empty if valid.
    """
    errors = []

    # Check top-level required sections
    required_sections = [
        "gcp",
        "auth",
        "pipeline",
        "server",
        "monitoring",
        "data_quality",
    ]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: {section}")

    # Validate GCP settings
    if "gcp" in config:
        gcp = config["gcp"]
        if "project_id" not in gcp:
            errors.append("Missing gcp.project_id")

        # Validate Spanner settings
        if "spanner" not in gcp:
            errors.append("Missing gcp.spanner section")
        else:
            spanner = gcp["spanner"]
            if "instance_id" not in spanner:
                errors.append("Missing gcp.spanner.instance_id")
            if "database_id" not in spanner:
                errors.append("Missing gcp.spanner.database_id")

        # Validate BigQuery settings
        if "bigquery" not in gcp:
            errors.append("Missing gcp.bigquery section")
        else:
            bq = gcp["bigquery"]
            if "dataset_id" not in bq:
                errors.append("Missing gcp.bigquery.dataset_id")
            if "views" not in bq:
                errors.append("Missing gcp.bigquery.views")
            else:
                if "entities" not in bq["views"]:
                    errors.append("Missing gcp.bigquery.views.entities")
                if "edges" not in bq["views"]:
                    errors.append("Missing gcp.bigquery.views.edges")

        # Validate Vertex AI settings
        if "vertex_ai" not in gcp:
            errors.append("Missing gcp.vertex_ai section")
        else:
            vertex = gcp["vertex_ai"]
            if "location" not in vertex:
                errors.append("Missing gcp.vertex_ai.location")
            if "model" not in vertex:
                errors.append("Missing gcp.vertex_ai.model")

    # Validate authentication settings
    if "auth" in config:
        auth = config["auth"]
        if "service_account_key" not in auth:
            errors.append("Missing auth.service_account_key")

    # Validate pipeline settings
    if "pipeline" in config:
        pipeline = config["pipeline"]
        if "ingestion" not in pipeline:
            errors.append("Missing pipeline.ingestion section")
        else:
            ingestion = pipeline["ingestion"]
            if "batch_size" not in ingestion:
                errors.append("Missing pipeline.ingestion.batch_size")

    # Validate server settings
    if "server" in config:
        server = config["server"]
        if "mcp" not in server:
            errors.append("Missing server.mcp section")
        else:
            mcp = server["mcp"]
            if "port" not in mcp:
                errors.append("Missing server.mcp.port")

    return errors


def print_config_summary(config: Dict[str, Any]) -> None:
    """Print a summary of the loaded configuration."""
    print("\n=== Configuration Summary ===")
    print(f"Project ID: {config.get('gcp', {}).get('project_id', 'NOT SET')}")
    print(
        f"Spanner Instance: {config.get('gcp', {}).get('spanner', {}).get('instance_id', 'NOT SET')}"
    )
    print(
        f"Spanner Database: {config.get('gcp', {}).get('spanner', {}).get('database_id', 'NOT SET')}"
    )
    print(
        f"BigQuery Dataset: {config.get('gcp', {}).get('bigquery', {}).get('dataset_id', 'NOT SET')}"
    )
    print(
        f"Vertex AI Location: {config.get('gcp', {}).get('vertex_ai', {}).get('location', 'NOT SET')}"
    )
    print(
        f"Vertex AI Model: {config.get('gcp', {}).get('vertex_ai', {}).get('model', 'NOT SET')}"
    )
    print(
        f"Server Port: {config.get('server', {}).get('mcp', {}).get('port', 'NOT SET')}"
    )
    print(
        f"Batch Size: {config.get('pipeline', {}).get('ingestion', {}).get('batch_size', 'NOT SET')}"
    )
    print("============================\n")


def main():
    """Main function to validate the configuration."""
    # Determine the config file path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, "config", "wikidata_poc.yaml")

    print(f"Validating configuration file: {config_path}")

    # Check if file exists
    if not os.path.exists(config_path):
        print(f"ERROR: Configuration file not found at {config_path}")
        sys.exit(1)

    try:
        # Load the configuration
        config = load_config(config_path)
        print("✓ Configuration file loaded successfully")

        # Print configuration summary
        print_config_summary(config)

        # Validate the configuration
        errors = validate_config(config)

        if errors:
            print("✗ Validation failed with the following errors:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
        else:
            print("✓ All required configuration keys are present")
            print("✓ Configuration validation passed!")

            # Check for specific values from our tasks
            expected_values = {
                "gcp.project_id": "imperial-ally-429713-v1",
                "gcp.spanner.instance_id": "wikidata-graph-instance",
                "gcp.spanner.database_id": "wikidata-graph-db",
                "gcp.bigquery.dataset_id": "wikidata_slice",
                "gcp.vertex_ai.location": "us-central1",
            }

            print("\n=== Expected Values Check ===")
            all_correct = True
            for path, expected in expected_values.items():
                keys = path.split(".")
                value = config
                for key in keys:
                    value = value.get(key, {})

                if value == expected:
                    print(f"✓ {path} = {expected}")
                else:
                    print(f"✗ {path} = {value} (expected: {expected})")
                    all_correct = False

            if all_correct:
                print("\n✓ All values match expected configuration!")
            else:
                print("\n⚠ Some values don't match expected configuration")

    except yaml.YAMLError as e:
        print(f"ERROR: Failed to parse YAML file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
