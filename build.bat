@echo off
REM Build script for Python MCP Server Template (Windows)

set IMAGE_NAME=python-mcp-server-template
set VERSION=%1
if "%VERSION%"=="" set VERSION=latest
set FULL_IMAGE_NAME=%IMAGE_NAME%:%VERSION%

echo 🏗️  Building MCP Server Docker image...
echo Image: %FULL_IMAGE_NAME%

REM Build the Docker image
docker build -t "%FULL_IMAGE_NAME%" .
if errorlevel 1 (
    echo ❌ Build failed!
    exit /b 1
)

echo ✅ Build completed successfully!
echo 📦 Image: %FULL_IMAGE_NAME%

REM Test the container
echo 🧪 Testing container startup...
docker run --rm "%FULL_IMAGE_NAME%" python -c "import fastmcp; print('FastMCP imported successfully')"
if errorlevel 1 (
    echo ❌ Container test failed!
    exit /b 1
)

echo ✅ Container test passed!
echo 🎉 Build and test completed successfully!
echo 💡 To run the server: docker run -it --rm %FULL_IMAGE_NAME%
