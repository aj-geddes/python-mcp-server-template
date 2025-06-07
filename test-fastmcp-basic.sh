#!/bin/bash

echo "🔍 Testing FastMCP package availability..."

# Test if we can install fastmcp in a fresh container
echo "Testing fastmcp installation in fresh Python container..."

docker run --rm python:3.12-slim /bin/bash -c "
echo 'Installing fastmcp...'
pip install fastmcp
echo 'Testing import...'
python -c 'from fastmcp import FastMCP; print(\"FastMCP imported successfully!\")'
echo 'FastMCP version:'
python -c 'import fastmcp; print(getattr(fastmcp, \"__version__\", \"Version not available\"))'
"
