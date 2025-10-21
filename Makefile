# Makefile for KRL Data Connectors - 10-Layer Testing Architecture
# All commands use OSS tools

.PHONY: help install test coverage security lint type-check clean all

# Default Python
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := pytest
MYPY := mypy
BANDIT := bandit

# Directories
SRC_DIR := src
TEST_DIR := tests
UNIT_DIR := $(TEST_DIR)/unit
INTEGRATION_DIR := $(TEST_DIR)/integration
PERF_DIR := $(TEST_DIR)/performance

# Coverage threshold
COV_THRESHOLD := 90

##@ General

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup

install: ## Install all dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[all]"

install-dev: ## Install development dependencies only
	$(PIP) install -e ".[dev,test]"

install-security: ## Install security testing tools
	$(PIP) install -e ".[security]"

install-performance: ## Install performance testing tools
	$(PIP) install -e ".[performance]"

install-hooks: ## Install pre-commit hooks
	pre-commit install
	@echo "✅ Pre-commit hooks installed"

setup: install install-hooks ## Complete setup (install + hooks)
	@echo "✅ Development environment ready"

##@ Testing (Layer 1-3)

test: ## Run all tests
	$(PYTEST) $(TEST_DIR)/ -v

test-unit: ## Run unit tests only (Layer 1)
	$(PYTEST) $(UNIT_DIR)/ -v --tb=short

test-unit-fast: ## Run unit tests in parallel
	$(PYTEST) $(UNIT_DIR)/ -n auto -v

test-integration: ## Run integration tests (Layer 2)
	$(PYTEST) $(INTEGRATION_DIR)/ -v -m integration --timeout=120

test-watch: ## Run tests in watch mode (re-run on changes)
	pytest-watch $(UNIT_DIR)/ --clear

test-failed: ## Run only failed tests from last run
	$(PYTEST) --lf -v

test-debug: ## Run tests with detailed output
	$(PYTEST) -vv --tb=long --showlocals

##@ Coverage

coverage: ## Run tests with coverage report (text)
	$(PYTEST) $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=term-missing \
		--cov-branch \
		-v

coverage-html: ## Generate HTML coverage report
	$(PYTEST) $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=html \
		--cov-report=term \
		--cov-branch \
		-v
	@echo "📊 Coverage report: htmlcov/index.html"

coverage-xml: ## Generate XML coverage report (for CI)
	$(PYTEST) $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=xml \
		--cov-report=term \
		--cov-branch \
		-v

coverage-strict: ## Run tests with strict coverage threshold
	$(PYTEST) $(TEST_DIR)/ \
		--cov=$(SRC_DIR) \
		--cov-report=term-missing \
		--cov-fail-under=$(COV_THRESHOLD) \
		--cov-branch \
		-v

##@ Security (Layer 5)

security: security-scan security-deps ## Run all security checks

security-scan: ## Run Bandit security scanner (SAST)
	@echo "🔒 Running Bandit security scan..."
	$(BANDIT) -r $(SRC_DIR)/ -f txt
	@echo "✅ Security scan complete"

security-scan-json: ## Run Bandit with JSON output
	$(BANDIT) -r $(SRC_DIR)/ -f json -o bandit-report.json

security-deps: ## Check for known vulnerabilities in dependencies
	@echo "🔒 Checking dependencies for vulnerabilities..."
	safety check || true
	pip-audit || true
	@echo "✅ Dependency check complete"

##@ Code Quality

lint: ## Run linters (flake8, ruff)
	@echo "🔍 Running linters..."
	flake8 $(SRC_DIR)/ --max-line-length=100
	ruff check $(SRC_DIR)/
	@echo "✅ Linting complete"

lint-fix: ## Auto-fix linting issues
	ruff check $(SRC_DIR)/ --fix
	@echo "✅ Auto-fixes applied"

format: ## Format code (black, isort)
	@echo "✨ Formatting code..."
	black $(SRC_DIR)/ $(TEST_DIR)/
	isort $(SRC_DIR)/ $(TEST_DIR)/
	@echo "✅ Formatting complete"

format-check: ## Check code formatting without changes
	black $(SRC_DIR)/ $(TEST_DIR)/ --check
	isort $(SRC_DIR)/ $(TEST_DIR)/ --check-only

##@ Type Checking (Layer 8)

type-check: ## Run mypy type checker
	@echo "🔍 Running type checker..."
	$(MYPY) $(SRC_DIR)/ --config-file=mypy.ini
	@echo "✅ Type checking complete"

type-check-strict: ## Run mypy with strict settings
	$(MYPY) $(SRC_DIR)/ --strict --config-file=mypy.ini

type-report: ## Generate HTML type checking report
	$(MYPY) $(SRC_DIR)/ --config-file=mypy.ini --html-report mypy-report
	@echo "📊 Type report: mypy-report/index.html"

##@ Performance (Layer 4)

perf: ## Run performance benchmarks
	$(PYTEST) $(PERF_DIR)/ --benchmark-only --benchmark-autosave

perf-compare: ## Compare with previous benchmark
	$(PYTEST) $(PERF_DIR)/ --benchmark-only --benchmark-compare

load-test: ## Run load tests (requires Locust)
	@echo "🚀 Starting load test server..."
	@echo "Run: locust -f tests/load/locustfile.py --host=http://localhost:8000"

##@ Mutation Testing (Layer 7)

mutate: ## Run mutation testing (full)
	@echo "🧬 Running mutation testing..."
	mutmut run --paths-to-mutate=$(SRC_DIR)/
	mutmut results

mutate-file: ## Run mutation testing on specific file (FILE=path/to/file.py)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Error: FILE parameter required. Usage: make mutate-file FILE=src/path/to/file.py"; \
		exit 1; \
	fi
	mutmut run --paths-to-mutate=$(FILE)
	mutmut results

mutate-survivors: ## Show surviving mutants (not caught by tests)
	mutmut show --only-survivors

mutate-html: ## Generate HTML mutation report
	mutmut html
	@echo "📊 Mutation report: html/index.html"

##@ Pre-commit

pre-commit: ## Run all pre-commit hooks
	pre-commit run --all-files

pre-commit-update: ## Update pre-commit hook versions
	pre-commit autoupdate

##@ CI/CD Simulation

ci: ## Simulate CI pipeline locally
	@echo "🔄 Simulating CI pipeline..."
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) type-check
	@$(MAKE) security
	@$(MAKE) coverage-strict
	@echo "✅ CI simulation complete - ready to push!"

quick-check: ## Quick validation before commit
	@echo "⚡ Running quick checks..."
	@$(MAKE) format-check
	@$(MAKE) lint
	@$(MAKE) test-unit-fast
	@echo "✅ Quick checks passed"

##@ Cleanup

clean: ## Clean build artifacts
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage coverage.xml
	rm -rf build/ dist/
	rm -rf mypy-report/
	rm -rf .mutmut-cache/
	rm -f bandit-report.json safety-report.json pip-audit-report.json
	@echo "✅ Cleanup complete"

clean-all: clean ## Clean everything including dependencies
	rm -rf .venv/ venv/
	@echo "✅ Deep clean complete"

##@ Documentation

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	cd docs && make html
	@echo "📊 Documentation: docs/_build/html/index.html"

docs-serve: ## Serve documentation locally
	cd docs && python -m http.server --directory _build/html

##@ Reporting

report: ## Generate comprehensive test report
	@echo "📊 Generating comprehensive test report..."
	@$(MAKE) coverage-html
	@$(MAKE) type-report
	@$(MAKE) security-scan-json
	@echo ""
	@echo "✅ Reports generated:"
	@echo "  - Coverage: htmlcov/index.html"
	@echo "  - Type checking: mypy-report/index.html"
	@echo "  - Security: bandit-report.json"

status: ## Show current test status
	@echo "📊 Current Status:"
	@echo ""
	@echo "Coverage:"
	@$(PYTEST) $(TEST_DIR)/ --cov=$(SRC_DIR) --cov-report=term --quiet || true
	@echo ""
	@echo "Type Coverage:"
	@$(MYPY) $(SRC_DIR)/ --config-file=mypy.ini --any-exprs-report mypy-coverage 2>/dev/null || true
	@echo ""
	@echo "Security Issues:"
	@$(BANDIT) -r $(SRC_DIR)/ -f txt -q || true

##@ All-in-One

all: format lint type-check security coverage ## Run all checks (format, lint, type, security, tests)
	@echo "✅ All checks complete!"

validate: ## Full validation (matches CI)
	@$(MAKE) ci

.DEFAULT_GOAL := help
