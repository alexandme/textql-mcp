"""
TextQL MCP Server - A standalone library for creating an MCP server that translates
natural language to Graph Query Language (GQL).
"""

from .core.server import (
    create_mcp_server,
    run_server,
    SchemaProvider,
    QueryExecutor,
    AmbiguityDetector,
)
from .main_spanner import create_mcp_server_with_spanner

__version__ = "0.1.0"

__all__ = [
    "create_mcp_server",
    "create_mcp_server_with_spanner",
    "run_server",
    "SchemaProvider",
    "QueryExecutor",
    "AmbiguityDetector",
]
