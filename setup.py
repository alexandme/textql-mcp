"""
Setup file for textql-mcp-server.
"""

from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = [line for line in f.read().splitlines() if not line.startswith('#')]

# Read Spanner-specific requirements
try:
    with open("requirements-spanner.txt") as f:
        spanner_requirements = [line for line in f.read().splitlines() if not line.startswith('#')]
except FileNotFoundError:
    spanner_requirements = [
        "google-auth",
        "google-cloud-spanner",
        "langchain-google-spanner>=0.0.1",
        "langchain-google-vertexai>=0.1.0",
    ]

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="textql-mcp",
    version="0.1.0",
    author="Sasha Alyushin",
    author_email="sasha@micra.io",
    description="An MCP server for translating natural language to `*` Query Language (`*`QL)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexandme/textql-mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache 2.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "spanner": spanner_requirements,
    },
)
