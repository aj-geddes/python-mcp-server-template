#!/usr/bin/env python3
"""
Streamlined MCP Server with Centralized Configuration
====================================================
This is the main server implementation that uses your centralized config.

🚀 QUICK START:
1. Configure your server in config.py
2. Add your tools in tools/custom_tools.py
3. Run: python mcp_server.py

The server automatically loads your configuration and tools.
"""

import asyncio
import importlib
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Awaitable

from fastmcp import FastMCP

# Import centralized configuration
try:
    from config import config, CUSTOM_TOOLS
except ImportError:
    print("❌ Error: config.py not found. Run 'python quick_setup.py' to configure your server.")
    sys.exit(1)

# Optional enhanced features
STRUCTURED_LOGGING = False
METRICS_ENABLED = False  
RATE_LIMITING = False

def _check_optional_features():
    """Check for optional dependencies."""
    global STRUCTURED_LOGGING, METRICS_ENABLED, RATE_LIMITING
    
    # Check for structured logging
    try:
        import structlog
        import prometheus_client
        STRUCTURED_LOGGING = config.enable_logging
        METRICS_ENABLED = config.enable_metrics
    except ImportError:
        pass
    
    # Check for rate limiting
    try:
        import limits
        RATE_LIMITING = config.enable_rate_limiting
    except ImportError:
        RATE_LIMITING = False

_check_optional_features()

# Initialize FastMCP server with configuration
mcp = FastMCP(name=config.server_name)

# Lazy-loaded components
logger = None
REQUEST_COUNT = None
REQUEST_DURATION = None
RATE_LIMITER = None

def _setup_logging():
    """Setup logging based on configuration."""
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
        logger = structlog.get_logger(config.server_name)
    else:
        from rich.console import Console
        from rich.logging import RichHandler
        console = Console()
        logging.basicConfig(
            level=getattr(logging, config.log_level, logging.INFO),
            format=f"%(asctime)s - {config.server_name} - %(levelname)s - %(message)s",
            handlers=[RichHandler(console=console, rich_tracebacks=True)],
        )
        logger = logging.getLogger(config.server_name)
    
    return logger

def _setup_metrics():
    """Setup Prometheus metrics if enabled."""
    global REQUEST_COUNT, REQUEST_DURATION
    if not METRICS_ENABLED or REQUEST_COUNT is not None:
        return
        
    from prometheus_client import Counter, Histogram, start_http_server
    REQUEST_COUNT = Counter(
        f"{config.server_name.replace('-', '_')}_requests_total", 
        "Total MCP requests", 
        ["tool", "status"]
    )
    REQUEST_DURATION = Histogram(
        f"{config.server_name.replace('-', '_')}_request_duration_seconds", 
        "Request duration", 
        ["tool"]
    )

    # Start metrics server
    metrics_port = getattr(config, 'metrics_port', 9090)
    try:
        start_http_server(metrics_port)
        logger = _setup_logging()
        if STRUCTURED_LOGGING:
            logger.info("metrics_server_started", port=metrics_port)
        else:
            logger.info(f"📊 Metrics server started on port {metrics_port}")
    except Exception as e:
        logger = _setup_logging()
        logger.warning(f"Failed to start metrics server: {e}")

def _setup_rate_limiting():
    """Setup rate limiting if enabled."""
    global RATE_LIMITER
    if RATE_LIMITER is not None or not RATE_LIMITING:
        return
        
    from limits import parse, strategies
    from limits.storage import MemoryStorage
    
    storage = MemoryStorage()
    RATE_LIMITER = strategies.FixedWindowRateLimiter(storage)
    
    logger = _setup_logging()
    if STRUCTURED_LOGGING:
        logger.info("rate_limiting_enabled", limit=config.rate_limit)
    else:
        logger.info(f"⚡ Rate limiting enabled: {config.rate_limit}")

def with_monitoring(tool_name: str):
    """Decorator to add monitoring to tools."""
    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Setup components on first use
            _setup_metrics()
            _setup_rate_limiting()
            logger = _setup_logging()
            
            start_time = time.time()
            
            # Rate limiting check
            if RATE_LIMITING and RATE_LIMITER is not None:
                from limits import parse
                rate_limit = parse(config.rate_limit)
                client_id = kwargs.get("client_id", "default")
                
                if not RATE_LIMITER.hit(rate_limit, "mcp_tools", f"{tool_name}:{client_id}"):
                    if METRICS_ENABLED and REQUEST_COUNT:
                        REQUEST_COUNT.labels(tool=tool_name, status="rate_limited").inc()
                    
                    error_msg = f"Rate limit exceeded for {tool_name}"
                    if STRUCTURED_LOGGING:
                        logger.warning("rate_limit_exceeded", tool=tool_name, client_id=client_id)
                    else:
                        logger.warning(error_msg)
                    raise Exception(error_msg)

            try:
                # Execute the tool
                result = await func(*args, **kwargs)
                
                # Record success metrics
                duration = time.time() - start_time
                if METRICS_ENABLED and REQUEST_COUNT:
                    REQUEST_COUNT.labels(tool=tool_name, status="success").inc()
                    if REQUEST_DURATION:
                        REQUEST_DURATION.labels(tool=tool_name).observe(duration)
                
                if STRUCTURED_LOGGING:
                    logger.info("tool_executed", tool=tool_name, duration=duration, status="success")
                
                return result
                
            except Exception as e:
                # Record error metrics
                duration = time.time() - start_time
                if METRICS_ENABLED and REQUEST_COUNT:
                    REQUEST_COUNT.labels(tool=tool_name, status="error").inc()
                
                if STRUCTURED_LOGGING:
                    logger.error("tool_failed", tool=tool_name, duration=duration, error=str(e))
                else:
                    logger.error(f"❌ Tool {tool_name} failed: {e}")
                
                raise
        
        return wrapper
    return decorator

# =============================================================================
# 🛠️ CORE MCP TOOLS - Always available
# =============================================================================

@with_monitoring("health_check")
async def health_check_impl() -> Dict[str, Any]:
    """Health check with server configuration."""
    return {
        "status": "healthy",
        "server": config.server_name,
        "version": config.version,
        "description": config.description,
        "transport": config.transport,
        "workspace": config.workspace_path,
        "timestamp": time.time(),
        "features": {
            "rate_limiting": RATE_LIMITING,
            "metrics": METRICS_ENABLED,
            "structured_logging": STRUCTURED_LOGGING
        },
        "custom_tools": len(CUSTOM_TOOLS),
        "branding": config.branding
    }

@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Get server health and configuration."""
    return await health_check_impl()

@with_monitoring("server_info")
async def server_info_impl() -> Dict[str, Any]:
    """Get detailed server information."""
    return config.to_dict()

@mcp.tool()
async def server_info() -> Dict[str, Any]:
    """Get detailed server configuration and status."""
    return await server_info_impl()

# =============================================================================
# 🔧 DYNAMIC TOOL LOADING - Load custom tools from configuration
# =============================================================================

def load_custom_tools():
    """Load custom tools from tools directory and configuration."""
    logger = _setup_logging()
    loaded_tools = 0
    
    # Try to import custom tools
    try:
        # Add tools directory to path
        tools_dir = Path("tools")
        if tools_dir.exists():
            sys.path.insert(0, str(tools_dir))
        
        # Import custom tools module
        try:
            custom_tools_module = importlib.import_module("custom_tools")
            logger.info("✅ Loaded custom_tools.py module")
        except ImportError:
            logger.info("💡 No custom_tools.py found - using configuration only")
            custom_tools_module = None
        
        # Register tools from configuration
        for tool_config in CUSTOM_TOOLS:
            try:
                tool_name = tool_config["name"]
                function_name = tool_config["function"]
                description = tool_config.get("description", f"Custom tool: {tool_name}")
                
                # Get implementation function
                if custom_tools_module and hasattr(custom_tools_module, function_name):
                    impl_func = getattr(custom_tools_module, function_name)
                    
                    # Wrap with monitoring
                    monitored_impl = with_monitoring(tool_name)(impl_func)
                    
                    # Create MCP tool wrapper
                    async def create_tool_wrapper(impl_function, name):
                        async def tool_wrapper(*args, **kwargs):
                            return await impl_function(*args, **kwargs)
                        tool_wrapper.__name__ = name
                        tool_wrapper.__doc__ = description
                        return tool_wrapper
                    
                    # Register with FastMCP
                    tool_wrapper = await create_tool_wrapper(monitored_impl, tool_name)
                    mcp.tool()(tool_wrapper)
                    
                    loaded_tools += 1
                    logger.info(f"✅ Registered tool: {tool_name}")
                    
                else:
                    logger.warning(f"⚠️  Tool function '{function_name}' not found for '{tool_name}'")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load tool '{tool_config.get('name', 'unknown')}': {e}")
        
        if loaded_tools > 0:
            logger.info(f"🛠️  Successfully loaded {loaded_tools} custom tools")
        else:
            logger.info("💡 No custom tools loaded. Add tools to config.py and implement in tools/custom_tools.py")
            
    except Exception as e:
        logger.error(f"❌ Error loading custom tools: {e}")

# =============================================================================
# 🚀 SERVER LIFECYCLE
# =============================================================================

def signal_handler(signum: int, frame: Any) -> None:
    """Handle shutdown signals gracefully."""
    logger = _setup_logging()
    logger.info(f"🛑 Received signal {signum}, shutting down {config.server_name}...")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def start_server() -> None:
    """Start the MCP server with configuration."""
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Setup logging
    logger = _setup_logging()
    
    # Print configuration
    if config.debug:
        from config import print_config
        print_config()
    
    # Load custom tools
    load_custom_tools()
    
    # Start server
    logger.info(f"🚀 Starting {config.server_name} v{config.version}")
    logger.info(f"📡 Transport: {config.transport}, Host: {config.host}, Port: {config.port}")
    
    try:
        if config.transport in ("http", "sse"):
            logger.info(f"🌐 Starting HTTP server on {config.host}:{config.port}")
            if config.transport == "http":
                mcp.run(transport="streamable-http", host=config.host, port=config.port)
            else:
                mcp.run(transport="sse", host=config.host, port=config.port)
        else:
            logger.info("📡 Starting STDIO transport")
            mcp.run()
            
    except KeyboardInterrupt:
        logger.info("🛑 Server interrupted by user")
    except Exception as e:
        logger.error(f"💥 Server error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    start_server()