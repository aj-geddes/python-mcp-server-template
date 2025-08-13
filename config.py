#!/usr/bin/env python3
"""
MCP Server Configuration
========================
Centralized configuration for your MCP server.

🚀 QUICK SETUP:
1. Change SERVER_NAME to your project name
2. Add your tools in the TOOLS section below  
3. Run: python mcp_server.py

That's it! Your MCP server is ready.
"""

import os
from typing import Dict, Any, List

# =============================================================================
# 🚀 BASIC CONFIGURATION - Change these to customize your MCP server
# =============================================================================

# Server Identity
SERVER_NAME = "my-awesome-mcp-server"  # 👈 CHANGE THIS to your project name
VERSION = "1.0.0"
DESCRIPTION = "My awesome MCP server built from template"

# Network Configuration
DEFAULT_HOST = "127.0.0.1"  # Secure default - localhost only
DEFAULT_PORT = 8080
DEFAULT_TRANSPORT = "stdio"  # Options: "stdio", "http", "sse"

# Security Configuration  
DEFAULT_RATE_LIMIT = "100/minute"  # Requests per minute per client
DEFAULT_WORKSPACE = "/workspace"   # Base path for file operations

# =============================================================================
# 🛠️ YOUR TOOLS - Add your custom MCP tools here
# =============================================================================

# Example: Add your tools to this list
# Each tool should be a dictionary with 'name', 'description', and 'function'
CUSTOM_TOOLS = [
    # Example tool - replace with your own
    {
        "name": "example_tool",
        "description": "An example tool to get you started",
        "function": "example_tool_impl",  # Function name in your code
        "parameters": {
            "message": {"type": "string", "description": "Message to process"}
        }
    },
    # Add more tools here...
    # {
    #     "name": "your_tool_name", 
    #     "description": "What your tool does",
    #     "function": "your_function_name",
    #     "parameters": {
    #         "param1": {"type": "string", "description": "Parameter description"}
    #     }
    # }
]

# =============================================================================
# 🎨 BRANDING - Customize the appearance of your server
# =============================================================================

BRANDING = {
    "author": "Your Name",
    "email": "you@example.com", 
    "website": "https://your-website.com",
    "repository": "https://github.com/yourusername/your-repo",
    "license": "MIT",
    "keywords": ["mcp", "ai", "tools", "automation"]
}

# =============================================================================
# ⚙️ ADVANCED CONFIGURATION - Usually don't need to change these
# =============================================================================

class Config:
    """Centralized configuration manager."""
    
    def __init__(self):
        self.server_name = os.getenv("MCP_SERVER_NAME", SERVER_NAME)
        self.version = VERSION
        self.description = DESCRIPTION
        self.branding = BRANDING
        
        # Network
        self.host = os.getenv("MCP_HOST", DEFAULT_HOST)
        self.port = int(os.getenv("MCP_PORT", str(DEFAULT_PORT)))
        self.transport = os.getenv("MCP_TRANSPORT", DEFAULT_TRANSPORT).lower()
        
        # Security & Performance
        self.rate_limit = os.getenv("MCP_RATE_LIMIT", DEFAULT_RATE_LIMIT)
        self.workspace_path = os.getenv("WORKSPACE_PATH", DEFAULT_WORKSPACE)
        self.max_file_size = int(os.getenv("MCP_MAX_FILE_SIZE", "10485760"))  # 10MB
        self.command_timeout = int(os.getenv("MCP_COMMAND_TIMEOUT", "30"))
        
        # Feature toggles
        self.enable_metrics = os.getenv("MCP_ENABLE_METRICS", "true").lower() == "true"
        self.enable_logging = os.getenv("MCP_ENABLE_LOGGING", "true").lower() == "true"  
        self.enable_rate_limiting = os.getenv("MCP_ENABLE_RATE_LIMITING", "true").lower() == "true"
        
        # Development
        self.debug = os.getenv("MCP_DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("MCP_LOG_LEVEL", "INFO").upper()

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "server_name": self.server_name,
            "version": self.version, 
            "description": self.description,
            "host": self.host,
            "port": self.port,
            "transport": self.transport,
            "workspace_path": self.workspace_path,
            "rate_limit": self.rate_limit,
            "features": {
                "metrics": self.enable_metrics,
                "logging": self.enable_logging,
                "rate_limiting": self.enable_rate_limiting,
                "debug": self.debug
            },
            "branding": self.branding,
            "custom_tools": len(CUSTOM_TOOLS)
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """Get configured custom tools."""
        return CUSTOM_TOOLS.copy()

# Global configuration instance
config = Config()

# =============================================================================
# 🔧 QUICK SETUP FUNCTIONS - Helper functions for common tasks
# =============================================================================

def setup_for_development():
    """Quick setup for development environment."""
    config.host = "127.0.0.1"
    config.transport = "http"
    config.debug = True
    config.log_level = "DEBUG"
    config.enable_rate_limiting = False
    print(f"🔧 Development mode enabled for {config.server_name}")
    return config

def setup_for_production():
    """Quick setup for production environment.""" 
    config.debug = False
    config.log_level = "INFO"
    config.enable_metrics = True
    config.enable_rate_limiting = True
    print(f"🚀 Production mode enabled for {config.server_name}")
    return config

def print_config():
    """Print current configuration for debugging."""
    print("\n" + "="*60)
    print(f"🚀 {config.server_name} v{config.version}")
    print("="*60)
    print(f"📡 Transport: {config.transport}://{config.host}:{config.port}")
    print(f"📁 Workspace: {config.workspace_path}")
    print(f"⚡ Rate Limit: {config.rate_limit}")
    print(f"🛠️  Custom Tools: {len(CUSTOM_TOOLS)}")
    print(f"🔒 Features: Metrics={config.enable_metrics}, Logging={config.enable_logging}")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Test configuration
    print_config()
    print("✅ Configuration loaded successfully!")
    
    if CUSTOM_TOOLS:
        print("\n📋 Your Custom Tools:")
        for i, tool in enumerate(CUSTOM_TOOLS, 1):
            print(f"  {i}. {tool['name']} - {tool['description']}")
    else:
        print("\n💡 Add your custom tools to CUSTOM_TOOLS in this file!")