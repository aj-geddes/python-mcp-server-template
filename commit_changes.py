#!/usr/bin/env python3
"""
Script to commit the Black formatting fixes using subprocess
"""

import subprocess
import os
import sys

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    # Change to the project directory
    project_dir = "/mnt/workspace/python-mcp-server-template"
    
    print("🔍 Checking git status...")
    success, stdout, stderr = run_command("git status --porcelain", cwd=project_dir)
    if success:
        print("Modified files:")
        print(stdout if stdout else "No changes detected")
    else:
        print(f"Error checking git status: {stderr}")
        return 1
    
    print("\n📝 Adding files to git...")
    files_to_add = [
        "tests/test_server.py",
        "tests/test_mcp_server.py", 
        "examples.py"
    ]
    
    for file in files_to_add:
        print(f"Adding {file}...")
        success, stdout, stderr = run_command(f"git add {file}", cwd=project_dir)
        if not success:
            print(f"Error adding {file}: {stderr}")
            return 1
    
    print("\n🚀 Committing changes...")
    commit_message = '''Fix Black code formatting issues

- Fix spacing and blank lines in tests/test_server.py
- Rewrite tests/test_mcp_server.py with proper Black formatting
- Apply Black formatting standards to examples.py
- Remove trailing whitespace across all files
- Add proper function parameter spacing and trailing commas
- Ensure compliance with 88-character line length

Resolves GitHub Actions CI formatting check failures.
Closes Black formatting violations found in lint workflow.'''
    
    success, stdout, stderr = run_command(
        f'git commit -m "{commit_message}"',
        cwd=project_dir
    )
    
    if success:
        print("✅ Successfully committed changes!")
        print("Commit output:", stdout)
        
        # Show the commit
        print("\n📋 Verifying commit...")
        success, stdout, stderr = run_command("git log --oneline -n 1", cwd=project_dir)
        if success:
            print("Latest commit:", stdout.strip())
        
        # Show changed files
        success, stdout, stderr = run_command("git diff HEAD~1 --name-only", cwd=project_dir)
        if success:
            print("Files changed in commit:")
            print(stdout)
            
    else:
        print(f"❌ Error committing: {stderr}")
        return 1
    
    print("\n🎉 Black formatting fixes have been committed!")
    print("The GitHub Actions workflow should now pass successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
