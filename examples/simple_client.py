"""
Simple client example for the TextQL MCP Server.

This module demonstrates how to use the MCP client to connect to the
TextQL MCP Server and send GraphQL queries.
"""

import asyncio
import json
from typing import Dict, Any

from mcp.client import Client
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters


async def query_graph(
    client: Client, query: str, agent_type: str = "default"
) -> Dict[str, Any]:
    """
    Send a GraphQL query to the MCP server's query_graph tool.

    Args:
        client: The MCP client
        query: The GraphQL query to execute
        agent_type: The agent type identifier (default: "default")

    Returns:
        Dict containing the response
    """
    result = await client.tools.query_graph(
        gql_query=query, 
        agent_type=agent_type
    )
    return result


async def translate_to_gql(
    client: Client, natural_language_query: str, agent_type: str = "default"
) -> Dict[str, Any]:
    """
    Translate a natural language query to GraphQL using the MCP server.

    Args:
        client: The MCP client
        natural_language_query: The natural language query to translate
        agent_type: The agent type identifier (default: "default")

    Returns:
        Dict containing the translated GraphQL query
    """
    result = await client.tools.translate_to_gql(
        natural_language_query=natural_language_query, 
        agent_type=agent_type
    )
    return result


async def process_query(
    client: Client, natural_language_query: str, agent_type: str = "default"
) -> Dict[str, Any]:
    """
    Process a natural language query using the MCP server.

    Args:
        client: The MCP client
        natural_language_query: The natural language query to process
        agent_type: The agent type identifier (default: "default")

    Returns:
        Dict containing the query results
    """
    result = await client.tools.process_natural_language_query(
        natural_language_query=natural_language_query, 
        agent_type=agent_type
    )
    return result


async def check_health(client: Client) -> Dict[str, str]:
    """
    Check the health of the MCP server.

    Args:
        client: The MCP client

    Returns:
        Dict containing health status information
    """
    health = await client.resources.get("http://localhost/health")
    return health


async def get_schema(client: Client, agent_type: str = "default") -> Dict[str, Any]:
    """
    Get schema information from the MCP server.

    Args:
        client: The MCP client
        agent_type: The agent type identifier (default: "default")

    Returns:
        Dict containing schema information
    """
    schema = await client.resources.get(f"http://localhost/schema/{agent_type}")
    return schema


async def run_example_queries(client: Client) -> None:
    """
    Run example queries.

    Args:
        client: The MCP client
    """
    # Example queries
    nl_query = "Get me a list of all employees in the sales department"
    gql_query = "{ employees(department: \"Sales\") { id, name, position } }"

    # Get schema
    print("\nGetting schema...")
    schema = await get_schema(client)
    print(f"Schema info length: {len(schema.get('schema_info', ''))}")

    # Translate natural language to GraphQL
    print(f"\nTranslating query: {nl_query}")
    translation = await translate_to_gql(client, nl_query)
    print("\nTranslation result:")
    print(json.dumps(translation, indent=2))

    # Execute GraphQL query
    print(f"\nExecuting GraphQL query: {gql_query}")
    result = await query_graph(client, gql_query)
    print("\nQuery result:")
    print(json.dumps(result, indent=2))

    # Process natural language query end-to-end
    print(f"\nProcessing natural language query: {nl_query}")
    process_result = await process_query(client, nl_query)
    print("\nProcess result:")
    print(json.dumps(process_result, indent=2))


async def main() -> None:
    """Main function to demonstrate the MCP client usage."""
    # Server connection parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "textql_mcp"],
        env=None
    )

    try:
        # Create an MCP client using stdio transport
        async with stdio_client(server_params) as transport:
            # Create client session
            async with ClientSession(*transport) as session:
                # Create client
                client = Client(session)
                
                # Check server health
                health = await check_health(client)
                print(f"Server health: {health}")

                # Run example queries
                await run_example_queries(client)
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
