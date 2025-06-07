# Python MCP Server Template

![Python](https://img.shields.io/badge/python-v3.10+-blue.svg)
![FastMCP](https://img.shields.io/badge/FastMCP-v0.1.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)
![GitHub Actions](https://github.com/aj-geddes/python-mcp-server-template/workflows/Python%20Code%20Quality%20Check/badge.svg)
![Security](https://img.shields.io/badge/security-bandit%20%7C%20safety-red.svg)
![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)

> 🚀 **Production-ready Python MCP server template using FastMCP framework**

A comprehensive, security-first template for building [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers with Python. Get from zero to production in minutes with built-in Docker support, automated testing, and enterprise-grade CI/CD.

## ✨ **Why This Template?**

- 🔒 **Security First**: Built-in path validation, security scanning, and vulnerability management
- ⚡ **Production Ready**: Docker containerization, health checks, and monitoring
- 🧪 **Quality Assured**: Automated testing, linting, and code formatting
- 📚 **Well Documented**: Comprehensive docs, examples, and contribution guidelines
- 🤝 **Community Driven**: Issue templates, PR workflows, and contributor tools

## 🎯 **Perfect For**

- **AI Developers** building MCP-enabled applications
- **Teams** integrating with Claude and other AI systems  
- **DevOps Engineers** deploying scalable AI tool services
- **Researchers** prototyping AI agent capabilities
- **Startups** building AI-powered products

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+ (3.12 recommended)
- Docker (optional, for containerized deployment)
- Git (for version control)

### 🔥 **One-Minute Setup**

```bash
# Use this template (click "Use this template" on GitHub)
# OR clone directly:
git clone https://github.com/aj-geddes/python-mcp-server-template.git my-mcp-server
cd my-mcp-server

# Install dependencies
pip install -r requirements.txt

# Run the server
python mcp_server.py
```

### 🐳 **Docker Deployment**

```bash
# Build and run with one command
./build.sh  # Linux/macOS
# OR
build.bat   # Windows

# Run the container
docker run -it --rm python-mcp-server-template:latest
```

## 🛠️ Available Tools

The template includes battle-tested tools to demonstrate FastMCP capabilities:

| Tool | Description | Use Case |
|------|-------------|----------|
| 🔊 **`echo`** | Message echo with testing | Health checks, connectivity testing |
| 📁 **`list_files`** | Directory listings with metadata | File exploration, content discovery |
| 📖 **`read_file`** | Safe file reading with validation | Content analysis, data processing |
| ✍️ **`write_file`** | File writing with directory creation | Content generation, data persistence |
| 💻 **`run_shell_command`** | Secure command execution | System operations, automation |

### 🌐 **Resources & Prompts**

- **📄 File Resources**: `file://{path}` - URI-style file access
- **🤖 Code Review Prompts**: Structured AI code analysis templates

## 🏗️ Architecture

### FastMCP Framework Benefits

```python
@mcp.tool()  # ← Simple decorator
async def my_tool(param: str) -> Dict[str, Any]:
    """Your tool description"""
    return {"result": "success"}
```

- **🎯 Zero Boilerplate**: Decorators eliminate MCP protocol complexity
- **🔒 Type Safety**: Full Python type hints and validation
- **⚡ Async Native**: Built-in async/await support
- **🛡️ Error Handling**: Custom exceptions with user-friendly messages

### 🔐 Security Features

- **Path Validation**: Prevents directory traversal attacks
- **Command Restrictions**: Timeouts and sandboxing
- **File Size Limits**: Resource exhaustion protection
- **Non-root Execution**: Container security hardening

## 📁 Project Structure

```
📦 python-mcp-server-template/
├── 🐍 mcp_server.py              # Main server implementation
├── 📋 requirements.txt           # Production dependencies  
├── 🧪 requirements-dev.txt       # Development tools
├── 🐳 Dockerfile                # Container configuration
├── ⚙️ pyproject.toml             # Tool configurations
├── 🔨 build.sh / build.bat       # Build scripts
├── 🧪 test_server.py             # Test suite
├── 📚 examples.py                # Extension examples
├── 📖 README.md                  # This documentation
├── 🔒 SECURITY.md                # Security policy
├── 🤝 CONTRIBUTING.md            # Contribution guidelines
├── 📋 CHANGELOG.md               # Version history
└── 🤖 .github/                   # GitHub automation
    ├── workflows/                # CI/CD pipelines
    ├── ISSUE_TEMPLATE/           # Issue templates
    └── pull_request_template.md  # PR template
```

## 🔧 Customization

### ➕ Adding New Tools

```python
@mcp.tool()
async def my_custom_tool(
    param1: str, 
    param2: int = 10
) -> Dict[str, Any]:
    """
    🎯 Tool description - what it does and why.
    
    Args:
        param1: Description with examples
        param2: Optional parameter with default
        
    Returns:
        Structured response with status
    """
    try:
        result = await your_logic_here(param1, param2)
        return {
            "result": result,
            "metadata": {"processed": param1},
            "status": "✅ Success"
        }
    except Exception as e:
        raise MCPError(f"Operation failed: {str(e)}")
```

### 🌐 Adding Resources

```python
@mcp.resource("config://{name}")
async def config_resource(name: str) -> str:
    """Access configuration as MCP resource."""
    return load_config(name)
```

### 🤖 Adding Prompts

```python
@mcp.prompt()
async def analysis_prompt(data: str, focus: str) -> str:
    """Generate analysis prompts."""
    return f"Analyze this {data} focusing on {focus}..."
```

## 🧪 Testing & Quality

### 🤖 **Automated Testing (GitHub Actions)**

Every commit triggers comprehensive testing:

| Check Type | Tools | Purpose |
|------------|-------|---------|
| 🎨 **Code Style** | Black, isort, Flake8 | Consistent formatting |
| 🔍 **Type Safety** | MyPy | Static type checking |
| 🔒 **Security** | Bandit, Safety | Vulnerability scanning |
| 🧪 **Testing** | Python 3.10-3.12 | Multi-version compatibility |
| 🐳 **Docker** | Container builds | Deployment verification |
| 📋 **Auto-Issues** | Failed checks → GitHub issues | Automated feedback |

### 🛠️ **Local Development**

```bash
# 📦 Install development tools
pip install -r requirements-dev.txt

# 🪝 Set up pre-commit hooks
pre-commit install

# 🧪 Run quality checks
black . && isort . && flake8 . && mypy *.py

# 🔒 Security scan
bandit -r . && safety check

# ✅ Run tests
python test_server.py
```

## 🚀 Deployment Options

### 🐳 **Docker (Recommended)**

```bash
# Production build
docker build -t my-mcp-server:latest .

# Run with volume mounting
docker run -d \
  --name mcp-server \
  -v /path/to/data:/workspace \
  my-mcp-server:latest
```

### ☁️ **Cloud Platforms**

| Platform | Configuration | Benefits |
|----------|---------------|----------|
| **AWS ECS** | Use provided Dockerfile | Auto-scaling, load balancing |
| **Google Cloud Run** | Serverless deployment | Pay-per-use, zero maintenance |
| **Azure Container Instances** | Quick container deployment | Simple setup, integrated monitoring |
| **Railway/Render** | Git-based deployment | Easy CI/CD, automatic SSL |

### 🏠 **Local Development**

```bash
# Development server with auto-reload
python mcp_server.py --debug

# Production server
python mcp_server.py
```

## 🤝 Contributing

### 🚀 **Quick Contributor Setup**

```bash
# 1. Fork & clone
git clone https://github.com/YOUR_USERNAME/python-mcp-server-template.git

# 2. Development environment
pip install -r requirements-dev.txt
pre-commit install

# 3. Create feature branch
git checkout -b feature/amazing-feature

# 4. Code, test, commit
# Your changes here...
python test_server.py
git commit -m "feat: add amazing feature"

# 5. Push & create PR
git push origin feature/amazing-feature
```

### ✅ **Code Quality Requirements**

All contributions must pass:
- ✅ **Black** code formatting
- ✅ **isort** import sorting  
- ✅ **Flake8** style compliance
- ✅ **MyPy** type checking
- ✅ **Bandit** security scanning
- ✅ All tests passing
- ✅ Documentation updated

*See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.*

## 🔗 **Ecosystem & Resources**

### 📚 **Documentation**
- [FastMCP Documentation](https://github.com/jlowin/fastmcp) - Framework docs
- [MCP Specification](https://modelcontextprotocol.io/) - Protocol details
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/) - Container optimization

### 🧪 **Example Implementations**
- [examples.py](examples.py) - Additional tool patterns
- [System Information Tools](examples.py#L25-L45) - Platform details
- [JSON Processing](examples.py#L47-L95) - Data manipulation
- [File Operations](examples.py#L97-L150) - Advanced file handling

### 🤝 **Community**
- [GitHub Discussions](https://github.com/aj-geddes/python-mcp-server-template/discussions) - Q&A and ideas
- [Issues](https://github.com/aj-geddes/python-mcp-server-template/issues) - Bug reports and features
- [Security Policy](SECURITY.md) - Vulnerability reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚨 Support & Troubleshooting

### 🐛 **Common Issues**

<details>
<summary><strong>❌ Module not found errors</strong></summary>

```bash
# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```
</details>

<details>
<summary><strong>🔒 Permission denied on build scripts</strong></summary>

```bash
# Make executable
chmod +x build.sh

# Or run directly
bash build.sh
```
</details>

<details>
<summary><strong>🐳 Docker build failures</strong></summary>

```bash
# Check Docker daemon
docker version

# Clean up space
docker system prune -a

# Check disk space
df -h
```
</details>

<details>
<summary><strong>🧪 Code quality checks failing</strong></summary>

```bash
# Auto-fix formatting
black . && isort .

# Check issues
flake8 . && mypy *.py

# Security scan
bandit -r .
```
</details>

### 🆘 **Get Help**

- 💬 [GitHub Discussions](https://github.com/aj-geddes/python-mcp-server-template/discussions) - Community support
- 🐛 [Create an Issue](https://github.com/aj-geddes/python-mcp-server-template/issues/new/choose) - Bug reports
- 🔒 [Security Issues](SECURITY.md) - Responsible disclosure

---

<div align="center">

**⭐ Star this repo if it helped you!**

Made with ❤️ for the MCP community

[🚀 Use This Template](https://github.com/aj-geddes/python-mcp-server-template/generate) • [📖 Documentation](https://github.com/aj-geddes/python-mcp-server-template/wiki) • [💬 Community](https://github.com/aj-geddes/python-mcp-server-template/discussions)

</div>
