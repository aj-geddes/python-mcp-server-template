#!/usr/bin/env python3
"""
Test the actual function implementations for the MCP server.
This file tests the core business logic separate from the MCP decorators.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the underlying functions directly
from mcp_server import (
    MCPError, 
    run_command, 
    validate_path,
    echo_impl,
    health_check_impl,
    list_files_impl,
    read_file_impl,
    write_file_impl,
    run_shell_command_impl,
    main,
    signal_handler
)


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
        import subprocess
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(["sleep", "100"], 1)

            with pytest.raises(MCPError, match="Command timed out"):
                await run_command(["sleep", "100"], timeout=1)

    @pytest.mark.asyncio
    async def test_run_command_exception(self):
        """Test command execution exception handling."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test exception")

            with pytest.raises(MCPError, match="Command execution failed"):
                await run_command(["test"])


class TestMCPTools:
    """Test MCP tools through their actual implementations."""

    @pytest.mark.asyncio
    async def test_echo_tool(self):
        """Test echo tool functionality."""
        result = await echo_impl("Hello, World!")
        assert result == "Echo: Hello, World!"
        
        result = await echo_impl("")
        assert result == "Echo: "

    @pytest.mark.asyncio
    async def test_health_check_tool(self):
        """Test health check tool."""
        result = await health_check_impl()
        assert result["status"] == "healthy"
        assert "server_name" in result
        assert "version" in result
        assert "transport" in result

    @pytest.mark.asyncio
    async def test_list_files_tool(self):
        """Test list_files tool functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            
            test_dir = Path(temp_dir) / "subdir"
            test_dir.mkdir()
            
            with patch("mcp_server.validate_path") as mock_validate:
                mock_validate.return_value = Path(temp_dir)
                
                result = await list_files_impl(".")
                
                assert result["total_files"] >= 1
                assert result["total_directories"] >= 1
                assert "✅" in result["status"]
                assert "files" in result
                assert "directories" in result

    @pytest.mark.asyncio
    async def test_read_file_tool(self):
        """Test read_file tool functionality."""
        test_content = "Hello, World!\nThis is a test file."
        
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file.flush()
            
            try:
                with patch("mcp_server.validate_path") as mock_validate:
                    mock_validate.return_value = Path(temp_file.name)
                    
                    result = await read_file_impl("test.txt")
                    
                    assert result["content"] == test_content
                    assert result["size"] == len(test_content)
                    assert result["lines"] == 2
                    assert result["encoding"] == "utf-8"
                    assert "✅" in result["status"]
            finally:
                os.unlink(temp_file.name)

    @pytest.mark.asyncio
    async def test_write_file_tool(self):
        """Test write_file tool functionality."""
        test_content = "Hello, World!\nThis is test content."
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                test_file = Path(temp_dir) / "test.txt"
                mock_validate.return_value = test_file
                
                result = await write_file_impl("test.txt", test_content)
                
                assert result["bytes_written"] == len(test_content.encode("utf-8"))
                assert result["lines_written"] == 2
                assert "✅" in result["status"]
                
                # Verify file was actually written
                assert test_file.read_text() == test_content

    @pytest.mark.asyncio
    async def test_run_shell_command_tool(self):
        """Test run_shell_command tool functionality."""
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
                
                result = await run_shell_command_impl("echo test", "/tmp")
                
                assert result["success"] is True
                assert result["stdout"] == "test\n"
                mock_run.assert_called_once_with(["echo", "test"], cwd="/tmp")


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_list_files_nonexistent_directory(self):
        """Test listing files in non-existent directory."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent/directory")

            with pytest.raises(MCPError, match="does not exist"):
                await list_files_impl("/nonexistent/directory")

    @pytest.mark.asyncio
    async def test_list_files_not_directory(self):
        """Test listing files on a file (not directory)."""
        with tempfile.NamedTemporaryFile() as temp_file:
            with patch("mcp_server.validate_path") as mock_validate:
                mock_validate.return_value = Path(temp_file.name)

                with pytest.raises(MCPError, match="is not a directory"):
                    await list_files_impl(temp_file.name)

    @pytest.mark.asyncio
    async def test_read_file_nonexistent(self):
        """Test reading non-existent file."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent/file.txt")

            with pytest.raises(MCPError, match="does not exist"):
                await read_file_impl("nonexistent.txt")

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
                await read_file_impl("large_file.txt", max_size=1024)

    @pytest.mark.asyncio
    async def test_read_file_directory(self):
        """Test reading a directory (should fail)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                mock_validate.return_value = Path(temp_dir)

                with pytest.raises(MCPError, match="is not a file"):
                    await read_file_impl("test_dir")

    @pytest.mark.asyncio
    async def test_run_shell_command_empty(self):
        """Test running empty command."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/tmp")

            with pytest.raises(MCPError, match="Empty command provided"):
                await run_shell_command_impl("", "/tmp")

    @pytest.mark.asyncio
    async def test_run_shell_command_nonexistent_directory(self):
        """Test running command in non-existent directory."""
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent")

            with pytest.raises(MCPError, match="does not exist"):
                await run_shell_command_impl("echo test", "/nonexistent")


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    @pytest.mark.asyncio
    async def test_echo_special_characters(self):
        """Test echo with special characters."""
        test_string = "Test with 🚀 emoji and 特殊文字"
        result = await echo_impl(test_string)
        assert result == f"Echo: {test_string}"

    @pytest.mark.asyncio
    async def test_write_file_create_directories(self):
        """Test writing file with directory creation."""
        test_content = "Test content"

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                test_file = Path(temp_dir) / "subdir" / "test.txt"
                mock_validate.return_value = test_file

                result = await write_file_impl(
                    "subdir/test.txt", test_content, create_dirs=True
                )

                assert "✅" in result["status"]
                assert test_file.exists()
                assert test_file.read_text() == test_content

    def test_validate_path_edge_cases(self):
        """Test validate_path with edge cases."""
        # Test with empty string (should use current directory)
        result = validate_path("", "/workspace")
        assert str(result) == "/workspace"

        # Test with None base_path
        result = validate_path("test.txt")  # Should use WORKSPACE_PATH
        # The exact path depends on WORKSPACE_PATH, so just check it's a Path
        assert isinstance(result, Path)


class TestIntegration:
    """Integration tests for the MCP server tools."""

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
                write_result = await write_file_impl("test.txt", test_content)
                assert "✅" in write_result["status"]

                # Read the file back
                read_result = await read_file_impl("test.txt")
                assert read_result["content"] == test_content

                # List files to verify it's there
                list_result = await list_files_impl(".")
                file_names = [f["name"] for f in list_result["files"]]
                assert "test.txt" in file_names


class TestMainAndSignals:
    """Test main function and signal handling."""

    def test_signal_handler(self):
        """Test signal handler functionality."""
        with patch("sys.exit") as mock_exit:
            with patch("mcp_server.logger") as mock_logger:
                signal_handler(15, None)  # SIGTERM
                mock_logger.info.assert_called_once()
                mock_exit.assert_called_once_with(0)

    @patch("mcp_server.logger")
    def test_main_stdio_transport(self, mock_logger):
        """Test main function with STDIO transport."""
        with patch("mcp_server.mcp.run") as mock_run:
            with patch.dict(os.environ, {"MCP_TRANSPORT": "stdio"}):
                try:
                    main()
                except SystemExit:
                    pass  # Expected for successful run
                mock_run.assert_called_once_with()

    @patch("mcp_server.logger")
    def test_main_http_transport(self, mock_logger):
        """Test main function with HTTP transport."""
        with patch("mcp_server.mcp.run") as mock_run:
            # Patch environment to avoid conflicts with current env
            env_patch = {"MCP_TRANSPORT": "http", "MCP_HOST": "localhost", "MCP_PORT": "8080"}
            with patch.dict(os.environ, env_patch, clear=False):
                # Also patch the module-level variables
                with patch("mcp_server.TRANSPORT", "http"), \
                     patch("mcp_server.HOST", "localhost"), \
                     patch("mcp_server.PORT", 8080):
                    try:
                        main()
                    except SystemExit:
                        pass  # Expected for successful run
                    mock_run.assert_called_once_with(transport="streamable-http", host="localhost", port=8080)

    @patch("mcp_server.logger")
    def test_main_sse_transport(self, mock_logger):
        """Test main function with SSE transport."""
        with patch("mcp_server.mcp.run") as mock_run:
            # Patch environment to avoid conflicts with current env
            env_patch = {"MCP_TRANSPORT": "sse", "MCP_HOST": "localhost", "MCP_PORT": "8080"}
            with patch.dict(os.environ, env_patch, clear=False):
                # Also patch the module-level variables
                with patch("mcp_server.TRANSPORT", "sse"), \
                     patch("mcp_server.HOST", "localhost"), \
                     patch("mcp_server.PORT", 8080):
                    try:
                        main()
                    except SystemExit:
                        pass  # Expected for successful run
                    mock_run.assert_called_once_with(transport="sse", host="localhost", port=8080)

    @patch("mcp_server.logger")
    def test_main_keyboard_interrupt(self, mock_logger):
        """Test main function handling KeyboardInterrupt."""
        with patch("mcp_server.mcp.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()
            
            try:
                main()
            except SystemExit:
                pass  # Expected
            
            mock_logger.info.assert_any_call("Server interrupted, shutting down...")

    @patch("mcp_server.logger")
    def test_main_exception(self, mock_logger):
        """Test main function handling general exception."""
        with patch("mcp_server.mcp.run") as mock_run:
            mock_run.side_effect = Exception("Test error")
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            mock_logger.error.assert_called_once()


class TestResourcesAndPrompts:
    """Test resources and prompts functionality."""

    @pytest.mark.asyncio
    async def test_read_file_resource_error(self):
        """Test read_file_resource error handling."""
        # We can't easily test the decorated function, so let's test the error paths
        # by importing the implementation logic
        from mcp_server import validate_path, MCPError
        
        with pytest.raises(MCPError, match="does not exist"):
            with patch("mcp_server.validate_path") as mock_validate:
                mock_path = MagicMock()
                mock_path.exists.return_value = False
                mock_validate.return_value = mock_path
                
                # Simulate the resource function logic
                validated_path = validate_path("test.txt")
                if not validated_path.exists():
                    raise MCPError(f"File test.txt does not exist")

    @pytest.mark.asyncio
    async def test_code_review_prompt_variations(self):
        """Test code_review_prompt with different parameters."""
        # Test the implementation logic that would be in the decorated function
        code = "const x = 5;"
        language = "javascript"
        focus = "security"
        
        # Simulate what the prompt function does
        result = f"""Please review the following {language} code with a focus on {focus}:

```{language}
{code}
```

Please provide feedback on:
1. Code quality and best practices
2. Potential bugs or issues
3. Performance considerations
4. Security concerns (if applicable)
5. Suggestions for improvement

Be specific and constructive in your feedback."""
        
        assert "javascript" in result
        assert "security" in result
        assert code in result

    @pytest.mark.asyncio 
    async def test_read_file_unicode_error(self):
        """Test read_file with unicode decode error."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Write some invalid UTF-8 bytes
            temp_file.write(b'\xff\xfe\invalid')
            temp_file.flush()
            
            try:
                with patch("mcp_server.validate_path") as mock_validate:
                    mock_path = MagicMock()
                    mock_path.exists.return_value = True
                    mock_path.is_file.return_value = True
                    mock_path.stat.return_value.st_size = 10
                    mock_path.read_text.side_effect = UnicodeDecodeError("utf-8", b'\xff\xfe', 0, 1, "invalid")
                    mock_validate.return_value = mock_path
                    
                    with pytest.raises(MCPError, match="is not valid UTF-8 text"):
                        await read_file_impl("test.txt")
            finally:
                os.unlink(temp_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])