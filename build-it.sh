#!/bin/bash

# Build script for Python MCP Server Template
set -e

# Configuration
IMAGE_NAME="python-mcp-server-template"
VERSION=${1:-"latest"}
FULL_IMAGE_NAME="${IMAGE_NAME}:${VERSION}"

echo "🏗️  Building MCP Server Docker image..."
echo "Image: ${FULL_IMAGE_NAME}"

# Build the Docker image
docker build -t "${FULL_IMAGE_NAME}" .

echo "✅ Build completed successfully!"
echo "📦 Image: ${FULL_IMAGE_NAME}"

# Test the container
echo "🧪 Testing container startup..."
echo "1. Testing FastMCP import..."
if docker run --rm "${FULL_IMAGE_NAME}" python -c "from fastmcp import FastMCP; print('FastMCP imported successfully')"; then
    echo "✅ FastMCP import test passed!"
else
    echo "❌ FastMCP import test failed!"
    exit 1
fi

echo "2. Testing server initialization..."
if timeout 10 docker run --rm "${FULL_IMAGE_NAME}" python -c "from mcp_server import mcp; print('MCP server initialized successfully')"; then
    echo "✅ Server initialization test passed!"
else
    echo "❌ Server initialization test failed!"
    exit 1
fi

echo "3. Testing health check tool..."
if docker run --rm "${FULL_IMAGE_NAME}" python -c "from mcp_server import mcp; import asyncio; print('Health check tool available:', 'health_check' in [tool.name for tool in mcp._tools])"; then
    echo "✅ Health check tool test passed!"
else
    echo "❌ Health check tool test failed!"
    exit 1
fi

echo "🎉 Build and test completed successfully!"
echo "💡 To run the server: docker run -it --rm ${FULL_IMAGE_NAME}"
