<!--
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
-->

<div align="center">
  <img src="docs/assets/KRLabs_WebLogo.png" alt="KR-Labs Logo" width="400"/>
</div>

# KRL Data Connectors

<div align="center">

<p>
<strong>Production-grade connectors for socioeconomic, demographic, and policy data infrastructure.</strong>
</p>

<p>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
  <a href="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/build-and-sign.yml"><img src="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/build-and-sign.yml/badge.svg" alt="Build"></a>
  <a href="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/tests.yml"><img src="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/comprehensive-testing.yml"><img src="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/comprehensive-testing.yml/badge.svg" alt="Comprehensive Tests"></a>
  <a href="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/lint.yml"><img src="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/lint.yml/badge.svg" alt="Lint"></a>
  <a href="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/security-checks.yml"><img src="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/security-checks.yml/badge.svg" alt="Security"></a>
  <a href="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/license-compliance.yml"><img src="https://github.com/KR-Labs/krl-data-connectors/actions/workflows/license-compliance.yml/badge.svg" alt="License Compliance"></a>
  <a href="https://github.com/psf/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"></a>
</p>

<p>
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="https://krl-data-connectors.readthedocs.io">Documentation</a> •
  <a href="./examples/">Examples</a> •
  <a href="./CONTRIBUTING.md">Contributing</a>
</p>

</div>

---

## Overview

KRL Data Connectors provide a unified, production-grade interface for institutional access to socioeconomic, demographic, health, and environmental datasets. Designed for operational discipline and engineered reliability, these connectors form the backbone of the [KRL Analytics Suite](https://krlabs.dev), supporting robust economic analysis, causal inference, and policy evaluation at scale.

### Infrastructure Guarantees

KRL Data Connectors guarantee:
- **Unified API Surface**: Consistent, type-safe interfaces across all supported data sources.
- **Operational Reliability**: Structured logging, resilient error handling, and automated retry mechanisms.
- **Type Safety and Validation**: Complete type hints and runtime input validation.
- **Optimized Caching**: Intelligent caching to reduce redundant data access and improve throughput.
- **Automated Metadata Extraction**: Standardized profiling of dataset metadata for downstream integration.
- **Comprehensive Testing**: >2,800 automated tests across 40 connectors, maintaining >80% code coverage.
- **Secure Credential Management**: Institutional-grade credential resolution and isolation.

### Supported Data Sources

KRL Data Connectors provide institutional-grade access to 40 production-ready datasets across 14 domains. Each domain is represented by connectors engineered for reliability and operational consistency.

#### Economic & Financial Data (8 connectors)
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| FRED                  | Economics      | Yes           | Daily/Real-time     | 800K+ series        | Production   |
| BLS                   | Labor          | Recommended   | Monthly             | National/State      | Production   |
| BEA                   | Economics      | Yes           | Quarterly/Annual    | National/Regional   | Production   |
| OECD                  | International  | No            | Varies              | Country-level       | Production   |
| World Bank            | International  | No            | Annual              | Country-level       | Production   |
| SEC                   | Financial      | No            | Real-time           | Public filings      | Production   |
| Treasury              | Financial      | No            | Daily               | Federal finances    | Production   |
| FDIC                  | Banking        | No            | Quarterly           | Bank data           | Production   |

#### Demographic & Labor Data (3 connectors)
Institutional connectors for core demographic and labor datasets.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| Census ACS            | Demographics   | Optional      | Annual              | All US geographies  | Production   |
| Census CBP            | Business       | Optional      | Annual              | County-level        | Production   |
| Census LEHD           | Employment     | No            | Quarterly           | County-level        | Production   |

#### Health & Wellbeing Data (5 connectors)
Connectors for health outcomes, provider, and wellbeing datasets.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| HRSA                  | Health         | No            | Annual              | HPSA/MUA/P          | Production   |
| CDC WONDER            | Health         | No            | Varies              | County-level        | Production   |
| County Health Rankings| Health         | No            | Annual              | County-level        | Production   |
| FDA                   | Health         | No            | Real-time           | Drugs/devices       | Production   |
| NIH                   | Research       | No            | Daily               | Grants/projects     | Production   |

#### Environmental & Climate Data (5 connectors)
Production connectors for environmental, air, and climate data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| EPA EJScreen          | Environment    | No            | Annual              | Block group         | Production   |
| EPA Air Quality       | Environment    | No            | Hourly/Real-time    | Station-level       | Production   |
| EPA Superfund         | Environment    | No            | Real-time           | Site-level          | Production   |
| EPA Water Quality     | Environment    | No            | Real-time           | Facility-level      | Production   |
| NOAA Climate          | Climate        | No            | Daily               | Station-level       | Production   |

#### Education Data (3 connectors)
Institutional connectors for education and postsecondary data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| NCES                  | Education      | No            | Annual              | School-level        | Production   |
| College Scorecard     | Education      | Yes           | Annual              | Institution         | Production   |
| IPEDS                 | Education      | No            | Annual              | Institution         | Production   |

#### Housing & Urban Data (2 connectors)
Production-ready connectors for housing and urban indicators.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| HUD Fair Market Rent  | Housing        | Yes           | Annual              | Metro/County        | Production   |
| Zillow Research       | Housing        | No            | Monthly             | Metro/ZIP           | Production   |

#### Agricultural Data (2 connectors)
Connectors for agricultural and food environment data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| USDA Food Atlas       | Agricultural   | Yes           | Annual              | County-level        | Production   |
| USDA NASS             | Agricultural   | Yes           | Varies              | National/State      | Production   |

#### Crime & Justice Data (3 connectors)
Production connectors for crime and justice data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| FBI UCR               | Crime          | Recommended   | Annual              | Agency-level        | Production   |
| Bureau of Justice     | Justice        | No            | Annual              | National            | Production   |
| Victims of Crime      | Justice        | No            | Annual              | State-level         | Production   |

#### Energy Data (1 connector)
Institutional connector for energy datasets.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| EIA                   | Energy         | Yes           | Real-time           | National/State      | Production   |

#### Science & Research Data (2 connectors)
Connectors for geoscience and research awards data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| USGS                  | Geoscience     | No            | Real-time           | National            | Production   |
| NSF                   | Research       | No            | Daily               | Awards/grants       | Production   |

#### Transportation Data (1 connector)
Production connector for aviation and transportation data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| FAA                   | Aviation       | No            | Real-time           | Airport/flight      | Production   |

#### Labor Safety Data (1 connector)
Connector for labor safety and inspection data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| OSHA                  | Safety         | No            | Real-time           | Inspections         | Production   |

#### Social Services Data (2 connectors)
Connectors for social services and benefits data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| Social Security Admin | Social         | No            | Annual              | National            | Production   |
| ACF                   | Social         | No            | Annual              | State/County        | Production   |

#### Veterans Services Data (1 connector)
Connector for veterans services and benefits data.
| Data Source           | Domain         | Auth Required | Update Frequency    | Coverage            | Status        |
|----------------------|---------------|---------------|---------------------|---------------------|--------------|
| VA                    | Veterans       | No            | Real-time           | Facilities/benefits | Production   |

**Total: 40 Production-Ready Connectors** | All connectors are maintained in production status.

---

## Security & IP Protection

KRL Data Connectors are developed and maintained under a comprehensive, audit-grade security and intellectual property (IP) protection framework. The repository implements a multi-layered defense strategy to ensure compliance, confidentiality, and operational integrity.

### Compliance and Protection Layers

| Layer | Control Area | Status | Coverage |
|-------|----------------|--------|----------|
| 1 | Legal Protection (Copyright, Trademark, License) | Enforced | 100% of files |
| 2 | Technical Protection (Secret Scanning) | Enforced | GitHub, Gitleaks, Pre-commit |
| 3 | Build Verification (CI/CD Security) | Enforced | All pull requests |
| 4 | License Compliance | Enforced | Apache 2.0, automated checks |
| 5 | Continuous Monitoring & Response | Enforced | Security advisories, multi-scanner validation |

### Automated Security Controls

All code contributions and repository changes are subject to:
- Automated secret scanning (Gitleaks, pre-commit)
- Vulnerability assessment (Trivy, CodeQL)
- Dependency security review (CVE scanning)
- License compatibility enforcement (GPL/AGPL blocklisting)
- Static and dynamic code analysis (Bandit, Safety)
- Copyright and trademark validation

### Repository Validation

All commits are continuously validated for secrets, license compliance, and legal attribution. Historical scans confirm:
- Zero secrets detected across repository history
- 100% of files with copyright headers
- Full adherence to Apache 2.0 licensing

### Contributor Compliance

- Credentials/secrets are automatically blocked at commit time
- All pull requests are subject to security and compliance validation
- Pre-commit hooks and automated tooling are required for all contributors

For detailed security practices and vulnerability reporting, refer to [SECURITY.md](./SECURITY.md).

---

## Installation

To ensure seamless integration with institutional environments, KRL Data Connectors support multiple installation profiles tailored for production, development, and extended use cases.

```bash
# Basic installation
pip install krl-data-connectors

# With all optional dependencies
pip install krl-data-connectors[all]

# Development installation
pip install krl-data-connectors[dev]
```

---

## Quick Start

The following examples demonstrate reproducible initialization and usage of KRL Data Connectors for primary data sources. All connectors are designed for direct integration into institutional analytics pipelines.

### County Business Patterns (CBP)

```python
from krl_data_connectors import CountyBusinessPatternsConnector

# Initialize connector using environment variable for API key
cbp = CountyBusinessPatternsConnector()

# Retrieve retail trade data for Rhode Island (FIPS 44, NAICS 44)
retail_data = cbp.get_state_data(
    year=2021,
    state='44',
    naics='44'
)

print(f"Records: {len(retail_data)}")
print(retail_data[['NAICS2017', 'ESTAB', 'EMP', 'PAYANN']].head())
```

### LEHD Origin-Destination

```python
from krl_data_connectors import LEHDConnector

# Initialize connector
lehd = LEHDConnector()

# Retrieve origin-destination employment flows for RI, 2021
od_data = lehd.get_od_data(
    state='ri',
    year=2021,
    job_type='JT00',
    segment='S000'
)

print(f"Origin-destination pairs: {len(od_data)}")
print(od_data[['w_geocode', 'h_geocode', 'S000', 'SA01']].head())
```

### FRED

```python
from krl_data_connectors import FREDConnector

# Initialize connector using FRED_API_KEY environment variable
fred = FREDConnector()

# Fetch unemployment rate time series
unemployment = fred.get_series(
    series_id="UNRATE",
    observation_start="2020-01-01",
    observation_end="2023-12-31"
)

print(unemployment.head())
```

### BLS

```python
from krl_data_connectors import BLSConnector

# Initialize connector using BLS_API_KEY environment variable
bls = BLSConnector()

# Retrieve unemployment rate for selected states
unemployment = bls.get_series(
    series_ids=['LASST060000000000003', 'LASST440000000000003'],
    start_year=2020,
    end_year=2023
)

print(unemployment.head())
```

### BEA

```python
from krl_data_connectors import BEAConnector

# Initialize connector using BEA_API_KEY environment variable
bea = BEAConnector()

# Retrieve GDP by state for 2021
gdp_data = bea.get_data(
    dataset='Regional',
    method='GetData',
    TableName='SAGDP2N',
    LineCode=1,
    Year='2021',
    GeoFips='STATE'
)

print(gdp_data.head())
```

### Caching and Base Connector

All connectors inherit from `BaseConnector`, which standardizes caching, configuration, and logging for operational consistency.

```python
from krl_data_connectors import FREDConnector

# Enable file-based caching with 1-hour TTL
fred = FREDConnector(
    api_key="your_api_key",
    cache_dir="/tmp/fred_cache",
    cache_ttl=3600
)

# Cached responses are handled automatically
data1 = fred.get_series("UNRATE")  # API call
data2 = fred.get_series("UNRATE")  # Served from cache

# Retrieve cache statistics
stats = fred.cache.get_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1f}%")
```

---

## Architecture

KRL Data Connectors are modular and auditable, supporting extensibility and institutional-scale deployment. All connectors derive from a unified `BaseConnector`, ensuring interface consistency and standardized operational controls.

### BaseConnector Capabilities

The `BaseConnector` class enforces:
- **Structured Logging**: JSON-formatted logs with complete request and response metadata.
- **Consistent Configuration**: Environment variable and YAML-based configuration for credentials, caching, and logging.
- **Intelligent Caching**: File-based and Redis support with configurable TTL.
- **Automated Error Handling**: Retry logic, API rate limiting, and request timeouts.
- **Standardized Request Management**: HTTP session pooling and connection reuse.

```python
from abc import ABC, abstractmethod
from krl_core import get_logger, ConfigManager, FileCache

class BaseConnector(ABC):
    """Abstract base class for all data connectors. Enforces interface and operational consistency."""
    def __init__(self, api_key=None, cache_dir=None, cache_ttl=3600):
        self.logger = get_logger(self.__class__.__name__)
        self.config = ConfigManager()
        self.cache = FileCache(
            cache_dir=cache_dir,
            default_ttl=cache_ttl,
            namespace=self.__class__.__name__.lower()
        )
        # ... initialization
```

---

## API Key Management

KRL Data Connectors implement secure, automated credential resolution for institutional and development use. The credential management system ensures operational consistency and auditability. See [API_KEY_SETUP.md](./API_KEY_SETUP.md) for procedural details.

### Credential Resolution Order

API credentials are resolved in the following order:
1. **Environment Variables** (preferred for production)
2. **Configuration file** at `~/.krl/apikeys` (recommended for development/testing)
3. **Direct assignment in code** (permitted for testing only)

#### Example: Environment Variables

```bash
export BEA_API_KEY="your_bea_key"
export FRED_API_KEY="your_fred_key"
export BLS_API_KEY="your_bls_key"
export CENSUS_API_KEY="your_census_key"
```

#### Example: Configuration File

```bash
mkdir -p ~/.krl
cat > ~/.krl/apikeys << EOF
BEA API KEY: your_bea_key
FRED API KEY: your_fred_key
BLS API KEY: your_bls_key
CENSUS API: your_census_key
EOF
chmod 600 ~/.krl/apikeys
```

#### Obtaining API Keys

| Service           | Required?    | Registration URL                                      |
|-------------------|--------------|-------------------------------------------------------|
| CBP/Census        | Optional     | https://api.census.gov/data/key_signup.html           |
| FRED              | Yes          | https://fred.stlouisfed.org/docs/api/api_key.html     |
| BLS               | Recommended* | https://www.bls.gov/developers/home.htm               |
| BEA               | Yes          | https://apps.bea.gov/api/signup/                      |
| LEHD              | No           | N/A                                                  |

*BLS is accessible without a key but with reduced rate limits.

#### Configuration Utilities

Automatic discovery and management of configuration files are supported:

```python
from krl_data_connectors import find_config_file, BEAConnector

config_path = find_config_file('apikeys')
print(f"Config found at: {config_path}")

# Connectors resolve credentials from configuration or environment
bea = BEAConnector()
```

---

## Configuration

KRL Data Connectors support robust, institution-ready configuration via environment variables and YAML files. This enables precise management of credentials, caching, and logging for reproducible deployments.

### Environment Variables

```bash
# API Keys
export CENSUS_API_KEY="your_census_key"
export FRED_API_KEY="your_fred_key"
export BLS_API_KEY="your_bls_key"
export BEA_API_KEY="your_bea_key"

# Cache settings
export KRL_CACHE_DIR="~/.krl_cache"
export KRL_CACHE_TTL="3600"

# Logging
export KRL_LOG_LEVEL="INFO"
export KRL_LOG_FORMAT="json"
```

### YAML Configuration File

```yaml
fred:
  api_key: "your_fred_key"
  base_url: "https://api.stlouisfed.org/fred"
  timeout: 30

census:
  api_key: "your_census_key"
  base_url: "https://api.census.gov/data"

cache:
  directory: "~/.krl_cache"
  ttl: 3600

logging:
  level: "INFO"
  format: "json"
```

Apply configuration in code:

```python
from krl_core import ConfigManager

config = ConfigManager("config.yaml")
fred = FREDConnector(api_key=config.get("fred.api_key"))
```

---

## Connector Catalog

KRL Data Connectors enable reliable, scalable integration with the following data sources. All connectors are engineered to institutional standards for reliability and seamless analytics integration.

### Production-Ready Connectors

- **County Business Patterns (CBP):** Establishment and employment statistics by industry and geography. [examples/cbp_quickstart.ipynb](examples/)
- **LEHD Origin-Destination:** Worker flows and employment demographics. [examples/lehd_quickstart.ipynb](examples/)
- **FRED:** Economic time series and metadata.
- **BLS:** Labor market and inflation statistics.
- **BEA:** GDP, regional accounts, and personal income.
- **EPA EJScreen:** Environmental justice indicators. [examples/ejscreen_quickstart.ipynb](examples/ejscreen_quickstart.ipynb)
- **HRSA:** Health Professional Shortage Areas, MUA/P, FQHC. [examples/hrsa_quickstart.ipynb](examples/hrsa_quickstart.ipynb)
- **County Health Rankings:** County-level health measures. [examples/chr_quickstart.ipynb](examples/chr_quickstart.ipynb)
- **EPA Air Quality / AirNow:** Real-time and historical AQI. [examples/air_quality_quickstart.ipynb](examples/air_quality_quickstart.ipynb)
- **Zillow Research:** Housing price and rent indices. [examples/zillow_quickstart.ipynb](examples/zillow_quickstart.ipynb)
- **HUD Fair Market Rents:** Rental affordability and income limits. [examples/hud_fmr_quickstart.ipynb](examples/hud_fmr_quickstart.ipynb)
- **FBI UCR:** Crime statistics and arrest data. [examples/fbi_ucr_quickstart.ipynb](examples/fbi_ucr_quickstart.ipynb)
- **NCES:** School and district education statistics. [examples/nces_quickstart.ipynb](examples/nces_quickstart.ipynb)

### In Development and Planned

- **CDC WONDER:** Mortality and natality data (API non-functional; web interface recommended).
- **USDA Food Environment Atlas:** Food access, insecurity, and local food systems.
- **OECD, World Bank, College Scorecard, IPEDS, Superfund Sites, and additional sources:** Refer to [ROADMAP.md](ROADMAP.md) for the complete development roadmap.

---

## Roadmap and Quality Standards

KRL Data Connectors are advanced in accordance with a structured roadmap, targeting 40 connectors across all major institutional domains. Prioritization is driven by institutional requirements, API availability, and domain coverage.

**Quality Standards:**
- ≥90% test coverage with comprehensive unit tests
- Full type hints and input validation on all public methods
- Robust error handling with informative diagnostics
- Intelligent, configurable caching
- Structured JSON logging for operational transparency
- Comprehensive documentation, usage examples, and quickstart notebooks
- Secure API key management and rigorous input validation

For implementation milestones and API specifications, consult [ROADMAP.md](ROADMAP.md).

---

## Testing

KRL Data Connectors utilize a 10-layer, open-source testing architecture aligned with institutional best practices. All tests and validation tools are fully auditable and reproducible.

### Testing Model

| Layer | Purpose | Tools | Status |
|-------|--------|-------|--------|
| 1. Unit Tests | Function correctness | pytest, hypothesis | Implemented (408 tests, 73% coverage) |
| 2. Integration | Component interaction | pytest, requests-mock | Implemented |
| 3. E2E Tests | Workflow validation | playwright | Planned |
| 4. Performance | Load/stress testing | locust, pytest-benchmark | Planned |
| 5. SAST | Static security analysis | bandit, safety, mypy | Configured |
| 6. DAST | Runtime security testing | OWASP ZAP | Planned |
| 7. Mutation | Test quality measurement | mutmut, hypothesis | Planned |
| 8. Contract | Type/interface validation | pydantic, mypy | Configured |
| 9. Penetration | Security assessment | metasploit, burp | Annual |
| 10. Monitoring | Continuous validation | GitHub Actions, Snyk | Active |

### Test Execution

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run security scans
make security

# Run type checking
make type-check

# Simulate full CI pipeline
make ci

# List available commands
make help
```

### Coverage Objectives

- Current: 73.30% overall, 408 tests passing
- Target: ≥90% line coverage, ≥85% branch coverage
- Mutation: ≥90% kill rate

For detailed procedures, see [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md).

---

## Development

All development must ensure reproducibility and full compliance with institutional contribution standards. Establish a local environment and follow the verified workflow:

```bash
# Clone the repository
git clone https://github.com/KR-Labs/krl-data-connectors.git
cd krl-data-connectors

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install development and test dependencies
pip install -e ".[dev,test]"

# Run pre-commit hooks for code compliance
pre-commit install
pre-commit run --all-files

# Execute tests
pytest

# Build documentation
cd docs && make html
```

---

## Contributing

All contributions must maintain reproducibility, compliance, and operational reliability. Review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting changes. A signed [Contributor License Agreement (CLA)](https://krlabs.dev/cla) is required for all code contributions.

---

## License

KRL Data Connectors are distributed under the **Apache License 2.0**. For the full license text, refer to the [LICENSE](LICENSE) file.

**Key License Terms:**
- Permits commercial use, modification, and redistribution
- Patent grant included
- Compatible with proprietary software

---

## Support

Use the following channels for verified support and communication:
- **Documentation:** https://docs.krlabs.dev/data-connectors
- **Issue Tracker:** https://github.com/KR-Labs/krl-data-connectors/issues
- **Discussions:** https://github.com/KR-Labs/krl-data-connectors/discussions
- **Email:** support@krlabs.dev

---

## Related Projects

KRL Data Connectors are a core component of the KR-Labs analytics infrastructure ecosystem:
- **[krl-open-core](https://github.com/KR-Labs/krl-open-core):** Logging, configuration, and caching utilities
- **[krl-model-zoo](https://github.com/KR-Labs/krl-model-zoo):** Causal inference and forecasting models
- **[krl-dashboard](https://github.com/KR-Labs/krl-dashboard):** Interactive analytics and visualization platform
- **[krl-tutorials](https://github.com/KR-Labs/krl-tutorials):** Reproducible example workflows and onboarding materials

---

## Citation

For institutional or research citation of KRL Data Connectors, use the following BibTeX entry:

```bibtex
@software{krl_data_connectors,
  title = {KRL Data Connectors: Standardized Interfaces for Economic and Social Data},
  author = {KR-Labs},
  year = {2025},
  url = {https://github.com/KR-Labs/krl-data-connectors},
  license = {Apache-2.0}
}
```

---

**Engineered for reproducibility, scalability, and institutional trust by [KR-Labs](https://krlabs.dev)**

© 2025 KR-Labs. All rights reserved.  
KR-Labs is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.
