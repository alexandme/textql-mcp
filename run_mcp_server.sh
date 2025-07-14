#!/bin/bash

# Script to run the MCP server in the correct Conda environment

# Get the directory of this script (handles symlinks)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Path to the server script (absolute)
SERVER_SCRIPT="$SCRIPT_DIR/spanner_wikidata_server.py"

# Log file for debugging
LOG_FILE="$SCRIPT_DIR/mcp_server.log"

# Full path to Python executable in the conda environment
PYTHON_BIN="/Users/alexanderalyushin/miniconda3/envs/textql-mcp/bin/python"

echo "Starting MCP Server Wrapper at $(date)" >> "$LOG_FILE"
echo "Script directory: $SCRIPT_DIR" >> "$LOG_FILE"
echo "Server script: $SERVER_SCRIPT" >> "$LOG_FILE"
echo "Using Python: $PYTHON_BIN" >> "$LOG_FILE"

# Use the conda environment's Python directly
# This ensures all packages installed in the environment are available
"$PYTHON_BIN" "$SERVER_SCRIPT" "$@" 2>&1 | tee -a "$LOG_FILE"

echo "Server exited at $(date)" >> "$LOG_FILE"
