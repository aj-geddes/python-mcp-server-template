@echo off
REM Git commit script for Black formatting fixes
REM Run this script in the project directory: /mnt/workspace/python-mcp-server-template

echo 🔍 Current directory: %CD%
echo 📍 Expected directory: /mnt/workspace/python-mcp-server-template
echo.

REM Check if we're in the right directory
if not exist ".git" (
    echo ❌ Error: Not in a git repository. Please navigate to the project directory first.
    echo    Run: cd /mnt/workspace/python-mcp-server-template
    exit /b 1
)

echo 🔍 Checking git status...
git status --porcelain

echo.
echo 📝 Adding modified files for Black formatting fixes...

REM Add the specific files that were modified for Black formatting
echo Adding tests/test_server.py...
git add tests/test_server.py

echo Adding tests/test_mcp_server.py...
git add tests/test_mcp_server.py

echo Adding examples.py...
git add examples.py

echo.
echo 📋 Checking what will be committed...
git diff --cached --name-only

echo.
echo 🚀 Committing changes...

REM Commit with the detailed message
git commit -m "Fix Black code formatting issues

- Fix spacing and blank lines in tests/test_server.py
- Rewrite tests/test_mcp_server.py with proper Black formatting
- Apply Black formatting standards to examples.py
- Remove trailing whitespace across all files
- Add proper function parameter spacing and trailing commas
- Ensure compliance with 88-character line length

Resolves GitHub Actions CI formatting check failures.
Closes Black formatting violations found in lint workflow."

if %ERRORLEVEL% equ 0 (
    echo.
    echo ✅ Successfully committed changes!
    
    echo.
    echo 📋 Verifying commit...
    echo Latest commit:
    git log --oneline -n 1
    
    echo.
    echo Files changed in this commit:
    git diff HEAD~1 --name-only
    
    echo.
    echo 🎉 Black formatting fixes have been committed!
    echo The GitHub Actions workflow should now pass successfully.
    echo.
    echo 🔄 To push to remote repository, run:
    echo    git push origin main
    echo    ^(or replace 'main' with your default branch name^)
    
) else (
    echo ❌ Error: Failed to commit changes
    echo Check the error messages above for details
    exit /b 1
)
