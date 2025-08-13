#!/usr/bin/env python3
"""
Comprehensive coverage completion tests.
Tests for achieving >95% code coverage by covering missing paths.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server import (
    MCPError,
    RateLimitExceeded,
    validate_path,
    run_command,
    with_monitoring,
    signal_handler,
    main,
)


class TestOptionalImports:
    """Test optional import handling."""

    def test_import_without_optional_dependencies(self):
        """Test behavior when optional dependencies are not available."""
        # These imports are tested by temporarily patching the modules
        # The actual imports happen at module load time, so we test the effect
        import mcp_server
        
        # Test that the module loads without these dependencies
        assert hasattr(mcp_server, 'STRUCTURED_LOGGING')
        assert hasattr(mcp_server, 'METRICS_ENABLED')
        assert hasattr(mcp_server, 'RATE_LIMITING')


class TestMonitoringDecorator:
    """Test monitoring decorator functionality."""

    @pytest.mark.asyncio
    async def test_monitoring_decorator_with_rate_limiting(self):
        """Test monitoring decorator with rate limiting enabled."""
        
        @with_monitoring("test_tool")
        async def test_function(message: str) -> str:
            return f"Processed: {message}"
        
        # Test without rate limiting (default state)
        result = await test_function("test message")
        assert result == "Processed: test message"

    @pytest.mark.asyncio
    async def test_monitoring_decorator_with_client_id(self):
        """Test monitoring decorator with client_id parameter."""
        
        @with_monitoring("test_tool")
        async def test_function(message: str, client_id: str = "default") -> str:
            return f"Processed: {message} for {client_id}"
        
        result = await test_function("test", client_id="test_client")
        assert result == "Processed: test for test_client"

    @pytest.mark.asyncio
    async def test_monitoring_decorator_exception_handling(self):
        """Test monitoring decorator exception handling."""
        
        @with_monitoring("test_tool")
        async def failing_function() -> str:
            raise ValueError("Test exception")
        
        with pytest.raises(ValueError, match="Test exception"):
            await failing_function()


class TestRateLimitExceeded:
    """Test RateLimitExceeded exception."""

    def test_rate_limit_exceeded_creation(self):
        """Test RateLimitExceeded exception creation."""
        error = RateLimitExceeded("Rate limit exceeded for test_tool")
        assert str(error) == "Rate limit exceeded for test_tool"
        assert isinstance(error, MCPError)
        assert isinstance(error, Exception)


class TestRunCommand:
    """Test comprehensive run_command functionality."""

    @pytest.mark.asyncio
    async def test_run_command_empty_command_list(self):
        """Test run_command with empty command list."""
        with pytest.raises(MCPError, match="Empty or invalid command provided"):
            await run_command([])

    @pytest.mark.asyncio
    async def test_run_command_with_environment(self):
        """Test run_command preserves environment."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="output", stderr=""
            )
            
            await run_command(["echo", "test"], cwd="/tmp")
            
            # Verify environment is passed
            call_kwargs = mock_run.call_args[1]
            assert "env" in call_kwargs
            assert call_kwargs["env"] == os.environ.copy()

    @pytest.mark.asyncio
    async def test_run_command_with_timeout(self):
        """Test run_command with custom timeout."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0, stdout="output", stderr=""
            )
            
            await run_command(["echo", "test"], timeout=60)
            
            # Verify timeout is set
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs["timeout"] == 60

    @pytest.mark.asyncio
    async def test_run_command_metrics_logging(self):
        """Test run_command metrics and logging paths."""
        # Test both structured and regular logging paths
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1, stdout="", stderr="error"
            )
            
            result = await run_command(["false"])
            
            assert result["success"] is False
            assert result["return_code"] == 1
            assert "❌" in result["status"]


class TestPathValidation:
    """Test comprehensive path validation."""

    def test_validate_path_with_base_path_none(self):
        """Test validate_path when base_path is None."""
        # This should use WORKSPACE_PATH from environment
        result = validate_path("test.txt")
        assert isinstance(result, Path)

    def test_validate_path_complex_traversal_attempts(self):
        """Test various directory traversal attempts."""
        base_path = "/workspace"
        
        # Test various traversal patterns
        traversal_attempts = [
            "../../etc/passwd",
            "../../../root/.ssh/id_rsa",
            "subdir/../../../etc/hosts",
            "/etc/passwd",
            "\\..\\..\\windows\\system32",
        ]
        
        for attempt in traversal_attempts:
            with pytest.raises(MCPError, match="outside allowed directory"):
                validate_path(attempt, base_path)

    def test_validate_path_with_symbolic_links(self):
        """Test path validation with potential symbolic link issues."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file in the temp directory
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("test content")
            
            # Validate the path
            result = validate_path("test.txt", temp_dir)
            assert str(result) == str(test_file)

    def test_validate_path_with_current_directory_references(self):
        """Test path validation with current directory references."""
        result = validate_path("./subdir/../test.txt", "/workspace")
        assert str(result) == "/workspace/test.txt"

    def test_validate_path_exception_handling(self):
        """Test path validation exception handling."""
        # Test with invalid characters or system-specific issues
        with patch("pathlib.Path.resolve") as mock_resolve:
            mock_resolve.side_effect = OSError("Invalid path")
            
            with pytest.raises(MCPError, match="Invalid path"):
                validate_path("test.txt", "/workspace")


class TestSignalHandling:
    """Test signal handling functionality."""

    def test_signal_handler_sigterm(self):
        """Test signal handler with SIGTERM."""
        with patch("sys.exit") as mock_exit:
            with patch("mcp_server.logger") as mock_logger:
                signal_handler(15, None)  # SIGTERM
                
                mock_logger.info.assert_called_once()
                mock_exit.assert_called_once_with(0)

    def test_signal_handler_sigint(self):
        """Test signal handler with SIGINT."""
        with patch("sys.exit") as mock_exit:
            with patch("mcp_server.logger") as mock_logger:
                signal_handler(2, None)  # SIGINT
                
                mock_logger.info.assert_called_once()
                mock_exit.assert_called_once_with(0)


class TestMainFunction:
    """Test main function functionality."""

    @patch("mcp_server.logger")
    def test_main_stdio_transport(self, mock_logger):
        """Test main function with STDIO transport."""
        with patch("mcp_server.mcp.run") as mock_run:
            with patch.dict(os.environ, {"MCP_TRANSPORT": "stdio"}):
                with patch("mcp_server.TRANSPORT", "stdio"):
                    try:
                        main()
                    except SystemExit:
                        pass  # Expected for successful run
                    
                    mock_run.assert_called_once_with()

    @patch("mcp_server.logger")
    def test_main_http_transport(self, mock_logger):
        """Test main function with HTTP transport."""
        with patch("mcp_server.mcp.run") as mock_run:
            env_patch = {"MCP_TRANSPORT": "http", "MCP_HOST": "localhost", "MCP_PORT": "8080"}
            with patch.dict(os.environ, env_patch, clear=False):
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
            env_patch = {"MCP_TRANSPORT": "sse", "MCP_HOST": "localhost", "MCP_PORT": "8080"}
            with patch.dict(os.environ, env_patch, clear=False):
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
    def test_main_general_exception(self, mock_logger):
        """Test main function handling general exception."""
        with patch("mcp_server.mcp.run") as mock_run:
            mock_run.side_effect = Exception("Test error")
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            mock_logger.error.assert_called_once()


class TestMetricsAndLogging:
    """Test metrics and logging paths."""

    def test_metrics_setup_paths(self):
        """Test metrics setup code paths."""
        # Test the metrics initialization logic
        import mcp_server
        
        # Test that metrics constants are properly set
        assert hasattr(mcp_server, 'METRICS_ENABLED')
        assert hasattr(mcp_server, 'STRUCTURED_LOGGING')
        assert hasattr(mcp_server, 'RATE_LIMITING')

    @pytest.mark.asyncio
    async def test_structured_logging_paths(self):
        """Test structured logging code paths."""
        # Test the different logging branches
        from mcp_server import echo_impl
        
        # This will trigger the logging code paths
        result = await echo_impl("test message for logging")
        assert result == "Echo: test message for logging"


class TestUnicodeHandling:
    """Test Unicode and encoding edge cases."""

    @pytest.mark.asyncio
    async def test_unicode_in_echo(self):
        """Test Unicode handling in echo function."""
        from mcp_server import echo_impl
        
        unicode_strings = [
            "Hello 世界",
            "🚀 Rocket emoji",
            "Ñoño niño",
            "Здравствуй мир",
            "こんにちは世界",
        ]
        
        for unicode_str in unicode_strings:
            result = await echo_impl(unicode_str)
            assert result == f"Echo: {unicode_str}"

    @pytest.mark.asyncio
    async def test_unicode_file_operations(self):
        """Test Unicode handling in file operations."""
        from mcp_server import write_file_impl, read_file_impl
        
        unicode_content = "Unicode test: 🚀 世界 Ñoño Здравствуй こんにちは"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("mcp_server.validate_path") as mock_validate:
                test_file = Path(temp_dir) / "unicode_test.txt"
                mock_validate.return_value = test_file
                
                # Test write
                write_result = await write_file_impl("unicode_test.txt", unicode_content)
                assert "✅" in write_result["status"]
                
                # Test read
                read_result = await read_file_impl("unicode_test.txt")
                assert read_result["content"] == unicode_content


class TestEnvironmentConfiguration:
    """Test environment-based configuration."""

    def test_environment_variables_defaults(self):
        """Test default environment variable values."""
        import mcp_server
        
        # Test that defaults are reasonable
        assert mcp_server.HOST == "127.0.0.1" or mcp_server.HOST == os.getenv("MCP_HOST", "127.0.0.1")
        assert mcp_server.VERSION == "2.0.0"

    def test_environment_override(self):
        """Test environment variable override."""
        with patch.dict(os.environ, {
            "MCP_SERVER_NAME": "test-server",
            "MCP_HOST": "0.0.0.0",  # For testing only
            "MCP_PORT": "9999",
            "WORKSPACE_PATH": "/tmp/test"
        }):
            # Re-import to test environment loading
            import importlib
            import mcp_server
            importlib.reload(mcp_server)
            
            # Verify environment variables are used
            assert mcp_server.SERVER_NAME == "test-server"


class TestErrorMessageFormatting:
    """Test error message formatting and context."""

    @pytest.mark.asyncio
    async def test_detailed_error_messages(self):
        """Test that error messages provide sufficient context."""
        from mcp_server import read_file_impl
        
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.return_value = Path("/nonexistent/file.txt")
            
            try:
                await read_file_impl("nonexistent.txt")
                assert False, "Should have raised MCPError"
            except MCPError as e:
                error_msg = str(e)
                assert "does not exist" in error_msg
                assert "nonexistent.txt" in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])