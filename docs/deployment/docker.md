# Docker Deployment Guide

Production-ready Docker deployment with security hardening and monitoring.

## Quick Start

```bash
# Build and run
docker build -t mcp-server .
docker run -p 8080:8080 -p 9090:9090 mcp-server
```

## Production Docker Configuration

### Dockerfile Features

✅ **Security Hardened**
- Non-root user execution (`mcpuser`)
- Specific version tags (no `:latest`)
- Minimal attack surface
- Proper file ownership

✅ **Production Optimized**  
- Multi-stage builds for size optimization
- Health checks with FastMCP validation
- Signal handling for graceful shutdown
- Environment-based configuration

### Build Options

**Standard Build (Recommended)**:
```bash
# Using UV Python image
docker build -t mcp-server .
```

**Alternative Build**:
```bash
# Using standard Python image
docker build -f Dockerfile.alternative -t mcp-server .
```

## Environment Configuration

### Required Environment Variables

```bash
# Server Configuration
MCP_SERVER_NAME=production-server
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8080

# Security
MCP_RATE_LIMIT=1000/minute
WORKSPACE_PATH=/workspace

# Monitoring
MCP_METRICS_PORT=9090
```

### Production .env File

```env
# Server Identity
MCP_SERVER_NAME=my-production-server
MCP_TRANSPORT=http
MCP_HOST=0.0.0.0
MCP_PORT=8080

# Security Configuration
MCP_RATE_LIMIT=1000/minute
WORKSPACE_PATH=/app/workspace

# Monitoring & Observability
MCP_METRICS_PORT=9090
PYTHONUNBUFFERED=1

# Resource Limits
MCP_MAX_FILE_SIZE=10485760
MCP_COMMAND_TIMEOUT=30
```

## Docker Compose Deployment

### Basic Production Stack

```yaml
# docker-compose.yml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8080:8080"
      - "9090:9090"
    environment:
      - MCP_SERVER_NAME=production-server
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_RATE_LIMIT=1000/minute
    volumes:
      - ./workspace:/workspace
      - ./logs:/tmp/mcp-logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "from fastmcp import FastMCP; import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
```

### Full Production Stack with Monitoring

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mcp-server:
    build: .
    ports:
      - "8080:8080"
    environment:
      - MCP_SERVER_NAME=production-server
      - MCP_TRANSPORT=http
      - MCP_HOST=0.0.0.0
      - MCP_RATE_LIMIT=1000/minute
      - MCP_METRICS_PORT=9090
    volumes:
      - workspace:/workspace
      - logs:/tmp/mcp-logs
    restart: unless-stopped
    networks:
      - mcp-network
    depends_on:
      - prometheus

  prometheus:
    image: prom/prometheus:v2.45.0
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - mcp-network

  grafana:
    image: grafana/grafana:10.0.0
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=secure-password-here
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - mcp-network

  nginx:
    image: nginx:1.25-alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - mcp-server
    networks:
      - mcp-network

volumes:
  workspace:
  logs:
  prometheus_data:
  grafana_data:

networks:
  mcp-network:
    driver: bridge
```

## Security Configuration

### Container Security

**Security Options**:
```yaml
security_opt:
  - no-new-privileges:true    # Prevent privilege escalation
  - apparmor:docker-default   # Use AppArmor profile
  - seccomp:default          # Use seccomp profile

# Read-only filesystem
read_only: true
tmpfs:
  - /tmp:noexec,nosuid,size=100m
```

**User Security**:
```dockerfile
# Dockerfile includes
RUN useradd -m -s /bin/bash mcpuser
USER mcpuser

# Runtime override if needed
docker run --user 1000:1000 mcp-server
```

### Network Security

**Internal Network**:
```yaml
networks:
  mcp-internal:
    driver: bridge
    internal: true  # No external access
```

**Reverse Proxy Configuration** (`nginx.conf`):
```nginx
upstream mcp-backend {
    server mcp-server:8080;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=mcp:10m rate=10r/s;
    limit_req zone=mcp burst=20 nodelay;
    
    location / {
        proxy_pass http://mcp-backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 30s;
    }
    
    # Metrics endpoint (restrict access)
    location /metrics {
        allow 10.0.0.0/8;   # Internal networks only
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
        
        proxy_pass http://mcp-backend:9090;
    }
}
```

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mcp-server'
    static_configs:
      - targets: ['mcp-server:9090']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']
```

### Grafana Dashboard

Key metrics to monitor:

```json
{
  "dashboard": {
    "title": "MCP Server Metrics",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(mcp_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate", 
        "targets": [
          {
            "expr": "rate(mcp_requests_total{status=\"error\"}[5m])"
          }
        ]
      },
      {
        "title": "Request Duration",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(mcp_request_duration_seconds_bucket[5m]))"
          }
        ]
      },
      {
        "title": "Rate Limit Violations",
        "targets": [
          {
            "expr": "rate(mcp_requests_total{status=\"rate_limited\"}[5m])"
          }
        ]
      }
    ]
  }
}
```

## Deployment Commands

### Development

```bash
# Build and run for development
docker build -t mcp-server-dev .
docker run -it --rm \
  -p 8080:8080 \
  -p 9090:9090 \
  -v $(pwd):/workspace \
  -e MCP_TRANSPORT=http \
  mcp-server-dev
```

### Staging

```bash
# Deploy to staging
docker-compose -f docker-compose.staging.yml up -d

# Check logs
docker-compose logs -f mcp-server

# Run security scan
docker exec mcp-server python security_scan.py
```

### Production

```bash
# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl -f http://localhost:8080/health || exit 1

# Monitoring check
curl -f http://localhost:9090/metrics | head -20
```

## Health Checks and Monitoring

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from fastmcp import FastMCP; import sys; sys.exit(0)" || exit 1
```

### External Health Monitoring

```bash
#!/bin/bash
# health-check.sh

HEALTH_URL="http://localhost:8080/health"
METRICS_URL="http://localhost:9090/metrics"

# Check health endpoint
if ! curl -f -s "$HEALTH_URL" > /dev/null; then
    echo "Health check failed"
    exit 1
fi

# Check metrics endpoint  
if ! curl -f -s "$METRICS_URL" | grep -q "mcp_requests_total"; then
    echo "Metrics check failed"
    exit 1
fi

echo "All checks passed"
```

## Troubleshooting

### Common Issues

**Container won't start**:
```bash
# Check logs
docker logs <container-id>

# Check resource usage
docker stats <container-id>

# Inspect configuration
docker inspect <container-id>
```

**Port conflicts**:
```bash
# Check what's using the port
netstat -tulpn | grep :8080

# Use different port
docker run -p 8081:8080 mcp-server
```

**Permission errors**:
```bash
# Fix file ownership
sudo chown -R 1000:1000 ./workspace

# Run with specific user
docker run --user 1000:1000 mcp-server
```

**Memory issues**:
```bash
# Set memory limits
docker run -m 512m mcp-server

# Monitor memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Performance Optimization

**Multi-stage builds** for smaller images:
```dockerfile
# Build stage
FROM python:3.12-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage  
FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
```

**Resource limits**:
```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

## Security Scanning

Run security scans on containers:

```bash
# Scan image for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $HOME/Library/Caches:/root/.cache/ \
  aquasec/trivy:latest image mcp-server

# Run application security scan
docker exec mcp-server python security_scan.py
```

---

*For advanced Kubernetes deployment, see the [Kubernetes Guide](kubernetes.md).*