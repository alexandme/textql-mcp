FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir mcp[cli]

# Copy the source code
COPY . .

# Install the package
RUN pip install -e .

# Expose the MCP server port
EXPOSE 8000

# Set the entrypoint
CMD ["python", "-m", "textql_mcp", "--host", "0.0.0.0", "--port", "8000"]
