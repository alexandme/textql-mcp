#!/usr/bin/env python3
"""Check dependencies and test Spanner connectivity for TextQL MCP server."""

import sys
import os
from google.cloud import spanner
from google.auth import default


def check_imports():
    """Check if all required packages can be imported."""
    print("=== Checking Python Package Imports ===")

    packages = [
        ("mcp", "MCP"),
        ("google.cloud.spanner", "Google Cloud Spanner"),
        ("langchain_google_vertexai", "LangChain Vertex AI"),
        ("langchain_google_spanner", "LangChain Spanner"),
        ("toml", "TOML"),
        ("yaml", "YAML"),
    ]

    all_good = True
    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError as e:
            print(f"✗ {display_name}: {e}")
            all_good = False

    return all_good


def check_authentication():
    """Check Google Cloud authentication."""
    print("\n=== Checking Google Cloud Authentication ===")

    try:
        credentials, project = default()
        print(f"✓ Default credentials found")
        print(f"  Project: {project}")

        # Check if service account key is set
        sa_key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if sa_key:
            print(f"  Service Account Key: {sa_key}")
        else:
            print("  Using Application Default Credentials (ADC)")

        return True, project
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False, None


def check_spanner_connectivity(project_id):
    """Test connection to Spanner."""
    print("\n=== Testing Spanner Connectivity ===")

    instance_id = "wikidata-graph-instance"
    database_id = "wikidata-graph-db"

    try:
        # Create Spanner client
        spanner_client = spanner.Client(project=project_id)
        instance = spanner_client.instance(instance_id)
        database = instance.database(database_id)

        print(f"✓ Connected to Spanner")
        print(f"  Instance: {instance_id}")
        print(f"  Database: {database_id}")

        # Test query - entities
        with database.snapshot() as snapshot:
            results = snapshot.execute_sql("SELECT COUNT(*) as count FROM entities")
            for row in results:
                print(f"  Entities count: {row[0]:,}")

        # Test query - edges (separate snapshot)
        with database.snapshot() as snapshot:
            results = snapshot.execute_sql("SELECT COUNT(*) as count FROM edges")
            for row in results:
                print(f"  Edges count: {row[0]:,}")

        return True
    except Exception as e:
        print(f"✗ Spanner connection failed: {e}")
        return False


def main():
    """Run all checks."""
    print("TextQL MCP Server Dependency Check")
    print("==================================\n")

    # Check imports
    imports_ok = check_imports()

    # Check authentication
    auth_ok, project_id = check_authentication()

    # Check Spanner connectivity if auth is OK
    spanner_ok = False
    if auth_ok and project_id:
        spanner_ok = check_spanner_connectivity(project_id)

    # Summary
    print("\n=== Summary ===")
    if imports_ok and auth_ok and spanner_ok:
        print("✓ All checks passed! Server is ready to run.")
        return 0
    else:
        print("✗ Some checks failed. Please resolve the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
