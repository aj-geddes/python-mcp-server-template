#!/usr/bin/env python3
"""
Simple test script for the MCP server template.
This demonstrates basic testing patterns for MCP tools.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the server
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import MCPError, echo, list_files, read_file, write_file


async def test_echo():
    """Test the echo tool."""
    print("🧪 Testing echo tool...")

    test_message = "Hello, MCP Server!"
    result = await echo(test_message)

    expected = f"Echo: {test_message}"
    assert result == expected, f"Expected '{expected}', got '{result}'"

    print("✅ Echo test passed!")


async def test_file_operations():
    """Test file read/write operations."""
    print("🧪 Testing file operations...")

    # Test write
    test_content = "This is a test file.\nLine 2\nLine 3"
    test_file = "test_output.txt"

    write_result = await write_file(test_file, test_content)
    assert write_result["status"] == "✅ Success"
    print("✅ File write test passed!")

    # Test read
    read_result = await read_file(test_file)
    assert read_result["content"] == test_content
    assert read_result["status"] == "✅ Success"
    print("✅ File read test passed!")

    # Test list files (should include our test file)
    list_result = await list_files(".")
    file_names = [f["name"] for f in list_result["files"]]
    assert test_file in file_names
    print("✅ File list test passed!")


async def test_error_handling():
    """Test error handling."""
    print("🧪 Testing error handling...")

    # Test reading non-existent file
    try:
        await read_file("non_existent_file.txt")
        assert False, "Should have raised MCPError"
    except MCPError as e:
        assert "does not exist" in str(e)
        print("✅ Error handling test passed!")


async def test_path_validation():
    """Test path validation security."""
    print("🧪 Testing path validation...")

    # Test directory traversal attempt
    try:
        await read_file("../../../etc/passwd")
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
