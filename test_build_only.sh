#!/bin/bash

cd /mnt/workspace/python-mcp-server-template

echo "=== Testing Docker Build Only ==="
echo "Building docker image..."
echo "Start time: $(date)"

# Build with verbose output to see what's happening
docker build -t python-mcp-server-template:test . 2>&1

BUILD_EXIT_CODE=$?

echo ""
echo "=== Build Results ==="
echo "Build exit code: $BUILD_EXIT_CODE"
echo "End time: $(date)"

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ Docker build completed successfully!"
    
    # Show image info
    echo ""
    echo "=== Image Information ==="
    docker images python-mcp-server-template:test
    
    echo ""
    echo "=== Image Size ==="
    docker images python-mcp-server-template:test --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
else
    echo "❌ Docker build failed with exit code: $BUILD_EXIT_CODE"
fi

echo "=== Build Test Complete ==="
