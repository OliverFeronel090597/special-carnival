Contributing Guidelines
Thank you for considering contributing to QtForge Studio!

<div align="center"> <img src="img/QtForge%20Studio.png" alt="QtForge Studio" width="400" height="350"> </div>
Table of Contents
How to Contribute

1. Report Bugs

2. Suggest Features

3. Submit Code Changes

Development Standards

Code Style Setup

Testing Process

Documentation Updates

Pull Request Process

Local Development Setup

Release Process

Code of Conduct

Main Contributors

How to Contribute
1. Report Bugs
Description: Report any issues or unexpected behavior in QtForge Studio.

Process & Commands:

bash
# Step 1: Check for existing bug reports
gh issue list --label "bug" --state "open"

# Step 2: Create detailed bug report
gh issue create \
  --title "[BUG]: Brief description" \
  --body "**OS:** [System Info]\n**Version:** [QtForge Version]\n**Steps:** 1. ... 2. ..." \
  --label "bug"
2. Suggest Features
Description: Propose new features or improvements.

Process & Commands:

bash
# Step 1: Search existing feature requests
gh issue list --label "enhancement" --state "open"

# Step 2: Submit feature proposal
gh issue create \
  --title "[FEATURE]: Feature title" \
  --body "**Use Case:** ...\n**Benefits:** ...\n**Complexity:** Low/Medium/High" \
  --label "enhancement"
3. Submit Code Changes
Description: Contribute code via pull requests.

Process & Commands:

bash
# Step 1: Clone and setup
git clone https://github.com/Queen0905/qtforge-studio.git
cd qtforge-studio

# Step 2: Create feature branch
git checkout -b feature/description

# Step 3: Install dependencies
pip install -r requirements-dev.txt

# Step 4: Make changes and format code
black . && isort .

# Step 5: Run tests
pytest tests/ -v

# Step 6: Commit and push
git add .
git commit -m "Add: Feature description"
git push origin feature/description

# Step 7: Create Pull Request
gh pr create --title "Add: Feature" --body "## Description\n...\n## Testing\n..."
Development Standards
Code Style Setup
Description: Ensure consistent code formatting and quality.

Process & Commands:

bash
# Install code quality tools
pip install black isort flake8 mypy

# Format all Python files
black src/ tests/

# Sort imports automatically
isort src/ tests/

# Check code style compliance
flake8 src/ --max-line-length=88

# Verify type hints
mypy src/ --ignore-missing-imports
Testing Process
Description: Write and execute comprehensive tests.

Process & Commands:

bash
# Install test dependencies
pip install pytest pytest-cov pytest-xdist

# Run all tests with verbosity
pytest tests/ -v

# Run tests with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test module
pytest tests/test_specific.py -xvs

# Run tests in parallel
pytest tests/ -n 4
Documentation Updates
Description: Maintain up-to-date documentation.

Process & Commands:

bash
# Add docstrings to new functions
"""
def example(param: str) -> bool:
    '''Brief description.
    
    Args:
        param: Description of parameter
        
    Returns:
        Boolean result
    '''
"""

# Update README.md with relevant changes
# (Manual editing required)

# Generate API documentation
cd docs && make html
Pull Request Process
Description: Complete PR review and merge workflow.

Process & Commands:

bash
# 1. Update CHANGELOG.md
# Add entry: - **Added**: New feature description

# 2. Request reviews from maintainers
gh pr edit --add-reviewer @maintainer1

# 3. Check CI/CD status
gh pr checks

# 4. Address review feedback
git add . && git commit -m "Address review comments"

# 5. Merge after approval (maintainers)
gh pr merge --squash --delete-branch

# 6. Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
Local Development Setup
Description: Configure local environment for development.

Process & Commands:

bash
# 1. Clone repository
git clone https://github.com/username/qtforge-studio.git
cd qtforge-studio

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Install in development mode
pip install -e .
pip install -r requirements-dev.txt

# 4. Run application in dev mode
python -m qtforge_studio --dev

# 5. Set up pre-commit hooks
pre-commit install
Release Process
Description: Package and publish new versions.

Process & Commands:

bash
# 1. Update version in pyproject.toml
# version = "1.2.0"

# 2. Build distribution packages
python -m build

# 3. Test installation
pip install dist/qtforge_studio-1.2.0-py3-none-any.whl

# 4. Upload to PyPI
twine upload dist/*

# 5. Create GitHub release
gh release create v1.2.0 \
  --title "v1.2.0 Release" \
  --notes-file CHANGELOG.md
Code of Conduct
Description: Report violations and maintain respectful environment.

Process:

Report via: just_report.com 😅

Include:

Date/time of incident

Platform (GitHub, Discord, etc.)

Description of behavior

Supporting evidence

Contact information

Main Contributors
Oliver Feronel: Initial codebase, function structure development, and UI design

<div align="center"> <small>Thank you for helping improve QtForge Studio! 🚀</small> </div>