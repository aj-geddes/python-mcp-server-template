#!/usr/bin/env python3
"""
Unit tests for the basic MCP server functionality.
Tests focus on individual tool implementations.
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Import the tools for testing
from mcp_server import MCPError, echo, list_files, read_file, write_file


@pytest.mark.unit
async def test_echo():
    """Test the echo tool."""
    test_message = "Hello, MCP Server!"
    result = await echo(test_message)

    expected = f"Echo: {test_message}"
    assert result == expected, f"Expected '{expected}', got '{result}'"


@pytest.mark.unit
async def test_file_write():
    """Test the file write operation."""
    test_content = "This is a test file.\nLine 2\nLine 3"
    test_file = "test_output.txt"

    write_result = await write_file(test_file, test_content)
    assert write_result["status"] == "✅ Success"


@pytest.mark.unit
async def test_file_read(tmp_path):
    """Test the file read operation."""
    # Create a test file
    test_content = "This is a test file.\nLine 2\nLine 3"
    test_file = tmp_path / "test_read.txt"
    test_file.write_text(test_content)
    
    # Test reading the file
    read_result = await read_file(str(test_file))
    assert read_result["content"] == test_content
    assert read_result["status"] == "✅ Success"


@pytest.mark.unit
async def test_list_files(tmp_path):
    """Test the list files operation."""
    # Create some test files
    (tmp_path / "file1.txt").write_text("File 1")
    (tmp_path / "file2.txt").write_text("File 2")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "file3.txt").write_text("File 3")
    
    # Test listing files
    list_result = await list_files(str(tmp_path))
    file_names = [f["name"] for f in list_result["files"]]
    
    assert "file1.txt" in file_names
    assert "file2.txt" in file_names
    assert "subdir" in file_names


@pytest.mark.unit
async def test_error_handling():
    """Test error handling for file operations."""
    # Test reading non-existent file
    with pytest.raises(MCPError) as excinfo:
        await read_file("non_existent_file.txt")
    
    assert "does not exist" in str(excinfo.value)


@pytest.mark.unit
async def test_path_validation():
    """Test path validation security."""
    # Test directory traversal attempt
    with pytest.raises(MCPError) as excinfo:
        await read_file("../../../etc/passwd")
    
    assert "outside allowed directory" in str(excinfo.value)
