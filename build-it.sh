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
if docker run --rm "${FULL_IMAGE_NAME}" python -c "from fastmcp import FastMCP; print('FastMCP imported successfully')"; then
    echo "✅ Container test passed!"
else
    echo "❌ Container test failed!"
    exit 1
fi

echo "🎉 Build and test completed successfully!"
echo "💡 To run the server: docker run -it --rm ${FULL_IMAGE_NAME}"
