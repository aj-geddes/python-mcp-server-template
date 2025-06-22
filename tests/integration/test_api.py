"""
Integration tests for the MCP server.
Tests focus on the API endpoints and request handling.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.integration
def test_mcp_endpoint_echo(client, mcp_request_sample):
    """Test the MCP endpoint with the echo tool."""
    # Modify the sample request to use echo tool
    request_data = mcp_request_sample.copy()
    request_data["toolName"] = "echo"
    request_data["parameters"] = "Hello from integration test"
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["result"] == "Echo: Hello from integration test"


@pytest.mark.integration
def test_mcp_endpoint_invalid_tool(client, mcp_request_sample):
    """Test the MCP endpoint with an invalid tool."""
    # Modify the sample request to use a non-existent tool
    request_data = mcp_request_sample.copy()
    request_data["toolName"] = "non_existent_tool"
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "Unknown tool" in data["error"]


@pytest.mark.integration
def test_mcp_endpoint_invalid_parameters(client, mcp_request_sample):
    """Test the MCP endpoint with invalid parameters."""
    # Modify the sample request to use echo tool with invalid parameters
    request_data = mcp_request_sample.copy()
    request_data["toolName"] = "echo"
    # Echo expects a string, but we're sending an object
    request_data["parameters"] = {"invalid": "parameter structure"}
    
    response = client.post("/mcp", json=request_data)
    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"


@pytest.mark.integration
def test_docs_endpoint(client):
    """Test the documentation endpoint (OpenAPI)."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    
    # Also test the OpenAPI JSON schema
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    schema = response.json()
    assert "paths" in schema
    assert "/mcp" in schema["paths"]
