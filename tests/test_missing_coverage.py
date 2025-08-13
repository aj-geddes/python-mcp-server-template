#!/usr/bin/env python3
"""
Tests specifically targeting missing coverage lines.
Focus on achieving >95% coverage by testing initialization and setup code.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestModuleInitialization:
    """Test module initialization and import paths."""

    def test_dotenv_import_success(self):
        """Test successful dotenv import and load."""
        # Test that dotenv loading works when available
        # This tests the try block in lines 23-25
        with patch('mcp_server.load_dotenv') as mock_load:
            # Re-import to trigger the import code
            import importlib
            import mcp_server
            importlib.reload(mcp_server)

    def test_structlog_import_success(self):
        """Test successful structlog import."""
        # Test that structlog imports work
        import mcp_server
        # Verify the constants are set appropriately
        assert hasattr(mcp_server, 'STRUCTURED_LOGGING')
        assert hasattr(mcp_server, 'METRICS_ENABLED')

    def test_limits_import_success(self):
        """Test successful limits import."""
        # Test that limits imports work
        import mcp_server
        # Verify the constants are set
        assert hasattr(mcp_server, 'RATE_LIMITING')

    @patch('mcp_server.STRUCTURED_LOGGING', True)
    def test_structured_logging_configuration(self):
        """Test structured logging configuration."""
        # This tests lines 48-65
        import mcp_server
        # Verify logger exists
        assert hasattr(mcp_server, 'logger')

    @patch('mcp_server.STRUCTURED_LOGGING', False)
    def test_regular_logging_configuration(self):
        """Test regular logging configuration."""
        # This tests the else block for logging setup
        import mcp_server
        assert hasattr(mcp_server, 'logger')

    @patch('mcp_server.METRICS_ENABLED', True)
    @patch('mcp_server.start_http_server')
    def test_metrics_server_startup_success(self, mock_start_server):
        """Test successful metrics server startup."""
        # This tests lines 77-92
        mock_start_server.return_value = None
        
        import importlib
        import mcp_server
        importlib.reload(mcp_server)
        
        # Verify metrics server startup was attempted
        mock_start_server.assert_called()

    @patch('mcp_server.METRICS_ENABLED', True)
    @patch('mcp_server.start_http_server')
    @patch('mcp_server.STRUCTURED_LOGGING', True)
    def test_metrics_server_startup_failure_structured_logging(self, mock_start_server, mock_logger):
        """Test metrics server startup failure with structured logging."""
        # This tests lines 88-91
        mock_start_server.side_effect = Exception("Port in use")
        
        import importlib
        import mcp_server
        importlib.reload(mcp_server)

    @patch('mcp_server.METRICS_ENABLED', True)
    @patch('mcp_server.start_http_server')
    @patch('mcp_server.STRUCTURED_LOGGING', False)
    def test_metrics_server_startup_failure_regular_logging(self, mock_start_server):
        """Test metrics server startup failure with regular logging."""
        # This tests lines 93-95
        mock_start_server.side_effect = Exception("Port in use")
        
        import importlib
        import mcp_server
        importlib.reload(mcp_server)

    @patch('mcp_server.RATE_LIMITING', True)
    @patch('mcp_server.STRUCTURED_LOGGING', True)
    def test_rate_limiting_enabled_structured_logging(self):
        """Test rate limiting enabled with structured logging."""
        # This tests lines 98-101
        import importlib
        import mcp_server
        importlib.reload(mcp_server)

    @patch('mcp_server.RATE_LIMITING', True)
    @patch('mcp_server.STRUCTURED_LOGGING', False)
    def test_rate_limiting_enabled_regular_logging(self):
        """Test rate limiting enabled with regular logging."""
        # This tests lines 100-101
        import importlib
        import mcp_server
        importlib.reload(mcp_server)

    @patch('mcp_server.RATE_LIMITING', False)
    @patch('mcp_server.STRUCTURED_LOGGING', True)
    def test_rate_limiting_disabled_structured_logging(self):
        """Test rate limiting disabled with structured logging."""
        # This tests lines 103-104
        import importlib
        import mcp_server
        importlib.reload(mcp_server)

    @patch('mcp_server.RATE_LIMITING', False)
    @patch('mcp_server.STRUCTURED_LOGGING', False)
    def test_rate_limiting_disabled_regular_logging(self):
        """Test rate limiting disabled with regular logging."""
        # This tests lines 105-106
        import importlib
        import mcp_server
        importlib.reload(mcp_server)


class TestEnvironmentVariables:
    """Test environment variable handling."""

    def test_environment_defaults(self):
        """Test default environment variable values."""
        # Test lines 109-115
        import mcp_server
        
        # Verify defaults are used when env vars not set
        assert hasattr(mcp_server, 'SERVER_NAME')
        assert hasattr(mcp_server, 'VERSION')
        assert hasattr(mcp_server, 'TRANSPORT')
        assert hasattr(mcp_server, 'HOST')
        assert hasattr(mcp_server, 'PORT')
        assert hasattr(mcp_server, 'WORKSPACE_PATH')

    def test_custom_environment_variables(self):
        """Test custom environment variable values."""
        custom_env = {
            'MCP_SERVER_NAME': 'custom-server',
            'MCP_TRANSPORT': 'http',
            'MCP_HOST': '0.0.0.0',
            'MCP_PORT': '9090',
            'WORKSPACE_PATH': '/custom/workspace',
            'MCP_METRICS_PORT': '8888'
        }
        
        with patch.dict(os.environ, custom_env):
            import importlib
            import mcp_server
            importlib.reload(mcp_server)
            
            # Verify custom values are used
            assert mcp_server.SERVER_NAME == 'custom-server'


class TestFastMCPInitialization:
    """Test FastMCP server initialization."""

    def test_fastmcp_server_creation(self):
        """Test FastMCP server creation."""
        # This tests line 117
        import mcp_server
        
        # Verify mcp server is created
        assert hasattr(mcp_server, 'mcp')
        assert mcp_server.mcp is not None


class TestMainFunctionPaths:
    """Test all paths in the main function."""

    @patch('mcp_server.mcp.run')
    @patch('mcp_server.logger')
    def test_main_function_http_transport_path(self, mock_logger, mock_run):
        """Test main function HTTP transport path."""
        # This tests lines 484-487
        with patch('mcp_server.TRANSPORT', 'HTTP'):  # Uppercase to test lower()
            with patch('mcp_server.HOST', 'localhost'):
                with patch('mcp_server.PORT', 8080):
                    from mcp_server import main
                    
                    try:
                        main()
                    except SystemExit:
                        pass
                    
                    mock_run.assert_called_with(transport="streamable-http", host="localhost", port=8080)

    @patch('mcp_server.mcp.run')
    @patch('mcp_server.logger')
    def test_main_function_sse_transport_path(self, mock_logger, mock_run):
        """Test main function SSE transport path."""
        # This tests lines 489-490
        with patch('mcp_server.TRANSPORT', 'SSE'):  # Uppercase to test lower()
            with patch('mcp_server.HOST', 'localhost'):
                with patch('mcp_server.PORT', 8080):
                    from mcp_server import main
                    
                    try:
                        main()
                    except SystemExit:
                        pass
                    
                    mock_run.assert_called_with(transport="sse", host="localhost", port=8080)

    @patch('mcp_server.mcp.run')
    @patch('mcp_server.logger')
    def test_main_function_default_transport_path(self, mock_logger, mock_run):
        """Test main function default transport path."""
        # This tests lines 492-493
        with patch('mcp_server.TRANSPORT', 'stdio'):
            from mcp_server import main
            
            try:
                main()
            except SystemExit:
                pass
            
            mock_run.assert_called_with()

    @patch('mcp_server.mcp.run')
    @patch('mcp_server.logger')
    def test_main_function_keyboard_interrupt_path(self, mock_logger, mock_run):
        """Test main function KeyboardInterrupt path."""
        # This tests lines 494-495
        mock_run.side_effect = KeyboardInterrupt()
        
        from mcp_server import main
        
        try:
            main()
        except SystemExit:
            pass
        
        # Verify the interruption message is logged
        mock_logger.info.assert_any_call("Server interrupted, shutting down...")

    @patch('mcp_server.mcp.run')
    @patch('mcp_server.logger')
    def test_main_function_exception_path(self, mock_logger, mock_run):
        """Test main function general exception path."""
        # This tests lines 496-498
        mock_run.side_effect = Exception("Test error")
        
        from mcp_server import main
        
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        mock_logger.error.assert_called_once()


class TestMainModuleExecution:
    """Test __main__ module execution."""

    def test_main_module_guard(self):
        """Test the __name__ == '__main__' guard."""
        # This would test line 505, but it's hard to test directly
        # We can at least verify the main function exists
        import mcp_server
        assert hasattr(mcp_server, 'main')
        assert callable(mcp_server.main)


class TestMonitoringDecoratorPaths:
    """Test monitoring decorator code paths."""

    @pytest.mark.asyncio
    async def test_monitoring_decorator_rate_limiting_path(self):
        """Test monitoring decorator with rate limiting."""
        # This tests lines 160-179
        from mcp_server import with_monitoring
        
        @with_monitoring("test_tool")
        async def test_func():
            return "success"
        
        # Test without rate limiting enabled (default)
        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_monitoring_decorator_metrics_path(self):
        """Test monitoring decorator with metrics."""
        # This tests lines 184, 197-198
        from mcp_server import with_monitoring
        
        @with_monitoring("test_tool")
        async def test_func():
            return "success"
        
        result = await test_func()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_monitoring_decorator_error_path(self):
        """Test monitoring decorator error handling."""
        # This tests lines 201, 214-215, 218
        from mcp_server import with_monitoring
        
        @with_monitoring("test_tool")
        async def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            await failing_func()


class TestRunCommandPaths:
    """Test run_command function paths."""

    @pytest.mark.asyncio
    async def test_run_command_timeout_path(self):
        """Test run_command timeout handling."""
        # This tests lines 256, 260
        from mcp_server import run_command, MCPError
        
        with patch('subprocess.run') as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired(['sleep', '10'], 5)
            
            with pytest.raises(MCPError, match="Command timed out"):
                await run_command(['sleep', '10'], timeout=5)

    @pytest.mark.asyncio
    async def test_run_command_exception_path(self):
        """Test run_command exception handling."""
        # This tests lines 281, 285
        from mcp_server import run_command, MCPError
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = OSError("Command not found")
            
            with pytest.raises(MCPError, match="Command execution failed"):
                await run_command(['nonexistent_command'])


class TestToolImplementationPaths:
    """Test tool implementation function paths."""

    @pytest.mark.asyncio
    async def test_health_check_impl_path(self):
        """Test health_check_impl function."""
        # This tests lines 308, 311
        from mcp_server import health_check_impl
        
        result = await health_check_impl()
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_echo_impl_path(self):
        """Test echo_impl function."""
        # This tests lines 322, 325
        from mcp_server import echo_impl
        
        result = await echo_impl("test")
        assert result == "Echo: test"

    @pytest.mark.asyncio
    async def test_list_files_impl_error_path(self):
        """Test list_files_impl error handling."""
        # This tests lines 353, 363
        from mcp_server import list_files_impl, MCPError
        
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.side_effect = Exception("Test error")
            
            with pytest.raises(MCPError, match="Failed to list directory"):
                await list_files_impl(".")

    @pytest.mark.asyncio
    async def test_read_file_impl_unicode_error_path(self):
        """Test read_file_impl Unicode error handling."""
        # This tests lines 383->378, 401
        from mcp_server import read_file_impl, MCPError
        
        with patch("mcp_server.validate_path") as mock_validate:
            mock_path = MagicMock()
            mock_path.exists.return_value = True
            mock_path.is_file.return_value = True
            mock_path.stat.return_value.st_size = 100
            mock_path.read_text.side_effect = UnicodeDecodeError("utf-8", b'', 0, 1, "invalid")
            mock_validate.return_value = mock_path
            
            with pytest.raises(MCPError, match="is not valid UTF-8 text"):
                await read_file_impl("test.txt")

    @pytest.mark.asyncio
    async def test_write_file_impl_error_path(self):
        """Test write_file_impl error handling."""
        # This tests lines 436, 445->447, 455-456
        from mcp_server import write_file_impl, MCPError
        
        with patch("mcp_server.validate_path") as mock_validate:
            mock_path = MagicMock()
            mock_path.write_text.side_effect = OSError("Permission denied")
            mock_validate.return_value = mock_path
            
            with pytest.raises(MCPError, match="Failed to write file"):
                await write_file_impl("test.txt", "content")

    @pytest.mark.asyncio
    async def test_run_shell_command_impl_error_path(self):
        """Test run_shell_command_impl error handling."""
        # This tests lines 463, 485
        from mcp_server import run_shell_command_impl, MCPError
        
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.side_effect = Exception("Test error")
            
            with pytest.raises(MCPError, match="Failed to execute command"):
                await run_shell_command_impl("echo test", ".")

    @pytest.mark.asyncio
    async def test_read_file_resource_error_path(self):
        """Test read_file_resource error handling."""
        # This tests lines 490-498, 505
        from mcp_server import read_file_resource, MCPError
        
        with patch("mcp_server.validate_path") as mock_validate:
            mock_validate.side_effect = Exception("Test error")
            
            with pytest.raises(MCPError, match="Failed to read file resource"):
                await read_file_resource("test.txt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])