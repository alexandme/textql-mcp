#!/usr/bin/env python3
"""
Test script for client-driven GQL workflow with TextQL MCP server.

This script simulates how a client would interact with the server:
1. Fetch schema information
2. Generate GQL queries (simulated - in reality the client's LLM would do this)
3. Execute GQL queries directly
4. Handle errors and iterate if needed
"""

import asyncio
import logging
from mcp import ClientSession
from mcp.client.stdio import stdio_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_client_workflow():
    """Test the client-driven workflow."""

    # Start the MCP server as a subprocess
    server_command = ["python", "spanner_wikidata_server.py"]

    async with stdio_client(server_command) as (read, write):
        async with ClientSession(read, write) as client:
            logger.info("Connected to TextQL MCP server")

            # Initialize the connection
            init_result = await client.initialize()
            logger.info(f"Client initialized: {init_result}")

            # List available tools
            tools_result = await client.list_tools()
            logger.info(
                f"Available tools: {[tool.name for tool in tools_result.tools]}"
            )

            # Test 1: Fetch schema information
            logger.info("\n=== Test 1: Fetching schema ===")
            try:
                schema_result = await client.call_tool(
                    "get_schema_for_query",
                    arguments={
                        "query": "entities and relationships",
                        "agent_type": "default",
                    },
                )
                logger.info(
                    f"Schema info received: {len(schema_result.content[0].text) if schema_result.content else 0} characters"
                )

                # In a real client, the LLM would analyze this schema to generate GQL
                if schema_result.content:
                    schema_info = schema_result.content[0].text
                    logger.info(f"Schema preview: {schema_info[:200]}...")
                else:
                    logger.warning("No schema content received")

            except Exception as e:
                logger.error(f"Error fetching schema: {e}")

            # Test 2: Execute a simple GQL query (count entities)
            logger.info("\n=== Test 2: Count entities ===")
            count_gql = """
            MATCH (n:entities {entity_type: 'Company'}) 
            RETURN count(n) AS count
            """

            try:
                count_result = await client.call_tool(
                    "query_graph",
                    arguments={"gql_query": count_gql, "agent_type": "default"},
                )

                if count_result.get("error"):
                    logger.error(f"Query error: {count_result['error']}")
                    # In a real client, the LLM would analyze the error and regenerate the query
                else:
                    logger.info(
                        f"Query result: {count_result.get('result', 'No result')}"
                    )

            except Exception as e:
                logger.error(f"Error executing count query: {e}")

            # Test 3: Execute entity lookup query
            logger.info("\n=== Test 3: Find specific entities ===")
            entity_gql = """
            MATCH (n:entities)
            WHERE n.name LIKE '%Apple%'
            RETURN n.vid AS id, n.name AS name, n.entity_type AS type
            LIMIT 5
            """

            try:
                entity_result = await client.call_tool(
                    "query_graph",
                    arguments={"gql_query": entity_gql, "agent_type": "default"},
                )

                if entity_result.get("error"):
                    logger.error(f"Query error: {entity_result['error']}")
                else:
                    logger.info(
                        f"Query result: {entity_result.get('result', 'No result')}"
                    )

            except Exception as e:
                logger.error(f"Error executing entity query: {e}")

            # Test 4: Execute relationship query
            logger.info("\n=== Test 4: Find relationships ===")
            relationship_gql = """
            MATCH (source:entities)-[r:edges]->(target:entities)
            WHERE source.name LIKE '%Google%'
            RETURN source.name AS source, r.label AS relationship, target.name AS target
            LIMIT 5
            """

            try:
                rel_result = await client.call_tool(
                    "query_graph",
                    arguments={"gql_query": relationship_gql, "agent_type": "default"},
                )

                if rel_result.get("error"):
                    logger.error(f"Query error: {rel_result['error']}")

                    # Simulate client iteration - try with a simpler query
                    logger.info("Retrying with simpler query...")
                    simpler_gql = """
                    MATCH (s:entities {entity_type: 'Company'})-[r:edges]->(t:entities)
                    RETURN s.name, r.label, t.name
                    LIMIT 3
                    """

                    retry_result = await client.call_tool(
                        "query_graph",
                        arguments={"gql_query": simpler_gql, "agent_type": "default"},
                    )

                    if retry_result.get("error"):
                        logger.error(f"Retry error: {retry_result['error']}")
                    else:
                        logger.info(
                            f"Retry result: {retry_result.get('result', 'No result')}"
                        )
                else:
                    logger.info(
                        f"Query result: {rel_result.get('result', 'No result')}"
                    )

            except Exception as e:
                logger.error(f"Error executing relationship query: {e}")

            # Test 5: Test error handling with invalid GQL
            logger.info("\n=== Test 5: Error handling ===")
            invalid_gql = """
            MATCH (n:invalid_table)
            RETURN n
            """

            try:
                error_result = await client.call_tool(
                    "query_graph",
                    arguments={"gql_query": invalid_gql, "agent_type": "default"},
                )

                if error_result.get("error"):
                    logger.info(f"Expected error received: {error_result['error']}")
                    # Client would analyze this error and correct the query
                else:
                    logger.warning("No error returned for invalid query")

            except Exception as e:
                logger.error(f"Error executing invalid query: {e}")

            logger.info("\n=== Client-driven workflow test completed ===")


if __name__ == "__main__":
    asyncio.run(test_client_workflow())
