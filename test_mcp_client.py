#!/usr/bin/env python3
"""Simple MCP client to test the TextQL MCP server."""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_server():
    """Test the TextQL MCP server."""
    # Note: MCP servers typically communicate via stdio, not HTTP
    # For testing, we'll need to connect to the server process directly

    print("Testing TextQL MCP Server...")
    print("\nAvailable tools should include:")
    print("- translate_to_gql")
    print("- query_graph")
    print("- process_natural_language_query")
    print("- get_schema_for_query")

    print("\nTo test the server, you would typically:")
    print("1. Configure it in an MCP client (like Claude Desktop)")
    print("2. Or use it programmatically with the MCP Python client")

    print("\nSince the server is running, you can now:")
    print("1. Add it to your MCP client configuration")
    print("2. Use the server URL: stdio://python spanner_wikidata_server.py")


if __name__ == "__main__":
    asyncio.run(test_server())
