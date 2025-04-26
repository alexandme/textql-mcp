#!/bin/bash
# TextQL MCP Environment Setup Script

# Create conda environment
echo "Creating conda environment for TextQL..."
conda create -n textql python=3.10 -y

# Activate environment (note: this script should be sourced, not executed)
# To use this script: source setup_env.sh
echo "Activating environment..."
eval "$(conda shell.bash hook)"
conda activate textql

# Install required dependencies
echo "Installing dependencies..."
pip install langchain google-cloud-aiplatform neo4j streamlit pytest black ruff

echo "TextQL environment setup complete!"
echo "To activate this environment in the future, run: conda activate textql"
