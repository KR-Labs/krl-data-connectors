# Internal Testing Strategy - 10-Layer Architecture
<!-- INTERNAL DOCUMENT - DO NOT PUBLISH -->

**Document Status**: INTERNAL - Engineering Reference Only  
**Last Updated**: October 20, 2025  
**Owner**: Engineering Team  
**Classification**: Confidential

---

## Executive Summary

This document defines KR-Labs' comprehensive testing architecture implementing defense-in-depth across 10 testing layers. All tooling is open-source (OSS), following industry best practices from FAANG, fintech, and defense sectors.

**Coverage Targets**:
- Unit/Integration: 90-100% line coverage
- E2E: 100% critical workflows
- Security: Zero critical vulnerabilities
- Mutation: ≥90% kill rate

---

## Testing Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTINUOUS MONITORING                     │
│           (GitHub Actions, Snyk, Dependabot)                 │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────┬───────────┴───────────┬──────────────────┐
│   LAYER 1-3     │     LAYER 4-5         │    LAYER 6-9     │
│  Functional     │     Security          │   Deep Testing   │
├─────────────────┼───────────────────────┼──────────────────┤
│ • Unit          │ • SAST (Bandit)       │ • DAST (ZAP)     │
│ • Integration   │ • Dependency Scan     │ • Fuzz Testing   │
│ • E2E           │ • Code Quality        │ • Mutation       │
│ • Performance   │                       │ • Pen Testing    │
└─────────────────┴───────────────────────┴──────────────────┘
```

---

## Layer 1: Unit Tests (Functional Baseline)

### Purpose
Validate correctness of individual functions in isolation.

### Current Status
- ✅ **Framework**: pytest 8.4.2
- ✅ **Coverage**: 73.30% overall (target: 90-100%)
- ✅ **Tests**: 408 passing, 0 failing

### OSS Stack
```yaml
Core:
  - pytest: Test framework
  - pytest-cov: Coverage measurement
  - pytest-mock: Mocking utilities
  - hypothesis: Property-based testing

Enhancements:
  - pytest-xdist: Parallel execution
  - pytest-timeout: Test time limits
  - pytest-randomly: Randomized test order
```

### Security Enhancements
```python
# Example: Testing against malicious inputs
def test_query_sql_injection():
    """Ensure connector sanitizes SQL-like inputs."""
    connector = Connector()
    malicious = "'; DROP TABLE users; --"
    result = connector.query(malicious)
    assert result is None or isinstance(result, pd.DataFrame)
    # Should not raise or execute injection

def test_xss_in_string_fields():
    """Ensure HTML/script tags are escaped."""
    connector = Connector()
    xss_input = "<script>alert('xss')</script>"
    result = connector.process_field(xss_input)
    assert "<script>" not in str(result)
```

### Branch Coverage Enforcement
```bash
# Require 90% branch coverage
pytest --cov=src --cov-report=term-missing --cov-fail-under=90 --cov-branch
```

### Implementation Tasks
- [ ] Add hypothesis property-based tests for all data transformations
- [ ] Add malicious input tests (SQL injection, XSS, path traversal)
- [ ] Add edge case tests (empty arrays, nulls, corrupted files)
- [ ] Enable branch coverage enforcement in CI/CD
- [ ] Add pytest-xdist for parallel execution

---

## Layer 2: Integration Tests (System Cohesion)

### Purpose
Validate interactions between components, API boundaries, data flow.

### Current Status
- ✅ **Framework**: pytest + requests-mock
- ⚠️ **Coverage**: Partial integration testing
- 🔄 **Needs**: Dedicated integration test suite

### OSS Stack
```yaml
Core:
  - pytest: Test framework
  - requests-mock: HTTP mocking
  - responses: Alternative HTTP mocking
  - httpretty: HTTP request interception
  
API Testing:
  - newman: Postman CLI runner
  - tavern: API testing framework
  - schemathesis: OpenAPI-based testing
```

### Security Enhancements
```python
# Example: Authentication/Authorization testing
def test_api_requires_authentication():
    """Ensure API endpoints require valid auth."""
    connector = APIConnector()
    with pytest.raises(AuthenticationError):
        connector.fetch_data(api_key=None)

def test_rate_limiting():
    """Ensure rate limiting is enforced."""
    connector = APIConnector()
    for i in range(100):
        response = connector.fetch_data()
    # Should trigger rate limit
    with pytest.raises(RateLimitError):
        connector.fetch_data()

def test_timeout_handling():
    """Ensure network timeouts are handled gracefully."""
    with requests_mock.Mocker() as m:
        m.get('http://api.example.com', exc=requests.Timeout)
        connector = APIConnector()
        result = connector.fetch_data()
        assert result is None or result.error_code == 'timeout'
```

### Implementation Tasks
- [ ] Create dedicated `tests/integration/` directory
- [ ] Add authentication/authorization tests for all API connectors
- [ ] Add network failure simulation tests (timeouts, 500s, 503s)
- [ ] Add data encryption validation tests
- [ ] Add cross-connector integration tests
- [ ] Implement API contract testing with schemathesis

---

## Layer 3: End-to-End Tests (Behavioral Realism)

### Purpose
Validate full workflows as end users experience them.

### Current Status
- ⚠️ **Status**: Not yet implemented
- 🎯 **Target**: 100% critical workflows

### OSS Stack
```yaml
Core:
  - playwright: Modern E2E testing (recommended)
  - selenium: Web automation
  - robot-framework: Keyword-driven testing
  
Python Specific:
  - pytest-playwright: Playwright integration
  - selenium-python: Python Selenium bindings
```

### Security Enhancements
```python
# Example: Session security testing
def test_session_hijacking_prevention():
    """Ensure session tokens are properly secured."""
    # Simulate session creation
    session = create_session(user="test")
    
    # Attempt to use token from different IP
    with pytest.raises(SecurityError):
        use_session(session.token, ip="different_ip")

def test_concurrent_session_handling():
    """Ensure system handles multiple sessions correctly."""
    sessions = [create_session(user="test") for _ in range(10)]
    results = [validate_session(s.token) for s in sessions]
    assert all(results)
```

### Critical Workflows to Test
```yaml
Data Connector Workflows:
  - Initialize → Authenticate → Fetch → Transform → Return
  - Cache Management: Fetch → Cache → Retrieve → Validate Freshness
  - Error Recovery: Fetch → Fail → Retry → Fallback → Return
  
Security Workflows:
  - API Key Validation → Request → Rate Limit Check → Response
  - Data Sanitization: Input → Validate → Clean → Process
  - Access Control: Request → Check Permissions → Allow/Deny
```

### Implementation Tasks
- [ ] Set up Playwright for Python
- [ ] Create E2E test suite for critical workflows
- [ ] Add session security tests
- [ ] Add concurrent access tests
- [ ] Add access control validation tests
- [ ] Implement smoke tests for production monitoring

---

## Layer 4: Performance & Load Tests (Resilience)

### Purpose
Ensure stability under stress, measure throughput and latency.

### Current Status
- ❌ **Status**: Not implemented
- 🎯 **Target**: P99 latency < 500ms under peak load

### OSS Stack
```yaml
Core:
  - locust: Python load testing framework (RECOMMENDED)
  - k6: Go-based load testing
  - jmeter: Java-based load testing
  
Python Specific:
  - pytest-benchmark: Microbenchmarking
  - memory_profiler: Memory usage profiling
```

### Test Scenarios
```python
# locustfile.py - Example load test
from locust import HttpUser, task, between

class DataConnectorUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def fetch_state_data(self):
        """Most common operation - higher weight."""
        self.client.get("/api/connector/state/CA")
    
    @task(1)
    def fetch_all_states(self):
        """Heavy operation - lower weight."""
        self.client.get("/api/connector/states/all")
    
    @task(2)
    def fetch_cached_data(self):
        """Test cache effectiveness."""
        self.client.get("/api/connector/cached/rankings")

# Performance benchmarks
@pytest.mark.benchmark
def test_data_transformation_performance(benchmark):
    """Ensure transformations complete within SLA."""
    connector = Connector()
    large_dataset = generate_test_data(rows=10000)
    
    result = benchmark(connector.transform, large_dataset)
    
    assert benchmark.stats.mean < 0.5  # 500ms average
    assert benchmark.stats.max < 2.0   # 2s maximum
```

### Load Test Requirements
```yaml
Scenarios:
  - Baseline: 10 concurrent users, 1 hour
  - Peak Load: 100 concurrent users, 30 minutes
  - Stress Test: Ramp to 500 users over 10 minutes
  - Spike Test: 0→200→0 users in 5 minutes
  - Soak Test: 50 users for 8 hours

Metrics:
  - Response Time: P50, P95, P99
  - Throughput: Requests/second
  - Error Rate: % failed requests
  - Resource Usage: CPU, memory, network
```

### Implementation Tasks
- [ ] Install and configure Locust
- [ ] Create load test scenarios for each connector
- [ ] Set up performance benchmarks with pytest-benchmark
- [ ] Define SLA thresholds for each endpoint
- [ ] Implement resource monitoring during tests
- [ ] Add performance regression tests to CI/CD

---

## Layer 5: Static Application Security Testing (SAST)

### Purpose
Identify vulnerabilities in code before runtime.

### Current Status
- ⚠️ **Partial**: Some static analysis via pytest
- 🎯 **Target**: Zero critical/high vulnerabilities

### OSS Stack
```yaml
Python Security:
  - bandit: Security linter for Python (CRITICAL)
  - safety: Dependency vulnerability scanner
  - pip-audit: Official PyPA audit tool
  
Code Quality:
  - pylint: Code quality and style
  - flake8: Linting and style checking
  - mypy: Static type checking
  - ruff: Fast Python linter (Rust-based)
  
Advanced:
  - semgrep: Multi-language static analysis
  - sonarqube-community: Code quality platform
```

### Bandit Configuration
```yaml
# .bandit.yml
exclude_dirs:
  - /tests/
  - /htmlcov/
  - /.venv/

tests:
  - B201  # flask_debug_true
  - B301  # pickle usage
  - B302  # marshal usage
  - B303  # md5/sha1 usage
  - B304  # insecure ciphers
  - B305  # insecure cipher modes
  - B306  # mktemp usage
  - B307  # eval usage
  - B308  # mark_safe usage
  - B310  # urllib with file protocol
  - B311  # random module for crypto
  - B312  # telnetlib usage
  - B313  # xml vulnerable to XXE
  - B314  # xml vulnerable to entity expansion
  - B315  # xml vulnerable to entity expansion
  - B316  # xml vulnerable to entity expansion
  - B317  # xml vulnerable to entity expansion
  - B318  # xml vulnerable to entity expansion
  - B319  # xml vulnerable to entity expansion
  - B320  # xml vulnerable to entity expansion
  - B321  # ftplib usage
  - B323  # unverified SSL/TLS
  - B324  # insecure hash functions
  - B325  # tempnam usage
  - B501  # request without verify
  - B502  # ssl with bad defaults
  - B503  # ssl with bad version
  - B504  # ssl with no version
  - B505  # weak crypto key
  - B506  # yaml_load
  - B507  # ssh no host key verification
  - B601  # paramiko shell injection
  - B602  # shell injection
  - B603  # subprocess without shell=True
  - B604  # shell=True
  - B605  # shell injection via shell=True
  - B606  # no shell injection via shell=False
  - B607  # partial path in start_process
  - B608  # SQL injection
  - B609  # wildcard injection

severity_level: low
confidence_level: low
```

### MyPy Configuration
```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

### Implementation Tasks
- [ ] Install bandit, safety, pip-audit
- [ ] Configure bandit with security-focused tests
- [ ] Add mypy for static type checking
- [ ] Integrate SAST tools into pre-commit hooks
- [ ] Add SAST checks to GitHub Actions
- [ ] Configure SonarQube Community Edition
- [ ] Set CI/CD gate: fail build on critical issues
- [ ] Create security vulnerability dashboard

---

## Layer 6: Dynamic Application Security Testing (DAST)

### Purpose
Detect vulnerabilities in running applications.

### Current Status
- ❌ **Status**: Not implemented
- 🎯 **Target**: OWASP Top 10 cleared

### OSS Stack
```yaml
Core:
  - owasp-zap: Industry-standard DAST scanner (CRITICAL)
  - w3af: Web application attack framework
  - nikto: Web server scanner
  
Fuzzing:
  - wfuzz: Web fuzzer
  - ffuf: Fast web fuzzer
```

### OWASP ZAP Automation
```yaml
# zap-automation.yaml
env:
  contexts:
    - name: krl-data-connectors
      urls:
        - http://localhost:8000
      includePaths:
        - "http://localhost:8000/api/.*"
      excludePaths:
        - "http://localhost:8000/static/.*"
      authentication:
        method: "http"
        parameters:
          hostname: "localhost"
          port: 8000
          realm: "API"

jobs:
  - type: spider
    parameters:
      maxDuration: 10
      maxDepth: 5
  
  - type: passiveScan-wait
    parameters:
      maxDuration: 10
  
  - type: activeScan
    parameters:
      policy: "API-Focused"
      maxDuration: 20
  
  - type: report
    parameters:
      template: "traditional-html"
      reportDir: "/reports"
      reportFile: "zap-report"
```

### Test Categories
```yaml
OWASP Top 10 Coverage:
  - A01: Broken Access Control
  - A02: Cryptographic Failures
  - A03: Injection (SQL, NoSQL, OS command)
  - A04: Insecure Design
  - A05: Security Misconfiguration
  - A06: Vulnerable Components
  - A07: Authentication Failures
  - A08: Software & Data Integrity
  - A09: Security Logging Failures
  - A10: Server-Side Request Forgery

Additional Tests:
  - Session Management
  - CSRF Protection
  - XSS Prevention
  - File Upload Validation
  - API Rate Limiting
```

### Implementation Tasks
- [ ] Install OWASP ZAP with automation framework
- [ ] Create DAST automation scripts
- [ ] Set up staging environment for DAST
- [ ] Configure OWASP ZAP for API testing
- [ ] Integrate DAST into nightly builds
- [ ] Create security finding remediation workflow
- [ ] Document DAST results and trends

---

## Layer 7: Fuzz & Mutation Testing (Behavioral Depth)

### Purpose
Stress logic with unpredictable inputs, measure test sensitivity.

### Current Status
- ❌ **Status**: Not implemented
- 🎯 **Target**: ≥90% mutation kill rate

### OSS Stack
```yaml
Fuzz Testing:
  - hypothesis: Property-based testing (CRITICAL)
  - atheris: Python fuzzing engine
  - pythonfuzz: Coverage-guided fuzzer
  
Mutation Testing:
  - mutmut: Mutation testing tool (RECOMMENDED)
  - cosmic-ray: Mutation testing
  - pytest-mutagen: Pytest plugin
```

### Hypothesis Examples
```python
from hypothesis import given, strategies as st
import pandas as pd

@given(st.lists(st.floats(allow_nan=False), min_size=0, max_size=1000))
def test_data_transformation_with_any_input(values):
    """Property test: transformation should never crash."""
    connector = Connector()
    df = pd.DataFrame({'value': values})
    
    # Should handle any input gracefully
    result = connector.transform(df)
    
    assert result is not None
    assert isinstance(result, pd.DataFrame)

@given(
    state=st.text(min_size=2, max_size=2, alphabet=st.characters(whitelist_categories=('Lu',))),
    year=st.integers(min_value=2000, max_value=2025)
)
def test_state_query_properties(state, year):
    """Property test: state queries should be consistent."""
    connector = Connector()
    result = connector.get_state_data(state, year)
    
    if result is not None:
        # Properties that should always hold
        assert len(result) >= 0
        assert 'state' in result.columns
        assert result['state'].unique()[0] == state

@given(st.binary(min_size=0, max_size=10000))
def test_file_parsing_robustness(binary_data):
    """Fuzz test: file parsing should not crash on any input."""
    connector = Connector()
    
    try:
        result = connector.parse_file(binary_data)
        # If it succeeds, should return valid structure
        assert result is None or isinstance(result, dict)
    except (ValueError, ParseError) as e:
        # Expected errors are fine
        pass
    # Should not raise unexpected exceptions
```

### Mutation Testing Configuration
```ini
# mutmut.ini
[mutmut]
paths_to_mutate=src/krl_data_connectors/
backup=False
runner=pytest -x --tb=short
tests_dir=tests/
dict_synonyms=Struct, NamedStruct

# Mutation operators enabled
enable_mutations=
    arithmetic
    comparison
    logical
    constant
    attribute
```

### Mutation Testing Process
```bash
# Run mutation testing on specific module
mutmut run --paths-to-mutate=src/krl_data_connectors/health/chr_connector.py

# Show results
mutmut results

# Show survivors (mutations not caught by tests)
mutmut show --only-survivors

# Target: <10% survivors (90%+ kill rate)
```

### Implementation Tasks
- [ ] Install hypothesis and create property-based tests
- [ ] Add hypothesis tests for all data transformations
- [ ] Install mutmut for mutation testing
- [ ] Run baseline mutation analysis
- [ ] Add tests to kill surviving mutants
- [ ] Add atheris for coverage-guided fuzzing
- [ ] Integrate mutation testing into weekly CI runs
- [ ] Create mutation coverage dashboard

---

## Layer 8: Static Typing & Contract Tests (Predictive Assurance)

### Purpose
Enforce structural and interface correctness before runtime.

### Current Status
- ⚠️ **Partial**: Some type hints exist
- 🎯 **Target**: 100% type coverage

### OSS Stack
```yaml
Type Checking:
  - mypy: Static type checker (CRITICAL)
  - pyright: Microsoft's type checker
  - pydantic: Data validation with types
  
Contract Testing:
  - pact-python: Consumer-driven contracts
  - schemathesis: OpenAPI contract testing
  - openapi-spec-validator: Schema validation
```

### Pydantic Models
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

class ConnectorConfig(BaseModel):
    """Type-safe connector configuration."""
    api_key: str = Field(..., min_length=10)
    base_url: str = Field(..., regex=r'^https?://')
    timeout: int = Field(default=30, ge=1, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    cache_enabled: bool = Field(default=True)
    
    @validator('api_key')
    def validate_api_key(cls, v):
        if 'test' in v.lower() and os.getenv('ENV') == 'production':
            raise ValueError('Test API keys not allowed in production')
        return v

class DataResponse(BaseModel):
    """Type-safe API response."""
    status: str = Field(..., regex=r'^(success|error)$')
    data: Optional[List[dict]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

### Contract Testing with Pact
```python
from pact import Consumer, Provider

# Consumer test
def test_api_contract():
    """Define expected API behavior."""
    pact = Consumer('data-connector').has_pact_with(
        Provider('external-api'),
        pact_dir='./pacts'
    )
    
    expected = {
        'status': 'success',
        'data': [
            {'state': 'CA', 'value': 100}
        ]
    }
    
    pact.given('state data exists')
    pact.upon_receiving('a request for CA data')
    pact.with_request('get', '/api/state/CA')
    pact.will_respond_with(200, body=expected)
    
    with pact:
        connector = Connector()
        result = connector.get_state_data('CA')
        assert result['status'] == 'success'
```

### Implementation Tasks
- [ ] Add type hints to all public functions (100% coverage)
- [ ] Configure mypy with strict mode
- [ ] Create pydantic models for all data structures
- [ ] Implement contract tests with pact-python
- [ ] Add OpenAPI schema validation
- [ ] Integrate type checking into pre-commit hooks
- [ ] Add type coverage metrics to CI/CD
- [ ] Document type conventions and patterns

---

## Layer 9: Penetration Testing (External Validation)

### Purpose
Human-led ethical hacking to probe entire attack surface.

### Current Status
- ❌ **Status**: Not conducted
- 🎯 **Target**: Annual or major release cycle

### OSS Stack
```yaml
Frameworks:
  - metasploit-framework: Penetration testing framework
  - burp-suite-community: Web security testing
  - nmap: Network reconnaissance
  - sqlmap: SQL injection testing
  
Specialized:
  - aircrack-ng: Wireless security
  - john-the-ripper: Password cracking
  - hydra: Network login cracker
  - gobuster: Directory/file brute forcing
```

### Penetration Test Scope
```yaml
External Testing:
  - Network Reconnaissance: Port scanning, service enumeration
  - Web Application: OWASP Top 10, business logic flaws
  - API Security: Authentication, authorization, rate limiting
  - Infrastructure: Server hardening, misconfigurations
  
Internal Testing:
  - Privilege Escalation: Local and domain escalation
  - Lateral Movement: Network segmentation, trust boundaries
  - Data Exfiltration: DLP controls, monitoring effectiveness
  
Social Engineering:
  - Phishing Campaigns: Email security awareness
  - Physical Security: Badge access, tailgating
```

### Annual Pen Test Process
```yaml
Phase 1 - Planning (Week 1):
  - Define scope and rules of engagement
  - Identify critical assets and workflows
  - Set up isolated test environment
  
Phase 2 - Reconnaissance (Week 2):
  - Passive information gathering
  - Active scanning and enumeration
  - Identify attack surface
  
Phase 3 - Exploitation (Weeks 3-4):
  - Attempt exploits on identified vulnerabilities
  - Document successful attacks
  - Capture proof-of-concept evidence
  
Phase 4 - Reporting (Week 5):
  - Detailed findings with CVSS scores
  - Remediation recommendations
  - Executive summary
  
Phase 5 - Remediation (Weeks 6-8):
  - Fix critical/high vulnerabilities
  - Validate fixes with re-testing
  - Update security documentation
```

### Implementation Tasks
- [ ] Set up isolated pen testing environment
- [ ] Document annual pen test schedule
- [ ] Create pen test engagement checklist
- [ ] Set up Metasploit and Burp Suite
- [ ] Define remediation SLAs by severity
- [ ] Create pen test findings database
- [ ] Schedule initial pen test engagement
- [ ] Document lessons learned and improvements

---

## Layer 10: Continuous Monitoring & Regression Testing

### Purpose
Detect degradations and regressions post-deployment.

### Current Status
- ✅ **Partial**: GitHub Actions for testing
- 🎯 **Target**: Full CI/CD pipeline with security gates

### OSS Stack
```yaml
CI/CD:
  - github-actions: Workflow automation (CURRENT)
  - gitlab-ci: Alternative CI/CD
  - jenkins: Self-hosted automation
  
Security Monitoring:
  - snyk: Vulnerability scanning (free tier)
  - dependabot: Dependency updates (CURRENT)
  - trivy: Container/dependency scanner
  
Observability:
  - prometheus: Metrics collection
  - grafana: Visualization
  - elk-stack: Log aggregation (Elasticsearch, Logstash, Kibana)
```

### GitHub Actions Workflow
```yaml
# .github/workflows/comprehensive-testing.yml
name: Comprehensive Testing Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Nightly at 2 AM

jobs:
  # Layer 1: Unit Tests
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist hypothesis
      - name: Run unit tests with coverage
        run: |
          pytest tests/unit/ \
            --cov=src \
            --cov-report=xml \
            --cov-report=term \
            --cov-fail-under=90 \
            --cov-branch \
            -n auto
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
  
  # Layer 2: Integration Tests
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest requests-mock
      - name: Run integration tests
        run: pytest tests/integration/ -v
  
  # Layer 4: Performance Tests (nightly only)
  performance-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install locust pytest-benchmark
      - name: Run performance benchmarks
        run: pytest tests/performance/ --benchmark-only
      - name: Run load tests
        run: |
          locust -f tests/load/locustfile.py \
            --headless \
            --users 100 \
            --spawn-rate 10 \
            --run-time 5m \
            --host http://localhost:8000
  
  # Layer 5: SAST
  sast-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install security tools
        run: |
          pip install bandit safety pip-audit mypy
      - name: Run Bandit
        run: bandit -r src/ -f json -o bandit-report.json
      - name: Run Safety check
        run: safety check --json > safety-report.json
      - name: Run pip-audit
        run: pip-audit --format json > pip-audit-report.json
      - name: Run MyPy
        run: mypy src/ --strict --junit-xml mypy-report.xml
      - name: Upload security reports
        uses: actions/upload-artifact@v4
        with:
          name: security-reports
          path: |
            bandit-report.json
            safety-report.json
            pip-audit-report.json
            mypy-report.xml
  
  # Layer 6: DAST (nightly only)
  dast-scan:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - name: Start application
        run: |
          docker-compose up -d
          sleep 30
      - name: Run OWASP ZAP scan
        uses: zaproxy/action-baseline@v0.10.0
        with:
          target: 'http://localhost:8000'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
  
  # Layer 7: Mutation Testing (weekly)
  mutation-testing:
    runs-on: ubuntu-latest
    if: github.event_name == 'schedule' && github.event.schedule == '0 2 * * 0'
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install mutmut
      - name: Run mutation testing
        run: |
          mutmut run --paths-to-mutate=src/
          mutmut results > mutation-report.txt
      - name: Upload mutation report
        uses: actions/upload-artifact@v4
        with:
          name: mutation-report
          path: mutation-report.txt
  
  # Dependency vulnerability scanning
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
  
  # Quality gate
  quality-gate:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, sast-scan]
    steps:
      - name: Check quality metrics
        run: |
          echo "All quality checks passed"
          # This job fails if any required job fails
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key
  
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', '.bandit.yml']
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
  
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
  
  - repo: local
    hooks:
      - id: pytest-quick
        name: pytest-quick
        entry: pytest tests/unit/ -x --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

### Implementation Tasks
- [ ] Enhance GitHub Actions with comprehensive testing pipeline
- [ ] Add SAST/DAST to CI/CD workflow
- [ ] Set up pre-commit hooks for all developers
- [ ] Configure Snyk for continuous vulnerability monitoring
- [ ] Set up Dependabot for automated dependency updates
- [ ] Create quality gates (fail build on critical issues)
- [ ] Implement automatic rollback on test failures
- [ ] Set up monitoring dashboards (Grafana)
- [ ] Configure alerts for test failures and vulnerabilities

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
**Priority**: High  
**Effort**: 20-30 hours

- [x] Unit test coverage to 90% (in progress)
- [ ] Add hypothesis property-based tests
- [ ] Configure mypy strict mode
- [ ] Set up bandit security scanning
- [ ] Create integration test suite
- [ ] Configure pre-commit hooks

**Deliverables**:
- 90%+ unit test coverage
- SAST integrated into CI/CD
- Type checking enabled

### Phase 2: Security Hardening (Weeks 3-4)
**Priority**: High  
**Effort**: 25-35 hours

- [ ] Set up OWASP ZAP for DAST
- [ ] Create contract tests with pydantic
- [ ] Add security-focused unit tests (injection, XSS)
- [ ] Configure dependency scanning (Snyk, Trivy)
- [ ] Implement API rate limiting tests
- [ ] Add authentication/authorization tests

**Deliverables**:
- DAST pipeline operational
- Zero critical vulnerabilities
- Contract tests for all APIs

### Phase 3: Advanced Testing (Weeks 5-6)
**Priority**: Medium  
**Effort**: 20-30 hours

- [ ] Set up Locust for load testing
- [ ] Create E2E test suite with Playwright
- [ ] Implement mutation testing with mutmut
- [ ] Add performance benchmarks
- [ ] Create fuzz testing suite with atheris
- [ ] Set up continuous monitoring

**Deliverables**:
- Performance baselines established
- E2E tests for critical workflows
- Mutation coverage ≥90%

### Phase 4: Operational Excellence (Weeks 7-8)
**Priority**: Medium  
**Effort**: 15-20 hours

- [ ] Configure monitoring dashboards
- [ ] Set up automated alerting
- [ ] Create security runbooks
- [ ] Document testing procedures
- [ ] Conduct initial pen test
- [ ] Establish quarterly review process

**Deliverables**:
- Full observability stack
- Penetration test report
- Complete documentation

---

## Maintenance & Governance

### Daily
- Automated unit/integration test runs on every commit
- SAST scanning on every PR
- Dependency vulnerability checks

### Weekly
- Review test coverage trends
- Triage new security findings
- Update test documentation

### Monthly
- Mutation testing analysis
- Performance regression review
- Security metrics dashboard review

### Quarterly
- Comprehensive E2E test review
- Load test at scale
- Security architecture review
- Update threat models

### Annually
- Full penetration test engagement
- Testing framework evaluation
- Tool stack assessment
- Training and certification updates

---

## Success Metrics

### Coverage Metrics
- **Unit Test Coverage**: ≥90% line, ≥85% branch
- **Integration Coverage**: 100% of interfaces tested
- **E2E Coverage**: 100% of critical workflows
- **Mutation Coverage**: ≥90% kill rate

### Security Metrics
- **SAST Findings**: 0 critical, <5 high severity
- **DAST Findings**: 0 exploitable vulnerabilities
- **Dependency Vulnerabilities**: 0 critical, <3 high
- **Pen Test Findings**: All remediated within SLA

### Performance Metrics
- **Unit Test Execution**: <30 seconds total
- **Integration Tests**: <5 minutes total
- **E2E Tests**: <15 minutes total
- **P99 API Latency**: <500ms under load

### Quality Metrics
- **Test Pass Rate**: 100% on main branch
- **Build Success Rate**: ≥95%
- **Time to Detect Issues**: <1 hour
- **Time to Remediate Critical**: <24 hours

---

## Tool Installation Guide

### Core Testing Stack
```bash
# Unit testing
pip install pytest pytest-cov pytest-xdist pytest-timeout pytest-randomly
pip install hypothesis pytest-benchmark

# Integration testing
pip install requests-mock responses httpretty pytest-httpserver

# Security (SAST)
pip install bandit safety pip-audit mypy pylint ruff

# Type checking and validation
pip install pydantic types-requests

# Mutation testing
pip install mutmut cosmic-ray

# Performance testing
pip install locust pytest-benchmark memory-profiler

# Contract testing
pip install pact-python schemathesis

# E2E testing
pip install playwright pytest-playwright
playwright install

# DAST - requires separate installation
# OWASP ZAP: https://www.zaproxy.org/download/

# Fuzzing
pip install atheris pythonfuzz
```

### CI/CD Integration
```bash
# Pre-commit hooks
pip install pre-commit
pre-commit install

# GitHub Actions - already configured
# See .github/workflows/

# Monitoring
# Prometheus + Grafana - Docker Compose setup
```

---

## References

### Standards & Frameworks
- OWASP Testing Guide v4.2
- NIST Cybersecurity Framework
- ISO/IEC 27001:2022
- PCI DSS v4.0
- SOC 2 Type II

### Tool Documentation
- pytest: https://docs.pytest.org/
- Hypothesis: https://hypothesis.readthedocs.io/
- Bandit: https://bandit.readthedocs.io/
- OWASP ZAP: https://www.zaproxy.org/docs/
- Locust: https://docs.locust.io/
- Playwright: https://playwright.dev/python/

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-20 | Engineering Team | Initial comprehensive testing strategy |

**Classification**: INTERNAL - DO NOT DISTRIBUTE
