#!/bin/bash

cd /mnt/workspace/python-mcp-server-template

echo "=== Starting Build Test ===" 
chmod +x build.sh
./build.sh 2>&1 | tee test_output/build_log.txt
echo "Build exit code: $?" >> test_output/build_log.txt
echo "=== Build Test Complete ===" 
