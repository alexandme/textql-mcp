---
id: task-4
title: Install Dependencies for TextQL MCP with Spanner Support
status: Done
assignee:
  - '@alexanderalyushin'
created_date: '2025-07-11'
updated_date: '2025-07-11'
labels: []
dependencies: []
---

## Description

Install required Python packages and dependencies to enable Spanner integration in the TextQL MCP project.

## Acceptance Criteria

- [x] Python 3.8+ is installed
- [x] TextQL MCP repository is cloned
- [x] Base package and Spanner extras are installed via pip
- [x] Installation is verified with pip list

## Implementation Plan

1. Create and switch to new Git branch spanner-graph-cline-task4\n2. Verify Python version meets requirements (3.8+ required, 3.11 preferred)\n3. Create conda environment textql-mcp with Python 3.11\n4. Activate the conda environment\n5. Install base dependencies from requirements.txt\n6. Install textql-mcp package in editable mode with Spanner extras\n7. Verify all packages are installed correctly\n8. Update task status and add implementation notes

## Implementation Notes

- Created and switched to new Git branch: spanner-graph-cline-task4
- Verified system has Python 3.10.14 which meets the minimum requirement
- Created a new conda environment textql-mcp with Python 3.11.13 using: `conda create -n textql-mcp python=3.11 -y`
- Successfully installed all base dependencies from requirements.txt including:
  - langchain>=0.3.24
  - google-cloud-aiplatform>=1.90.0
  - neo4j>=5.28.1
  - streamlit>=1.9.0
  - pytest>=8.3.5
  - black>=25.1.0
  - ruff>=0.11.7
- Installed textql-mcp package in editable mode with Spanner extras using: `pip install -e ".[spanner]"`
- Verified installation of Spanner-related packages:
  - google-auth 2.40.3
  - google-cloud-spanner 3.55.0
  - langchain-google-spanner 0.8.2
  - langchain-google-vertexai 2.0.27
  - textql-mcp 0.1.0 (editable installation)
- All dependencies installed successfully, ready for Spanner integration development
