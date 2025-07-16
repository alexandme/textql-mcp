#!/usr/bin/env python3
"""
TextQL MCP Server with Google Spanner backend for Wikidata graph database.

This server provides natural language to GraphQL query capabilities for the
Wikidata entities and relationships stored in Google Spanner.
"""

import os
import sys
import argparse
import logging
import yaml
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Make sure textql_mcp is in the path
sys.path.insert(0, str(SCRIPT_DIR))

from textql_mcp.main_spanner import create_mcp_server_with_spanner  # noqa: E402
from textql_mcp.core.server import run_server  # noqa: E402
from textql_mcp.utils.ambiguity_detector import SimpleAmbiguityDetector  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("spanner_wikidata_server")


def load_config(config_path: str = None) -> dict:
    """Load configuration from YAML file."""
    if config_path is None:
        # Default to config/wikidata_poc.yaml relative to script directory
        config_path = SCRIPT_DIR / "config" / "wikidata_poc.yaml"
    else:
        config_path = Path(config_path)
        # If the path is relative, make it relative to the script directory
        if not config_path.is_absolute():
            config_path = SCRIPT_DIR / config_path

    logger.debug(f"Loading configuration from: {config_path}")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def main():
    """Main entry point for the Wikidata Spanner MCP server."""
    parser = argparse.ArgumentParser(
        description="TextQL MCP Server for Wikidata Graph in Spanner"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/wikidata_poc.yaml",
        help="Path to configuration file (default: config/wikidata_poc.yaml)",
    )

    parser.add_argument(
        "--host",
        type=str,
        help="Host to bind to (overrides config)",
    )

    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind to (overrides config)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level",
    )

    args = parser.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    try:
        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)

        # Extract configuration values
        gcp_config = config["gcp"]
        server_config = config["server"]
        auth_config = config["auth"]

        # Get server host and port (command line overrides config)
        host = args.host or server_config["mcp"]["host"]
        port = args.port or server_config["mcp"]["port"]

        # Set up authentication
        service_account_path = auth_config["service_account_key"]
        if os.path.exists(service_account_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
            logger.info(f"Using service account key: {service_account_path}")
        else:
            logger.warning(f"Service account key not found: {service_account_path}")
            logger.warning("Falling back to Application Default Credentials")

        # Create MCP server with Spanner backend
        logger.info(
            f"Creating TextQL MCP Server with Spanner: "
            f"instance={gcp_config['spanner']['instance_id']}, "
            f"database={gcp_config['spanner']['database_id']}"
        )

        server = create_mcp_server_with_spanner(
            instance_id=gcp_config["spanner"]["instance_id"],
            database_id=gcp_config["spanner"]["database_id"],
            ambiguity_detector=SimpleAmbiguityDetector(),
            server_name=server_config["mcp"]["name"],
            spanner_project_id=gcp_config["project_id"],
            graph_name="wikidata_graph",
        )

        # Log server configuration
        logger.info("Server configuration:")
        logger.info(f"  Name: {server_config['mcp']['name']}")
        logger.info(f"  Host: {host}")
        logger.info(f"  Port: {port}")
        logger.info(f"  Spanner Instance: {gcp_config['spanner']['instance_id']}")
        logger.info(f"  Spanner Database: {gcp_config['spanner']['database_id']}")
        logger.info("  Graph Name: wikidata_graph")

        # Run server
        logger.info("Starting TextQL MCP Server")
        logger.info("Server is ready to accept connections")

        # Set environment variables for host and port if specified
        if host:
            os.environ["MCP_HOST"] = host
        if port:
            os.environ["MCP_PORT"] = str(port)

        run_server(server)

    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.error(
            "Make sure to install the Spanner dependencies with: "
            "pip install -r requirements-spanner.txt"
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error creating or running server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
