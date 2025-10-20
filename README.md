---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# KRL Data Connectors

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![Tests](https://github.com/KR-Labs/krl-data-connectors/workflows/tests/badge.svg)](https://github.com/KR-Labs/krl-data-connectors/actions)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://docs.krlabs.dev/data-connectors)

**Production-ready data connectors for economic, demographic, and financial data sources.**

Part of the [KRL Analytics Suite](https://krlabs.dev) - an open-source platform for economic analysis, causal inference, and policy evaluation.

## Overview

KRL Data Connectors provides a unified interface for accessing data from major economic and demographic data providers:

- **Federal Reserve Economic Data (FRED)** - 800,000+ economic time series
- **U.S. Census Bureau** - Demographic, economic, and geographic data
- **Bureau of Labor Statistics (BLS)** - Labor market and inflation data
- **World Bank** - Global development indicators
- **OECD** - International economic statistics

### Key Features

✨ **Unified API** - Consistent interface across all data sources  
⚡ **Intelligent Caching** - Reduce API calls and improve performance  
🔒 **Type-Safe** - Full type hints and validation  
📊 **Rich Metadata** - Automatic metadata extraction and documentation  
🚀 **Production-Ready** - Comprehensive error handling and logging  
🔄 **Async Support** - High-performance async operations  
🧪 **Well-Tested** - >90% test coverage  

## Installation

```bash
# Basic installation
pip install krl-data-connectors

# With all optional dependencies
pip install krl-data-connectors[all]

# Development installation
pip install krl-data-connectors[dev]
```

## Quick Start

### County Business Patterns (CBP) Connector

```python
from krl_data_connectors import CountyBusinessPatternsConnector

# Initialize connector (API key from environment: CENSUS_API_KEY)
cbp = CountyBusinessPatternsConnector()

# Get retail trade data for Rhode Island
retail_data = cbp.get_state_data(
    year=2021,
    state='44',  # Rhode Island FIPS code
    naics='44'   # Retail trade sector
)

print(f"Retrieved {len(retail_data)} records")
print(retail_data[['NAICS2017', 'ESTAB', 'EMP', 'PAYANN']].head())
```

### LEHD Origin-Destination Connector

```python
from krl_data_connectors import LEHDConnector

# Initialize connector
lehd = LEHDConnector()

# Get origin-destination employment flows
od_data = lehd.get_od_data(
    state='ri',
    year=2021,
    job_type='JT00',  # All jobs
    segment='S000'     # All workers
)

print(f"Retrieved {len(od_data)} origin-destination pairs")
print(od_data[['w_geocode', 'h_geocode', 'S000', 'SA01']].head())
```

### FRED Connector

```python
from krl_data_connectors import FREDConnector

# Initialize connector (API key from environment: FRED_API_KEY)
fred = FREDConnector()

# Fetch unemployment rate time series
unemployment = fred.get_series(
    series_id="UNRATE",
    observation_start="2020-01-01",
    observation_end="2023-12-31"
)

print(unemployment.head())
```

### BLS Connector

```python
from krl_data_connectors import BLSConnector

# Initialize connector (API key from environment: BLS_API_KEY)
bls = BLSConnector()

# Get unemployment rate for multiple states
unemployment = bls.get_series(
    series_ids=['LASST060000000000003', 'LASST440000000000003'],
    start_year=2020,
    end_year=2023
)

print(unemployment.head())
```

### BEA Connector

```python
from krl_data_connectors import BEAConnector

# Initialize connector (API key from environment: BEA_API_KEY)
bea = BEAConnector()

# Get GDP by state
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

### Using the Base Connector

All connectors inherit from `BaseConnector` and support:

```python
from krl_data_connectors import FREDConnector

# Automatic caching
fred = FREDConnector(
    api_key="your_api_key",
    cache_dir="/tmp/fred_cache",
    cache_ttl=3600  # 1 hour
)

# Cached responses are automatic
data1 = fred.get_series("UNRATE")  # Fetches from API
data2 = fred.get_series("UNRATE")  # Returns from cache

# Check cache statistics
stats = fred.cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.1f}%")
```

## Architecture

### BaseConnector

All data connectors inherit from `BaseConnector`, which provides:

- **Structured Logging** - JSON logs with request/response metadata
- **Configuration Management** - Environment variables and YAML config
- **Intelligent Caching** - File-based or Redis caching
- **Error Handling** - Retries, rate limiting, timeout handling
- **Request Management** - HTTP session pooling, connection reuse

```python
from abc import ABC, abstractmethod
from krl_core import get_logger, ConfigManager, FileCache

class BaseConnector(ABC):
    """Abstract base class for data connectors."""
    
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

## API Keys Setup

📖 **See [API_KEY_SETUP.md](./API_KEY_SETUP.md) for complete setup guide with multiple configuration options.**

### Quick Setup

The package automatically finds API keys from multiple locations:

1. **Environment variables** (recommended for production)
2. **Config file** at `~/.krl/apikeys` (recommended for development)
3. **Direct in code** (not recommended for production)

#### Option 1: Environment Variables (Recommended)

```bash
export BEA_API_KEY="your_bea_key"
export FRED_API_KEY="your_fred_key"
export BLS_API_KEY="your_bls_key"
export CENSUS_API_KEY="your_census_key"
```

#### Option 2: Config File (Easy Setup)

```bash
# Create config file
mkdir -p ~/.krl
cat > ~/.krl/apikeys << EOF
BEA API KEY: your_bea_key
FRED API KEY: your_fred_key
BLS API KEY: your_bls_key
CENSUS API: your_census_key
EOF
chmod 600 ~/.krl/apikeys
```

The package will automatically find and use this file!

#### Get Free API Keys

| Service | Required? | Registration URL |
|---------|-----------|------------------|
| **CBP/Census** | Optional | https://api.census.gov/data/key_signup.html |
| **FRED** | Yes | https://fred.stlouisfed.org/docs/api/api_key.html |
| **BLS** | Recommended* | https://www.bls.gov/developers/home.htm |
| **BEA** | Yes | https://apps.bea.gov/api/signup/ |
| **LEHD** | No | N/A |

*BLS works without a key but has limited rate limits (25 vs 500 requests/day)

### Using Config Utilities

```python
from krl_data_connectors import find_config_file, BEAConnector

# Find config file automatically
config_path = find_config_file('apikeys')
print(f"Config found at: {config_path}")

# Connectors automatically use config file
bea = BEAConnector()  # Finds API key from env or config file
```

## Configuration

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

### Configuration File

Create `config.yaml`:

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

Load configuration:

```python
from krl_core import ConfigManager

config = ConfigManager("config.yaml")
fred = FREDConnector(api_key=config.get("fred.api_key"))
```

## Available Connectors

### ✅ Production-Ready (100% Test Coverage)

#### County Business Patterns (CBP) Connector
**Status:** ✅ Complete | **Tests:** 33 passing | **Coverage:** 77%

- Business establishment counts by industry (NAICS)
- Employment and payroll data
- County, state, and metro-level statistics
- Historical data back to 1986
- **API:** Census Bureau CBP API (free, requires key)

#### LEHD Origin-Destination Connector
**Status:** ✅ Complete | **Tests:** 28 passing | **Coverage:** 74%

- Worker employment flows (home-to-work)
- Residence and workplace characteristics
- Job counts by segment (age, earnings, industry)
- Block-level geographic resolution
- **API:** Census LEHD (free, no key required)

#### FRED Connector
**Status:** ✅ Complete | **Tests:** TBD | **Coverage:** 17%

- 800,000+ economic time series
- Real-time and historical data
- Series metadata and release information
- Category browsing and search
- **API:** Federal Reserve (free, requires key, 120k requests/day)

#### BLS Connector
**Status:** ✅ Complete | **Tests:** 31 passing | **Coverage:** 87%

- Employment and unemployment statistics
- Consumer Price Index (CPI)
- Producer Price Index (PPI)
- Wages and earnings data
- **API:** Bureau of Labor Statistics (free, requires key, 500 requests/day)

#### BEA Connector
**Status:** ✅ Complete | **Tests:** 28 passing | **Coverage:** 72%

- GDP by state and metro area
- Regional economic accounts
- Personal income statistics
- Industry-level data
- **API:** Bureau of Economic Analysis (free, requires key)

### 🚧 In Development

#### CDC WONDER Connector
**Status:** ⚠️ BETA - API Non-Functional | **Tests:** 13 passing | **Coverage:** 74%

- Mortality data (underlying cause of death)
- Natality data (birth statistics)
- Population estimates
- **CRITICAL ISSUE:** CDC WONDER does NOT provide a functional programmatic API
- The API endpoint returns HTTP 500 errors
- API documentation pages return 404 errors
- CDC redirects API requests to web form interface
- **Recommendation:** Use CDC WONDER web interface (https://wonder.cdc.gov/)
- **Connector Status:** Implementation complete but unusable due to CDC API limitations
- **API:** CDC WONDER (free, no key required, BUT NON-FUNCTIONAL)

#### World Bank Connector
**Status:** 🔄 Planned | **Tests:** Not started

- Global development indicators
- Country-level data
- Historical time series

#### OECD Connector
**Status:** 🔄 Planned | **Tests:** Not started

- International economic data
- Member country statistics
- Standardized indicators

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific connector tests
pytest tests/unit/test_fred_connector.py -v

# Run integration tests (requires API keys)
pytest tests/integration/ -v
```

## Development

```bash
# Clone repository
git clone https://github.com/KR-Labs/krl-data-connectors.git
cd krl-data-connectors

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev,test]"

# Run pre-commit hooks
pre-commit install
pre-commit run --all-files

# Run tests
pytest

# Build documentation
cd docs && make html
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Contributor License Agreement

All contributors must sign the [Contributor License Agreement (CLA)](https://krlabs.dev/cla) before their contributions can be merged.

## License

This project is licensed under the **Apache License 2.0** - see [LICENSE](LICENSE) file for details.

**Why Apache 2.0?**
- ✅ Commercial use allowed
- ✅ Modification allowed
- ✅ Distribution allowed
- ✅ Patent grant included
- ✅ Can be used in proprietary software

## Support

- **Documentation**: https://docs.krlabs.dev/data-connectors
- **Issue Tracker**: https://github.com/KR-Labs/krl-data-connectors/issues
- **Discussions**: https://github.com/KR-Labs/krl-data-connectors/discussions
- **Email**: support@krlabs.dev

## Related Projects

- **[krl-open-core](https://github.com/KR-Labs/krl-open-core)** - Core utilities (logging, config, caching)
- **[krl-model-zoo](https://github.com/KR-Labs/krl-model-zoo)** - Causal inference and forecasting models
- **[krl-dashboard](https://github.com/KR-Labs/krl-dashboard)** - Interactive data visualization
- **[krl-tutorials](https://github.com/KR-Labs/krl-tutorials)** - Hands-on learning materials

## Citation

If you use KRL Data Connectors in your research, please cite:

```bibtex
@software{krl_data_connectors,
  title = {KRL Data Connectors: Production-Ready Economic Data Integration},
  author = {KR-Labs Foundation},
  year = {2025},
  url = {https://github.com/KR-Labs/krl-data-connectors}
}
```

---

**Built with ❤️ by [KR-Labs Foundation](https://krlabs.dev)**

Part of the mission to make economic analysis accessible, reproducible, and transparent.
