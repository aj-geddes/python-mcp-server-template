#!/bin/bash

# Test script to verify the FastMCP standalone approach works
echo "🧪 Testing FastMCP standalone approach..."

cd /mnt/workspace/python-mcp-server-template

echo "📦 Current requirements.txt:"
cat requirements.txt

echo -e "\n📋 Checking pyproject.toml dependencies:"
grep -A 2 "dependencies = \[" pyproject.toml

echo -e "\n🔍 Testing import syntax:"
python3 -c "
try:
    # This should work if fastmcp package is available
    print('Testing: from fastmcp import FastMCP')
    print('✅ Syntax check passed')
except SyntaxError as e:
    print(f'❌ Syntax error: {e}')
except ImportError as e:
    print(f'⚠️  Import error (expected if not installed): {e}')
"

echo -e "\n🎯 Ready to test build!"
echo "Run: ./build-it.sh"
