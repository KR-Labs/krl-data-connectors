---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# Contributing to KRL Data Connectors

Thank you for your interest in contributing to KRL Data Connectors! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Adding New Connectors](#adding-new-connectors)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Code of Conduct

This project follows a professional code of conduct. We expect all contributors to:

- Be respectful and inclusive
- Focus on constructive feedback
- Prioritize the project's goals over personal preferences
- Maintain professional communication in all interactions

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account
- (Optional) API keys for connectors you want to test

### Finding Issues to Work On

1. Check the [issue tracker](https://github.com/KR-Labs/krl-data-connectors/issues)
2. Look for issues labeled `good first issue` or `help wanted`
3. Comment on the issue to let others know you're working on it
4. Wait for maintainer acknowledgment before starting work

### Proposing New Features

Before implementing a new feature:

1. Open an issue to discuss the feature
2. Explain the use case and benefit
3. Wait for maintainer approval
4. Follow the guidelines below for implementation

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/krl-data-connectors.git
cd krl-data-connectors
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n krl-connectors python=3.12
conda activate krl-connectors
```

### 3. Install Development Dependencies

```bash
# Install package in editable mode with dev dependencies
pip install -e ".[dev,docs]"

# Install pre-commit hooks
pre-commit install
```

### 4. Verify Installation

```bash
# Run tests to verify setup
pytest

# Check code style
black --check src/
isort --check-only src/
flake8 src/
mypy src/
```

### 5. Set Up API Keys

Create a `.env` file (not committed to git):

```bash
# .env
FRED_API_KEY=your_key_here
CENSUS_API_KEY=your_key_here
BLS_API_KEY=your_key_here
# Add other keys as needed
```

## Code Standards

### Code Style

We use automated tools to enforce consistent code style:

- **Black**: Code formatting (line length: 88)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

These are automatically run via pre-commit hooks.

### Type Hints

All code must include type hints:

```python
# Good
def get_series(self, series_id: str, start_date: Optional[str] = None) -> pd.DataFrame:
    """Fetch time series data."""
    pass

# Bad
def get_series(self, series_id, start_date=None):
    """Fetch time series data."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def get_data(self, dataset: str, variables: List[str], geography: str) -> pd.DataFrame:
    """Fetch data from Census API.

    Args:
        dataset: Census dataset name (e.g., 'acs/acs5')
        variables: List of variable codes to fetch
        geography: Geographic level (e.g., 'county:*')

    Returns:
        DataFrame with requested data

    Raises:
        APIError: If API request fails
        ValueError: If parameters are invalid

    Example:
        >>> connector = CensusConnector()
        >>> data = connector.get_data(
        ...     dataset="acs/acs5",
        ...     variables=["B01003_001E"],
        ...     geography="state:06"
        ... )
    """
    pass
```

### Error Handling

Use custom exceptions from `krl_data_connectors.exceptions`:

```python
from krl_data_connectors.exceptions import APIError, ConfigurationError

def fetch_data(self, endpoint: str) -> Dict[str, Any]:
    """Fetch data from API."""
    try:
        response = self._get(endpoint)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        raise APIError(f"API request failed: {e}")
    except Exception as e:
        raise APIError(f"Unexpected error: {e}")
```

### Logging

Use the built-in logger:

```python
import logging

logger = logging.getLogger(__name__)

def fetch_data(self, endpoint: str) -> Dict[str, Any]:
    """Fetch data from API."""
    logger.debug(f"Fetching data from {endpoint}")
    response = self._get(endpoint)
    logger.info(f"Successfully fetched data from {endpoint}")
    return response.json()
```

## Testing Requirements

### Writing Tests

All new code must include tests:

```python
# tests/connectors/test_fred.py
import pytest
from krl_data_connectors import FREDConnector
from krl_data_connectors.exceptions import APIError

class TestFREDConnector:
    """Test suite for FRED connector."""

    @pytest.fixture
    def connector(self):
        """Create connector instance."""
        return FREDConnector()

    def test_get_series_success(self, connector, requests_mock):
        """Test successful series retrieval."""
        # Mock API response
        requests_mock.get(
            "https://api.stlouisfed.org/fred/series/observations",
            json={"observations": [{"date": "2024-01-01", "value": "3.7"}]}
        )

        # Test
        result = connector.get_series("UNRATE")

        # Assertions
        assert not result.empty
        assert "value" in result.columns

    def test_get_series_invalid_id(self, connector, requests_mock):
        """Test error handling for invalid series ID."""
        requests_mock.get(
            "https://api.stlouisfed.org/fred/series/observations",
            status_code=404
        )

        with pytest.raises(APIError):
            connector.get_series("INVALID_ID")
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/krl_data_connectors --cov-report=html

# Run specific test file
pytest tests/connectors/test_fred.py

# Run specific test
pytest tests/connectors/test_fred.py::TestFREDConnector::test_get_series_success

# Run tests matching pattern
pytest -k "test_get_series"
```

### Coverage Requirements

- **Minimum coverage**: 90%
- **Target coverage**: 95%+
- All new code must be covered by tests
- Coverage reports are generated in `htmlcov/`

### Test Categories

```python
# Unit tests - test individual methods in isolation
@pytest.mark.unit
def test_parse_response():
    """Test response parsing."""
    pass

# Integration tests - test API interactions (may require API keys)
@pytest.mark.integration
def test_api_call():
    """Test real API call."""
    pass

# Slow tests - skip during rapid development
@pytest.mark.slow
def test_large_dataset():
    """Test with large dataset."""
    pass
```

Run specific categories:
```bash
pytest -m unit          # Only unit tests
pytest -m integration   # Only integration tests
pytest -m "not slow"    # Skip slow tests
```

## Security Guidelines

###  KRL Defense & Protection Stack

All contributions must adhere to our 10-layer security architecture. Please review our [SECURITY.md](SECURITY.md) for complete details.

### Critical Security Rules

**❌ NEVER commit:**
- API keys, tokens, or credentials
- Private keys or certificates
- Passwords or secrets
- Real user data
- Internal documentation patterns (INTERNAL, _SUMMARY, _ROADMAP, etc.)

**✅ ALWAYS:**
- Use environment variables for credentials
- Add copyright headers to new files
- Run pre-commit hooks before committing
- Review `git diff` before committing
- Test with demo/public API keys when possible

### Pre-Commit Security Checks

Our pre-commit hooks automatically:
1. **Add copyright headers** to all files
2. **Verify trademark notices** in README
3. **Detect secrets** using Gitleaks
4. **Run security scanners** (Bandit)
5. **Block internal documents** from commits

If a hook fails, fix the issue before committing.

### Secret Management

#### Using API Keys in Development

```python
# ❌ WRONG - Never hardcode secrets
api_key = "sk_test_FAKE_EXAMPLE_KEY_DO_NOT_USE"

# ✅ CORRECT - Use environment variables
import os
api_key = os.environ.get('FRED_API_KEY')

# ✅ CORRECT - Use dotenv for local development
from dotenv import load_dotenv
load_dotenv()
api_key = os.environ.get('FRED_API_KEY')
```

#### .env File (gitignored)

```bash
# .env - This file is NOT committed
FRED_API_KEY=your_real_key_here
CENSUS_API_KEY=your_real_key_here
BLS_API_KEY=your_real_key_here
```

#### Example Code & Documentation

When writing examples, use placeholder values:

```python
# ✅ Good - Obvious placeholder
connector = FREDConnector(api_key='YOUR_FRED_API_KEY')

# ✅ Good - Environment variable reference
connector = FREDConnector(api_key=os.environ.get('FRED_API_KEY'))

# ❌ Bad - Looks like a real key
connector = FREDConnector(api_key='8ec3c8309e60d874eae960d407f15460')
```

### Copyright & License Headers

All new files must include copyright headers:

```python
# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Your module docstring here."""
```

For Markdown files:

```markdown
---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# Document Title
```

**Note:** Pre-commit hooks will automatically add these headers, but you can add them manually if preferred.

### Running Security Checks Locally

Before submitting a PR:

```bash
# 1. Run all pre-commit hooks
pre-commit run --all-files

# 2. Scan for secrets with Gitleaks
gitleaks detect --config .gitleaks.toml --verbose

# 3. Run security linters
bandit -r src/

# 4. Check for vulnerable dependencies
safety check

# 5. Verify copyright headers
python scripts/security/verify_copyright_headers.py
```

### Dependency Security

When adding new dependencies:

1. **Check for known vulnerabilities:**
   ```bash
   pip install safety
   safety check --json
   ```

2. **Verify license compatibility:**
   - ✅ Allowed: MIT, Apache-2.0, BSD, ISC
   - ⚠️ Review needed: LGPL, MPL
   - ❌ Prohibited: GPL, AGPL

3. **Update requirements:**
   ```bash
   # Add to requirements_opensource.txt for public dependencies
   # Add to requirements_full.txt for all dependencies
   pip freeze > requirements_full.txt
   ```

### Security Incident Response

If you discover a security vulnerability:

1. **DO NOT** open a public GitHub issue
2. **DO NOT** commit the vulnerability or exploit
3. **DO** email security@kr-labs.org immediately
4. **DO** include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and coordinate a fix.

### IP Protection & Trade Secrets

Some parts of the codebase contain proprietary algorithms or configurations:

- **Do not share** internal documentation externally
- **Do not discuss** proprietary methods in public forums
- **Do ask** maintainers if unsure about IP status
- **Do review** contributor license agreement (CLA)

By contributing, you agree to assign copyright of your contributions to KR-Labs and license them under Apache 2.0.

## Pull Request Process

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements

### 2. Make Changes

- Write code following our style guidelines
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 3. Commit Changes

```bash
git add .
git commit -m "feat: add OECD connector for development indicators"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 4. Run Pre-commit Checks

```bash
# Pre-commit hooks run automatically, but you can run manually:
pre-commit run --all-files

# Or run individual checks:
black src/
isort src/
flake8 src/
mypy src/
pytest
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub with:
- Clear title and description
- Reference to related issues (e.g., "Fixes #123")
- Screenshots/examples if applicable
- Checklist completed (see template)

### 6. PR Review Process

- Maintainers will review your PR
- Address feedback by pushing new commits
- Once approved, your PR will be merged
- Your contribution will be included in the next release

### PR Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines (Black, isort, flake8, mypy pass)
- [ ] Tests added/updated and passing (pytest)
- [ ] Coverage remains above 90% (pytest --cov)
- [ ] Documentation updated (docstrings, README, docs/)
- [ ] CHANGELOG.md updated with your changes
- [ ] No sensitive data or API keys in code
- [ ] Pre-commit hooks pass
- [ ] Commits are clean and well-described

## Adding New Connectors

### Connector Structure

All connectors must inherit from `BaseConnector`:

```python
# src/krl_data_connectors/connectors/your_connector.py
from typing import Dict, Any, Optional, List
import pandas as pd
from krl_data_connectors.base import BaseConnector
from krl_data_connectors.exceptions import APIError

class YourConnector(BaseConnector):
    """Connector for Your Data Source API.

    This connector provides access to [describe data source].

    Environment Variables:
        YOUR_API_KEY: API key for Your Data Source

    Example:
        >>> connector = YourConnector()
        >>> data = connector.get_data(param="value")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[str] = None,
        rate_limit: Optional[int] = None
    ):
        """Initialize connector.

        Args:
            api_key: API key (defaults to YOUR_API_KEY env var)
            cache_dir: Cache directory path
            rate_limit: Max requests per second
        """
        super().__init__(
            base_url="https://api.example.com",
            api_key=api_key,
            api_key_env="YOUR_API_KEY",
            cache_dir=cache_dir,
            rate_limit=rate_limit
        )

    def get_data(
        self,
        param: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch data from API.

        Args:
            param: Parameter to fetch
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            DataFrame with fetched data

        Raises:
            APIError: If API request fails
            ValueError: If parameters are invalid

        Example:
            >>> connector = YourConnector()
            >>> data = connector.get_data("population")
        """
        # Validate parameters
        if not param:
            raise ValueError("param is required")

        # Build endpoint
        endpoint = f"/data/{param}"
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        # Fetch data (uses caching automatically)
        response = self._get(endpoint, params=params)

        # Parse and return as DataFrame
        return self._parse_response(response)

    def _parse_response(self, response: Dict[str, Any]) -> pd.DataFrame:
        """Parse API response into DataFrame.

        Args:
            response: Raw API response

        Returns:
            Parsed DataFrame
        """
        # Implement parsing logic
        data = response.get("data", [])
        return pd.DataFrame(data)
```

### Required Components

1. **Class docstring** with description and example
2. **Environment variable** documentation
3. **Type hints** for all methods
4. **Comprehensive docstrings** for public methods
5. **Error handling** with custom exceptions
6. **Response parsing** to pandas DataFrame
7. **Unit tests** with mocked responses
8. **Integration tests** (if API key available)
9. **Example notebook** in `examples/`
10. **Documentation** in `docs/api/`

### Connector Checklist

When adding a new connector:

- [ ] Connector class created in `src/krl_data_connectors/connectors/`
- [ ] Inherits from `BaseConnector`
- [ ] All methods have type hints
- [ ] All methods have docstrings with examples
- [ ] Error handling implemented
- [ ] Test file created in `tests/connectors/`
- [ ] Unit tests with mocked responses (90%+ coverage)
- [ ] Integration test (if API key available)
- [ ] Example notebook created in `examples/`
- [ ] Documentation added to `docs/api/[category].rst`
- [ ] README.md updated with connector info
- [ ] API key setup instructions in API_KEY_SETUP.md
- [ ] CHANGELOG.md updated

## Documentation

### Types of Documentation

1. **Code documentation**: Docstrings in code
2. **User guide**: README.md, docs/
3. **API reference**: Sphinx autodoc in docs/api/
4. **Examples**: Jupyter notebooks in examples/
5. **Troubleshooting**: TROUBLESHOOTING.md, FAQ.md

### Building Documentation Locally

```bash
# Install docs dependencies
pip install -e ".[docs]"

# Build HTML docs
cd docs
make html

# View in browser
open _build/html/index.html  # macOS
# or
xdg-open _build/html/index.html  # Linux
# or
start _build/html/index.html  # Windows
```

### Documentation Style

- Use clear, concise language
- Provide code examples
- Include expected output
- Explain common pitfalls
- Link to related documentation

## Release Process

Releases are managed by maintainers. The process:

1. **Version bump**: Update version in `pyproject.toml`
2. **CHANGELOG**: Update `CHANGELOG.md` with changes
3. **Tag**: Create git tag (e.g., `v0.2.0`)
4. **GitHub Release**: Create release with notes
5. **PyPI**: Publish to PyPI (automated via GitHub Actions)
6. **ReadTheDocs**: Documentation auto-updates

## Getting Help

- **Documentation**: https://krl-data-connectors.readthedocs.io
- **Issues**: https://github.com/KR-Labs/krl-data-connectors/issues
- **Discussions**: https://github.com/KR-Labs/krl-data-connectors/discussions

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for contributing to KRL Data Connectors!**
