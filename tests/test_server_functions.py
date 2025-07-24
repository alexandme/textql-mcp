#!/usr/bin/env python3
"""
Test script to verify MCP server functionality with actual queries.
"""

import asyncio
import json
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@pytest.mark.asyncio
async def test_mcp_server():
    """Test the MCP server with various operations."""
    server_params = StdioServerParameters(
        command="python", args=["spanner_wikidata_server.py"], env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # List available tools
            print("Available tools:")
            tools_response = await session.list_tools()
            if hasattr(tools_response, "tools"):
                for tool in tools_response.tools:
                    print(f"  - {tool.name}: {tool.description}")
            else:
                print(f"  Tools response: {tools_response}")
            print()

            # Test 1: Get schema for query
            print("Test 1: Getting schema for query...")
            try:
                result = await session.call_tool(
                    "get_schema_for_query",
                    arguments={
                        "query": "Find all companies and their relationships",
                        "agent_type": "default",
                    },
                )
                # Extract the actual content from the MCP response
                if hasattr(result, "content"):
                    content = result.content[0].text if result.content else None
                    if content:
                        print(f"Schema result: {content[:500]}...")
                else:
                    print(f"Schema result: {result}")
                print()
            except Exception as e:
                print(f"Error getting schema: {e}")
                print()

            # Test 2: Execute a simple GraphQL query
            print("Test 2: Executing GraphQL query to count entities...")
            try:
                # Simple query to count entities - using 'Unknown' which we know exists
                gql_query = "SELECT COUNT(*) as total FROM entities WHERE entity_type = 'Unknown' LIMIT 10"

                result = await session.call_tool(
                    "query_graph",
                    arguments={"gql_query": gql_query, "agent_type": "default"},
                )
                # Extract the actual content from the MCP response
                if hasattr(result, "content"):
                    content = result.content[0].text if result.content else None
                    if content:
                        data = json.loads(content)
                        print(f"Query result: {json.dumps(data, indent=2)}")
                else:
                    print(f"Query result: {result}")
                print()
            except Exception as e:
                print(f"Error executing query: {e}")
                print()

            # Test 3: Execute a query to get sample entities
            print("Test 3: Getting sample entities...")
            try:
                gql_query = "SELECT vid, label, entity_type FROM entities LIMIT 5"

                result = await session.call_tool(
                    "query_graph",
                    arguments={"gql_query": gql_query, "agent_type": "default"},
                )
                # Extract the actual content from the MCP response
                if hasattr(result, "content"):
                    content = result.content[0].text if result.content else None
                    if content:
                        data = json.loads(content)
                        print(f"Sample entities: {json.dumps(data, indent=2)}")
                else:
                    print(f"Sample entities: {result}")
                print()
            except Exception as e:
                print(f"Error getting entities: {e}")
                print()

            # Test 4: Test relationships query
            print("Test 4: Testing relationships query...")
            try:
                # Query to find relationships - using correct column names
                gql_query = """
                SELECT 
                    e.from_vid,
                    e.to_vid,
                    e.edge_type,
                    s.label as source_label,
                    t.label as target_label
                FROM edges e
                JOIN entities s ON e.from_vid = s.vid
                JOIN entities t ON e.to_vid = t.vid
                WHERE e.edge_type = 'SUBCLASS_OF'
                LIMIT 5
                """

                result = await session.call_tool(
                    "query_graph",
                    arguments={"gql_query": gql_query.strip(), "agent_type": "default"},
                )
                # Extract the actual content from the MCP response
                if hasattr(result, "content"):
                    content = result.content[0].text if result.content else None
                    if content:
                        data = json.loads(content)
                        print(f"Relationships: {json.dumps(data, indent=2)}")
                else:
                    print(f"Relationships: {result}")
            except Exception as e:
                print(f"Error getting relationships: {e}")

            print("\nAll tests completed!")


if __name__ == "__main__":
    print("Testing TextQL MCP Server functionality...\n")
    asyncio.run(test_mcp_server())
