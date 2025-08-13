#!/usr/bin/env python3
"""
Simple test script for the MCP server template.
This demonstrates basic testing patterns for MCP tools.
"""

import asyncio
import json
import sys
from pathlib import Path
import pytest

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import MCPError, echo_impl, list_files_impl, read_file_impl, write_file_impl


@pytest.mark.asyncio
async def test_echo():
    """Test the echo tool."""
    print("🧪 Testing echo tool...")

    test_message = "Hello, MCP Server!"
    result = await echo_impl(test_message)

    expected = f"Echo: {test_message}"
    assert result == expected, f"Expected '{expected}', got '{result}'"

    print("✅ Echo test passed!")


@pytest.mark.asyncio
async def test_file_operations():
    """Test file read/write operations."""
    print("🧪 Testing file operations...")
    
    import tempfile
    from unittest.mock import patch
    from pathlib import Path

    # Use temporary directory to avoid permission issues
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("mcp_server.validate_path") as mock_validate:
            def mock_validate_side_effect(path, base_path=None):
                return Path(temp_dir) / path
            
            mock_validate.side_effect = mock_validate_side_effect

            # Test write
            test_content = "This is a test file.\nLine 2\nLine 3"
            test_file = "test_output.txt"

            write_result = await write_file_impl(test_file, test_content)
            assert write_result["status"] == "✅ Success"
            print("✅ File write test passed!")

            # Test read
            read_result = await read_file_impl(test_file)
            assert read_result["content"] == test_content
            assert read_result["status"] == "✅ Success"
            print("✅ File read test passed!")

            # Test list files (should include our test file)
            list_result = await list_files_impl(".")
            file_names = [f["name"] for f in list_result["files"]]
            assert test_file in file_names
            print("✅ File list test passed!")


@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling."""
    print("🧪 Testing error handling...")
    
    import tempfile
    from unittest.mock import patch
    from pathlib import Path

    # Use temporary directory to avoid permission issues
    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("mcp_server.validate_path") as mock_validate:
            def mock_validate_side_effect(path, base_path=None):
                return Path(temp_dir) / path
            
            mock_validate.side_effect = mock_validate_side_effect

            # Test reading non-existent file
            try:
                await read_file_impl("non_existent_file.txt")
                assert False, "Should have raised MCPError"
            except MCPError as e:
                assert "does not exist" in str(e)
                print("✅ Error handling test passed!")


@pytest.mark.asyncio
async def test_path_validation():
    """Test path validation security."""
    print("🧪 Testing path validation...")

    # Test directory traversal attempt
    try:
        await read_file_impl("../../../etc/passwd")
        assert False, "Should have raised MCPError for path traversal"
    except MCPError as e:
        assert "outside allowed directory" in str(e)
        print("✅ Path validation test passed!")


async def run_all_tests():
    """Run all tests."""
    print("🚀 Starting MCP Server Template Tests\n")

    tests = [
        test_echo,
        test_file_operations,
        test_error_handling,
        test_path_validation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            failed += 1
        print()

    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(
        f"   📈 Success Rate: {passed}/{passed+failed} ({passed/(passed+failed)*100:.1f}%)"
    )

    if failed > 0:
        print("\n🔍 Some tests failed. Check the output above for details.")
        sys.exit(1)
    else:
        print("\n🎉 All tests passed!")


if __name__ == "__main__":
    # Change to the workspace directory for testing
    import os

    os.chdir("/workspace" if Path("/workspace").exists() else ".")

    asyncio.run(run_all_tests())
