"""
FastMCP Server Template
A template for creating MCP servers using the FastMCP framework.
Production-ready with environment configuration and structured logging.
"""

import logging
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import FastMCP

# Optional imports for enhanced features - defer expensive imports
STRUCTURED_LOGGING = False
METRICS_ENABLED = False
RATE_LIMITING = False

# Defer dotenv loading
def _load_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

# Check for optional dependencies without importing
def _check_structlog():
    try:
        import structlog
        import prometheus_client
        return True
    except ImportError:
        return False

def _check_limits():
    try:
        import limits
        return True
    except ImportError:
        return False

# Set flags based on availability
STRUCTURED_LOGGING = _check_structlog()
METRICS_ENABLED = _check_structlog()
RATE_LIMITING = _check_limits()

# Defer logging setup
logger = None

def _setup_logging():
    global logger
    if logger is not None:
        return logger
        
    if STRUCTURED_LOGGING:
        import structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        logger = structlog.get_logger(__name__)
    else:
        from rich.console import Console
        from rich.logging import RichHandler
        console = Console()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True)],
        )
        logger = logging.getLogger(__name__)
    
    return logger

# Defer metrics and rate limiting setup
REQUEST_COUNT = None
REQUEST_DURATION = None
COMMAND_EXECUTIONS = None
RATE_LIMITER = None
DEFAULT_RATE_LIMIT = None

def _setup_metrics():
    global REQUEST_COUNT, REQUEST_DURATION, COMMAND_EXECUTIONS
    if not METRICS_ENABLED or REQUEST_COUNT is not None:
        return
        
    from prometheus_client import Counter, Histogram, start_http_server
    REQUEST_COUNT = Counter(
        "mcp_requests_total", "Total MCP requests", ["tool", "status"]
    )
    REQUEST_DURATION = Histogram(
        "mcp_request_duration_seconds", "Request duration", ["tool"]
    )
    COMMAND_EXECUTIONS = Counter(
        "mcp_commands_total", "Total command executions", ["status"]
    )

    # Start metrics server on a separate port
    METRICS_PORT = int(os.getenv("MCP_METRICS_PORT", "9090"))
    if METRICS_PORT > 0:  # Allow disabling with port 0
        try:
            start_http_server(METRICS_PORT)
            logger = _setup_logging()
            if STRUCTURED_LOGGING:
                logger.info("metrics_server_started", port=METRICS_PORT)
            else:
                logger.info(f"Metrics server started on port {METRICS_PORT}")
        except Exception as e:
            logger = _setup_logging()
            if STRUCTURED_LOGGING:
                logger.warning("metrics_server_failed", error=str(e))
            else:
                logger.warning(f"Failed to start metrics server: {e}")

def _setup_rate_limiting():
    global RATE_LIMITER, DEFAULT_RATE_LIMIT
    if RATE_LIMITER is not None:
        return
        
    if RATE_LIMITING:
        from limits import parse, strategies
        from limits.storage import MemoryStorage
        RATE_LIMIT_STORAGE = MemoryStorage()
        RATE_LIMITER = strategies.FixedWindowRateLimiter(RATE_LIMIT_STORAGE)
        DEFAULT_RATE_LIMIT = parse(os.getenv("MCP_RATE_LIMIT", "100/minute"))
        logger = _setup_logging()
        if STRUCTURED_LOGGING:
            logger.info("rate_limiting_enabled", limit=str(DEFAULT_RATE_LIMIT))
        else:
            logger.info(f"Rate limiting enabled: {DEFAULT_RATE_LIMIT}")
    else:
        logger = _setup_logging()
        if STRUCTURED_LOGGING:
            logger.warning("rate_limiting_disabled", reason="limits package not installed")
        else:
            logger.warning(
                "Rate limiting disabled - install limits package for production use"
            )

# Environment-first configuration
SERVER_NAME = os.getenv("MCP_SERVER_NAME", "template-server")
VERSION = "2.0.0"
TRANSPORT = os.getenv("MCP_TRANSPORT", "stdio")
HOST = os.getenv("MCP_HOST", "127.0.0.1")  # Secure default - localhost only
PORT = int(os.getenv("MCP_PORT", "8080"))
WORKSPACE_PATH = os.getenv("WORKSPACE_PATH", "/workspace")

# Initialize FastMCP server
mcp = FastMCP(name=SERVER_NAME)


# Graceful shutdown handling
def signal_handler(signum: int, frame: Any) -> None:
    logger = _setup_logging()
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


class MCPError(Exception):
    pass


class RateLimitExceeded(MCPError):
    """Raised when rate limit is exceeded."""

    pass


def with_monitoring(tool_name: str) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """Decorator to add rate limiting, metrics, and structured logging to MCP tools."""

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Lazy initialization on first use
            _setup_rate_limiting()
            _setup_metrics()
            logger = _setup_logging()
            
            start_time = time.time()
            request_id = f"{tool_name}_{int(start_time * 1000)}"

            # Check rate limit
            if RATE_LIMITING and RATE_LIMITER is not None:
                client_id = kwargs.get("client_id", "default")
                if not RATE_LIMITER.hit(
                    DEFAULT_RATE_LIMIT, "mcp_tools", f"{tool_name}:{client_id}"
                ):
                    if METRICS_ENABLED:
                        REQUEST_COUNT.labels(
                            tool=tool_name, status="rate_limited"
                        ).inc()
                    if STRUCTURED_LOGGING:
                        logger.warning(
                            "rate_limit_exceeded",
                            tool=tool_name,
                            client_id=client_id,
                            request_id=request_id,
                        )
                    else:
                        logger.warning(
                            f"Rate limit exceeded for {tool_name} by {client_id}"
                        )
                    raise RateLimitExceeded(f"Rate limit exceeded for {tool_name}")

            try:
                # Execute the function
                if STRUCTURED_LOGGING:
                    logger.info(
                        "tool_request_started",
                        tool=tool_name,
                        request_id=request_id,
                        args=len(args),
                        kwargs=list(kwargs.keys()),
                    )

                result = await func(*args, **kwargs)

                # Record success metrics
                duration = time.time() - start_time
                if METRICS_ENABLED:
                    REQUEST_COUNT.labels(tool=tool_name, status="success").inc()
                    REQUEST_DURATION.labels(tool=tool_name).observe(duration)

                if STRUCTURED_LOGGING:
                    logger.info(
                        "tool_request_completed",
                        tool=tool_name,
                        request_id=request_id,
                        duration=duration,
                    )

                return result

            except Exception as e:
                # Record error metrics
                duration = time.time() - start_time
                if METRICS_ENABLED:
                    REQUEST_COUNT.labels(tool=tool_name, status="error").inc()
                    REQUEST_DURATION.labels(tool=tool_name).observe(duration)

                if STRUCTURED_LOGGING:
                    logger.error(
                        "tool_request_failed",
                        tool=tool_name,
                        request_id=request_id,
                        duration=duration,
                        error=str(e),
                        error_type=type(e).__name__,
                    )
                else:
                    logger.error(f"Tool {tool_name} failed: {e}")

                raise

        return wrapper

    return decorator


def validate_path(path: str, base_path: Optional[str] = None) -> Path:
    base_path = base_path or WORKSPACE_PATH
    try:
        resolved = Path(base_path) / path
        resolved = resolved.resolve()
        if not str(resolved).startswith(str(Path(base_path).resolve())):
            raise MCPError(f"Path {path} is outside allowed directory")
        return resolved
    except Exception as e:
        raise MCPError(f"Invalid path {path}: {str(e)}")


async def run_command(
    command: List[str], cwd: Optional[str] = None, timeout: int = 30
) -> Dict[str, Any]:
    logger = _setup_logging()
    command_str = " ".join(command)
    start_time = time.time()

    # Security: Basic command validation
    if not command or not command[0]:
        raise MCPError("Empty or invalid command provided")

    # Log command execution start
    if STRUCTURED_LOGGING:
        logger.info(
            "command_execution_started", command=command_str, cwd=cwd, timeout=timeout
        )
    else:
        logger.info(f"Executing command: {command_str}")

    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
        )

        duration = time.time() - start_time
        success = result.returncode == 0

        # Record metrics
        if METRICS_ENABLED:
            COMMAND_EXECUTIONS.labels(status="success" if success else "failed").inc()

        # Log completion
        if STRUCTURED_LOGGING:
            logger.info(
                "command_execution_completed",
                command=command_str,
                return_code=result.returncode,
                duration=duration,
                stdout_length=len(result.stdout),
                stderr_length=len(result.stderr),
            )

        return {
            "command": command_str,
            "directory": cwd or os.getcwd(),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": success,
            "return_code": result.returncode,
            "duration": duration,
            "status": "✅ Success" if success else "❌ Failed",
        }

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        if METRICS_ENABLED:
            COMMAND_EXECUTIONS.labels(status="timeout").inc()

        if STRUCTURED_LOGGING:
            logger.error(
                "command_execution_timeout",
                command=command_str,
                timeout=timeout,
                duration=duration,
            )

        raise MCPError(f"Command timed out after {timeout} seconds: {command_str}")
    except Exception as e:
        duration = time.time() - start_time
        if METRICS_ENABLED:
            COMMAND_EXECUTIONS.labels(status="error").inc()

        if STRUCTURED_LOGGING:
            logger.error(
                "command_execution_error",
                command=command_str,
                error=str(e),
                error_type=type(e).__name__,
                duration=duration,
            )

        raise MCPError(f"Command execution failed: {command_str} - {str(e)}")


@with_monitoring("health_check")
async def health_check_impl() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "server_name": SERVER_NAME,
        "version": VERSION,
        "transport": TRANSPORT,
        "workspace": WORKSPACE_PATH,
        "timestamp": str(Path().stat().st_mtime),
        "rate_limiting_enabled": RATE_LIMITING,
        "metrics_enabled": METRICS_ENABLED,
        "structured_logging": STRUCTURED_LOGGING,
    }


@mcp.tool()
async def health_check() -> Dict[str, Any]:
    result: Dict[str, Any] = await health_check_impl()
    return result


@with_monitoring("echo")
async def echo_impl(message: str) -> str:
    return f"Echo: {message}"


@mcp.tool()
async def echo(message: str) -> str:
    result: str = await echo_impl(message)
    return result


@with_monitoring("list_files")
async def list_files_impl(directory: str = ".") -> Dict[str, Any]:
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

    except Exception as e:
        raise MCPError(f"Failed to list directory: {str(e)}")


@mcp.tool()
async def list_files(directory: str = ".") -> Dict[str, Any]:
    result: Dict[str, Any] = await list_files_impl(directory)
    return result


@with_monitoring("read_file")
async def read_file_impl(file_path: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
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
async def read_file(file_path: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
    result: Dict[str, Any] = await read_file_impl(file_path, max_size)
    return result


@with_monitoring("write_file")
async def write_file_impl(
    file_path: str, content: str, create_dirs: bool = True
) -> Dict[str, Any]:
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
async def write_file(
    file_path: str, content: str, create_dirs: bool = True
) -> Dict[str, Any]:
    result: Dict[str, Any] = await write_file_impl(file_path, content, create_dirs)
    return result


@with_monitoring("run_shell_command")
async def run_shell_command_impl(command: str, directory: str = ".") -> Dict[str, Any]:
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


@mcp.tool()
async def run_shell_command(command: str, directory: str = ".") -> Dict[str, Any]:
    result: Dict[str, Any] = await run_shell_command_impl(command, directory)
    return result


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
async def code_review_prompt(
    code: str, language: str = "python", focus: str = "general"
) -> str:
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


def main() -> None:
    """Synchronous entrypoint — delegates async lifecycle to FastMCP."""
    # Initialize lazy components
    _load_dotenv()
    logger = _setup_logging()
    
    logger.info(f"Starting {SERVER_NAME} v{VERSION}")
    logger.info(f"Transport: {TRANSPORT}, Host: {HOST}, Port: {PORT}")
    logger.info(f"Workspace: {WORKSPACE_PATH}")

    try:
        transport_lower = TRANSPORT.lower()
        if transport_lower in ("http", "sse"):
            logger.info(f"Starting server on {HOST}:{PORT} with {TRANSPORT} transport")
            if transport_lower == "http":
                mcp.run(transport="streamable-http", host=HOST, port=PORT)
            else:
                mcp.run(transport="sse", host=HOST, port=PORT)
        else:
            logger.info("Starting server with STDIO transport")
            mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
