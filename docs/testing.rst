.. Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Testing Guide
=============

This guide shows developers how to use the comprehensive testing stack in day-to-day development.

Quick Start
-----------

1. Install Testing Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install all testing tools
   pip install -e ".[test,security,performance,mutation,contract]"

   # Set up pre-commit hooks
   pre-commit install

2. Run Tests Locally
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Fast: Run unit tests only
   pytest tests/unit/ -v

   # With coverage
   pytest tests/unit/ --cov=src --cov-report=term-missing

   # All tests
   pytest tests/ -v

   # Parallel execution (faster)
   pytest tests/unit/ -n auto

Using Make Commands
-------------------

The Makefile provides convenient shortcuts for all testing operations:

.. code-block:: bash

   # Testing
   make test              # Run all tests
   make test-unit        # Unit tests only
   make test-unit-fast   # Parallel execution
   make coverage         # Coverage report
   make coverage-html    # HTML coverage report

   # Security
   make security         # All security checks
   make security-scan    # Bandit scan
   make security-deps    # Dependency check

   # Quality
   make lint             # Run linters
   make format           # Format code
   make type-check       # Type checking

   # Advanced
   make mutate           # Mutation testing
   make perf             # Performance benchmarks
   make ci               # Full CI simulation

   # Utilities
   make clean            # Clean artifacts
   make help             # Show all commands

Testing Architecture
--------------------

KRL Data Connectors implement a **10-layer testing architecture** following industry best practices:

.. list-table:: Testing Layers
   :header-rows: 1
   :widths: 10 30 30 30

   * - Layer
     - Purpose
     - Tools
     - Status
   * - 1
     - Unit Tests
     - pytest, hypothesis
     - ✅ 408 tests, 73% coverage
   * - 2
     - Integration Tests
     - pytest, requests-mock
     - ✅ Implemented
   * - 3
     - E2E Tests
     - playwright
     - 🔄 Planned
   * - 4
     - Performance Tests
     - locust, pytest-benchmark
     - 🔄 Planned
   * - 5
     - SAST Security
     - bandit, safety, mypy
     - ✅ Configured
   * - 6
     - DAST Security
     - OWASP ZAP
     - 🔄 Planned
   * - 7
     - Mutation Testing
     - mutmut, hypothesis
     - 🔄 Planned
   * - 8
     - Contract Testing
     - pydantic, mypy
     - ✅ Configured
   * - 9
     - Penetration Testing
     - metasploit, burp
     - 📅 Annual
   * - 10
     - Continuous Monitoring
     - GitHub Actions, Snyk
     - ✅ Active

Layer 1: Unit Tests
--------------------

Unit tests validate individual functions in isolation.

Running Unit Tests
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Run specific test file
   pytest tests/unit/test_chr_connector.py -v

   # Run specific test
   pytest tests/unit/test_chr_connector.py::test_initialization -v

   # Run with markers
   pytest tests/unit/ -m "fast" -v

Writing Unit Tests
~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

Layer 2: Integration Tests
---------------------------

Integration tests validate component interactions.

.. code-block:: bash

   # Run integration tests
   pytest tests/integration/ -v -m integration

   # With slower timeout
   pytest tests/integration/ --timeout=120

Layer 4: Performance Tests
---------------------------

Performance tests benchmark speed and find bottlenecks.

.. code-block:: bash

   # Run performance benchmarks
   pytest tests/performance/ --benchmark-only

   # Save benchmark results
   pytest tests/performance/ --benchmark-autosave

   # Compare with previous
   pytest tests/performance/ --benchmark-compare

Layer 5: SAST (Security Scanning)
----------------------------------

Static Application Security Testing finds vulnerabilities before runtime.

.. code-block:: bash

   # Run Bandit security scan
   bandit -r src/ -f txt

   # Check for known vulnerabilities
   safety check

   # Audit pip packages
   pip-audit

   # All security checks
   make security-scan

Layer 7: Mutation Testing
--------------------------

Mutation testing measures test quality by introducing bugs.

.. code-block:: bash

   # Run mutation testing on specific file
   mutmut run --paths-to-mutate=src/krl_data_connectors/health/chr_connector.py

   # View results
   mutmut results

   # Show surviving mutants (tests didn't catch)
   mutmut show --only-survivors

**Target**: ≥90% kill rate

Layer 8: Type Checking
-----------------------

Type checking catches type errors before runtime.

.. code-block:: bash

   # Run mypy type checker
   mypy src/ --config-file=mypy.ini

   # Check specific file
   mypy src/krl_data_connectors/health/chr_connector.py

   # Generate HTML report
   mypy src/ --html-report mypy-report

Adding Type Hints
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from typing import Optional, List, Dict
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

Pre-commit Hooks
----------------

Pre-commit hooks run automatically before every commit:

.. code-block:: bash

   # Install hooks (one time)
   pre-commit install

   # Run manually on all files
   pre-commit run --all-files

   # Run on staged files
   pre-commit run

What Runs on Commit
~~~~~~~~~~~~~~~~~~~

1. Code formatting (Black, isort)
2. Security scan (Bandit)
3. Type checking (mypy)
4. Quick unit tests
5. Detect secrets
6. Check for internal docs

CI/CD Pipeline
--------------

What Runs When
~~~~~~~~~~~~~~

**On Every Commit (PR)**:

- ✅ Unit tests (all Python versions)
- ✅ Integration tests
- ✅ SAST security scan
- ✅ Type checking
- ✅ Dependency vulnerability scan
- ✅ Coverage report

**Nightly (Scheduled)**:

- ✅ Full test suite
- ✅ Performance benchmarks
- ✅ DAST security scan
- ✅ Load testing

**Weekly (Sunday 2 AM)**:

- ✅ Mutation testing

Coverage Goals
--------------

.. list-table:: Coverage Targets
   :header-rows: 1
   :widths: 30 20 20 30

   * - Metric
     - Current
     - Target
     - Status
   * - Line Coverage
     - 73.30%
     - 90%
     - 🟡 In Progress
   * - Branch Coverage
     - ~70%
     - 85%
     - 🟡 In Progress
   * - Mutation Score
     - TBD
     - 90%
     - ⚪ Not Started

Common Commands
---------------

.. code-block:: bash

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
   make ci

Troubleshooting
---------------

Tests Running Slow
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Use parallel execution
   pytest tests/ -n auto

   # Run only changed tests
   pytest --lf  # last failed
   pytest --ff  # failed first

   # Skip slow tests
   pytest -m "not slow"

Coverage Not Increasing
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # See what's not covered
   pytest --cov=src --cov-report=term-missing

   # Generate HTML report for detailed view
   pytest --cov=src --cov-report=html
   open htmlcov/index.html

Pre-commit Hooks Failing
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # See what failed
   pre-commit run --all-files --verbose

   # Update hooks
   pre-commit autoupdate

   # Skip problematic hook temporarily
   SKIP=mypy git commit -m "..."

Best Practices
--------------

1. Write Tests First (TDD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # 1. Write failing test
   def test_new_feature():
       result = connector.new_feature()
       assert result == expected

   # 2. Run test (should fail)
   # 3. Implement feature
   # 4. Run test (should pass)

2. Test Edge Cases
~~~~~~~~~~~~~~~~~~

.. code-block:: python

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

3. Use Fixtures
~~~~~~~~~~~~~~~

.. code-block:: python

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

Resources
---------

- **pytest**: https://docs.pytest.org/
- **Hypothesis**: https://hypothesis.readthedocs.io/
- **Bandit**: https://bandit.readthedocs.io/
- **mypy**: https://mypy.readthedocs.io/
- **Locust**: https://docs.locust.io/
- **Mutmut**: https://mutmut.readthedocs.io/

Getting Help
------------

1. Check this guide first
2. Look at existing test examples in ``tests/``
3. Check tool documentation (links above)
4. GitHub issues for specific problems
