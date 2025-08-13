# Documentation

This directory contains the comprehensive documentation for the Python MCP Server Template, designed for GitHub Pages deployment.

## 📚 Documentation Structure

- **[Home](index.md)** - Overview and quick reference
- **[Quick Start](deployment/quickstart.md)** - Get running in 5 minutes
- **[Security Guide](security/overview.md)** - Comprehensive security features
- **[API Reference](api/overview.md)** - Complete API documentation
- **[Development Setup](development/setup.md)** - Contributing and extending
- **[Docker Guide](deployment/docker.md)** - Production Docker deployment

## 🌐 GitHub Pages

This documentation is automatically published to GitHub Pages at:
**https://aj-geddes.github.io/python-mcp-server-template/**

### Local Development

To preview documentation locally:

```bash
# Install Jekyll dependencies
cd docs
bundle install

# Serve locally
bundle exec jekyll serve

# Open http://localhost:4000/python-mcp-server-template/
```

### Automatic Deployment

Documentation is automatically deployed when:
- Changes are pushed to `master` branch
- Files in `docs/` directory are modified
- Workflow can also be triggered manually

## 📝 Contributing to Documentation

When adding new documentation:

1. **Follow the existing structure** - Use the established directory layout
2. **Update navigation** - Add new pages to `_config.yml` if needed
3. **Use consistent formatting** - Follow markdown conventions
4. **Test locally** - Preview changes before pushing
5. **Update index pages** - Add links to new content

### Markdown Guidelines

- Use descriptive headers with emoji for visual appeal
- Include code examples with proper syntax highlighting
- Add tables for structured information
- Use badges and status indicators where appropriate
- Link between related documentation pages

### File Organization

```
docs/
├── index.md              # Main landing page
├── _config.yml           # Jekyll configuration
├── deployment/           # Deployment guides
│   ├── quickstart.md    # Quick start guide
│   └── docker.md        # Docker deployment
├── security/             # Security documentation  
│   └── overview.md      # Security features
├── api/                  # API documentation
│   └── overview.md      # API reference
└── development/          # Development guides
    └── setup.md         # Development setup
```

## 🔧 Technical Setup

The documentation uses:
- **Jekyll** static site generator
- **Minima** theme with customizations
- **GitHub Actions** for automatic deployment
- **Markdown** with GitHub Flavored Markdown extensions

### Dependencies

```yaml
# _config.yml
plugins:
  - jekyll-feed        # RSS feeds
  - jekyll-sitemap     # XML sitemap
  - jekyll-seo-tag     # SEO meta tags

theme: minima          # GitHub Pages compatible theme
```

## 📊 Documentation Quality

Current documentation covers:
- ✅ **Installation & Setup** - Complete quick start guide
- ✅ **Security Features** - Comprehensive security documentation  
- ✅ **API Reference** - All tools, resources, and prompts documented
- ✅ **Development Guide** - Contributing and extension guidelines
- ✅ **Deployment Guide** - Docker and production deployment
- ✅ **GitHub Pages** - Automatic documentation deployment

---

*For questions about documentation, please create an issue or start a discussion.*