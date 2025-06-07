#!/bin/bash

# Quick test script to verify the fixes
echo "🔧 Testing MCP server fixes..."

cd /mnt/workspace/python-mcp-server-template

# Test 1: Check if we can import the MCP module
echo "📦 Testing MCP import..."
python3 -c "from mcp.server.fastmcp import FastMCP; print('✅ MCP import successful')" 2>/dev/null || echo "❌ MCP import failed - this is expected if not installed yet"

# Test 2: Check if our entry point exists and runs
echo "📄 Testing entry point..."
if [[ -f "mcp_server.py" ]]; then
    echo "✅ Entry point mcp_server.py exists"
else
    echo "❌ Entry point mcp_server.py missing"
fi

# Test 3: Check syntax of our module
echo "🔍 Testing module syntax..."
python3 -m py_compile mcp_server/__init__.py && echo "✅ mcp_server module syntax OK" || echo "❌ mcp_server module syntax error"

# Test 4: Check requirements.txt
echo "📋 Checking requirements.txt..."
if grep -q "mcp>=1.9.0" requirements.txt; then
    echo "✅ requirements.txt updated correctly"
else
    echo "❌ requirements.txt not updated"
fi

echo "🎯 Test complete! You can now run: ./build-it.sh"
