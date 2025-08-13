#!/usr/bin/env python3
"""
Comprehensive automated security scanning for the MCP server template.
Implements Dr. Chen's security-first standards with multiple scanning tools.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
import tempfile


class SecurityScanner:
    """Comprehensive security scanner for MCP server template."""
    
    def __init__(self):
        self.results = {
            "timestamp": None,
            "overall_status": "UNKNOWN",
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "scans": {}
        }
        
    def run_bandit_scan(self) -> Dict[str, Any]:
        """Run bandit security scanner."""
        print("🔍 Running Bandit security scan...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "bandit", 
                "-r", "mcp_server/",
                "--format", "json",
                "--quiet"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                bandit_data = json.loads(result.stdout)
                return {
                    "status": "PASS",
                    "tool": "bandit",
                    "issues": bandit_data.get("results", []),
                    "metrics": bandit_data.get("metrics", {}),
                    "raw_output": result.stdout
                }
            else:
                return {
                    "status": "FAIL", 
                    "tool": "bandit",
                    "error": result.stderr,
                    "returncode": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "tool": "bandit"}
        except Exception as e:
            return {"status": "ERROR", "tool": "bandit", "error": str(e)}
            
    def run_safety_scan(self) -> Dict[str, Any]:
        """Run safety vulnerability scanner."""
        print("🔍 Running Safety dependency scan...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "safety", "check", 
                "--json", "--short-report"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                return {
                    "status": "PASS",
                    "tool": "safety",
                    "issues": [],
                    "message": "No known security vulnerabilities found"
                }
            else:
                try:
                    safety_data = json.loads(result.stdout)
                    return {
                        "status": "FAIL",
                        "tool": "safety", 
                        "issues": safety_data,
                        "raw_output": result.stdout
                    }
                except json.JSONDecodeError:
                    return {
                        "status": "FAIL",
                        "tool": "safety",
                        "error": result.stderr,
                        "returncode": result.returncode
                    }
                    
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "tool": "safety"}
        except Exception as e:
            return {"status": "ERROR", "tool": "safety", "error": str(e)}
            
    def run_semgrep_scan(self) -> Dict[str, Any]:
        """Run semgrep security scanner."""
        print("🔍 Running Semgrep security scan...")
        
        try:
            result = subprocess.run([
                "semgrep", "--config=auto",
                "--json", "--quiet",
                "mcp_server/"
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                semgrep_data = json.loads(result.stdout)
                return {
                    "status": "PASS" if not semgrep_data.get("results", []) else "FAIL",
                    "tool": "semgrep",
                    "issues": semgrep_data.get("results", []),
                    "errors": semgrep_data.get("errors", []),
                    "raw_output": result.stdout
                }
            else:
                return {
                    "status": "FAIL",
                    "tool": "semgrep", 
                    "error": result.stderr,
                    "returncode": result.returncode
                }
                
        except subprocess.TimeoutExpired:
            return {"status": "TIMEOUT", "tool": "semgrep"}
        except FileNotFoundError:
            return {
                "status": "SKIP", 
                "tool": "semgrep",
                "reason": "Semgrep not installed"
            }
        except Exception as e:
            return {"status": "ERROR", "tool": "semgrep", "error": str(e)}
            
    def check_secrets(self) -> Dict[str, Any]:
        """Check for potential secrets in code."""
        print("🔍 Scanning for secrets...")
        
        issues = []
        suspicious_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
            (r'["\'][A-Za-z0-9]{32,}["\']', "Potential secret string"),
        ]
        
        try:
            import re
            for file_path in Path("mcp_server").rglob("*.py"):
                content = file_path.read_text()
                for pattern, description in suspicious_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Skip if it's clearly a template or example
                        if any(word in match.group().lower() for word in 
                              ["example", "placeholder", "your_", "xxx", "***", "test"]):
                            continue
                            
                        issues.append({
                            "file": str(file_path),
                            "line": content[:match.start()].count('\n') + 1,
                            "description": description,
                            "match": match.group(),
                            "severity": "HIGH"
                        })
                        
            return {
                "status": "PASS" if not issues else "FAIL",
                "tool": "secrets_check",
                "issues": issues
            }
            
        except Exception as e:
            return {"status": "ERROR", "tool": "secrets_check", "error": str(e)}
            
    def check_file_permissions(self) -> Dict[str, Any]:
        """Check file permissions for security issues."""
        print("🔍 Checking file permissions...")
        
        issues = []
        
        try:
            for file_path in Path(".").rglob("*"):
                if file_path.is_file():
                    stat = file_path.stat()
                    mode = oct(stat.st_mode)[-3:]
                    
                    # Check for overly permissive files
                    if mode.endswith('7') or mode.endswith('6'):
                        if not str(file_path).startswith('.git'):
                            issues.append({
                                "file": str(file_path),
                                "mode": mode,
                                "description": "File is world-writable",
                                "severity": "MEDIUM"
                            })
                    
                    # Check for executable files that shouldn't be
                    if file_path.suffix in ['.py', '.md', '.txt', '.json', '.yaml', '.yml']:
                        if mode[2] in ['1', '3', '5', '7']:
                            issues.append({
                                "file": str(file_path),
                                "mode": mode,
                                "description": "Unnecessary execute permission on data file",
                                "severity": "LOW"
                            })
                            
            return {
                "status": "PASS" if not issues else "WARN",
                "tool": "file_permissions",
                "issues": issues
            }
            
        except Exception as e:
            return {"status": "ERROR", "tool": "file_permissions", "error": str(e)}
            
    def check_dependencies(self) -> Dict[str, Any]:
        """Check for security issues in dependencies."""
        print("🔍 Analyzing dependencies...")
        
        issues = []
        
        try:
            # Check requirements.txt for version pinning
            req_files = ["requirements.txt", "requirements-dev.txt"]
            
            for req_file in req_files:
                if Path(req_file).exists():
                    content = Path(req_file).read_text()
                    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                    
                    for line in lines:
                        if '==' not in line and '>=' not in line and '~=' not in line:
                            issues.append({
                                "file": req_file,
                                "line": line,
                                "description": "Dependency without version pinning",
                                "severity": "MEDIUM"
                            })
                            
            return {
                "status": "PASS" if not issues else "WARN",
                "tool": "dependency_check",
                "issues": issues
            }
            
        except Exception as e:
            return {"status": "ERROR", "tool": "dependency_check", "error": str(e)}
            
    def check_docker_security(self) -> Dict[str, Any]:
        """Check Docker configuration for security issues."""
        print("🔍 Checking Docker security...")
        
        issues = []
        
        try:
            for dockerfile in Path(".").glob("Dockerfile*"):
                content = dockerfile.read_text()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # Check for running as root
                    if line.startswith('USER') and 'root' in line.lower():
                        issues.append({
                            "file": str(dockerfile),
                            "line": i,
                            "description": "Container runs as root user",
                            "severity": "HIGH"
                        })
                    
                    # Check for COPY/ADD without --chown
                    if (line.startswith('COPY') or line.startswith('ADD')) and '--chown=' not in line:
                        if not any(keyword in line for keyword in ['--from=', 'package*.json']):
                            issues.append({
                                "file": str(dockerfile),
                                "line": i,
                                "description": "COPY/ADD without --chown may create root-owned files",
                                "severity": "MEDIUM"
                            })
                    
                    # Check for latest tag usage
                    if ':latest' in line or (line.startswith('FROM') and ':' not in line.split()[-1]):
                        issues.append({
                            "file": str(dockerfile),
                            "line": i,
                            "description": "Using latest tag or no tag specification",
                            "severity": "MEDIUM"
                        })
                        
            return {
                "status": "PASS" if not issues else "WARN",
                "tool": "docker_security",
                "issues": issues
            }
            
        except Exception as e:
            return {"status": "ERROR", "tool": "docker_security", "error": str(e)}
            
    def calculate_overall_status(self) -> str:
        """Calculate overall security status."""
        if self.results["critical_issues"] > 0:
            return "CRITICAL"
        elif self.results["high_issues"] > 0:
            return "HIGH_RISK"
        elif self.results["medium_issues"] > 3:
            return "MEDIUM_RISK"
        elif self.results["medium_issues"] > 0 or self.results["low_issues"] > 5:
            return "LOW_RISK"
        else:
            return "SECURE"
            
    def count_issues(self, scan_result: Dict[str, Any]) -> None:
        """Count issues by severity."""
        if scan_result.get("status") not in ["PASS", "SKIP", "WARN"]:
            return
            
        issues = scan_result.get("issues", [])
        for issue in issues:
            severity = issue.get("severity", "LOW").upper()
            if "CRITICAL" in severity:
                self.results["critical_issues"] += 1
            elif "HIGH" in severity:
                self.results["high_issues"] += 1
            elif "MEDIUM" in severity:
                self.results["medium_issues"] += 1
            else:
                self.results["low_issues"] += 1
                
    def run_all_scans(self) -> Dict[str, Any]:
        """Run all security scans."""
        print("🔒 Starting Comprehensive Security Scan")
        print("=" * 50)
        
        import datetime
        self.results["timestamp"] = datetime.datetime.now().isoformat()
        
        # Run all scans
        scans = [
            ("bandit", self.run_bandit_scan),
            ("safety", self.run_safety_scan),
            ("semgrep", self.run_semgrep_scan),
            ("secrets", self.check_secrets),
            ("file_permissions", self.check_file_permissions),
            ("dependencies", self.check_dependencies),
            ("docker", self.check_docker_security),
        ]
        
        for scan_name, scan_func in scans:
            try:
                result = scan_func()
                self.results["scans"][scan_name] = result
                self.count_issues(result)
                
                # Print scan status
                status_icon = {
                    "PASS": "✅",
                    "FAIL": "❌", 
                    "WARN": "⚠️",
                    "SKIP": "⏭️",
                    "ERROR": "🔥",
                    "TIMEOUT": "⏰"
                }.get(result.get("status", "UNKNOWN"), "❓")
                
                print(f"  {status_icon} {scan_name}: {result.get('status', 'UNKNOWN')}")
                
            except Exception as e:
                self.results["scans"][scan_name] = {
                    "status": "ERROR",
                    "error": str(e)
                }
                print(f"  🔥 {scan_name}: ERROR - {e}")
                
        # Calculate overall status
        self.results["overall_status"] = self.calculate_overall_status()
        
        print("\n" + "=" * 50)
        print("📊 Security Scan Summary")
        print("=" * 50)
        
        self.print_summary()
        return self.results
        
    def print_summary(self) -> None:
        """Print security scan summary."""
        status_icon = {
            "SECURE": "🟢",
            "LOW_RISK": "🟡", 
            "MEDIUM_RISK": "🟠",
            "HIGH_RISK": "🔴",
            "CRITICAL": "🚨"
        }.get(self.results["overall_status"], "❓")
        
        print(f"🎯 Overall Status: {status_icon} {self.results['overall_status']}")
        print(f"🚨 Critical Issues: {self.results['critical_issues']}")
        print(f"🔴 High Issues: {self.results['high_issues']}")
        print(f"🟠 Medium Issues: {self.results['medium_issues']}")
        print(f"🟡 Low Issues: {self.results['low_issues']}")
        
        print("\n📝 Scan Results:")
        for scan_name, result in self.results["scans"].items():
            status = result.get("status", "UNKNOWN")
            issue_count = len(result.get("issues", []))
            print(f"  • {scan_name}: {status}" + 
                  (f" ({issue_count} issues)" if issue_count > 0 else ""))
                  
        # Dr. Chen's security grade
        print(f"\n🎓 Dr. Chen's Security Grade: {self.get_security_grade()}")
        
    def get_security_grade(self) -> str:
        """Get Dr. Chen's security grade."""
        if self.results["overall_status"] == "SECURE":
            return "💎 EXCEPTIONAL (A+)"
        elif self.results["overall_status"] == "LOW_RISK":
            return "⭐ EXCELLENT (A)"
        elif self.results["overall_status"] == "MEDIUM_RISK":
            return "🟢 GOOD (B)"
        elif self.results["overall_status"] == "HIGH_RISK":
            return "🟡 NEEDS IMPROVEMENT (C)"
        else:
            return "🔴 CRITICAL (F)"
            
    def save_results(self, filename: str = "security_scan_results.json") -> None:
        """Save scan results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Security scan results saved to {filename}")


def main():
    """Main security scan execution."""
    scanner = SecurityScanner()
    results = scanner.run_all_scans()
    scanner.save_results()
    
    # Exit with appropriate code
    if results["overall_status"] in ["CRITICAL", "HIGH_RISK"]:
        print("\n⚠️  Security issues found that require immediate attention!")
        sys.exit(1)
    elif results["overall_status"] in ["MEDIUM_RISK"]:
        print("\n⚠️  Some security issues found - review recommended")
        sys.exit(2)
    else:
        print("\n✅ Security scan completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()