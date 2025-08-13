#!/usr/bin/env python3
"""
MCP Server Entry Point
======================
🚀 Quick Start:
1. Configure your server: python quick_setup.py
2. Start your server: python mcp_server.py

Your server will automatically load configuration from config.py
and custom tools from tools/custom_tools.py
"""

if __name__ == "__main__":
    try:
        from mcp_server.server import start_server
        start_server()
    except ImportError as e:
        print(f"❌ Error importing server: {e}")
        print("💡 Make sure you've run 'python quick_setup.py' to configure your server")
        exit(1)
