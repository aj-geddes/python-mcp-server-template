#!/usr/bin/env python3
"""
FastMCP Server Template
A template for creating MCP servers using the FastMCP framework.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Server configuration
SERVER_NAME = "template-server"
VERSION = "1.0.0"

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
    command: List[str], 
    cwd: Optional[str] = None, 
    timeout: int = 30
) -> Dict[str, Any]:
    """Execute a command and return structured results."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy()
        )
        
        return {
            "command": " ".join(command),
            "directory": cwd or os.getcwd(),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "status": "✅ Success" if result.returncode == 0 else "❌ Failed"
        }
    except subprocess.TimeoutExpired:
        raise MCPError(f"Command timed out after {timeout} seconds: {' '.join(command)}")
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
                files.append({
                    "name": item.name,
                    "size": item.stat().st_size,
                    "type": "file"
                })
            elif item.is_dir():
                dirs.append({
                    "name": item.name,
                    "type": "directory"
                })
        
        return {
            "directory": str(path),
            "files": files,
            "directories": dirs,
            "total_files": len(files),
            "total_directories": len(dirs),
            "status": "✅ Success"
        }
        
    except MCPError:
        raise
    except Exception as e:
        raise MCPError(f"Failed to list directory: {str(e)}")


@mcp.tool()
async def read_file(file_path: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        max_size: Maximum file size to read (default: 1MB)
        
    Returns:
        Dictionary with file contents and metadata
    """
    try:
        path = validate_path(file_path)
        
        if not path.exists():
            raise MCPError(f"File {file_path} does not exist")
        
        if not path.is_file():
            raise MCPError(f"{file_path} is not a file")
        
        file_size = path.stat().st_size
        if file_size > max_size:
            raise MCPError(f"File too large: {file_size} bytes (max: {max_size})")
        
        content = path.read_text(encoding='utf-8')
        
        return {
            "file_path": str(path),
            "content": content,
            "size": file_size,
            "lines": len(content.splitlines()),
            "encoding": "utf-8",
            "status": "✅ Success"
        }
        
    except MCPError:
        raise
    except UnicodeDecodeError:
        raise MCPError(f"File {file_path} is not valid UTF-8 text")
    except Exception as e:
        raise MCPError(f"Failed to read file: {str(e)}")


@mcp.tool()
async def write_file(file_path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        Dictionary with write operation results
    """
    try:
        path = validate_path(file_path)
        
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding='utf-8')
        
        return {
            "file_path": str(path),
            "bytes_written": len(content.encode('utf-8')),
            "lines_written": len(content.splitlines()),
            "status": "✅ Success"
        }
        
    except MCPError:
        raise
    except Exception as e:
        raise MCPError(f"Failed to write file: {str(e)}")


@mcp.tool()
async def run_shell_command(command: str, directory: str = ".") -> Dict[str, Any]:
    """
    Execute a shell command.
    
    Args:
        command: The shell command to execute
        directory: Directory to run the command in (default: current directory)
        
    Returns:
        Dictionary with command execution results
    """
    try:
        path = validate_path(directory)
        
        if not path.exists():
            raise MCPError(f"Directory {directory} does not exist")
        
        # Split command into parts for subprocess
        cmd_parts = command.split()
        if not cmd_parts:
            raise MCPError("Empty command provided")
        
        result = await run_command(cmd_parts, cwd=str(path))
        return result
        
    except MCPError:
        raise
    except Exception as e:
        raise MCPError(f"Failed to execute command: {str(e)}")


@mcp.resource("file://{path}")
async def read_file_resource(path: str) -> str:
    """Read a file as a resource."""
    try:
        validated_path = validate_path(path)
        
        if not validated_path.exists():
            raise MCPError(f"File {path} does not exist")
        
        if not validated_path.is_file():
            raise MCPError(f"{path} is not a file")
        
        return validated_path.read_text(encoding='utf-8')
        
    except MCPError:
        raise
    except Exception as e:
        raise MCPError(f"Failed to read file resource: {str(e)}")


@mcp.prompt()
async def code_review_prompt(
    code: str, 
    language: str = "python", 
    focus: str = "general"
) -> str:
    """
    Generate a code review prompt.
    
    Args:
        code: The code to review
        language: Programming language of the code
        focus: Focus area for the review (security, performance, style, general)
        
    Returns:
        A formatted code review prompt
    """
    return f"""Please review the following {language} code with a focus on {focus}:

```{language}
{code}
```

Please provide feedback on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Security concerns (if applicable)
5. Suggestions for improvement

Be specific and constructive in your feedback."""


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
