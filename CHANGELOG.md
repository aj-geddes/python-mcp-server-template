# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-07

### Added
- Initial release of Python MCP Server Template
- FastMCP framework integration with decorators
- Core tools: echo, list_files, read_file, write_file, run_shell_command
- Resource endpoint for file access via URI
- Code review prompt template
- Docker support with security best practices
- Comprehensive documentation and examples
- Build scripts for Linux/macOS and Windows
- Path validation and security features
- Error handling with custom MCPError exception
- Non-root Docker container execution
- Health checks and monitoring
- MIT License

### Security
- Path validation prevents directory traversal attacks
- File size limits prevent memory exhaustion
- Command execution timeouts prevent hanging processes
- Non-root Docker user for container security
- Input validation and sanitization

## [Unreleased]

### Planned
- Unit tests and test coverage
- Configuration file support
- Logging configuration
- Performance monitoring
- Additional example tools
- CI/CD pipeline templates
