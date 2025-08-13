# Development Setup

Complete guide for contributing to and extending the MCP server template.

## Prerequisites

- **Python 3.10+** (3.12 recommended)
- **Git** for version control
- **Docker** (optional but recommended)
- **IDE** with Python support (VS Code, PyCharm, etc.)

## Development Environment

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/aj-geddes/python-mcp-server-template.git
cd python-mcp-server-template

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt
pip install -r requirements.txt
```

### 2. Development Dependencies

```bash
# Core testing and development tools
pytest>=8.0.0
pytest-asyncio>=0.25.0
pytest-cov>=6.0.0
coverage[toml]>=7.6.0

# Code quality
mypy>=1.13.0
black>=24.0.0
isort>=5.13.0
flake8>=7.1.0

# Security tools
bandit[toml]>=1.7.0
safety>=3.2.0

# Optional enhanced tools
structlog>=24.4.0
prometheus-client>=0.21.0
limits>=3.13.0
rich>=13.9.0
```

### 3. IDE Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

**PyCharm Configuration**:
- Set Python interpreter to `./venv/bin/python`
- Enable pytest as test runner
- Configure MyPy as external tool
- Set Black as code formatter

## Development Workflow

### 1. Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mcp_server --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_mcp_server.py -v

# Run tests matching pattern
pytest tests/ -k "test_health" -v
```

**Coverage Goals**:
- **Target**: >95% coverage
- **Current**: ~72% (functional but improving)
- **Priority Areas**: Core functionality, error handling, security

### 2. Code Quality Checks

```bash
# Type checking with MyPy
mypy mcp_server/ --ignore-missing-imports

# Code formatting with Black
black mcp_server/ tests/

# Import sorting with isort
isort mcp_server/ tests/

# Linting with flake8
flake8 mcp_server/ tests/

# Security scan with Bandit
bandit -r mcp_server/ -f json

# Comprehensive security scan
python security_scan.py
```

### 3. Development Server

```bash
# Run in development mode with auto-reload
python -m mcp_server

# Run with HTTP transport for testing
MCP_TRANSPORT=http MCP_HOST=127.0.0.1 MCP_PORT=8080 python mcp_server.py

# Run with enhanced logging
PYTHONUNBUFFERED=1 python mcp_server.py
```

### 4. Docker Development

```bash
# Build development image
docker build -t mcp-server-dev .

# Run with volume mounting for live development
docker run -v $(pwd):/workspace -p 8080:8080 mcp-server-dev

# Run with docker-compose for full stack
docker-compose -f docker-compose.dev.yml up
```

## Project Structure

```
python-mcp-server-template/
├── mcp_server/              # Main server package
│   ├── __init__.py         # Core server implementation
│   └── __main__.py         # Entry point module
├── tests/                  # Test suite
│   ├── test_mcp_server.py  # Main functionality tests
│   ├── test_server.py      # Server lifecycle tests
│   └── ...                 # Additional test modules
├── docs/                   # Documentation (GitHub Pages)
├── security_scan.py        # Automated security scanning
├── benchmark.py            # Performance benchmarking
├── monitoring.py           # Advanced monitoring tools
├── requirements*.txt       # Dependency specifications
├── pyproject.toml         # Project configuration
├── Dockerfile             # Production container
└── docker-compose.yml     # Multi-service orchestration
```

## Adding New Tools

### 1. Basic Tool Implementation

```python
# In mcp_server/__init__.py

@with_monitoring("my_new_tool")
async def my_new_tool_impl(param1: str, param2: int = 10) -> Dict[str, Any]:
    """Implementation function with monitoring."""
    try:
        # Your business logic here
        result = f"Processed {param1} with {param2}"
        
        return {
            "result": result,
            "status": "✅ Success",
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise MCPError(f"Tool failed: {str(e)}")

@mcp.tool()
async def my_new_tool(param1: str, param2: int = 10) -> Dict[str, Any]:
    """User-facing tool function."""
    result: Dict[str, Any] = await my_new_tool_impl(param1, param2)
    return result
```

### 2. Tool Testing

```python
# In tests/test_my_tool.py

import pytest
from mcp_server import my_new_tool_impl, MCPError

@pytest.mark.asyncio
async def test_my_new_tool_success():
    """Test successful tool execution."""
    result = await my_new_tool_impl("test", 5)
    
    assert result["status"] == "✅ Success"
    assert "test" in result["result"]
    assert result["timestamp"] > 0

@pytest.mark.asyncio
async def test_my_new_tool_error_handling():
    """Test error handling."""
    with pytest.raises(MCPError):
        await my_new_tool_impl("", -1)  # Invalid inputs
```

### 3. Security Considerations

**Input Validation**:
```python
def validate_input(param: str) -> str:
    """Validate and sanitize inputs."""
    if not param or len(param.strip()) == 0:
        raise MCPError("Parameter cannot be empty")
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"]', '', param.strip())
    return sanitized
```

**Path Operations**:
```python
async def secure_file_operation(file_path: str) -> Dict[str, Any]:
    """Always use validate_path for file operations."""
    try:
        validated_path = validate_path(file_path)
        # Safe to proceed with validated_path
        return {"path": str(validated_path)}
    except Exception as e:
        raise MCPError(f"Invalid path: {str(e)}")
```

## Testing Guidelines

### 1. Test Structure

```python
import pytest
from unittest.mock import patch, AsyncMock
from mcp_server import tool_function_impl, MCPError

class TestMyTool:
    """Test suite for my_tool functionality."""
    
    @pytest.mark.asyncio
    async def test_happy_path(self):
        """Test normal operation."""
        # Setup
        # Execute  
        # Assert
        
    @pytest.mark.asyncio
    async def test_error_conditions(self):
        """Test error handling."""
        # Test various error scenarios
        
    @pytest.mark.asyncio  
    async def test_edge_cases(self):
        """Test boundary conditions."""
        # Test edge cases and limits
```

### 2. Mocking External Dependencies

```python
@patch('mcp_server.subprocess.run')
@pytest.mark.asyncio
async def test_command_execution(mock_run):
    """Test command execution with mocked subprocess."""
    # Mock the subprocess.run call
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "success"
    mock_run.return_value.stderr = ""
    
    result = await run_command_impl(["echo", "test"])
    assert result["success"] is True
```

### 3. Async Testing Patterns

```python
@pytest.mark.asyncio
async def test_async_operations():
    """Test asynchronous operations properly."""
    # Use await for async functions
    result = await async_function()
    
    # Use AsyncMock for async mocks
    with patch('mcp_server.async_dep', new_callable=AsyncMock) as mock:
        mock.return_value = "mocked"
        result = await function_using_async_dep()
        mock.assert_called_once()
```

## Performance Considerations

### 1. Benchmarking New Features

```python
# Add benchmark for new tools
import time

@with_monitoring("performance_test")
async def benchmark_my_tool():
    """Benchmark tool performance."""
    start = time.time()
    
    # Run tool multiple times
    for _ in range(100):
        await my_new_tool_impl("test", 10)
    
    duration = time.time() - start
    return {
        "tool": "my_new_tool",
        "iterations": 100,
        "total_duration": duration,
        "avg_duration": duration / 100
    }
```

### 2. Memory Usage

```python
import tracemalloc

async def test_memory_usage():
    """Test memory usage of tools."""
    tracemalloc.start()
    
    # Run your tool
    await my_new_tool_impl("test", 10)
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    assert peak < 10 * 1024 * 1024  # Less than 10MB
```

## Security Testing

### 1. Input Validation Tests

```python
@pytest.mark.asyncio
async def test_path_traversal_prevention():
    """Test directory traversal attack prevention."""
    dangerous_paths = [
        "../../../etc/passwd",
        "/etc/passwd", 
        "\\..\\..\\windows\\system32"
    ]
    
    for path in dangerous_paths:
        with pytest.raises(MCPError, match="outside allowed directory"):
            await read_file_impl(path)
```

### 2. Rate Limiting Tests

```python
@patch('mcp_server.RATE_LIMITER')
@pytest.mark.asyncio
async def test_rate_limiting(mock_limiter):
    """Test rate limiting behavior."""
    mock_limiter.hit.return_value = False  # Simulate rate limit exceeded
    
    with pytest.raises(RateLimitExceeded):
        await my_tool_impl("test")
```

## Contributing Guidelines

### 1. Code Standards

- **Black** formatting (line length 100)
- **isort** import organization
- **MyPy** type checking compliance
- **Comprehensive docstrings** for all public functions
- **Security-first** development approach

### 2. Commit Messages

```bash
# Format: <type>(<scope>): <description>
feat(tools): add new file compression tool
fix(security): resolve path validation vulnerability  
docs(api): update tool documentation
test(coverage): add missing test cases
security(scan): enhance automated security checks
```

### 3. Pull Request Process

1. **Create feature branch** from `master`
2. **Implement changes** with tests
3. **Run all checks**: `make check` (or manual)
4. **Update documentation** as needed
5. **Submit pull request** with description
6. **Address review feedback**
7. **Squash and merge** when approved

### 4. Documentation Updates

When adding features:
- Update API documentation in `docs/api/`
- Add examples to quickstart guide
- Update security considerations if applicable
- Test documentation with GitHub Pages locally

## Troubleshooting

### Common Development Issues

**Import Errors**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements-dev.txt
```

**Test Failures**:
```bash
# Run specific failing test with verbose output
pytest tests/test_failing.py::test_function -vvs

# Check test dependencies
pip install pytest-asyncio
```

**Type Errors**:
```bash
# Install type stubs
pip install types-requests types-setuptools

# Run MyPy on specific file
mypy mcp_server/__init__.py --show-error-codes
```

**Docker Issues**:
```bash
# Rebuild without cache
docker build --no-cache -t mcp-server-dev .

# Check container logs
docker logs <container-id>
```

## Support and Community

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support  
- **Security Issues**: Follow responsible disclosure in SECURITY.md
- **Documentation**: Contribute to docs/ directory

---

*Happy coding! 🚀*