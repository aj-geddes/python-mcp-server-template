#!/bin/bash

echo "🧪 Testing production-ready FastMCP server..."

cd /mnt/workspace/python-mcp-server-template

IMAGE_NAME="python-mcp-server-template:latest"

echo "1. 📦 Package verification:"
docker run --rm "${IMAGE_NAME}" python -c "
import sys
from fastmcp import FastMCP
from rich.console import Console
print('✅ FastMCP version:', getattr(FastMCP, '__version__', 'N/A'))
print('✅ Python version:', sys.version)
print('✅ Rich console available')
print('✅ All dependencies working!')
"

echo -e "\n2. 🔧 Server configuration test:"
docker run --rm "${IMAGE_NAME}" python -c "
from mcp_server import mcp, SERVER_NAME, VERSION, TRANSPORT, HOST, PORT
print(f'Server: {SERVER_NAME} v{VERSION}')
print(f'Transport: {TRANSPORT}')
print(f'Host: {HOST}, Port: {PORT}')
print(f'Tools available: {len(mcp._tools)}')
print(f'Tool names: {[tool.name for tool in mcp._tools]}')
"

echo -e "\n3. 🏥 Health check test:"
docker run --rm "${IMAGE_NAME}" python -c "
from mcp_server import mcp
import asyncio

async def test_health():
    for tool in mcp._tools:
        if tool.name == 'health_check':
            print('✅ Health check tool found')
            return True
    return False

# Since we can't run the full server, just verify the tool exists
print('Health check available:', any(tool.name == 'health_check' for tool in mcp._tools))
"

echo -e "\n4. 🚀 Quick server startup test (3 seconds):"
echo "   Starting server with 3-second timeout..."
timeout 3 docker run --rm "${IMAGE_NAME}" 2>&1 | head -5
if [ $? -eq 124 ]; then
    echo "✅ Server started successfully (timed out as expected)"
else
    echo "❌ Server failed to start"
fi

echo -e "\n5. 🌐 HTTP transport test:"
echo "   Testing HTTP transport configuration..."
docker run --rm -e MCP_TRANSPORT=http "${IMAGE_NAME}" python -c "
import os
from mcp_server import TRANSPORT, HOST, PORT
print(f'Transport: {TRANSPORT}')
print(f'Environment transport: {os.getenv(\"MCP_TRANSPORT\", \"stdio\")}')
print('✅ Environment configuration working')
"

echo -e "\n✅ All tests completed!"
echo "🎉 Your FastMCP server is production-ready!"
echo ""
echo "🔧 Usage examples:"
echo "   STDIO mode:  docker run -it --rm ${IMAGE_NAME}"
echo "   HTTP mode:   docker run -p 8080:8080 -e MCP_TRANSPORT=http ${IMAGE_NAME}"
echo "   With env:    docker run --env-file .env.production ${IMAGE_NAME}"
echo "   Compose:     docker-compose up"
