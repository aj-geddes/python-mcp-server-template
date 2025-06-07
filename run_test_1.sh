#!/bin/bash

cd /mnt/workspace/python-mcp-server-template

echo "=== Starting Docker Build Test ===" 
chmod +x test_build_only.sh
./test_build_only.sh 2>&1 | tee test_output/build_only_log.txt
echo "Build test complete - check test_output/build_only_log.txt for results"
