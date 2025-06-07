#!/usr/bin/env python3
"""
Entry point for the MCP server template.
This file serves as the main entry point for running the server.
"""

from mcp_server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
