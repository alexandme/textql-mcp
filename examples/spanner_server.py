"""
Example of running the TextQL MCP Server with Google Spanner integration.

This example demonstrates how to create and run an MCP server that uses
Google Spanner as the backend database for query execution.
"""

import os
import sys
import argparse
import logging

# Make sure textql_mcp is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from textql_mcp.main import create_mcp_server_with_spanner, run_server
from textql_mcp.utils.schema_provider import StringSchemaProvider
from textql_mcp.utils.ambiguity_detector import SimpleAmbiguityDetector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("spanner_example")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="TextQL MCP Server with Google Spanner")

    # Basic server configuration
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="TextQL-MCP-Spanner-Example",
        help="Name of the MCP server",
    )

    # Spanner configuration (required)
    parser.add_argument(
        "--instance-id",
        type=str,
        required=True,
        help="Google Spanner instance ID (required)",
    )
    parser.add_argument(
        "--database-id",
        type=str,
        required=True,
        help="Google Spanner database ID (required)",
    )
    parser.add_argument(
        "--project-id",
        type=str,
        help="Google Cloud project ID (defaults to Application Default Credentials)",
    )

    # VertexAI configuration
    parser.add_argument(
        "--vertex-project-id",
        type=str,
        help="Google Cloud project ID for VertexAI (defaults to Spanner project ID)",
    )
    parser.add_argument(
        "--vertex-location",
        type=str,
        default="us-central1",
        help="Google Cloud location for VertexAI (default: us-central1)",
    )
    parser.add_argument(
        "--vertex-model",
        type=str,
        default="gemini-pro",
        help="Model name for VertexAI (default: gemini-pro)",
    )

    return parser.parse_args()


def main():
    """Main entry point for the example."""
    # Parse command-line arguments
    args = parse_args()

    # Set up a custom schema provider (optional)
    # You could also implement a provider that fetches the schema from Spanner
    schema_provider = StringSchemaProvider("""
    type Query {
        # This is a placeholder schema
        # The actual schema would be derived from Spanner
        entity(id: ID!): Entity
        search(term: String!): [Entity]
    }

    type Entity {
        id: ID!
        name: String
        description: String
        properties: [Property]
        relationships: [Relationship]
    }

    type Property {
        name: String!
        value: String
    }

    type Relationship {
        type: String!
        target: Entity
    }
    """)

    try:
        # Create MCP server with Spanner backend
        logger.info(f"Creating TextQL MCP Server with Spanner: instance={args.instance_id}, database={args.database_id}")

        # Determine project IDs
        spanner_project_id = args.project_id
        llm_project_id = args.vertex_project_id or spanner_project_id

        server = create_mcp_server_with_spanner(
            instance_id=args.instance_id,
            database_id=args.database_id,
            llm_project_id=llm_project_id,
            llm_location=args.vertex_location,
            llm_model_name=args.vertex_model,
            schema_provider=schema_provider,
            ambiguity_detector=SimpleAmbiguityDetector(),
            server_name=args.name,
            spanner_project_id=spanner_project_id,
        )

        # Run server
        logger.info(f"Starting TextQL MCP Server on {args.host}:{args.port}")
        run_server(server, args.host, args.port)

    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.error("Make sure to install the Spanner dependencies with: pip install textql-mcp[spanner]")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error creating or running server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
