#!/bin/bash

cd /mnt/workspace/python-mcp-server-template

echo "🐳 Starting Docker build test..."
echo "This will build the image: python-mcp-server-template:test"
echo ""

# Make script executable and run
chmod +x test_build_only.sh
./test_build_only.sh

echo ""
echo "📋 To check the results, I can read the output or you can tell me what happened!"
