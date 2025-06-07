# Security Policy

## 🔒 Supported Versions

We actively support the following versions of the Python MCP Server Template:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Yes             |
| < 1.0   | ❌ No              |

## 🚨 Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### 🔐 Private Reporting (Recommended)

1. **DO NOT** open a public issue for security vulnerabilities
2. Use GitHub's private vulnerability reporting:
   - Go to the [Security tab](https://github.com/[your-username]/python-mcp-server-template/security)
   - Click "Report a vulnerability"
   - Fill out the advisory form with details

### 📧 Alternative Contact

If GitHub's private reporting is not available, you can email security issues to:
- **Email**: [your-security-email@domain.com]
- **Subject**: `[SECURITY] Python MCP Server Template - [Brief Description]`

### 📋 What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: Potential impact and attack scenarios
- **Reproduction**: Step-by-step instructions to reproduce
- **Affected Components**: Which files/functions are affected
- **Suggested Fix**: If you have ideas for fixes
- **Disclosure Timeline**: Your preferred disclosure timeline

### 🕐 Response Timeline

- **Initial Response**: Within 48 hours
- **Triage**: Within 1 week
- **Fix Development**: Depends on severity (hours to weeks)
- **Security Advisory**: Published with fix release

### 🏆 Recognition

We appreciate security researchers who help keep our users safe:

- We'll acknowledge your contribution in security advisories (if you wish)
- We'll credit you in our security hall of fame
- For significant vulnerabilities, we may offer recognition rewards

## 🛡️ Security Best Practices

### For Users

- **Keep Updated**: Always use the latest version
- **Review Dependencies**: Check for vulnerable dependencies regularly
- **Secure Configuration**: Follow security guidelines in documentation
- **Network Security**: Use proper network isolation and access controls
- **Secrets Management**: Never commit secrets to version control

### For Contributors

- **Input Validation**: Always validate and sanitize user inputs
- **Path Traversal**: Use the provided `validate_path()` function
- **Command Injection**: Avoid shell injection in command execution
- **Dependencies**: Keep dependencies updated and secure
- **Security Testing**: Include security tests for new features

## 🔍 Security Features

This template includes several security features:

### ✅ Built-in Protections

- **Path Validation**: Prevents directory traversal attacks
- **File Size Limits**: Prevents resource exhaustion
- **Command Timeouts**: Prevents hanging processes
- **Input Sanitization**: Validates user inputs
- **Non-root Execution**: Docker containers run as non-root user

### 🔧 Security Tools Integration

- **Bandit**: Static security analysis for Python code
- **Safety**: Dependency vulnerability scanning
- **Docker Security**: Multi-stage builds and minimal attack surface

### 📊 Security Monitoring

Our CI/CD pipeline includes:

- Automated security scanning on every commit
- Dependency vulnerability checks
- Container security scanning
- Security issue creation for violations

## 📚 Security Resources

### Documentation

- [OWASP Python Security](https://owasp.org/www-pdf-archive/OWASP_Python_Security_Project_Technical_Implementation_Guide.pdf)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [FastMCP Security Guidelines](https://github.com/jlowin/fastmcp#security)

### Tools

- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Safety](https://pyup.io/safety/) - Dependency vulnerability scanner
- [Semgrep](https://semgrep.dev/) - Static analysis security scanner

## 🚫 Out of Scope

The following are generally not considered security vulnerabilities:

- Issues requiring local file system access
- Denial of service through resource exhaustion (covered by limits)
- Issues in development/test configurations
- Social engineering attacks
- Physical access attacks

## 📝 Disclosure Policy

### Coordinated Disclosure

We follow responsible disclosure practices:

1. **Private Report**: Vulnerability reported privately
2. **Investigation**: We investigate and develop fixes
3. **Coordination**: We coordinate with reporter on disclosure
4. **Public Disclosure**: Security advisory published with fix
5. **Recognition**: Reporter credited (if desired)

### Timeline

- **Critical**: Immediate fix and disclosure
- **High**: Fix within 1 week, disclosure within 2 weeks
- **Medium**: Fix within 1 month, disclosure within 6 weeks
- **Low**: Fix in next release cycle

---

**Thank you for helping keep the Python MCP Server Template secure! 🛡️**

*Last updated: June 2025*
