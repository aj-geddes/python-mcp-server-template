# Contributing to Python MCP Server Template

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide clear reproduction steps** for bugs
4. **Include environment information** (Python version, OS, Docker version)

### Suggesting Features

1. **Check if the feature already exists** in the codebase
2. **Open an issue** with the "enhancement" label
3. **Describe the use case** and expected behavior
4. **Consider backward compatibility** implications

### Pull Requests

1. **Fork the repository** and create a feature branch
2. **Follow the coding standards** outlined below
3. **Write or update tests** for your changes
4. **Update documentation** if needed
5. **Ensure all checks pass** before submitting

## 🏗️ Development Setup

### Local Environment

```bash
# Clone your fork
git clone https://github.com/your-username/python-mcp-server-template.git
cd python-mcp-server-template

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (if you add any)
pip install pytest black flake8 mypy
```

### Docker Environment

```bash
# Build the development image
docker build -t mcp-server-dev .

# Run development container
docker run -it --rm -v $(pwd):/workspace mcp-server-dev bash
```

## 📝 Coding Standards

### Python Style

- **Follow PEP 8** for Python code style
- **Use type hints** for all function parameters and return values
- **Write docstrings** for all public functions and classes
- **Use async/await** for all MCP tools and operations
- **Handle exceptions** properly with custom MCPError

### Code Format

```python
@mcp.tool()
async def example_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """
    Brief description of what the tool does.
    
    Args:
        param1: Description of the first parameter
        param2: Description of the second parameter with default value
        
    Returns:
        Dictionary containing the results and status
        
    Raises:
        MCPError: When the operation fails
    """
    try:
        # Implementation here
        result = perform_operation(param1, param2)
        
        return {
            "result": result,
            "status": "✅ Success"
        }
    except Exception as e:
        raise MCPError(f"Operation failed: {str(e)}")
```

### Error Handling

- **Always use MCPError** for tool-related errors
- **Provide meaningful error messages** that help users understand the issue
- **Include context** in error messages (file paths, command names, etc.)
- **Don't expose internal errors** to users unless necessary

### Security Guidelines

- **Validate all inputs** using the `validate_path()` function
- **Use timeouts** for long-running operations
- **Limit resource usage** (file sizes, memory, etc.)
- **Sanitize user inputs** before using in commands or file operations

### Documentation

- **Update README.md** for new features
- **Add docstrings** for all public functions
- **Include examples** in docstrings when helpful
- **Update CHANGELOG.md** for notable changes

## 🧪 Testing

### Manual Testing

```bash
# Test the server locally
python mcp_server.py

# Test Docker build
./build.sh

# Test individual tools (implementation depends on your MCP client)
```

### Automated Testing (Future)

```bash
# Run tests (when implemented)
pytest

# Check code style
black --check .
flake8 .

# Type checking
mypy mcp_server.py
```

## 🚀 Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backward-compatible functionality additions
- **PATCH**: Backward-compatible bug fixes

### Release Steps

1. **Update version** in `mcp_server.py`
2. **Update CHANGELOG.md** with new version and changes
3. **Test thoroughly** with Docker and local environments
4. **Create release tag**: `git tag v1.x.x`
5. **Push tag**: `git push origin v1.x.x`

## 🎯 Contribution Areas

### High Priority

- **Unit tests** and test coverage
- **Configuration file** support (YAML/JSON)
- **Logging configuration** with different levels
- **Performance monitoring** and metrics
- **CI/CD pipeline** templates

### Medium Priority

- **Additional example tools** for common use cases
- **Plugin system** for extending functionality
- **Better error recovery** and graceful failures
- **Documentation improvements** and tutorials

### Low Priority

- **Web UI** for server management
- **Multiple transport methods** (HTTP, WebSocket)
- **Clustering support** for high availability
- **Advanced security features** (OAuth, JWT)

## 📋 Code Review Checklist

### For Contributors

- [ ] Code follows the style guidelines
- [ ] All functions have type hints and docstrings
- [ ] Error handling uses MCPError appropriately
- [ ] Security considerations are addressed
- [ ] Documentation is updated
- [ ] Manual testing is performed

### For Reviewers

- [ ] Code is readable and well-structured
- [ ] Security implications are considered
- [ ] Performance impact is acceptable
- [ ] Backward compatibility is maintained
- [ ] Documentation is accurate and complete

## 🆘 Getting Help

### Resources

- **FastMCP Documentation**: [GitHub](https://github.com/jlowin/fastmcp)
- **MCP Specification**: [Official Site](https://modelcontextprotocol.io/)
- **Python Type Hints**: [Official Docs](https://docs.python.org/3/library/typing.html)

### Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Email**: Contact maintainers for security issues

## 🙏 Recognition

Contributors will be recognized in:
- **CHANGELOG.md**: For significant contributions
- **README.md**: For major features or ongoing maintenance
- **GitHub releases**: In release notes

Thank you for contributing to make this template better for everyone! 🎉
