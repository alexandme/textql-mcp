### Using Standalone Library

```python
# Import the standalone library
from textql_mcp import create_simple_server, run_server
from textql_mcp.utils.schema_provider import FileSchemaProvider
from textql_mcp.utils.query_executor import LLMQueryExecutor
from mcp.client import Client
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp import StdioServerParameters

# Create a schema provider
schema_provider = FileSchemaProvider("path/to/schema.graphql")

# Create a query executor
def get_llm_chain(agent_type):
    # Your logic to get the LLM chain for the given agent type
    return your_llm_chain

query_executor = LLMQueryExecutor(get_llm_chain)

# Create and start the MCP server
server = create_simple_server(
    schema_file_path="path/to/schema.graphql",
    query_executor_callback=query_executor.execute_query,
    server_name="TextQL-MCP-Server"
)

# Run the server in a separate process
import subprocess
import time
server_process = subprocess.Popen(["python", "-m", "textql_mcp"])
time.sleep(2)  # Wait for the server to start

# Connect to the server using the client
async def connect_to_server():
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "textql_mcp"],
        env=None
    )
    
    async with stdio_client(server_params) as transport:
        async with ClientSession(*transport) as session:
            client = Client(session)
            
            # Use the client to call the tools
            result = await client.tools.process_natural_language_query(
                natural_language_query="Who is the CEO of Apple?",
                agent_type="CNE"
            )
            print(result)

# Run the client
import asyncio
asyncio.run(connect_to_server())
```

## Integration with Existing Schema and Query Functions

If you already have functions for retrieving schemas and executing queries, you can integrate them with the standalone library by implementing the corresponding protocols:

```python
from textql_mcp import SchemaProvider, QueryExecutor, create_server, run_server

# Implement schema provider using your existing function
class CustomSchemaProvider(SchemaProvider):
    def __init__(self, get_schema_function):
        self.get_schema_function = get_schema_function
    
    def get_schema(self, query, agent_type="default"):
        return self.get_schema_function(query, agent_type)

# Implement query executor using your existing function
class CustomQueryExecutor(QueryExecutor):
    def __init__(self, get_retrieval_chain):
        self.get_retrieval_chain = get_retrieval_chain
    
    def execute_query(self, query, agent_type="default"):
        chain = self.get_retrieval_chain(agent_type)
        result = chain.invoke(query)
        return result

# Create the server with your custom components
from * import get_relevant_schema_for_query
from * import get_retrieval_chain

schema_provider = CustomSchemaProvider(get_relevant_schema_for_query)
query_executor = CustomQueryExecutor(get_retrieval_chain)

server = create_server(
    schema_provider=schema_provider,
    query_executor=query_executor,
    server_name="TextQL-MCP-Server"
)

# Run the server
run_server(server)
```

## Docker Deployment

You can also deploy the standalone library as a Docker container:

```bash
# Build the Docker image
docker build -t textql-mcp .

# Run the container
docker run -p 8000:8000 textql-mcp
```

## Further Customization

The standalone library provides several extension points for customizing its behavior:

- `SchemaProvider`: For providing schema information
- `QueryExecutor`: For executing queries
- `AmbiguityDetector`: For detecting ambiguities in natural language queries

Refer to the documentation and examples for more details on how to implement these interfaces.
