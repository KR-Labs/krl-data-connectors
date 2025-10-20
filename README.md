# KRL Data Connectors

<div align="center">

[![PyPI version](https://img.shields.io/pypi/v/krl-data-connectors.svg)](https://pypi.org/project/krl-data-connectors/)
[![Python Version](https://img.shields.io/pypi/pyversions/krl-data-connectors.svg)](https://pypi.org/project/krl-data-connectors/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation Status](https://readthedocs.org/projects/krl-data-connectors/badge/?version=latest)](https://krl-data-connectors.readthedocs.io/en/latest/?badge=latest)
[![Tests](https://github.com/KR-Labs/krl-data-connectors/workflows/tests/badge.svg)](https://github.com/KR-Labs/krl-data-connectors/actions)
[![Coverage](https://img.shields.io/badge/coverage-90%25%2B-green)](https://github.com/KR-Labs/krl-data-connectors)
[![Downloads](https://img.shields.io/pypi/dm/krl-data-connectors.svg)](https://pypi.org/project/krl-data-connectors/)

**Production-ready data connectors for socioeconomic research and policy analysis**

[Installation](#installation) •
[Quick Start](#quick-start) •
[Documentation](https://krl-data-connectors.readthedocs.io) •
[Examples](./examples/) •
[Contributing](./CONTRIBUTING.md)

</div>

---

## 🎯 Overview

KRL Data Connectors deliver **robust, standardized interfaces** for accessing 10+ socioeconomic data sources, with 30+ additional connectors planned. Designed for **institutional reliability**, these connectors are built for reproducibility, scalability, and production use.

**Part of the [KRL Analytics Suite](https://krlabs.dev)** - an open-source platform supporting economic analysis, causal inference, and policy evaluation at scale.

### ✨ Why KRL Data Connectors?

- **🔌 Unified API:** Consistent interface across all data sources
- **⚡ Production-Ready:** Robust error handling, retry logic, and structured logging
- **🎯 Type-Safe:** Full type hints and validation
- **💾 Smart Caching:** Minimize API calls, maximize performance
- **📊 Rich Metadata:** Automatic documentation and data profiling
- **✅ Well-Tested:** 297+ tests with 90%+ coverage
- **📚 Quickstart Notebooks:** 10+ Jupyter notebooks for immediate use
- **🔒 Secure:** Multiple API key management methods (env vars, config files, AWS Secrets Manager)

### 📊 Supported Data Sources

| Data Source | Domain | Auth Required | Update Frequency | Coverage | Status |
|-------------|--------|---------------|------------------|----------|--------|
| **Census ACS** | Demographics | Optional | Annual | All US geographies | ✅ Production |
| **Census CBP** | Business | Optional | Annual | County-level | ✅ Production |
| **Census LEHD** | Employment | No | Quarterly | County-level | ✅ Production |
| **FRED** | Economics | Yes | Daily/Real-time | 800K+ series | ✅ Production |
| **BLS** | Labor | Recommended | Monthly | National/State | ✅ Production |
| **BEA** | Economics | Yes | Quarterly/Annual | National/Regional | ✅ Production |
| **CDC WONDER** | Health | No | Varies | County-level | ✅ Production |
| **HRSA** | Health | No | Annual | HPSA/MUA/P | ✅ Production |
| **County Health Rankings** | Health | No | Annual | County-level | ✅ Production |
| **EPA EJScreen** | Environment | No | Annual | Block group | ✅ Production |
| **EPA Air Quality** | Environment | No | Hourly/Real-time | Station-level | ✅ Production |
| **HUD Fair Market Rent** | Housing | Yes | Annual | Metro/County | ✅ Production |
| **FBI UCR** | Crime | Recommended | Annual | Agency-level | ✅ Production |
| **NCES** | Education | No | Annual | School-level | ✅ Production |
| **Zillow Research** | Housing | No | Monthly | Metro/ZIP | ✅ Production |
| **USDA Food Atlas** | Food Security | No | Annual | County-level | 🔄 Planned |
| **College Scorecard** | Education | Yes | Annual | Institution | 🔄 Planned |
| **World Bank** | International | No | Annual | Country-level | 🔄 Planned |
| **OECD** | International | No | Varies | Country-level | 🔄 Planned |

**Legend:** ✅ Production | 🔄 Planned | ⚠️ Beta

## Overview

KRL Data Connectors offer a unified, type-safe interface to data providers spanning economic, demographic, health, environmental, and social datasets. The platform currently supports 12 production connectors, with an additional 28 connectors planned across housing, education, crime, food security, international development, civic engagement, and transportation domains. Each connector is engineered for consistent integration within institutional data pipelines and analytics workflows.

**Economic & Financial Data Sources:**
- **Federal Reserve Economic Data (FRED):** Access over 800,000 economic time series.
- **U.S. Census Bureau:** Retrieve demographic, economic, and geographic data, including CBP and LEHD.
- **Bureau of Labor Statistics (BLS):** Obtain labor market and inflation statistics.
- **Bureau of Economic Analysis (BEA):** Access GDP, regional accounts, and personal income data.

**Health & Environmental Data Sources:**
- **EPA EJScreen:** Environmental justice screening; 13 environmental and 6 demographic indicators. **NEW**
- **HRSA:** Health Professional Shortage Areas (HPSA), Medically Underserved Areas/Populations (MUA/P). **NEW**
- **County Health Rankings:** Over 30 county-level health measures and rankings (2010–present). **NEW**
- **EPA Air Quality / AirNow:** Real-time AQI, forecasts, and data from 2,500+ monitoring stations. **NEW**
- **CDC WONDER:** Mortality, natality, and population data (⚠️ API non-functional).

**Planned Data Domains (24 Additional Connectors):**
- **Housing & Urban Development:** EPA Superfund sites (Zillow, HUD FMR now in production)
- **Education:** College Scorecard, IPEDS higher education data, Stanford Education Data Archive, EdGap equity metrics
- **Food Security & Agriculture:** USDA Food Environment Atlas, NASS agricultural statistics, SNAP participation, Feeding America estimates
- **International Development:** World Bank development indicators, OECD Better Life Index, WHO global health data, UN statistical databases
- **Civic & Cultural Engagement:** IRS nonprofit financial data (Form 990), NEA arts participation, MIT Election Lab voting data, volunteering metrics
- **Transportation & Infrastructure:** National Household Travel Survey, Federal Transit Administration ridership, DOT traffic safety data
- **Climate & Weather:** NOAA climate normals, temperature and precipitation data

### Key Features

KRL Data Connectors are built for reproducibility, scalability, and institutional trust. Key features include:

- **Unified API:** Consistent interface across all supported data sources.
- **Intelligent Caching:** Minimize API calls and optimize performance.
- **Type-Safe:** Comprehensive type hints and validation for all connectors.
- **Rich Metadata:** Automated metadata extraction and documentation.
- **Production-Ready:** Robust error handling and structured logging.
- **Well-Tested:** 123+ tests, with over 90% coverage on new connectors.
- **Multi-Domain:** Seamless access to economic, health, environmental, and demographic data.
- **Quickstart Notebooks:** Jupyter notebooks for rapid onboarding and reproducible analysis.

## Installation

Install KRL Data Connectors via pip. The package supports optional and development dependencies for advanced use cases.

```bash
# Basic installation
pip install krl-data-connectors

# With all optional dependencies
pip install krl-data-connectors[all]

# Development installation
pip install krl-data-connectors[dev]
```

## Quick Start

This section demonstrates how to initialize and use key connectors. Each example is designed for clarity and immediate integration into institutional workflows.

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

All connectors inherit from `BaseConnector`. The base class provides standardized caching, configuration, and logging capabilities.

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

KRL Data Connectors are architected for extensibility and operational precision. Each connector extends `BaseConnector`, which standardizes logging, configuration, caching, and request management across all sources.

### BaseConnector

`BaseConnector` implements the following infrastructure features:

- **Structured Logging:** JSON-formatted logs with request and response metadata.
- **Configuration Management:** Supports environment variables and YAML-based configuration.
- **Intelligent Caching:** File-based and Redis caching with configurable TTL.
- **Error Handling:** Automatic retries, API rate limiting, and timeout management.
- **Request Management:** HTTP session pooling and connection reuse for efficiency.

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

KRL Data Connectors automatically detect API keys using multiple secure methods, ensuring seamless integration in both production and development environments. For comprehensive instructions, refer to [API_KEY_SETUP.md](./API_KEY_SETUP.md).

### Quick Setup

API keys are resolved in the following order:

1. **Environment variables** (recommended for production deployments)
2. **Configuration file** at `~/.krl/apikeys` (recommended for development)
3. **Direct assignment in code** (not recommended for production)

#### Option 1: Environment Variables (Recommended)

```bash
export BEA_API_KEY="your_bea_key"
export FRED_API_KEY="your_fred_key"
export BLS_API_KEY="your_bls_key"
export CENSUS_API_KEY="your_census_key"
```

#### Option 2: Configuration File (For Development)

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

KRL Data Connectors will automatically detect and use this file if present.

#### Obtaining API Keys

| Service           | Required?    | Registration URL                                      |
|-------------------|--------------|-------------------------------------------------------|
| **CBP/Census**    | Optional     | https://api.census.gov/data/key_signup.html           |
| **FRED**          | Yes          | https://fred.stlouisfed.org/docs/api/api_key.html     |
| **BLS**           | Recommended* | https://www.bls.gov/developers/home.htm               |
| **BEA**           | Yes          | https://apps.bea.gov/api/signup/                      |
| **LEHD**          | No           | N/A                                                  |

*BLS is accessible without a key but with reduced rate limits (25 vs. 500 requests/day).

### Using Config Utilities

The package provides utilities for automatic config discovery:

```python
from krl_data_connectors import find_config_file, BEAConnector

# Automatically locate the config file
config_path = find_config_file('apikeys')
print(f"Config found at: {config_path}")

# Connectors will use the config file or environment variables if available
bea = BEAConnector()
```

## Configuration

KRL Data Connectors support flexible configuration via environment variables and YAML files. This enables precise control over API keys, caching, and logging for institutional deployments.

### Environment Variables

Define environment variables to configure API credentials, caching, and logging:

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

Alternatively, use a YAML configuration file for advanced customization:

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

Load and apply the configuration in your workflow:

```python
from krl_core import ConfigManager

config = ConfigManager("config.yaml")
fred = FREDConnector(api_key=config.get("fred.api_key"))
```

## Available Connectors

KRL Data Connectors support 12 data sources, with 8 production-ready connectors, 1 in beta, and 3 planned. Each connector is engineered for reliability and institutional integration.

### ✅ Production-Ready (Well-Tested)

#### County Business Patterns (CBP) Connector
**Status:** ✅ Complete | **Tests:** 33 passing | **Coverage:** 77%

- Business establishment counts by NAICS industry
- Employment and payroll statistics
- County, state, and metropolitan-level data
- Historical coverage from 1986 onward
- **API:** U.S. Census Bureau CBP API (free, API key required)
- **Quickstart:** [examples/cbp_quickstart.ipynb](examples/)

#### LEHD Origin-Destination Connector
**Status:** ✅ Complete | **Tests:** 28 passing | **Coverage:** 74%

- Worker origin-destination employment flows
- Home and workplace demographic characteristics
- Job counts by segment (age, earnings, industry)
- Block-level geospatial granularity
- **API:** Census LEHD (free, no API key required)
- **Quickstart:** [examples/lehd_quickstart.ipynb](examples/)

#### FRED Connector
**Status:** ✅ Complete | **Tests:** TBD | **Coverage:** 17%

- Access to 800,000+ economic time series
- Real-time and historical data retrieval
- Series metadata and release context
- Hierarchical category browsing and search
- **API:** Federal Reserve (free, API key required; 120k requests/day)

#### BLS Connector
**Status:** ✅ Complete | **Tests:** 31 passing | **Coverage:** 87%

- Employment and unemployment time series
- Consumer Price Index (CPI) and Producer Price Index (PPI)
- Wages and earnings statistics
- **API:** Bureau of Labor Statistics (free, API key required; 500 requests/day)

#### BEA Connector
**Status:** ✅ Complete | **Tests:** 28 passing | **Coverage:** 72%

- GDP by state and metropolitan area
- Regional economic accounts
- Personal income and industry-level data
- **API:** Bureau of Economic Analysis (free, API key required)

#### EPA EJScreen Connector
**Status:** Complete | **Tests:** 29/29 passing | **Coverage:** 96.34% | **NEW**

- Environmental justice screening and mapping
- 13 environmental indicators (e.g., PM2.5, Ozone, Traffic, Hazardous Waste)
- 6 demographic indicators (e.g., Minority %, Low Income %, Limited English)
- Census tract-level data (74,000+ tracts)
- EJ Index scores integrating environmental and demographic data
- **API:** File-based (CSV downloads from EPA EJScreen)
- **Data Source:** https://www.epa.gov/ejscreen
- **Domains:** D06 (Public Health), D14 (Environmental Quality)
- **Quickstart:** [examples/ejscreen_quickstart.ipynb](examples/ejscreen_quickstart.ipynb)

#### HRSA Connector
**Status:** Complete | **Tests:** 45/45 passing | **Coverage:** 90.51% | **NEW**

- Health Professional Shortage Areas (HPSA): Primary Care, Dental, Mental Health
- Medically Underserved Areas/Populations (MUA/P)
- Health Centers (FQHC)
- HPSA scoring (0–26 scale)
- Geographic, population, and facility-based designations
- **API:** File-based (CSV/XLSX downloads from HRSA Data Warehouse)
- **Data Source:** https://data.hrsa.gov/data/download
- **Domains:** D05 (Healthcare Access), D06 (Public Health), D24 (Geographic Data)
- **Quickstart:** [examples/hrsa_quickstart.ipynb](examples/hrsa_quickstart.ipynb)

#### County Health Rankings & Roadmaps Connector
**Status:** Complete | **Tests:** Pending | **Coverage:** TBD | **NEW**

- Health Outcomes Rankings (Length and Quality of Life)
- Health Factors Rankings (Behaviors, Clinical Care, Social/Economic, Environment)
- 30+ county-level health measures
- Trend data from 2010 onward
- Comparative state and county analytics
- Top and bottom performer identification
- **API:** File-based (CSV downloads from County Health Rankings)
- **Data Source:** https://www.countyhealthrankings.org/health-data
- **Domains:** D05 (Healthcare Access), D06 (Public Health), D24 (Geographic Data)
- **Quickstart:** [examples/chr_quickstart.ipynb](examples/chr_quickstart.ipynb)

#### EPA Air Quality / AirNow Connector
**Status:** Complete | **Tests:** 49/49 passing | **Coverage:** 83.82% | **NEW**

- Real-time Air Quality Index (AQI) and forecasts
- Current observations by ZIP code or geocoordinates
- Historical AQI data retrieval
- Six AQI parameters: PM2.5, PM10, Ozone, CO, NO2, SO2
- 2,500+ monitoring stations (U.S., Canada, Mexico)
- AQI health categories: Good, Moderate, Unhealthy, etc.
- **API:** EPA AirNow REST API (free, API key required; 500 requests/hour)
- **Data Source:** https://docs.airnowapi.org/
- **Domains:** D06 (Public Health), D14 (Environmental Quality), D24 (Geographic Data)
- **Quickstart:** [examples/air_quality_quickstart.ipynb](examples/air_quality_quickstart.ipynb)

#### Zillow Research Data Connector
**Status:** Complete | **Tests:** 36/36 passing | **Coverage:** TBD | **NEW**

- Zillow Home Value Index (ZHVI) - typical home values
- Zillow Rent Index (ZRI) - typical market rents
- Inventory metrics - for-sale homes, new listings
- Sales data - list prices, sale prices
- Geographic filtering: National, state, metro, county, city, ZIP, neighborhood
- Time series analysis and growth calculations
- **API:** File-based (download from Zillow Research)
- **Data Source:** https://www.zillow.com/research/data/
- **Domains:** D03 (Housing & Real Estate), D08 (Economic Development), D24 (Geographic Data)
- **Quickstart:** [examples/zillow_quickstart.ipynb](examples/zillow_quickstart.ipynb)

#### HUD Fair Market Rents Connector
**Status:** Complete | **Tests:** 34/34 passing | **Coverage:** TBD | **NEW**

- Fair Market Rents (FMR) by bedroom count (0BR-4BR)
- Small Area FMRs (ZIP code level)
- Income limits (very low, low, median income)
- Affordability calculations (30% income rule)
- Year-over-year FMR comparisons
- State, metro, and county-level data
- **API:** HUD USER API (free, API key required) + downloadable files
- **Data Source:** https://www.huduser.gov/portal/datasets/fmr.html
- **Domains:** D03 (Housing & Real Estate), D08 (Economic Development), D24 (Geographic Data)
- **Quickstart:** [examples/hud_fmr_quickstart.ipynb](examples/hud_fmr_quickstart.ipynb)

#### FBI Uniform Crime Reporting (UCR) Connector
**Status:** Complete | **Tests:** 42/42 passing | **Coverage:** TBD | **NEW**

- Violent crime statistics (murder, rape, robbery, aggravated assault)
- Property crime statistics (burglary, larceny-theft, motor vehicle theft, arson)
- Arrest data by offense type and demographics
- Crime rates per capita calculations
- National, state, and agency-level data
- Historical data from 1960s-present
- **API:** Crime Data Explorer API (free, no key required)
- **Data Source:** https://cde.ucr.cjis.gov/LATEST/webapp/
- **Domains:** D10 (Public Safety & Crime), D19 (Governance & Civic Infrastructure), D24 (Geographic Data)
- **Quickstart:** [examples/fbi_ucr_quickstart.ipynb](examples/fbi_ucr_quickstart.ipynb)

#### National Center for Education Statistics (NCES) Connector
**Status:** Complete | **Tests:** 48/48 passing | **Coverage:** TBD | **NEW**

- School directory and enrollment data (CCD - Common Core of Data)
- Student demographics by race/ethnicity and gender
- Performance metrics (test scores, graduation rates)
- District finances and per-pupil spending calculations
- Teacher and staff statistics
- National, state, district, and school-level data
- **API:** Urban Institute Education Data Portal (free, no key required)
- **Data Source:** https://educationdata.urban.org/ | https://nces.ed.gov/
- **Domains:** D09 (Education & Workforce Development), D19 (Governance), D24 (Geographic Data)
- **Quickstart:** [examples/nces_quickstart.ipynb](examples/nces_quickstart.ipynb)

### In Development

#### CDC WONDER Connector
**Status:** BETA – API Non-Functional | **Tests:** 13 passing | **Coverage:** 74%

- Mortality and natality data
- Population estimates
- **Known Limitation:** CDC WONDER does not provide a functional programmatic API.
    - API endpoints return HTTP 500 errors
    - API documentation is unavailable (404)
    - Web form interface is required for access
- **Recommendation:** Use the CDC WONDER web interface: https://wonder.cdc.gov/
- **Connector Status:** Implementation complete; not usable due to upstream API limitations.
- **API:** CDC WONDER (free, no key required, but non-functional)

### Planned Connectors (24 Additional Data Sources)

KRL Data Connectors will expand to 40 total connectors, spanning additional critical domains for comprehensive institutional analysis. The following connectors are prioritized for implementation:

#### Housing & Urban Development (1 Connector)
- **EPA Superfund Sites:** Hazardous waste site locations, contamination status, and remediation progress

#### Crime & Public Safety (1 Connector)
- **Gun Violence Archive:** Incident-level gun violence data, including mass shootings and firearm-related events

#### Education (4 Connectors)
- **College Scorecard:** College costs, student outcomes, graduate earnings, and debt statistics
- **IPEDS (Integrated Postsecondary Education):** Comprehensive higher education institutional data and trends
- **Stanford Education Data Archive:** K-12 test score data with longitudinal coverage
- **EdGap:** Educational opportunity gaps and equity metrics

#### Food Security & Agriculture (4 Connectors)
- **USDA Food Environment Atlas:** County-level food access, food insecurity prevalence, and local food system metrics
- **USDA NASS (National Agricultural Statistics):** Crop production, livestock inventory, and farm economic indicators
- **USDA SNAP:** Supplemental Nutrition Assistance Program participation and benefit distribution data
- **Feeding America MAP the Meal Gap:** County-level food insecurity estimates and vulnerable population statistics

#### International Development (6 Connectors)
- **World Bank:** Global development indicators spanning economic, social, and environmental dimensions
- **OECD:** Better Life Index, inequality metrics, governance indicators, and gender gap statistics across member countries
- **WHO (World Health Organization):** Global health indicators and disease surveillance data
- **World Economic Forum (WEF):** Global Competitiveness Index and Global Gender Gap Report data
- **Freedom House:** Freedom in the World scores, civil liberties, and political rights assessments
- **UN Data:** United Nations statistical databases covering diverse development metrics

#### Civic & Cultural Engagement (5 Connectors)
- **IRS Form 990:** Nonprofit organization financial data, including revenue, expenses, programs, and governance
- **National Endowment for the Arts (NEA):** Arts participation rates and cultural engagement statistics
- **Institute of Museum and Library Services (IMLS):** Public library and museum operational data
- **MIT Election Lab:** Election results, voter turnout, and voting law data across jurisdictions
- **Volunteering in America:** Volunteer rates, civic engagement metrics, and community service statistics

#### Transportation & Infrastructure (3 Connectors)
- **National Household Travel Survey (NHTS):** Travel behavior, commuting patterns, and mode choice data
- **Federal Transit Administration (FTA):** Public transit ridership, service metrics, and National Transit Database
- **DOT Fatality Analysis Reporting System (FARS):** Traffic fatality data and crash characteristics

#### Climate & Weather (1 Connector)
- **NOAA Climate Data:** Temperature, precipitation, climate normals, and historical weather observations

**Implementation Timeline:** Connectors will be added incrementally, prioritizing high-demand data sources and institutional requirements. For detailed roadmap and priority matrix, see [REMAINING_CONNECTORS_ROADMAP.md](REMAINING_CONNECTORS_ROADMAP.md).

## Roadmap & Development Priorities

KRL Data Connectors follow a structured development roadmap targeting 40 total connectors. The roadmap prioritizes data sources by institutional demand, API availability, and domain coverage requirements.

### Current Status
- **Production Connectors:** 12/40 (30% complete)
- **Test Coverage:** 137+ tests passing, 90%+ average coverage on new connectors
- **Documentation:** Quickstart notebooks for all production connectors
- **Security Audit:** 100/100 score maintained

### Implementation Priorities

**High Priority (Next 10 Connectors):**
1. **USDA Food Environment Atlas** – County food access and insecurity metrics
2. **OECD Better Life Index** – Cross-country well-being and governance indicators
3. **World Bank Development Indicators** – Global economic and social development data
4. **FBI Uniform Crime Reporting** – Crime statistics and law enforcement data
5. **NCES Education Statistics** – School demographics, performance, and financing
6. **Zillow Housing Data** – Housing market prices, rents, and inventory
7. **IRS Form 990 Nonprofit Data** – Nonprofit financial and operational metrics
8. **EPA Superfund Sites** – Environmental contamination site data
9. **WHO Global Health Indicators** – International health statistics
10. **HUD Fair Market Rents** – Rental affordability and income limit data

**Medium Priority (Next 12 Connectors):**
- USDA NASS agricultural statistics
- College Scorecard higher education outcomes
- IPEDS postsecondary education data
- MIT Election Lab voting data
- National Household Travel Survey
- NEA arts participation metrics
- IMLS library and museum data
- WEF Global Competitiveness data
- Freedom House civil liberties scores
- USDA SNAP participation data
- Federal Transit Administration ridership
- Stanford Education Data Archive

**Lower Priority (Final 6 Connectors):**
- Gun Violence Archive incident data
- EdGap educational equity metrics
- Feeding America food insecurity estimates
- Volunteering in America civic engagement
- DOT traffic fatality data
- UN Data statistical databases

### Quality Standards

All connectors adhere to rigorous engineering and documentation standards:
- **Test Coverage:** Minimum 80% coverage with comprehensive unit tests
- **Type Safety:** Full type hints and validation for all public methods
- **Error Handling:** Graceful degradation with informative error messages
- **Caching:** Intelligent caching with configurable TTL
- **Logging:** Structured JSON logging with request/response metadata
- **Documentation:** Docstrings, usage examples, and quickstart notebooks
- **Security:** API key protection, input validation, secure defaults

### Domain Coverage Goals

The 40-connector roadmap ensures comprehensive coverage across critical analytical domains:

| Domain | Current | Planned | Total |
|--------|---------|---------|-------|
| **Economic & Financial** | 4 | 0 | 4 |
| **Health & Public Health** | 4 | 0 | 4 |
| **Environmental Quality** | 3 | 2 | 5 |
| **Housing & Urban Development** | 0 | 3 | 3 |
| **Education** | 0 | 5 | 5 |
| **Crime & Public Safety** | 0 | 2 | 2 |
| **Food Security & Agriculture** | 0 | 4 | 4 |
| **International Development** | 0 | 6 | 6 |
| **Civic & Cultural Engagement** | 0 | 5 | 5 |
| **Transportation & Infrastructure** | 0 | 3 | 3 |
| **Climate & Weather** | 0 | 1 | 1 |

For detailed implementation schedules, API specifications, and connector templates, refer to [REMAINING_CONNECTORS_ROADMAP.md](REMAINING_CONNECTORS_ROADMAP.md).

## Testing

KRL Data Connectors include a comprehensive test suite to ensure reliability and reproducibility. Use the following commands to execute tests and measure code coverage:

```bash
# Run all tests
pytest

# Run specific connector tests
pytest tests/unit/test_ejscreen_connector.py tests/unit/test_hrsa_connector.py tests/unit/test_air_quality_connector.py -v

# Run with coverage reporting
pytest --cov=src --cov-report=html

# Run individual connector tests
pytest tests/unit/test_fred_connector.py -v

# Run integration tests (requires API keys)
pytest tests/integration/ -v
```

## Development

Follow these steps to set up the development environment and contribute to KRL Data Connectors. The workflow ensures code quality and reproducibility at every stage.

```bash
# Clone the repository
git clone https://github.com/KR-Labs/krl-data-connectors.git
cd krl-data-connectors

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install development and test dependencies
pip install -e ".[dev,test]"

# Run pre-commit hooks for code quality
pre-commit install
pre-commit run --all-files

# Execute tests
pytest

# Build documentation
cd docs && make html
```

## Contributing

Contributions are encouraged and help maintain the integrity and scalability of KRL Data Connectors. Review the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines prior to submitting changes.

### Contributor License Agreement

All contributors are required to sign the [Contributor License Agreement (CLA)](https://krlabs.dev/cla) before changes can be merged.

## License

KRL Data Connectors are licensed under the **Apache License 2.0**. See the [LICENSE](LICENSE) file for full details.

**Apache 2.0 License Highlights:**
- Commercial use permitted
- Modification and redistribution allowed
- Patent grant included
- Compatible with proprietary software

## Support

For technical support, documentation, and community engagement:
- **Documentation:** https://docs.krlabs.dev/data-connectors
- **Issue Tracker:** https://github.com/KR-Labs/krl-data-connectors/issues
- **Discussions:** https://github.com/KR-Labs/krl-data-connectors/discussions
- **Email:** support@krlabs.dev

## Related Projects

KRL Data Connectors are part of a broader ecosystem supporting institutional analytics:
- **[krl-open-core](https://github.com/KR-Labs/krl-open-core):** Core utilities for logging, configuration, and caching.
- **[krl-model-zoo](https://github.com/KR-Labs/krl-model-zoo):** Causal inference and forecasting models.
- **[krl-dashboard](https://github.com/KR-Labs/krl-dashboard):** Interactive data visualization platform.
- **[krl-tutorials](https://github.com/KR-Labs/krl-tutorials):** Hands-on learning materials and example workflows.

## Citation

If you use KRL Data Connectors in your research or institutional work, please cite:

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

**Built for reproducibility, scalability, and institutional trust by [KR-Labs](https://krlabs.dev)**

*© 2025 KR-Labs. All rights reserved.*  
*KR-Labs is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.*
