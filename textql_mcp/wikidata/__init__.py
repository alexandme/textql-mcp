"""
Wikidata to Spanner pipeline components for TextQL MCP.

This package contains utilities for loading Wikidata entities and relationships
from BigQuery into Google Cloud Spanner.
"""

from .unified_loader import UnifiedLoader

__all__ = ["UnifiedLoader"]
