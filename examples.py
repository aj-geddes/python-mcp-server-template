#!/usr/bin/env python3
"""
Example: How to extend the MCP server template with custom tools.

This file demonstrates common patterns for adding new tools to your MCP server.
Copy the patterns you need into your main mcp_server.py file.

"""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Initialize FastMCP server (you would add this to your existing server)
mcp = FastMCP("example-extensions", version="1.0.0")


class MCPError(Exception):
    """Custom exception for MCP-related errors."""

    pass


# Example 1: System Information Tool
@mcp.tool()
async def get_system_info() -> Dict[str, Any]:
    """
    Get basic system information.

    Returns:
        Dictionary with system information
    """
    try:
        import platform

        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "hostname": platform.node(),
            "current_time": datetime.now().isoformat(),
            "status": "✅ Success",
        }
    except Exception as e:
        raise MCPError(f"Failed to get system info: {str(e)}")


# Example 2: JSON Processing Tool
@mcp.tool()
async def process_json(
    json_string: str, operation: str = "validate", path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process JSON data with various operations.

    Args:
        json_string: JSON string to process
        operation: Operation to perform (validate, format, extract, minify)
        path: JSONPath expression for extraction (when operation=extract)

    Returns:
        Dictionary with processing results
    """
    try:
        # Parse JSON
        data = json.loads(json_string)

        if operation == "validate":
            return {
                "valid": True,
                "type": type(data).__name__,
                "keys": list(data.keys()) if isinstance(data, dict) else None,
                "length": len(data) if hasattr(data, "__len__") else None,
                "status": "✅ Valid JSON",
            }

        elif operation == "format":
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return {
                "formatted_json": formatted,
                "original_length": len(json_string),
                "formatted_length": len(formatted),
                "status": "✅ Formatted",
            }

        elif operation == "minify":
            minified = json.dumps(data, separators=(",", ":"))
            return {
                "minified_json": minified,
                "original_length": len(json_string),
                "minified_length": len(minified),
                "compression_ratio": f"{(1 - len(minified)/len(json_string))*100:.1f}%",
                "status": "✅ Minified",
            }

        elif operation == "extract":
            if not path:
                raise MCPError("Path is required for extract operation")

            # Simple path extraction (you could use jsonpath-ng for more complex paths)
            keys = path.split(".")
            result = data
            for key in keys:
                if isinstance(result, dict) and key in result:
                    result = result[key]
                else:
                    raise MCPError(f"Path '{path}' not found in JSON")

            return {
                "extracted_value": result,
                "path": path,
                "type": type(result).__name__,
                "status": "✅ Extracted",
            }

        else:
            raise MCPError(f"Unknown operation: {operation}")

    except json.JSONDecodeError as e:
        raise MCPError(f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise MCPError(f"JSON processing failed: {str(e)}")


if __name__ == "__main__":
    print("This file contains example extensions for the MCP server template.")
    print("Copy the tools you need into your main mcp_server.py file.")
