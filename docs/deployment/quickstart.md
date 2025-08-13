---
layout: default
title: "Quick Start Guide"
description: "Get your MCP server running in production in under 5 minutes"
---

Get your MCP server running in production in under 5 minutes.

## Prerequisites

- Python 3.10+
- Docker (optional but recommended)
- Git

## Installation

### Method 1: Direct Installation

```bash
# Clone the repository
git clone https://github.com/aj-geddes/python-mcp-server-template.git
cd python-mcp-server-template

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python mcp_server.py
```

### Method 2: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/aj-geddes/python-mcp-server-template.git
cd python-mcp-server-template

# Build and run with Docker
docker build -t mcp-server .
docker run -p 8080:8080 mcp-server
```

### Method 3: Docker Compose

```bash
# Start with full monitoring stack
docker-compose up -d
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_SERVER_NAME` | `template-server` | Server identification |
| `MCP_TRANSPORT` | `stdio` | Transport protocol (`stdio`, `http`, `sse`) |
| `MCP_HOST` | `127.0.0.1` | Bind address (localhost for security) |
| `MCP_PORT` | `8080` | Server port |
| `MCP_RATE_LIMIT` | `100/minute` | Rate limiting configuration |
| `MCP_METRICS_PORT` | `9090` | Prometheus metrics port |
| `WORKSPACE_PATH` | `/workspace` | Working directory path |

### Production Configuration

Create a `.env` file:

```env
MCP_SERVER_NAME=my-production-server
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8080
MCP_RATE_LIMIT=1000/minute
MCP_METRICS_PORT=9090
WORKSPACE_PATH=/app/workspace
```

## Health Check

Verify your server is running:

```bash
# Using the health check tool
curl http://localhost:8080/health

# Expected response
{
  "status": "healthy",
  "server_name": "template-server",
  "version": "2.0.0",
  "transport": "http",
  "workspace": "/workspace",
  "rate_limiting_enabled": true,
  "metrics_enabled": true,
  "structured_logging": true
}
```

## Testing the Server

```bash
# Run the test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mcp_server --cov-report=html
```

## Security Scan

```bash
# Run comprehensive security scan
python security_scan.py

# Expected: SECURE status with A+ grade
```

## Monitoring

Access monitoring endpoints:

- **Metrics**: http://localhost:9090/metrics (Prometheus format)
- **Health**: http://localhost:8080/health
- **Logs**: Structured JSON logs to stdout

## Next Steps

1. **Customize Your Server**: Modify `mcp_server/__init__.py` to add your tools
2. **Security Review**: Check [Security Guide](../security/overview.md)
3. **Production Deployment**: See [Docker Guide](docker.md)
4. **Development**: Follow [Development Setup](../development/setup.md)

## Troubleshooting

### Common Issues

**Server won't start**
```bash
# Check if port is in use
netstat -tulpn | grep :8080

# Use different port
export MCP_PORT=8081
python mcp_server.py
```

**Permission errors**
```bash
# Fix ownership in Docker
docker run --user $(id -u):$(id -g) -v $PWD:/workspace mcp-server
```

**Rate limiting issues**
```bash
# Disable rate limiting for testing
export MCP_RATE_LIMIT=0
```

## Support

- 📚 [Full Documentation](../index.md)
- 🐛 [Report Issues](https://github.com/aj-geddes/python-mcp-server-template/issues)
- 💬 [Community Discussions](https://github.com/aj-geddes/python-mcp-server-template/discussions)