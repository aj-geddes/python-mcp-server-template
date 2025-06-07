# Python MCP Server Template

A production-ready template for creating MCP (Model Context Protocol) servers using the FastMCP framework.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker (optional, for containerized deployment)
- Git (for version control)

### Local Development

1. **Clone or create your project:**
   ```bash
   git clone <your-repo-url>
   cd python-mcp-server-template
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python mcp_server.py
   ```

### Docker Deployment

1. **Build the Docker image:**
   ```bash
   # Linux/macOS
   ./build.sh

   # Windows
   build.bat
   ```

2. **Run the container:**
   ```bash
   docker run -it --rm python-mcp-server-template:latest
   ```

## 🛠️ Available Tools

The template includes several built-in tools to demonstrate FastMCP capabilities:

### Core Tools

- **`echo`** - Echo a message back (useful for testing)
- **`list_files`** - List files and directories in a given path
- **`read_file`** - Read file contents with size limits and encoding validation
- **`write_file`** - Write content to files with directory creation support
- **`run_shell_command`** - Execute shell commands safely in specified directories

### Resources

- **`file://{path}`** - Read files as MCP resources using URI-style addressing

### Prompts

- **`code_review_prompt`** - Generate structured code review prompts with customizable focus areas

## 🏗️ Architecture

### FastMCP Framework

This template uses [FastMCP](https://github.com/jlowin/fastmcp) which provides:

- **Decorators**: `@mcp.tool()`, `@mcp.resource()`, `@mcp.prompt()`
- **Type Safety**: Full Python type hints and validation
- **Error Handling**: Custom exception classes with user-friendly messages
- **Async Support**: Built-in async/await support for all operations

### Security Features

- **Path Validation**: All file operations are validated against a base directory
- **Command Restrictions**: Shell commands are executed with proper timeouts and error handling
- **File Size Limits**: Configurable limits for file read operations
- **Non-root Execution**: Docker container runs as non-root user

## 📁 Project Structure

```
python-mcp-server-template/
├── mcp_server.py          # Main FastMCP server implementation
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── build.sh              # Linux/macOS build script
├── build.bat             # Windows build script
├── .gitignore           # Git ignore patterns
├── README.md            # This file
└── [your custom tools]   # Add your own tools here
```

## 🔧 Customization

### Adding New Tools

1. **Create a new tool function:**
   ```python
   @mcp.tool()
   async def my_custom_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
       """
       Description of what your tool does.
       
       Args:
           param1: Description of param1
           param2: Description of param2 with default value
           
       Returns:
           Dictionary with results
       """
       try:
           # Your tool logic here
           result = do_something(param1, param2)
           
           return {
               "result": result,
               "status": "✅ Success"
           }
       except Exception as e:
           raise MCPError(f"Tool failed: {str(e)}")
   ```

2. **Add the function to your server file**
3. **Test your tool with the echo tool first**

### Adding Resources

```python
@mcp.resource("my-resource://{identifier}")
async def my_resource(identifier: str) -> str:
    """Read data as a resource."""
    # Implement your resource logic
    return "resource content"
```

### Adding Prompts

```python
@mcp.prompt()
async def my_prompt_template(context: str, task: str) -> str:
    """Generate a prompt for a specific task."""
    return f"Given this context: {context}\nPlease: {task}"
```

### Configuration

Modify these constants in `mcp_server.py`:

```python
SERVER_NAME = "your-server-name"  # Change this to your server name
VERSION = "1.0.0"                 # Update version as needed
```

## 🐳 Docker Configuration

The Dockerfile follows security best practices:

- **Base Image**: `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`
- **Non-root User**: Runs as `mcpuser`
- **Health Checks**: Built-in container health monitoring
- **Optimized Layers**: Efficient Docker layer caching
- **Security**: Minimal attack surface with only required packages

### Build Arguments

```bash
docker build \
  --build-arg VERSION=1.0.0 \
  -t your-server-name:1.0.0 \
  .
```

## 🧪 Testing

### Manual Testing

1. **Test with echo tool:**
   ```bash
   # In one terminal, start the server
   python mcp_server.py
   
   # In another terminal, test with MCP client
   # (Tool-specific testing depends on your MCP client)
   ```

2. **Docker testing:**
   ```bash
   # Build and test automatically
   ./build.sh
   ```

### Integration Testing

The template includes validation for:
- Path security (prevents directory traversal)
- File size limits
- Command timeouts
- Error handling

## 📝 Best Practices

### Error Handling

Always use the custom `MCPError` exception:

```python
try:
    result = risky_operation()
except SomeException as e:
    raise MCPError(f"Operation failed: {str(e)}")
```

### Path Validation

Use the built-in `validate_path()` function:

```python
safe_path = validate_path(user_input, base_path="/workspace")
```

### Async Operations

All tools should be async:

```python
@mcp.tool()
async def my_tool():  # Note: async
    result = await async_operation()
    return result
```

### Documentation

Follow the docstring pattern:

```python
@mcp.tool()
async def tool_name(param: str) -> Dict[str, Any]:
    """
    Brief description.
    
    Args:
        param: Parameter description
        
    Returns:
        Description of return value
    """
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Permission denied on build.sh:**
   ```bash
   chmod +x build.sh
   ```

3. **Docker build failures:**
   - Check Docker daemon is running
   - Ensure you have sufficient disk space
   - Try `docker system prune` to clean up

4. **Path validation errors:**
   - Ensure file paths are relative to the working directory
   - Check that files exist before accessing them

### Debug Mode

Add debug logging to your tools:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

@mcp.tool()
async def debug_tool():
    logging.debug("Debug information here")
```

## 🔗 Links

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Happy coding! 🎉**
