#!/bin/bash

# Comprehensive Docker container debugging script
echo "🔍 Debugging FastMCP Docker container..."

cd /mnt/workspace/python-mcp-server-template

IMAGE_NAME="python-mcp-server-template:latest"

echo "1. 📂 Container file system inspection:"
echo "   Checking workspace contents:"
docker run --rm "${IMAGE_NAME}" ls -la /workspace/

echo -e "\n   Checking if .venv exists:"
docker run --rm "${IMAGE_NAME}" ls -la /workspace/.venv/

echo -e "\n   Checking .venv/bin contents:"
docker run --rm "${IMAGE_NAME}" ls -la /workspace/.venv/bin/ 2>/dev/null || echo "   ❌ .venv/bin not found"

echo -e "\n   Checking .venv/lib contents:"
docker run --rm "${IMAGE_NAME}" ls -la /workspace/.venv/lib/ 2>/dev/null || echo "   ❌ .venv/lib not found"

echo -e "\n2. 🐍 Python environment inspection:"
echo "   Python version:"
docker run --rm "${IMAGE_NAME}" python --version

echo -e "\n   Python executable location:"
docker run --rm "${IMAGE_NAME}" which python

echo -e "\n   Python path:"
docker run --rm "${IMAGE_NAME}" python -c "import sys; print('\\n'.join(sys.path))"

echo -e "\n   Python site-packages:"
docker run --rm "${IMAGE_NAME}" python -c "import site; print(site.getsitepackages())"

echo -e "\n3. 📦 Package installation verification:"
echo "   UV version:"
docker run --rm "${IMAGE_NAME}" uv --version 2>/dev/null || echo "   ❌ UV not found"

echo -e "\n   UV pip list:"
docker run --rm "${IMAGE_NAME}" uv pip list 2>/dev/null || echo "   ❌ UV pip list failed"

echo -e "\n   Standard pip list:"
docker run --rm "${IMAGE_NAME}" pip list 2>/dev/null || echo "   ❌ pip list failed"

echo -e "\n   Python -m pip list:"
docker run --rm "${IMAGE_NAME}" python -m pip list

echo -e "\n4. 🎯 FastMCP specific checks:"
echo "   Direct fastmcp import test:"
docker run --rm "${IMAGE_NAME}" python -c "import fastmcp" 2>&1 || echo "   ❌ FastMCP import failed"

echo -e "\n   Check if fastmcp is in site-packages:"
docker run --rm "${IMAGE_NAME}" python -c "import pkg_resources; print([p.project_name for p in pkg_resources.working_set if 'fastmcp' in p.project_name.lower()])"

echo -e "\n   Find fastmcp files:"
docker run --rm "${IMAGE_NAME}" find /workspace -name "*fastmcp*" 2>/dev/null || echo "   ❌ No fastmcp files found in workspace"

echo -e "\n5. 🔧 Environment variables:"
docker run --rm "${IMAGE_NAME}" env | grep -E "(PATH|PYTHON|UV|MCP)" | sort

echo -e "\n6. 📋 Requirements file content:"
echo "   requirements.txt:"
docker run --rm "${IMAGE_NAME}" cat /workspace/requirements.txt

echo -e "\n7. 🧪 Manual installation test:"
echo "   Testing manual fastmcp installation:"
docker run --rm "${IMAGE_NAME}" pip install fastmcp 2>&1 | head -10

echo -e "\n✅ Debug complete!"
