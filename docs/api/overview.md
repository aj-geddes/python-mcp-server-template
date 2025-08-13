---
layout: default
title: "API Reference"
description: "Complete documentation for all MCP tools, resources, and prompts"
---

Complete documentation for all MCP tools, resources, and prompts in the template.

## Tools

### Health Check

Check server status and configuration.

**Function**: `health_check()`

```python
@mcp.tool()
async def health_check() -> Dict[str, Any]:
    """Returns server health and configuration information."""
```

**Response**:
```json
{
  "status": "healthy",
  "server_name": "template-server",
  "version": "2.0.0",
  "transport": "stdio",
  "workspace": "/workspace",
  "timestamp": "1692123456.789",
  "rate_limiting_enabled": true,
  "metrics_enabled": true,
  "structured_logging": true
}
```

### Echo

Simple echo tool for testing connectivity.

**Function**: `echo(message: str)`

```python
@mcp.tool()
async def echo(message: str) -> str:
    """Echoes the provided message back to the client."""
```

**Parameters**:
- `message` (string): Message to echo back

**Response**: `"Echo: {message}"`

### List Files

List files and directories in a specified path.

**Function**: `list_files(directory: str = ".")`

```python
@mcp.tool()
async def list_files(directory: str = ".") -> Dict[str, Any]:
    """List files and directories in the specified path."""
```

**Parameters**:
- `directory` (string, optional): Directory to list (default: current directory)

**Response**:
```json
{
  "directory": "/workspace/example",
  "files": [
    {"name": "file1.txt", "size": 1024, "type": "file"},
    {"name": "file2.py", "size": 2048, "type": "file"}
  ],
  "directories": [
    {"name": "subdir", "type": "directory"}
  ],
  "total_files": 2,
  "total_directories": 1,
  "status": "✅ Success"
}
```

**Security**: Path validation prevents directory traversal attacks.

### Read File

Read the contents of a file.

**Function**: `read_file(file_path: str, max_size: int = 1024 * 1024)`

```python
@mcp.tool()
async def read_file(file_path: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
    """Read file contents with size limits and encoding validation."""
```

**Parameters**:
- `file_path` (string): Path to the file to read
- `max_size` (integer, optional): Maximum file size in bytes (default: 1MB)

**Response**:
```json
{
  "file_path": "/workspace/example.txt",
  "content": "File contents here...",
  "size": 256,
  "lines": 10,
  "encoding": "utf-8",
  "status": "✅ Success"
}
```

**Security**: 
- Path validation prevents unauthorized access
- Size limits prevent memory exhaustion
- UTF-8 validation prevents binary file issues

### Write File

Write content to a file.

**Function**: `write_file(file_path: str, content: str, create_dirs: bool = True)`

```python
@mcp.tool()
async def write_file(file_path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    """Write content to a file with optional directory creation."""
```

**Parameters**:
- `file_path` (string): Path where to write the file
- `content` (string): Content to write
- `create_dirs` (boolean, optional): Create parent directories if needed (default: true)

**Response**:
```json
{
  "file_path": "/workspace/output.txt",
  "bytes_written": 1024,
  "lines_written": 25,
  "status": "✅ Success"
}
```

**Security**: Path validation ensures files are written within allowed directories.

### Run Shell Command

Execute shell commands in a controlled environment.

**Function**: `run_shell_command(command: str, directory: str = ".")`

```python
@mcp.tool()
async def run_shell_command(command: str, directory: str = ".") -> Dict[str, Any]:
    """Execute shell commands with security controls and monitoring."""
```

**Parameters**:
- `command` (string): Shell command to execute
- `directory` (string, optional): Working directory (default: current directory)

**Response**:
```json
{
  "command": "ls -la",
  "directory": "/workspace",
  "stdout": "total 8\ndrwxr-xr-x 2 user user 4096 Aug 13 01:30 .\n...",
  "stderr": "",
  "success": true,
  "return_code": 0,
  "duration": 0.123,
  "status": "✅ Success"
}
```

**Security**:
- Commands run in validated directories only
- 30-second timeout prevents hanging processes
- Full command logging for audit trails

## Resources

### File Resource

Access files through MCP resource protocol.

**Resource**: `file://{path}`

```python
@mcp.resource("file://{path}")
async def read_file_resource(path: str) -> str:
    """Provide file access through MCP resource protocol."""
```

**Usage**: `mcp://file:///workspace/example.txt`

**Security**: Same path validation as file tools.

## Prompts

### Code Review Prompt

Generate structured code review prompts.

**Function**: `code_review_prompt(code: str, language: str = "python", focus: str = "general")`

```python
@mcp.prompt()
async def code_review_prompt(code: str, language: str = "python", focus: str = "general") -> str:
    """Generate comprehensive code review prompts."""
```

**Parameters**:
- `code` (string): Code to review
- `language` (string, optional): Programming language (default: "python")
- `focus` (string, optional): Review focus area (default: "general")

**Response**: Formatted code review prompt with:
1. Code quality and best practices
2. Potential bugs or issues  
3. Performance considerations
4. Security concerns
5. Improvement suggestions

## Error Handling

All tools implement consistent error handling:

### Error Types

**MCPError**: Base exception for all MCP-related errors
```python
class MCPError(Exception):
    """Base exception for MCP server errors."""
    pass

class RateLimitExceeded(MCPError):
    """Raised when rate limit is exceeded."""
    pass
```

### Common Error Responses

**Path Validation Errors**:
```json
{
  "error": "Path ../../../etc/passwd is outside allowed directory",
  "type": "MCPError"
}
```

**Rate Limiting Errors**:
```json
{
  "error": "Rate limit exceeded for read_file", 
  "type": "RateLimitExceeded"
}
```

**File Operation Errors**:
```json
{
  "error": "File /path/to/file.txt does not exist",
  "type": "MCPError"  
}
```

## Monitoring Integration

All tools include built-in monitoring:

### Metrics

**Request Counters**:
- `mcp_requests_total{tool="read_file", status="success"}`
- `mcp_requests_total{tool="read_file", status="error"}`
- `mcp_requests_total{tool="read_file", status="rate_limited"}`

**Duration Histograms**:
- `mcp_request_duration_seconds{tool="read_file"}`

**Command Execution**:
- `mcp_commands_total{status="success"}`
- `mcp_commands_total{status="failed"}`
- `mcp_commands_total{status="timeout"}`

### Structured Logging

**Request Started**:
```json
{
  "event": "tool_request_started",
  "tool": "read_file",
  "request_id": "read_file_1692123456789",
  "args": 2,
  "kwargs": ["file_path", "max_size"]
}
```

**Request Completed**:
```json
{
  "event": "tool_request_completed",
  "tool": "read_file", 
  "request_id": "read_file_1692123456789",
  "duration": 0.123
}
```

**Request Failed**:
```json
{
  "event": "tool_request_failed",
  "tool": "read_file",
  "request_id": "read_file_1692123456789", 
  "duration": 0.089,
  "error": "File not found",
  "error_type": "MCPError"
}
```

## Rate Limiting

All tools are protected by configurable rate limiting:

```python
@with_monitoring("tool_name")
async def tool_impl():
    """Rate limiting is automatically applied via decorator"""
```

**Configuration**:
- `MCP_RATE_LIMIT=100/minute` (default)
- `MCP_RATE_LIMIT=1000/hour` 
- `MCP_RATE_LIMIT=0` (disable)

**Per-client limiting** using client identification from request context.

---

For implementation examples, see the [Development Guide](../development/setup.md).