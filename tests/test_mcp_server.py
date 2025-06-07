#!/usr/bin/env python3
"""
Comprehensive test suite for the MCP server template.
Tests for high coverage and functionality validation.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

# Import our server modules
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import (
    MCPError,
    echo,
    list_files,
    read_file,
    write_file,
    run_shell_command,
    validate_path,
    run_command,
    code_review_prompt,
    read_file_resource,
)


class TestMCPError:
    """Test custom MCPError exception."""

    def test_mcp_error_creation(self):
        """Test MCPError can be created and has correct message."""
        error = MCPError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)


class TestValidatePath:
    """Test path validation functionality."""

    def test_validate_path_simple(self):
        """Test basic path validation."""
        result = validate_path("test.txt", "/workspace")
        assert str(result) == "/workspace/test.txt"

    def test_validate_path_subdirectory(self):
        """Test path validation with subdirectories."""
        result = validate_path("subdir/test.txt", "/workspace")
        assert str(result) == "/workspace/subdir/test.txt"

    def test_validate_path_traversal_blocked(self):
        """Test that directory traversal is blocked."""
        with pytest.raises(MCPError, match="outside allowed directory"):
            validate_path("../../../etc/passwd", "/workspace")

    def test_validate_path_absolute_blocked(self):
        """Test that absolute paths outside base are blocked."""
        with pytest.raises(MCPError, match="outside allowed directory"):
            validate_path("/etc/passwd", "/workspace")

    def test_validate_path_current_dir(self):
        """Test validation with current directory reference."""
        result = validate_path("./test.txt", "/workspace")
        assert str(result) == "/workspace/test.txt"


class TestRunCommand:
    """Test command execution functionality."""

    @pytest.mark.asyncio
    async def test_run_command_success(self):
        """Test successful command execution."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="success output", stderr=""
            )

            result = await run_command(["echo", "test"], cwd="/tmp")

            assert result["success"] is True
            assert result["stdout"] == "success output"
            assert result["stderr"] == ""
            assert result["command"] == "echo test"
            assert result["directory"] == "/tmp"
            assert "✅" in result["status"]

    @pytest.mark.asyncio
    async def test_run_command_failure(self):
        """Test failed command execution."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="error output"
            )

            result = await run_command(["false"])

            assert result["success"] is False
            assert result["stderr"] == "error output"
            assert result["return_code"] == 1
            assert "❌" in result["status"]

    @pytest.mark.asyncio
    async def test_run_command_timeout(self):
        """Test command timeout handling."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = asyncio.TimeoutError()

            with pytest.raises(MCPError, match="Command timed out"):
                await run_command(["sleep", "100"], timeout=1)

    @pytest.mark.asyncio
    async def test_run_command_exception(self):
        """Test command execution exception handling."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test exception")

            with pytest.raises(MCPError, match="Command execution failed"):
                await run_command(["test"])


class TestEcho:
    """Test echo tool functionality."""

    @pytest.mark.asyncio
    async def test_echo_basic(self):
        """Test basic echo functionality."""
        result = await echo("Hello, World!")
        assert result == "Echo: Hello, World!"

    @pytest.mark.asyncio
    async def test_echo_empty_string(self):
        """Test echo with empty string."""
        result = await echo("")
        assert result == "Echo: "

    @pytest.mark.asyncio
    async def test_echo_special_characters(self):
        """Test echo with special characters."""
        test_string = "Test with 🚀 emoji and 特殊文字"
        result = await echo(test_string)
        assert result == f"Echo: {test_string}"


class TestListFiles:
    """Test list_files tool functionality."""

    @pytest.mark.asyncio
    async def test_list_files_success(self):
        """Test successful file listing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")

            test_dir = Path(temp_dir) / "subdir"
            test_dir.mkdir()

            with patch("mcp_server.validate_path") as mock_validate:
                mock_validate.return_value = Path(temp_dir)

                result = await list_files(".")

                assert result["total_files"] >= 1
                assert result["total_directories"] >= 1
                assert "✅" in result["status"]
                assert "files" in result
                assert "directories" in result

    @pytest.mark.asyncio
    async def test_list_files_nonexistent_directory(self):
        """Test listing files in non-existent directory."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent/directory")

            with pytest.raises(MCPError, match="does not exist"):
                await list_files("/nonexistent/directory")

    @pytest.mark.asyncio
    async def test_list_files_not_directory(self):
        """Test listing files on a file (not directory)."""
        with tempfile.NamedTemporaryFile() as temp_file:
            with patch("mcp_server.validate_path") as mock_validate:
                mock_validate.return_value = Path(temp_file.name)

                with pytest.raises(MCPError, match="is not a directory"):
                    await list_files(temp_file.name)


class TestReadFile:
    """Test read_file tool functionality."""

    @pytest.mark.asyncio
    async def test_read_file_success(self):
        """Test successful file reading."""
        test_content = "Hello, World!\nThis is a test file."

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()

            try:
                with patch("mcp_server.validate_path") as mock_validate:
                    mock_validate.return_value = Path(temp_file.name)

                    result = await read_file("test.txt")

                    assert result["content"] == test_content
                    assert result["size"] == len(test_content)
                    assert result["lines"] == 2
                    assert result["encoding"] == "utf-8"
                    assert "✅" in result["status"]
            finally:
                os.unlink(temp_file.name)

    @pytest.mark.asyncio
    async def test_read_file_nonexistent(self):
        """Test reading non-existent file."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent/file.txt")

            with pytest.raises(MCPError, match="does not exist"):
                await read_file("nonexistent.txt")

    @pytest.mark.asyncio
    async def test_read_file_too_large(self):
        """Test reading file that exceeds size limit."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = True
            mock_path.stat.return_value.st_size = 2 * 1024 * 1024  # 2MB
            mock_validate.return_value = mock_path

            with pytest.raises(MCPError, match="File too large"):
                await read_file("large_file.txt", max_size=1024)

    @pytest.mark.asyncio
    async def test_read_file_directory(self):
        """Test reading a directory (should fail)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                mock_validate.return_value = Path(temp_dir)

                with pytest.raises(MCPError, match="is not a file"):
                    await read_file("test_dir")


class TestWriteFile:
    """Test write_file tool functionality."""

    @pytest.mark.asyncio
    async def test_write_file_success(self):
        """Test successful file writing."""
        test_content = "Hello, World!\nThis is test content."

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                test_file = Path(temp_dir) / "test.txt"
                mock_validate.return_value = test_file

                result = await write_file("test.txt", test_content)

                assert result["bytes_written"] == len(test_content.encode("utf-8"))
                assert result["lines_written"] == 2
                assert "✅" in result["status"]

                # Verify file was actually written
                assert test_file.read_text() == test_content

    @pytest.mark.asyncio
    async def test_write_file_create_directories(self):
        """Test writing file with directory creation."""
        test_content = "Test content"

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                test_file = Path(temp_dir) / "subdir" / "test.txt"
                mock_validate.return_value = test_file

                result = await write_file("subdir/test.txt", test_content, create_dirs=True)

                assert "✅" in result["status"]
                assert test_file.exists()
                assert test_file.read_text() == test_content


class TestRunShellCommand:
    """Test run_shell_command tool functionality."""

    @pytest.mark.asyncio
    async def test_run_shell_command_success(self):
        """Test successful shell command execution."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/tmp")

            with patch("mcp_server.run_command") as mock_run:
                mock_run.return_value = {
                    "command": "echo test",
                    "directory": "/tmp",
                    "stdout": "test\n",
                    "stderr": "",
                    "success": True,
                    "return_code": 0,
                    "status": "✅ Success",
                }

                result = await run_shell_command("echo test", "/tmp")

                assert result["success"] is True
                assert result["stdout"] == "test\n"
                mock_run.assert_called_once_with(["echo", "test"], cwd="/tmp")

    @pytest.mark.asyncio
    async def test_run_shell_command_empty(self):
        """Test running empty command."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/tmp")

            with pytest.raises(MCPError, match="Empty command provided"):
                await run_shell_command("", "/tmp")

    @pytest.mark.asyncio
    async def test_run_shell_command_nonexistent_directory(self):
        """Test running command in non-existent directory."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent")

            with pytest.raises(MCPError, match="does not exist"):
                await run_shell_command("echo test", "/nonexistent")


class TestReadFileResource:
    """Test read_file_resource functionality."""

    @pytest.mark.asyncio
    async def test_read_file_resource_success(self):
        """Test successful file resource reading."""
        test_content = "Resource content"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()

            try:
                with patch("mcp_server.validate_path") as mock_validate:
                    mock_validate.return_value = Path(temp_file.name)

                    result = await read_file_resource("test.txt")
                    assert result == test_content
            finally:
                os.unlink(temp_file.name)

    @pytest.mark.asyncio
    async def test_read_file_resource_nonexistent(self):
        """Test reading non-existent file resource."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent/file.txt")

            with pytest.raises(MCPError, match="does not exist"):
                await read_file_resource("nonexistent.txt")


class TestCodeReviewPrompt:
    """Test code_review_prompt functionality."""

    @pytest.mark.asyncio
    async def test_code_review_prompt_default(self):
        """Test code review prompt with default parameters."""
        test_code = "def hello():\n    print('Hello, World!')"

        result = await code_review_prompt(test_code)

        assert "python" in result
        assert "general" in result
        assert test_code in result
        assert "Please review the following" in result
        assert "Code quality and best practices" in result

    @pytest.mark.asyncio
    async def test_code_review_prompt_custom(self):
        """Test code review prompt with custom parameters."""
        test_code = "const x = 5;"

        result = await code_review_prompt(
            test_code, language="javascript", focus="security"
        )

        assert "javascript" in result
        assert "security" in result
        assert test_code in result

    @pytest.mark.asyncio
    async def test_code_review_prompt_all_languages(self):
        """Test code review prompt with different languages."""
        languages = ["python", "javascript", "java", "go", "rust"]

        for lang in languages:
            result = await code_review_prompt("test code", language=lang)
            assert lang in result


# Integration Tests
class TestIntegration:
    """Integration tests for the MCP server."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete workflow: write, read, list files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                # Setup mock to return paths in temp directory
                def mock_validate_side_effect(path, base_path="/workspace"):
                    return Path(temp_dir) / path

                mock_validate.side_effect = mock_validate_side_effect

                # Write a file
                test_content = "Integration test content"
                write_result = await write_file("test.txt", test_content)
                assert "✅" in write_result["status"]

                # Read the file back
                read_result = await read_file("test.txt")
                assert read_result["content"] == test_content

                # List files to verify it's there
                list_result = await list_files(".")
                file_names = [f["name"] for f in list_result["files"]]
                assert "test.txt" in file_names


# Coverage helper tests
class TestCoverageHelpers:
    """Tests to ensure high coverage of edge cases."""

    def test_imports(self):
        """Test that all imports work correctly."""
        import mcp_server

        assert hasattr(mcp_server, "echo")
        assert hasattr(mcp_server, "list_files")
        assert hasattr(mcp_server, "read_file")
        assert hasattr(mcp_server, "write_file")
        assert hasattr(mcp_server, "run_shell_command")
        assert hasattr(mcp_server, "MCPError")

    @pytest.mark.asyncio
    async def test_error_handling_edge_cases(self):
        """Test various error handling edge cases."""
        # Test validate_path with empty string
        with pytest.raises(MCPError):
            validate_path("", "/workspace")

        # Test validate_path with None (should raise TypeError)
        with pytest.raises(TypeError):
            validate_path(None, "/workspace")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--cov=mcp_server", "--cov-report=term-missing"])
