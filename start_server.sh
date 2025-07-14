#!/bin/bash
# Startup script for TextQL MCP Server with Spanner Backend

set -e  # Exit on error

echo "=== TextQL MCP Server Startup Script ==="
echo

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "ERROR: conda is not installed or not in PATH"
    exit 1
fi

# Activate conda environment
echo "1. Activating conda environment: textql-mcp"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate textql-mcp

# Verify Python environment
echo "2. Python environment:"
which python
python --version
echo

# Check dependencies
echo "3. Checking critical dependencies..."
python -c "import mcp; print(f'  ✓ MCP version: {mcp.__version__}')" || echo "  ✗ MCP not installed"
python -c "import google.cloud.spanner; print('  ✓ Google Cloud Spanner installed')" || echo "  ✗ Spanner not installed"
python -c "import langchain_google_vertexai; print('  ✓ LangChain VertexAI installed')" || echo "  ✗ LangChain VertexAI not installed"
echo

# Check authentication
echo "4. Checking Google Cloud authentication..."
if [ -f "spanner-graph-sa-key.json" ]; then
    echo "  ✓ Service account key found: spanner-graph-sa-key.json"
    export GOOGLE_APPLICATION_CREDENTIALS="spanner-graph-sa-key.json"
else
    echo "  ⚠️  Service account key not found, using Application Default Credentials"
    gcloud auth application-default print-access-token > /dev/null 2>&1 && echo "  ✓ ADC configured" || echo "  ✗ ADC not configured"
fi
echo

# Start the server
echo "5. Starting TextQL MCP Server..."
echo "   Configuration: config/wikidata_poc.yaml"
echo "   Host: 0.0.0.0"
echo "   Port: 8000"
echo "   Project: imperial-ally-429713-v1"
echo "   Spanner Instance: wikidata-graph-instance"
echo "   Spanner Database: wikidata-graph-db"
echo
echo "Server starting..."
echo "============================================"
echo

# Run the server
python spanner_wikidata_server.py
