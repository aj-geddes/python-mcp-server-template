#!/bin/bash

echo "🧪 Testing different Docker approaches for FastMCP..."

cd /mnt/workspace/python-mcp-server-template

# Test 1: Current approach
echo "1. Testing current Dockerfile..."
docker build -t fastmcp-test-current -f Dockerfile . >/dev/null 2>&1
if docker run --rm fastmcp-test-current python -c "from fastmcp import FastMCP; print('✅ Current approach works!')" 2>/dev/null; then
    echo "✅ Current Dockerfile works!"
else
    echo "❌ Current Dockerfile failed"
fi

# Test 2: Fixed approach (no venv)
echo "2. Testing fixed Dockerfile (--system install)..."
docker build -t fastmcp-test-fixed -f Dockerfile.fixed . >/dev/null 2>&1
if docker run --rm fastmcp-test-fixed python -c "from fastmcp import FastMCP; print('✅ Fixed approach works!')" 2>/dev/null; then
    echo "✅ Fixed Dockerfile works!"
else
    echo "❌ Fixed Dockerfile failed"
fi

# Test 3: Alternative approach (standard Python + UV)
echo "3. Testing alternative Dockerfile (Python + UV)..."
docker build -t fastmcp-test-alt -f Dockerfile.alternative . >/dev/null 2>&1
if docker run --rm fastmcp-test-alt python -c "from fastmcp import FastMCP; print('✅ Alternative approach works!')" 2>/dev/null; then
    echo "✅ Alternative Dockerfile works!"
else
    echo "❌ Alternative Dockerfile failed"
fi

echo "🎯 Testing complete!"
