# Pull Request

## 📋 Description
<!-- Provide a clear and concise description of what this PR does -->

**Type of Change:**
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🔧 Configuration change
- [ ] 🧪 Test improvement
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security enhancement

## 🔗 Related Issues
<!-- Link to related issues -->
Fixes #(issue_number)
Closes #(issue_number)
Related to #(issue_number)

## 🧪 Testing
<!-- Describe how you tested your changes -->

### Test Environment
- [ ] Local development
- [ ] Docker container
- [ ] Multiple Python versions (specify: )

### Testing Checklist
- [ ] Existing tests pass
- [ ] New tests added (if applicable)
- [ ] Manual testing completed
- [ ] Code formatting checked (Black, isort)
- [ ] Linting passed (Flake8)
- [ ] Type checking passed (MyPy)
- [ ] Security scan passed (Bandit)

### Test Commands Run
```bash
# Add the commands you used to test
python test_server.py
black --check .
flake8 .
mypy *.py
```

## 📝 Changes Made
<!-- List the specific changes made -->

### New Features
- 

### Bug Fixes
- 

### Documentation Changes
- 

### Configuration Changes
- 

## 🔄 Migration Required
<!-- If this is a breaking change, describe migration steps -->
- [ ] No migration required
- [ ] Migration required (described below)

### Migration Steps
<!-- If migration is required, provide steps -->
1. 
2. 
3. 

## 📸 Screenshots/Examples
<!-- If applicable, add screenshots or code examples -->

### Before
```python
# Old code or behavior
```

### After
```python
# New code or behavior
```

## ⚠️ Breaking Changes
<!-- Describe any breaking changes and their impact -->
- 

## 📋 Checklist
<!-- Check all applicable items -->

### Code Quality
- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] No debug/console.log statements left in code
- [ ] No sensitive information (keys, passwords) in code

### Documentation
- [ ] README updated (if needed)
- [ ] CHANGELOG.md updated
- [ ] Docstrings added/updated for new functions
- [ ] Examples updated (if needed)
- [ ] Configuration documentation updated (if needed)

### Testing
- [ ] Tests added for new functionality
- [ ] All existing tests pass
- [ ] Edge cases considered and tested
- [ ] Error handling tested

### Security
- [ ] Security implications considered
- [ ] Input validation added where needed
- [ ] No new security vulnerabilities introduced
- [ ] Dependencies are secure and up-to-date

### Performance
- [ ] Performance implications considered
- [ ] No significant performance regression
- [ ] Memory usage considered
- [ ] Async/await used appropriately

## 🚀 Deployment Notes
<!-- Any special deployment considerations -->
- [ ] No special deployment steps required
- [ ] Requires environment variable changes
- [ ] Requires Docker image rebuild
- [ ] Requires dependency updates

### Environment Variables (if applicable)
```bash
# New or changed environment variables
NEW_VAR=example_value
```

## 👥 Reviewers
<!-- Tag specific people for review if needed -->
@mention-reviewers

## 📋 Additional Notes
<!-- Any additional information for reviewers -->

---

**Thank you for contributing to the Python MCP Server Template! 🎉**

<!-- 
Please make sure you have:
1. Read the CONTRIBUTING.md file
2. Followed the code style guidelines
3. Added appropriate tests
4. Updated documentation as needed
5. Filled out this template completely
-->
