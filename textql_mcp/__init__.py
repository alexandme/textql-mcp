"""
TextQL MCP Server - A standalone library for creating an MCP server that translates
natural language to Graph Query Language (GQL).
"""

from .core.server import (
    create_mcp_server,
    SchemaProvider,
    QueryExecutor,
    AmbiguityDetector,
)
from .main import create_server, create_simple_server, run_server

__version__ = "0.1.0"

__all__ = [
    "create_mcp_server",
    "create_server",
    "create_simple_server",
    "run_server",
    "SchemaProvider",
    "QueryExecutor",
    "AmbiguityDetector",
]
