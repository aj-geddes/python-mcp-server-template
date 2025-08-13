# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a production-ready Python MCP (Model Context Protocol) server template built with the FastMCP framework. The project includes comprehensive testing, Docker containerization, security-first design, and automated CI/CD workflows.

## Development Commands

### Package Management
```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install with optional dev dependencies
pip install -e ".[dev]"
```

### Code Quality & Testing
```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Type checking with mypy
mypy mcp_server/

# Linting with flake8
flake8 mcp_server/

# Security analysis with bandit
bandit -r mcp_server/

# Run tests with pytest
pytest

# Run tests with coverage report
pytest --cov=mcp_server --cov-report=term-missing --cov-report=html

# Run specific test markers
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

### Build & Docker
```bash
# Build Docker image
./build.sh [version]

# Quick build test only
./test_build_only.sh

# Production build with testing
./build-it.sh

# Run production tests
./test-production.sh

# Debug container interactively
./debug-container.sh
```

### Running the Server
```bash
# Run locally with STDIO transport (default)
python mcp_server.py

# Run with HTTP transport
MCP_TRANSPORT=http MCP_PORT=8080 python mcp_server.py

# Run in Docker
docker run -it --rm python-mcp-server-template:latest

# Run with custom workspace
docker run -v /path/to/workspace:/workspace python-mcp-server-template:latest
```

## Architecture

### Core Components

- **`mcp_server/__init__.py`**: Main server implementation using FastMCP framework
- **`mcp_server.py`**: Entry point script that imports and runs the server
- **`mcp_server/__main__.py`**: Alternative entry point for module execution

### Key Features

1. **FastMCP Integration**: Built on FastMCP 2.0+ framework for modern MCP server development
2. **Security First**: Path validation, directory traversal protection, command execution safeguards
3. **Environment Configuration**: Uses environment variables for transport, host, port, and workspace settings
4. **Structured Logging**: Rich console output with proper log levels and formatting
5. **Error Handling**: Custom MCPError exception with comprehensive error reporting

### Available Tools

- `health_check()`: Server health and status information
- `echo(message)`: Simple echo functionality for testing
- `list_files(directory)`: Safe directory listing with metadata
- `read_file(file_path, max_size)`: Secure file reading with size limits
- `write_file(file_path, content, create_dirs)`: File writing with directory creation
- `run_shell_command(command, directory)`: Sandboxed command execution

### Available Resources

- `file://{path}`: File resource access with path validation

### Available Prompts

- `code_review_prompt(code, language, focus)`: Structured code review prompting

### Environment Variables

- `MCP_SERVER_NAME`: Server name (default: "template-server")
- `MCP_TRANSPORT`: Transport type - "stdio", "http", "sse" (default: "stdio")
- `MCP_HOST`: Host for HTTP transport (default: "0.0.0.0")
- `MCP_PORT`: Port for HTTP transport (default: "8080")
- `WORKSPACE_PATH`: Base path for file operations (default: "/workspace")

### Testing Strategy

The project uses pytest with comprehensive test coverage:
- Unit tests for individual functions
- Integration tests for complete workflows
- Mock-based testing for external dependencies
- Coverage tracking with 80%+ requirement
- Async test support with pytest-asyncio

### Docker Configuration

Multiple Docker approaches are available:
- **`Dockerfile`**: Main production build
- **`Dockerfile.fixed`**: Alternative fixed approach
- **`Dockerfile.alternative`**: Alternative implementation
- **`docker-compose.yml`**: Container orchestration

### Security Considerations

- Path validation prevents directory traversal attacks
- Command execution is sandboxed with timeout limits
- File size limits prevent resource exhaustion
- Environment-based configuration avoids hardcoded secrets
- Bandit security scanning integrated into CI/CD

## Development Notes

- The project uses semantic versioning with pinned major versions
- Code style enforced with Black (88 character line length)
- Import sorting handled by isort with Black profile
- Type hints required for all function definitions
- Rich library used for enhanced console output and logging