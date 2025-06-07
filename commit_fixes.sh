#!/bin/bash
# Git commit script for formatting fixes

cd /mnt/workspace/python-mcp-server-template

echo "=== Current Git Status ==="
git status

echo -e "\n=== Adding modified files ==="
git add tests/test_server.py
git add tests/test_mcp_server.py  
git add examples.py

echo -e "\n=== Checking what will be committed ==="
git diff --cached --name-only

echo -e "\n=== Committing changes ==="
git commit -m "Fix Black code formatting issues

- Fix spacing and blank lines in tests/test_server.py
- Rewrite tests/test_mcp_server.py with proper Black formatting
- Apply Black formatting standards to examples.py
- Remove trailing whitespace across all files
- Add proper function parameter spacing and trailing commas
- Ensure compliance with 88-character line length

Resolves GitHub Actions CI formatting check failures.
Closes Black formatting violations found in lint workflow."

echo -e "\n=== Commit completed ==="
git log --oneline -n 3
