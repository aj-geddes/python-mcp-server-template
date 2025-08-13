#!/usr/bin/env python3
"""
MCP Server Quick Setup Wizard
=============================
Interactive setup to customize your MCP server in minutes.

Usage: python quick_setup.py
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any

def print_banner():
    """Print welcome banner."""
    print("\n" + "="*60)
    print("🚀 MCP SERVER QUICK SETUP WIZARD")
    print("="*60)
    print("Transform this template into your custom MCP server!")
    print("⏱️  Estimated time: 2-3 minutes")
    print("-"*60 + "\n")

def get_user_input(prompt: str, default: str = "") -> str:
    """Get user input with default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

def validate_server_name(name: str) -> str:
    """Validate and normalize server name."""
    # Convert to lowercase with hyphens
    normalized = re.sub(r'[^a-zA-Z0-9\-_]', '-', name.lower())
    normalized = re.sub(r'-+', '-', normalized)  # Remove multiple hyphens
    normalized = normalized.strip('-')  # Remove leading/trailing hyphens
    return normalized

def collect_basic_info() -> Dict[str, Any]:
    """Collect basic server information."""
    print("📋 BASIC INFORMATION")
    print("-" * 20)
    
    config = {}
    
    # Server name
    while True:
        name = get_user_input("Server name (e.g., 'weather-tools-server')", "my-mcp-server")
        normalized = validate_server_name(name)
        if normalized and len(normalized) >= 3:
            config['server_name'] = normalized
            break
        print("❌ Server name must be at least 3 characters and contain only letters, numbers, hyphens, and underscores")
    
    # Description
    config['description'] = get_user_input(
        "Server description", 
        f"Custom MCP server built from template"
    )
    
    # Version
    config['version'] = get_user_input("Version", "1.0.0")
    
    print()
    return config

def collect_branding_info() -> Dict[str, Any]:
    """Collect branding information."""
    print("🎨 BRANDING (Optional - press Enter to skip)")
    print("-" * 20)
    
    branding = {}
    branding['author'] = get_user_input("Your name", "")
    branding['email'] = get_user_input("Your email", "")
    branding['repository'] = get_user_input("GitHub repository URL", "")
    branding['website'] = get_user_input("Website URL", "")
    
    print()
    return branding

def collect_tools_info() -> Dict[str, Any]:
    """Collect information about custom tools."""
    print("🛠️  CUSTOM TOOLS")
    print("-" * 20)
    print("What kind of tools will your MCP server provide?")
    print("Examples:")
    print("  • File operations (read, write, search)")
    print("  • API integrations (weather, news, databases)")  
    print("  • Data processing (JSON, CSV, calculations)")
    print("  • System utilities (commands, monitoring)")
    print()
    
    tools_purpose = get_user_input(
        "Describe your tools' purpose", 
        "Custom automation and integration tools"
    )
    
    print()
    return {"tools_purpose": tools_purpose}

def update_config_file(config: Dict[str, Any], branding: Dict[str, Any]) -> None:
    """Update the config.py file with user's choices."""
    config_path = Path("config.py")
    
    if not config_path.exists():
        print("❌ Error: config.py not found. Make sure you're in the template directory.")
        return
    
    # Read current config
    content = config_path.read_text()
    
    # Update basic configuration
    content = re.sub(
        r'SERVER_NAME = "[^"]*"',
        f'SERVER_NAME = "{config["server_name"]}"',
        content
    )
    
    content = re.sub(
        r'VERSION = "[^"]*"',
        f'VERSION = "{config["version"]}"', 
        content
    )
    
    content = re.sub(
        r'DESCRIPTION = "[^"]*"',
        f'DESCRIPTION = "{config["description"]}"',
        content
    )
    
    # Update branding if provided
    if branding.get('author'):
        content = re.sub(
            r'"author": "[^"]*"',
            f'"author": "{branding["author"]}"',
            content
        )
    
    if branding.get('email'):
        content = re.sub(
            r'"email": "[^"]*"',
            f'"email": "{branding["email"]}"',
            content
        )
        
    if branding.get('repository'):
        content = re.sub(
            r'"repository": "[^"]*"',
            f'"repository": "{branding["repository"]}"',
            content
        )
    
    if branding.get('website'):
        content = re.sub(
            r'"website": "[^"]*"',
            f'"website": "{branding["website"]}"',
            content
        )
    
    # Write updated config
    config_path.write_text(content)
    print(f"✅ Updated config.py with your settings")

def update_readme(config: Dict[str, Any]) -> None:
    """Update README.md with project-specific information."""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        return
        
    content = readme_path.read_text()
    
    # Update title and description
    old_title_pattern = r"# Python MCP Server Template"
    new_title = f"# {config['server_name'].replace('-', ' ').title()}"
    content = re.sub(old_title_pattern, new_title, content)
    
    # Update description
    old_desc_pattern = r"> 🚀 \*\*.*?\*\*"
    new_desc = f"> 🚀 **{config['description']}**"
    content = re.sub(old_desc_pattern, new_desc, content)
    
    readme_path.write_text(content)
    print(f"✅ Updated README.md")

def create_example_tool(config: Dict[str, Any]) -> None:
    """Create an example custom tool file."""
    tools_dir = Path("tools")
    tools_dir.mkdir(exist_ok=True)
    
    example_tool = f"""#!/usr/bin/env python3
\"\"\"
Example Custom Tool for {config['server_name']}
===============================================
This is an example of how to add custom tools to your MCP server.

Replace this with your actual tool implementations.
\"\"\"

from typing import Dict, Any
import asyncio

async def example_tool_impl(message: str) -> Dict[str, Any]:
    \"\"\"
    Example tool implementation.
    
    Args:
        message: Input message to process
        
    Returns:
        Dict containing the processed result
    \"\"\"
    # TODO: Replace this with your actual tool logic
    processed_message = f"Processed: {{message}}"
    
    return {{
        "result": processed_message,
        "timestamp": "2025-01-01T00:00:00Z",
        "status": "✅ Success",
        "tool": "example_tool",
        "server": "{config['server_name']}"
    }}

# Add more tool implementations here...

async def your_custom_tool_impl(param1: str, param2: int = 10) -> Dict[str, Any]:
    \"\"\"
    Template for your custom tool.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        Dict containing your tool's results
    \"\"\"
    # TODO: Implement your tool logic here
    
    return {{
        "message": f"Your tool processed {{param1}} with value {{param2}}",
        "status": "✅ Success"
    }}

if __name__ == "__main__":
    # Test your tools
    async def test_tools():
        result1 = await example_tool_impl("Hello, World!")
        print("Example Tool Result:", result1)
        
        result2 = await your_custom_tool_impl("test", 42)
        print("Custom Tool Result:", result2)
    
    asyncio.run(test_tools())
"""
    
    tools_file = tools_dir / "custom_tools.py"
    tools_file.write_text(example_tool)
    print(f"✅ Created tools/custom_tools.py with example implementations")

def print_next_steps(config: Dict[str, Any]) -> None:
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETE!")
    print("="*60)
    print(f"Your '{config['server_name']}' MCP server is ready!")
    print("\n📋 NEXT STEPS:")
    print("-" * 15)
    print("1. 🛠️  Edit tools/custom_tools.py - Add your actual tool implementations")
    print("2. 🧪 Test your server:")
    print(f"   python config.py  # Verify configuration") 
    print(f"   python mcp_server.py  # Start your server")
    print("3. 🚀 Deploy:")
    print("   docker build -t my-mcp-server .")
    print("   docker run -p 8080:8080 my-mcp-server")
    print("\n💡 HELPFUL COMMANDS:")
    print("-" * 20)
    print("• python config.py          - View your configuration")
    print("• python tools/custom_tools.py - Test your tools")
    print("• python security_scan.py  - Run security checks")
    print("• pytest tests/            - Run test suite")
    
    print("\n📚 DOCUMENTATION:")
    print("-" * 18)
    print("• docs/                    - Full documentation")
    print("• README.md               - Updated project info") 
    print("• config.py               - All configuration options")
    
    print("\n🤝 SUPPORT:")
    print("-" * 12) 
    print("• GitHub Issues: Report bugs and request features")
    print("• Documentation: https://aj-geddes.github.io/python-mcp-server-template/")
    
    print("\n" + "="*60)
    print("Happy coding! 🚀")
    print("="*60 + "\n")

def main():
    """Main setup wizard."""
    print_banner()
    
    try:
        # Collect information
        config = collect_basic_info()
        branding = collect_branding_info() 
        tools_info = collect_tools_info()
        
        # Update files
        print("🔧 Updating configuration files...")
        update_config_file(config, branding)
        update_readme(config)
        create_example_tool(config)
        
        # Show next steps
        print_next_steps(config)
        
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()