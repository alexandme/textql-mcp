"""CLI tool for Wikidata ingestion into Google Cloud Spanner.

This module provides a command-line interface to orchestrate the data loading
process using the UnifiedLoader class.
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from .unified_loader import UnifiedLoader


# Configure logging
def configure_logging(verbose: bool = False):
    """Configure logging for the CLI."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    return logging.getLogger(__name__)


@click.command(name="ingest-wikidata")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default="config/wikidata_poc.yaml",
    help="Path to the configuration file (default: config/wikidata_poc.yaml)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Run in dry-run mode without making actual database changes",
)
@click.option(
    "--limit",
    "-l",
    type=int,
    default=None,
    help="Limit the number of records to process (useful for testing)",
)
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Enable verbose logging"
)
def ingest_wikidata(
    config: Path, dry_run: bool, limit: Optional[int], verbose: bool
) -> None:
    """Ingest Wikidata entities and edges into Google Cloud Spanner.

    This command loads data from BigQuery views into Spanner using batch inserts.
    It supports dry-run mode for testing and can limit the number of records
    processed for development purposes.
    """
    logger = configure_logging(verbose)

    click.echo(f"{'='*60}")
    click.echo("Wikidata to Spanner Ingestion Tool")
    click.echo(f"{'='*60}")

    # Display configuration
    click.echo("\nConfiguration:")
    click.echo(f"  Config file: {config}")
    click.echo(f"  Dry run: {dry_run}")
    click.echo(f"  Limit: {limit if limit else 'No limit'}")
    click.echo(f"  Verbose: {verbose}")

    if dry_run:
        click.secho(
            "\n⚠️  Running in DRY-RUN mode - no data will be written to Spanner",
            fg="yellow",
        )

    click.echo("\n" + "-" * 60)

    try:
        # Initialize the loader
        click.echo("\n📚 Initializing UnifiedLoader...")
        loader = UnifiedLoader(str(config))
        click.secho("✓ Loader initialized successfully", fg="green")

        # Run the ingestion
        click.echo("\n🚀 Starting data ingestion...")
        if limit:
            click.echo(f"   Processing up to {limit} records per table")

        loader.run(dry_run=dry_run, limit=limit)

        click.echo("\n" + "-" * 60)
        click.secho("✓ Ingestion completed successfully!", fg="green")

    except FileNotFoundError as e:
        click.secho(f"\n❌ Configuration file not found: {e}", fg="red")
        logger.error(f"Configuration file error: {e}")
        sys.exit(1)
    except Exception as e:
        click.secho(f"\n❌ Error during ingestion: {e}", fg="red")
        logger.error(f"Ingestion error: {e}", exc_info=True)
        sys.exit(1)


@click.group()
def cli():
    """Wikidata to Spanner CLI tools."""
    pass


# Add the ingest command to the group
cli.add_command(ingest_wikidata, name="ingest")


if __name__ == "__main__":
    cli()
