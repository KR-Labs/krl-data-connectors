---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# Testing Guide - 10-Layer Architecture

This guide shows developers how to use the comprehensive testing stack in day-to-day development.

## Quick Start

### 1. Install Testing Dependencies

```bash
# Install all testing tools
pip install -e ".[test,security,performance,mutation,contract]"

# Set up pre-commit hooks
pre-commit install
```

### 2. Run Tests Locally

```bash
# Fast: Run unit tests only (Layer 1)
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=src --cov-report=term-missing

# All tests
pytest tests/ -v

# Parallel execution (faster)
pytest tests/unit/ -n auto
```

## Layer-by-Layer Usage

### Layer 1: Unit Tests (Daily Use)

**Purpose**: Test individual functions in isolation.

```bash
# Run specific test file
pytest tests/unit/test_chr_connector.py -v

# Run specific test
pytest tests/unit/test_chr_connector.py::test_initialization -v

# Run with markers
pytest tests/unit/ -m "fast" -v

# Watch mode (re-run on file changes)
pytest-watch tests/unit/
```

**Writing Unit Tests**:
```python
import pytest
from krl_data_connectors.health.chr_connector import CHRConnector

def test_chr_initialization():
    """Test connector initializes correctly."""
    connector = CHRConnector(api_key="test_key")
    assert connector.api_key == "test_key"
    assert connector.base_url is not None

@pytest.mark.parametrize("state,expected", [
    ("CA", True),
    ("XX", False),
    ("", False),
])
def test_state_validation(state, expected):
    """Test state code validation."""
    connector = CHRConnector()
    result = connector.validate_state(state)
    assert result == expected

# Security test
def test_sql_injection_prevention():
    """Ensure SQL injection attempts are handled."""
    connector = CHRConnector()
    malicious = "'; DROP TABLE data; --"
    result = connector.query(malicious)
    # Should return None or handle gracefully
    assert result is None or isinstance(result, pd.DataFrame)
```

### Layer 2: Integration Tests

**Purpose**: Test component interactions.

```bash
# Run integration tests
pytest tests/integration/ -v -m integration

# With slower timeout
pytest tests/integration/ --timeout=120
```

**Writing Integration Tests**:
```python
import pytest
import requests_mock

def test_api_authentication():
    """Test API key authentication flow."""
    with requests_mock.Mocker() as m:
        m.get('https://api.example.com/data', 
              status_code=401,
              text='Unauthorized')
        
        connector = CHRConnector(api_key="invalid")
        with pytest.raises(AuthenticationError):
            connector.fetch_data()

def test_rate_limiting():
    """Test rate limit handling."""
    connector = CHRConnector()
    
    # Make multiple requests
    for i in range(100):
        result = connector.fetch_data()
    
    # Should handle rate limiting gracefully
    assert connector.requests_made <= connector.rate_limit
```

### Layer 4: Performance Tests

**Purpose**: Benchmark performance, find bottlenecks.

```bash
# Run performance benchmarks
pytest tests/performance/ --benchmark-only

# Save benchmark results
pytest tests/performance/ --benchmark-autosave

# Compare with previous
pytest tests/performance/ --benchmark-compare
```

**Writing Performance Tests**:
```python
import pytest

@pytest.mark.benchmark
def test_data_transformation_performance(benchmark):
    """Benchmark data transformation speed."""
    connector = CHRConnector()
    large_dataset = generate_test_data(rows=10000)
    
    result = benchmark(connector.transform, large_dataset)
    
    # Assert performance SLAs
    assert benchmark.stats.mean < 0.5  # 500ms average
    assert benchmark.stats.max < 2.0   # 2s maximum

@pytest.mark.performance
def test_concurrent_requests():
    """Test performance under concurrent load."""
    import concurrent.futures
    
    connector = CHRConnector()
    
    def fetch():
        return connector.get_state_data("CA")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch) for _ in range(100)]
        results = [f.result() for f in futures]
    
    assert all(r is not None for r in results)
```

### Layer 5: SAST (Security Scanning)

**Purpose**: Find security vulnerabilities in code.

```bash
# Run Bandit security scan
bandit -r src/ -f txt

# Check for known vulnerabilities
safety check

# Audit pip packages
pip-audit

# All security checks
make security-scan  # If Makefile exists
```

**Common Issues & Fixes**:
```python
#  Bad: Using eval with user input
result = eval(user_input)

#  Good: Parse safely
import ast
result = ast.literal_eval(user_input)

#  Bad: SQL injection risk
query = f"SELECT * FROM data WHERE state = '{state}'"

#  Good: Parameterized query
query = "SELECT * FROM data WHERE state = ?"
cursor.execute(query, (state,))

#  Bad: Insecure request
response = requests.get(url, verify=False)

#  Good: Verify SSL
response = requests.get(url, verify=True)
```

### Layer 7: Mutation Testing

**Purpose**: Measure test quality by introducing bugs.

```bash
# Run mutation testing on specific file
mutmut run --paths-to-mutate=src/krl_data_connectors/health/chr_connector.py

# View results
mutmut results

# Show surviving mutants (tests didn't catch)
mutmut show --only-survivors

# Show specific mutant
mutmut show 42

# Run tests on specific mutant
mutmut run 42
```

**Understanding Mutation Results**:
- **Killed**: Test caught the mutation 
- **Survived**: Test missed the mutation 
- **Incompetent**: Mutation created invalid syntax
- **Timeout**: Mutation caused infinite loop

**Target**: ≥90% kill rate

### Layer 8: Type Checking

**Purpose**: Catch type errors before runtime.

```bash
# Run mypy type checker
mypy src/ --config-file mypy.ini

# Check specific file
mypy src/krl_data_connectors/health/chr_connector.py

# Generate HTML report
mypy src/ --html-report mypy-report
```

**Adding Type Hints**:
```python
from typing import Optional, List, Dict, Union
import pandas as pd

def get_state_data(
    self,
    state: str,
    year: Optional[int] = None
) -> Optional[pd.DataFrame]:
    """
    Get data for a specific state.
    
    Args:
        state: Two-letter state code
        year: Optional year filter
        
    Returns:
        DataFrame with state data, or None if not found
    """
    pass

# Use pydantic for validation
from pydantic import BaseModel, Field, validator

class ConnectorConfig(BaseModel):
    api_key: str = Field(..., min_length=10)
    timeout: int = Field(default=30, ge=1, le=300)
    base_url: str = Field(..., regex=r'^https?://')
```

### Layer 10: Pre-commit Hooks

**Purpose**: Automatic checks before every commit.

```bash
# Install hooks (one time)
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on staged files
pre-commit run

# Skip hooks (not recommended)
git commit --no-verify
```

**What Runs on Commit**:
1. Code formatting (Black, isort)
2. Security scan (Bandit)
3. Type checking (mypy)
4. Quick unit tests
5. Detect secrets
6. Check for internal docs

## Property-Based Testing with Hypothesis

**Purpose**: Test with automatically generated inputs.

```bash
pip install hypothesis
```

**Example**:
```python
from hypothesis import given, strategies as st
import pandas as pd

@given(st.lists(st.floats(allow_nan=False), min_size=0, max_size=1000))
def test_transformation_never_crashes(values):
    """Property: transformation should handle any numeric input."""
    connector = CHRConnector()
    df = pd.DataFrame({'value': values})
    
    result = connector.transform(df)
    
    # Should always return valid DataFrame
    assert isinstance(result, pd.DataFrame)
    assert len(result) >= 0

@given(
    state=st.text(min_size=2, max_size=2),
    year=st.integers(min_value=2000, max_value=2025)
)
def test_state_query_properties(state, year):
    """Property: queries should be consistent."""
    connector = CHRConnector()
    result = connector.get_state_data(state, year)
    
    if result is not None:
        assert 'state' in result.columns
        assert all(result['year'] == year)
```

## CI/CD Pipeline

### What Runs When

**On Every Commit (PR)**:
-  Unit tests (all Python versions)
-  Integration tests
-  SAST security scan
-  Type checking
-  Dependency vulnerability scan
-  Coverage report

**Nightly (Scheduled)**:
-  Full test suite
-  Performance benchmarks
-  DAST security scan
-  Load testing

**Weekly (Sunday 2 AM)**:
-  Mutation testing

### Viewing CI Results

1. **GitHub Actions**: Check Actions tab
2. **Coverage**: View in PR comment or Codecov
3. **Security**: Check Security tab → Code scanning alerts
4. **Artifacts**: Download reports from workflow runs

## Coverage Goals

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Line Coverage | 73.30% | 90% | 🟡 In Progress |
| Branch Coverage | ~70% | 85% | 🟡 In Progress |
| Mutation Score | TBD | 90% |  Not Started |

## Common Commands

```bash
# Daily development
pytest tests/unit/ -v --cov=src

# Before committing
pre-commit run --all-files

# Before opening PR
pytest tests/ --cov=src --cov-fail-under=90

# Security check
bandit -r src/ && safety check

# Type check
mypy src/

# Full local validation (matches CI)
pytest tests/ --cov=src --cov-fail-under=90 && \
bandit -r src/ && \
safety check && \
mypy src/
```

## Troubleshooting

### Tests Running Slow
```bash
# Use parallel execution
pytest tests/ -n auto

# Run only changed tests
pytest --lf  # last failed
pytest --ff  # failed first

# Skip slow tests
pytest -m "not slow"
```

### Coverage Not Increasing
```bash
# See what's not covered
pytest --cov=src --cov-report=term-missing

# Generate HTML report for detailed view
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Pre-commit Hooks Failing
```bash
# See what failed
pre-commit run --all-files --verbose

# Update hooks
pre-commit autoupdate

# Skip problematic hook temporarily
SKIP=mypy git commit -m "..."
```

### Type Errors
```bash
# Ignore specific line
result = some_function()  # type: ignore

# Ignore specific error
result = some_function()  # type: ignore[arg-type]

# Check what's wrong
mypy src/file.py --show-error-codes
```

## Best Practices

### 1. Write Tests First (TDD)
```python
# 1. Write failing test
def test_new_feature():
    result = connector.new_feature()
    assert result == expected

# 2. Run test (should fail)
pytest tests/unit/test_connector.py::test_new_feature

# 3. Implement feature
def new_feature(self):
    return implementation

# 4. Run test (should pass)
pytest tests/unit/test_connector.py::test_new_feature
```

### 2. Test Edge Cases
```python
@pytest.mark.parametrize("input,expected", [
    (None, None),  # Null input
    ("", None),  # Empty string
    ("X", None),  # Invalid short
    ("XXX", None),  # Invalid long
    ("CA", data),  # Valid
    ("ca", data),  # Lowercase
    (" CA ", data),  # Whitespace
])
def test_edge_cases(input, expected):
    result = connector.get_state_data(input)
    assert result == expected
```

### 3. Use Fixtures
```python
@pytest.fixture
def connector():
    """Reusable connector instance."""
    return CHRConnector(api_key="test_key")

@pytest.fixture
def sample_data():
    """Reusable test data."""
    return pd.DataFrame({
        'state': ['CA', 'NY', 'TX'],
        'value': [100, 200, 300]
    })

def test_with_fixtures(connector, sample_data):
    result = connector.process(sample_data)
    assert len(result) == 3
```

### 4. Mock External APIs
```python
import requests_mock

def test_api_call():
    with requests_mock.Mocker() as m:
        m.get('https://api.example.com/data', json={'status': 'ok'})
        
        connector = CHRConnector()
        result = connector.fetch()
        
        assert result['status'] == 'ok'
        assert m.called
        assert m.call_count == 1
```

## Resources

- **pytest**: https://docs.pytest.org/
- **Hypothesis**: https://hypothesis.readthedocs.io/
- **Bandit**: https://bandit.readthedocs.io/
- **mypy**: https://mypy.readthedocs.io/
- **Locust**: https://docs.locust.io/
- **Mutmut**: https://mutmut.readthedocs.io/

## Getting Help

1. Check this guide first
2. Look at existing test examples in `tests/`
3. Ask in team chat
4. Check tool documentation (links above)
5. GitHub issues for specific problems
