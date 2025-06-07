#!/usr/bin/env python3
"""
Alternative MCP server template using official MCP SDK.
Use this version if you prefer the official SDK over standalone FastMCP.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Server configuration
SERVER_NAME = "template-server"
VERSION = "2.0.0"

# Initialize FastMCP server
mcp = FastMCP(SERVER_NAME, version=VERSION)


class MCPError(Exception):
    """Custom exception for MCP-related errors."""
    pass


def validate_path(path: str, base_path: str = "/workspace") -> Path:
    """Validate and resolve a path relative to the base path."""
    try:
        resolved = Path(base_path) / path
        resolved = resolved.resolve()

        # Ensure the path is within the base path
        if not str(resolved).startswith(str(Path(base_path).resolve())):
            raise MCPError(f"Path {path} is outside allowed directory")

        return resolved
    except Exception as e:
        raise MCPError(f"Invalid path {path}: {str(e)}")


async def run_command(
    command: List[str], cwd: Optional[str] = None, timeout: int = 30
) -> Dict[str, Any]:
    """Execute a command and return structured results."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )

        return {
            "command": " ".join(command),
            "directory": cwd or os.getcwd(),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "status": "✅ Success" if result.returncode == 0 else "❌ Failed",
        }
    except subprocess.TimeoutExpired:
        raise MCPError(
            f"Command timed out after {timeout} seconds: {' '.join(command)}"
        )
    except Exception as e:
        raise MCPError(f"Command execution failed: {str(e)}")


@mcp.tool()
async def echo(message: str) -> str:
    """
    Echo a message back to test the server.

    Args:
        message: The message to echo back

    Returns:
        The echoed message with a prefix
    """
    return f"Echo: {message}"


@mcp.tool()
async def list_files(directory: str = ".") -> Dict[str, Any]:
    """
    List files in a directory.

    Args:
        directory: Directory to list (default: current directory)

    Returns:
        Dictionary with file listing results
    """
    try:
        path = validate_path(directory)

        if not path.exists():
            raise MCPError(f"Directory {directory} does not exist")

        if not path.is_dir():
            raise MCPError(f"{directory} is not a directory")

        files = []
        dirs = []

        for item in sorted(path.iterdir()):
            if item.is_file():
                files.append(
                    {"name": item.name, "size": item.stat().st_size, "type": "file"}
                )
            elif item.is_dir():
                dirs.append({"name": item.name, "type": "directory"})

        return {
            "directory": str(path),
            "files": files,
            "directories": dirs,
            "total_files": len(files),
            "total_directories": len(dirs),
            "status": "✅ Success",
        }

    except MCPError:
        raise
    except Exception as e:
        raise MCPError(f"Failed to list directory: {str(e)}")


async def main():
    """Main entry point for the MCP server."""
    try:
        # Run the FastMCP server
        await mcp.run()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
