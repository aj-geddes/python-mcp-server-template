# Use the official UV Python image with Python 3.12
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/workspace/.venv/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create a non-root user
RUN useradd -m -s /bin/bash mcpuser && \
    mkdir -p /workspace /tmp/mcp-logs && \
    chown -R mcpuser:mcpuser /workspace /tmp/mcp-logs

# Switch to non-root user
USER mcpuser
WORKDIR /workspace

# Copy requirements file
COPY --chown=mcpuser:mcpuser requirements.txt .

# Create a local virtual environment and install Python dependencies using UV
RUN uv venv .venv && \
    uv pip install -r requirements.txt

# Copy the rest of the application
COPY --chown=mcpuser:mcpuser . .

# Make the main script executable
# Old way we converted to a more modular way
#RUN chmod +x mcp_server.py

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD .venv/bin/python -c "import sys; sys.exit(0)" || exit 1

# Expose the default MCP port (if needed for future transport methods)
EXPOSE 8080

# Default command using venv Python
CMD ["python", "mcp_server.py"]
