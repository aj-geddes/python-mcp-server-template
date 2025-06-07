# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-07

### Added
- **Code of Conduct**: Simple, clear community guidelines (CODE_OF_CONDUCT.md)
- **Comprehensive Test Suite**: 80%+ code coverage with pytest framework
- **Coverage Reporting**: HTML and XML coverage reports with GitHub Actions integration
- **Professional Test Structure**: Moved to tests/ directory with proper pytest organization
- **GitHub Actions Integration**: Automated coverage reporting and artifact uploads
- **Codecov Integration**: Automated coverage tracking and reporting
- **Enhanced CI/CD**: Improved testing workflow with coverage requirements

### Changed
- **BREAKING**: Moved test_server.py to tests/test_mcp_server.py
- **Enhanced GitHub Actions**: Now includes coverage reporting and stricter quality gates
- **Improved Documentation**: Added coverage badges and testing information to README
- **Development Workflow**: Added coverage requirements (80% minimum) to development process

### Testing
- Unit tests for all core functions with comprehensive edge case coverage
- Integration tests for complete file operation workflows
- Async testing support with pytest-asyncio
- Coverage reporting with fail-under threshold of 80%
- Comprehensive error handling and input validation tests
- Mock-based testing for isolated unit testing

### Security
- Enhanced path validation testing with directory traversal prevention
- Security-focused test coverage for all input validation functions
- Comprehensive error handling validation and exception testing

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
- GitHub Actions workflow for code quality
- Issue templates and pull request templates
- Security policy and contributing guidelines

### Security
- Path validation prevents directory traversal attacks
- File size limits prevent memory exhaustion
- Command execution timeouts prevent hanging processes
- Non-root Docker user for container security
- Input validation and sanitization

## [Unreleased]

### Planned
- Configuration file support with YAML/JSON
- Structured logging configuration
- Performance monitoring and metrics
- Additional example tools and use cases
- PyPI package publication
- Documentation website with MkDocs
- Performance benchmarks and load testing examples
