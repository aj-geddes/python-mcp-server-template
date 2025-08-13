#!/usr/bin/env python3
"""
Entry point for the MCP server template.
This file serves as the main entry point for running the server.
"""

import asyncio

from mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
