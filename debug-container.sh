#!/bin/bash

# Debug script to inspect the Docker container contents
echo "🔍 Debugging Docker container contents..."

cd /mnt/workspace/python-mcp-server-template

IMAGE_NAME="python-mcp-server-template:latest"

echo "📦 Checking Python path in container:"
docker run --rm "${IMAGE_NAME}" which python

echo -e "\n🐍 Checking Python version:"
docker run --rm "${IMAGE_NAME}" python --version

echo -e "\n📋 Checking installed packages:"
docker run --rm "${IMAGE_NAME}" python -m pip list

echo -e "\n🔍 Checking if .venv exists:"
docker run --rm "${IMAGE_NAME}" ls -la /workspace/.venv/

echo -e "\n📁 Checking .venv/bin contents:"
docker run --rm "${IMAGE_NAME}" ls -la /workspace/.venv/bin/

echo -e "\n🎯 Checking PATH variable:"
docker run --rm "${IMAGE_NAME}" echo \$PATH

echo -e "\n🔧 Checking uv pip list:"
docker run --rm "${IMAGE_NAME}" .venv/bin/python -m pip list

echo -e "\n⚡ Testing fastmcp import with full path:"
docker run --rm "${IMAGE_NAME}" .venv/bin/python -c "import fastmcp; print('FastMCP found!')"
