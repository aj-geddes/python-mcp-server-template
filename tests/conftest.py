"""Test configuration for python-mcp-server-template."""

import pytest
from fastapi.testclient import TestClient

# Import your app here - adjust as needed for your specific structure
try:
    from mcp_server.server import app
except ImportError:
    # Fallback import paths
    try:
        from mcp_server import app
    except ImportError:
        try:
            from mcp_server_official import app
        except ImportError:
            # Create a mock app for tests to run
            from fastapi import FastAPI
            app = FastAPI()


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mcp_request_sample():
    """Return a sample MCP request for testing."""
    return {
        "toolName": "sample_tool",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    }
