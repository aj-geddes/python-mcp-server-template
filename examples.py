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
            "status": "✅ Success"
        }
    except Exception as e:
        raise MCPError(f"Failed to get system info: {str(e)}")


# Example 2: JSON Processing Tool
@mcp.tool()
async def process_json(
    json_string: str, 
    operation: str = "validate",
    path: Optional[str] = None
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
                "length": len(data) if hasattr(data, '__len__') else None,
                "status": "✅ Valid JSON"
            }
        
        elif operation == "format":
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return {
                "formatted_json": formatted,
                "original_length": len(json_string),
                "formatted_length": len(formatted),
                "status": "✅ Formatted"
            }
        
        elif operation == "minify":
            minified = json.dumps(data, separators=(',', ':'))
            return {
                "minified_json": minified,
                "original_length": len(json_string),
                "minified_length": len(minified),
                "compression_ratio": f"{(1 - len(minified)/len(json_string))*100:.1f}%",
                "status": "✅ Minified"
            }
        
        elif operation == "extract":
            if not path:
                raise MCPError("Path is required for extract operation")
            
            # Simple path extraction (you could use jsonpath-ng for more complex paths)
            keys = path.split('.')
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
                "status": "✅ Extracted"
            }
        
        else:
            raise MCPError(f"Unknown operation: {operation}")
            
    except json.JSONDecodeError as e:
        raise MCPError(f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise MCPError(f"JSON processing failed: {str(e)}")


# Example 3: Environment Variables Tool
@mcp.tool()
async def manage_env_vars(
    action: str = "list",
    var_name: Optional[str] = None,
    var_value: Optional[str] = None
) -> Dict[str, Any]:
    """
    Manage environment variables.
    
    Args:
        action: Action to perform (list, get, set, unset)
        var_name: Name of the environment variable
        var_value: Value to set (for set action)
        
    Returns:
        Dictionary with environment variable information
    """
    try:
        if action == "list":
            # List all environment variables (filtered for security)
            env_vars = {}
            for key, value in os.environ.items():
                # Filter out potentially sensitive variables
                if not any(sensitive in key.lower() for sensitive in 
                          ['password', 'secret', 'key', 'token', 'auth']):
                    env_vars[key] = value
            
            return {
                "action": "list",
                "total_vars": len(os.environ),
                "shown_vars": len(env_vars),
                "environment_variables": env_vars,
                "status": "✅ Listed"
            }
        
        elif action == "get":
            if not var_name:
                raise MCPError("Variable name is required for get action")
            
            value = os.environ.get(var_name)
            return {
                "action": "get",
                "variable": var_name,
                "value": value,
                "exists": value is not None,
                "status": "✅ Retrieved" if value is not None else "ℹ️  Not Found"
            }
        
        elif action == "set":
            if not var_name or var_value is None:
                raise MCPError("Variable name and value are required for set action")
            
            old_value = os.environ.get(var_name)
            os.environ[var_name] = var_value
            
            return {
                "action": "set",
                "variable": var_name,
                "old_value": old_value,
                "new_value": var_value,
                "was_existing": old_value is not None,
                "status": "✅ Set"
            }
        
        elif action == "unset":
            if not var_name:
                raise MCPError("Variable name is required for unset action")
            
            old_value = os.environ.get(var_name)
            if old_value is not None:
                del os.environ[var_name]
                removed = True
            else:
                removed = False
            
            return {
                "action": "unset",
                "variable": var_name,
                "old_value": old_value,
                "removed": removed,
                "status": "✅ Removed" if removed else "ℹ️  Not Found"
            }
        
        else:
            raise MCPError(f"Unknown action: {action}")
            
    except MCPError:
        raise
    except Exception as e:
        raise MCPError(f"Environment variable operation failed: {str(e)}")


# Example 4: File Search Tool
@mcp.tool()
async def search_files(
    pattern: str,
    directory: str = ".",
    file_type: str = "all",
    case_sensitive: bool = False,
    max_results: int = 100
) -> Dict[str, Any]:
    """
    Search for files matching a pattern.
    
    Args:
        pattern: Search pattern (supports wildcards)
        directory: Directory to search in
        file_type: Type of files to search (all, files, dirs)
        case_sensitive: Whether search should be case sensitive
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with search results
    """
    try:
        import fnmatch
        
        search_dir = Path(directory).resolve()
        if not search_dir.exists():
            raise MCPError(f"Directory {directory} does not exist")
        
        if not case_sensitive:
            pattern = pattern.lower()
        
        results = []
        total_found = 0
        
        for item in search_dir.rglob("*"):
            # Apply file type filter
            if file_type == "files" and not item.is_file():
                continue
            elif file_type == "dirs" and not item.is_dir():
                continue
            
            # Apply pattern matching
            name = item.name if case_sensitive else item.name.lower()
            if fnmatch.fnmatch(name, pattern):
                total_found += 1
                
                if len(results) < max_results:
                    relative_path = item.relative_to(search_dir)
                    results.append({
                        "name": item.name,
                        "path": str(relative_path),
                        "full_path": str(item),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
        
        return {
            "pattern": pattern,
            "directory": str(search_dir),
            "file_type": file_type,
            "case_sensitive": case_sensitive,
            "total_found": total_found,
            "results_shown": len(results),
            "truncated": total_found > max_results,
            "results": results,
            "status": f"✅ Found {total_found} matches"
        }
        
    except Exception as e:
        raise MCPError(f"File search failed: {str(e)}")


# Example 5: Hash/Checksum Tool
@mcp.tool()
async def calculate_hash(
    content: Optional[str] = None,
    file_path: Optional[str] = None,
    algorithm: str = "sha256"
) -> Dict[str, Any]:
    """
    Calculate hash/checksum of content or file.
    
    Args:
        content: Text content to hash (mutually exclusive with file_path)
        file_path: Path to file to hash (mutually exclusive with content)
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Dictionary with hash results
    """
    try:
        import hashlib
        
        if content is not None and file_path is not None:
            raise MCPError("Provide either content or file_path, not both")
        
        if content is None and file_path is None:
            raise MCPError("Must provide either content or file_path")
        
        # Validate algorithm
        if algorithm not in ['md5', 'sha1', 'sha256', 'sha512']:
            raise MCPError(f"Unsupported algorithm: {algorithm}")
        
        hasher = hashlib.new(algorithm)
        
        if content is not None:
            # Hash string content
            hasher.update(content.encode('utf-8'))
            source_type = "content"
            source_info = {
                "type": "string",
                "length": len(content),
                "encoding": "utf-8"
            }
        else:
            # Hash file content
            file_path_obj = Path(file_path).resolve()
            if not file_path_obj.exists():
                raise MCPError(f"File {file_path} does not exist")
            
            if not file_path_obj.is_file():
                raise MCPError(f"{file_path} is not a file")
            
            with open(file_path_obj, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            
            source_type = "file"
            source_info = {
                "type": "file",
                "path": str(file_path_obj),
                "size": file_path_obj.stat().st_size
            }
        
        hash_value = hasher.hexdigest()
        
        return {
            "algorithm": algorithm,
            "hash": hash_value,
            "source": source_type,
            "source_info": source_info,
            "status": "✅ Hash Calculated"
        }
        
    except MCPError:
        raise
    except Exception as e:
        raise MCPError(f"Hash calculation failed: {str(e)}")


if __name__ == "__main__":
    print("This file contains example extensions for the MCP server template.")
    print("Copy the tools you need into your main mcp_server.py file.")
    print("\nAvailable example tools:")
    print("1. get_system_info - System information")
    print("2. process_json - JSON processing and validation")
    print("3. manage_env_vars - Environment variable management")
    print("4. search_files - File pattern searching")
    print("5. calculate_hash - File/content hashing")
