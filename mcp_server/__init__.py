"""
FastMCP Server Template
A template for creating MCP servers using the FastMCP framework.
Production-ready with environment configuration and structured logging.
"""

import json
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from rich.console import Console
from rich.logging import RichHandler

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional

# Production logging setup
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

# Environment-first configuration
SERVER_NAME = os.getenv("MCP_SERVER_NAME", "template-server")
VERSION = "2.0.0"
TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")
HOST = os.getenv("MCP_HOST", "0.0.0.0")
PORT = int(os.getenv("MCP_PORT", "8080"))
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "/workspace")

# Initialize FastMCP server
mcp = FastMCP(name=SERVER_NAME)

# Graceful shutdown handling
def signal_handler(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

class MCPError(Exception):
    pass

def validate_path(path: str, base_path: str = None) -> Path:
    base_path = base_path or WORKSPACE_PATH
    try:
        resolved = Path(base_path) / path
        resolved = resolved.resolve()
        if not str(resolved).startswith(str(Path(base_path).resolve())):
            raise MCPError(f"Path {path} is outside allowed directory")
        return resolved
    except Exception as e:
        raise MCPError(f"Invalid path {path}: {str(e)}")

async def run_command(command: List[str], cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, Any]:
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
        raise MCPError(f"Command timed out after {timeout} seconds: {' '.join(command)}")
    except Exception as e:
        raise MCPError(f"Command execution failed: {str(e)}")

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "server_name": SERVER_NAME,
        "version": VERSION,
        "transport": TRANSPORT,
        "workspace": WORKSPACE_PATH,
        "timestamp": str(Path().stat().st_mtime),
    }

@mcp.tool()
async def echo(message: str) -> str:
    return f"Echo: {message}"

@mcp.tool()
async def list_files(directory: str = ".") -> Dict[str, Any]:
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
                files.append({"name": item.name, "size": item.stat().st_size, "type": "file"})
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

    except Exception as e:
        raise MCPError(f"Failed to list directory: {str(e)}")

@mcp.tool()
async def read_file(file_path: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
    try:
        path = validate_path(file_path)
        if not path.exists():
            raise MCPError(f"File {file_path} does not exist")
        if not path.is_file():
            raise MCPError(f"{file_path} is not a file")

        file_size = path.stat().st_size
        if file_size > max_size:
            raise MCPError(f"File too large: {file_size} bytes (max: {max_size})")

        content = path.read_text(encoding="utf-8")

        return {
            "file_path": str(path),
            "content": content,
            "size": file_size,
            "lines": len(content.splitlines()),
            "encoding": "utf-8",
            "status": "✅ Success",
        }

    except UnicodeDecodeError:
        raise MCPError(f"File {file_path} is not valid UTF-8 text")
    except Exception as e:
        raise MCPError(f"Failed to read file: {str(e)}")

@mcp.tool()
async def write_file(file_path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    try:
        path = validate_path(file_path)
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {
            "file_path": str(path),
            "bytes_written": len(content.encode("utf-8")),
            "lines_written": len(content.splitlines()),
            "status": "✅ Success",
        }

    except Exception as e:
        raise MCPError(f"Failed to write file: {str(e)}")

@mcp.tool()
async def run_shell_command(command: str, directory: str = ".") -> Dict[str, Any]:
    try:
        path = validate_path(directory)
        if not path.exists():
            raise MCPError(f"Directory {directory} does not exist")

        cmd_parts = command.split()
        if not cmd_parts:
            raise MCPError("Empty command provided")

        return await run_command(cmd_parts, cwd=str(path))

    except Exception as e:
        raise MCPError(f"Failed to execute command: {str(e)}")

@mcp.resource("file://{path}")
async def read_file_resource(path: str) -> str:
    try:
        validated_path = validate_path(path)
        if not validated_path.exists():
            raise MCPError(f"File {path} does not exist")
        if not validated_path.is_file():
            raise MCPError(f"{path} is not a file")
        return validated_path.read_text(encoding="utf-8")
    except Exception as e:
        raise MCPError(f"Failed to read file resource: {str(e)}")

@mcp.prompt()
async def code_review_prompt(code: str, language: str = "python", focus: str = "general") -> str:
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

def main():
    """Synchronous entrypoint — delegates async lifecycle to FastMCP."""
    logger.info(f"Starting {SERVER_NAME} v{VERSION}")
    logger.info(f"Transport: {TRANSPORT}, Host: {HOST}, Port: {PORT}")
    logger.info(f"Workspace: {WORKSPACE_PATH}")

    try:
        if TRANSPORT.lower() in ("http", "sse"):
            logger.info(f"Starting server on {HOST}:{PORT} with {TRANSPORT} transport")
            mcp.run(transport=TRANSPORT.lower(), host=HOST, port=PORT)
        else:
            logger.info("Starting server with STDIO transport")
            mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
