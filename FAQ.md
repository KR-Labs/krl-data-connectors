---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# Frequently Asked Questions (FAQ)

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [API Keys & Authentication](#api-keys--authentication)
- [Data Access & Usage](#data-access--usage)
- [Performance & Caching](#performance--caching)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Commercial Use & Licensing](#commercial-use--licensing)

---

## General Questions

### What is KRL Data Connectors?

KRL Data Connectors is a Python package providing standardized, production-ready interfaces to 15+ socioeconomic data sources. It handles API authentication, caching, error handling, and data normalization automatically, letting you focus on analysis rather than data wrangling.

### Who should use this package?

- **Researchers** conducting economic, demographic, or policy analysis
- **Data Scientists** building analytical pipelines
- **Policy Analysts** evaluating program impacts
- **Government Agencies** building data infrastructure
- **Nonprofits** analyzing community data
- **Students** learning data science with real-world data

### What data sources are supported?

Currently **15 production connectors:**
- **Economic:** FRED, BEA, BLS, Census CBP
- **Demographic:** Census ACS, LEHD
- **Health:** CDC WONDER, HRSA, County Health Rankings
- **Environment:** EPA EJScreen, EPA Air Quality
- **Housing:** HUD Fair Market Rent, Zillow Research Data
- **Crime:** FBI Uniform Crime Reporting
- **Education:** NCES Education Data

See [README](./README.md#supported-data-sources) for full list and planned connectors.

### Is this package free?

**Yes!** KRL Data Connectors is 100% free and open source under the Apache 2.0 license. You can use it for:
- Academic research
- Commercial products
- Government projects
- Personal projects
- Any purpose allowed by Apache 2.0

Some data sources require free API keys, but the package itself is free.

### How is this different from accessing APIs directly?

| Feature | Direct API Access | KRL Data Connectors |
|---------|-------------------|---------------------|
| **API Key Management** | Manual in each script | Automatic detection |
| **Caching** | Build yourself | Built-in, configurable |
| **Error Handling** | Manual try/except | Automatic retries |
| **Rate Limiting** | Track yourself | Automatic throttling |
| **Data Normalization** | Manual parsing | Consistent DataFrames |
| **Type Safety** | None | Full type hints |
| **Testing** | Your responsibility | 297+ tests included |
| **Documentation** | Read API docs | Unified documentation |

---

## Installation & Setup

### How do I install KRL Data Connectors?

```bash
# Basic installation
pip install krl-data-connectors

# With all optional dependencies
pip install krl-data-connectors[all]

# Development installation (if cloning from GitHub)
git clone https://github.com/KR-Labs/krl-data-connectors.git
cd krl-data-connectors
pip install -e ".[dev]"
```

### What Python versions are supported?

Python 3.9, 3.10, 3.11, and 3.12 are officially supported and tested.

### Do I need to install anything else?

No! All dependencies are installed automatically:
- `pandas` - Data manipulation
- `requests` - HTTP requests
- `pyyaml` - Configuration files
- `pytest` (dev) - Testing

Optional dependencies for specific features:
- `boto3` - AWS Secrets Manager support
- `redis` - Redis caching (alternative to file cache)

### Can I use this in Jupyter notebooks?

Absolutely! All connectors work great in Jupyter. We even provide quickstart notebooks:

```python
# In Jupyter
from krl_data_connectors import FREDConnector
fred = FREDConnector()
data = fred.get_series("UNRATE")
data.plot(title="US Unemployment Rate")
```

### Can I use this in production applications?

Yes! KRL Data Connectors is designed for production use:
- Robust error handling and retries
- Structured logging
- Configurable caching
- Type-safe interfaces
- Well-tested (90%+ coverage)
- AWS Secrets Manager integration

---

## API Keys & Authentication

### Which data sources require API keys?

| Data Source | API Key Required? | Get Key From |
|-------------|-------------------|--------------|
| FRED | ✅ Yes | https://fred.stlouisfed.org/docs/api/api_key.html |
| BEA | ✅ Yes | https://apps.bea.gov/api/signup/ |
| BLS | ⚠️ Recommended* | https://www.bls.gov/developers/home.htm |
| Census (ACS/CBP) | ⚠️ Recommended* | https://api.census.gov/data/key_signup.html |
| HUD FMR | ✅ Yes | https://www.huduser.gov/portal/dataset/fmr-api.html |
| FBI UCR | ⚠️ Recommended* | https://api.data.gov/signup/ |
| LEHD | ❌ No | N/A |
| CDC WONDER | ❌ No | N/A |
| HRSA | ❌ No | N/A |
| County Health Rankings | ❌ No | N/A |
| EPA EJScreen | ❌ No | N/A |
| EPA Air Quality | ❌ No | N/A |
| NCES | ❌ No | N/A |
| Zillow | ❌ No (file-based) | Download CSVs from zillow.com/research/data |

*Works without key but with reduced rate limits

### How do I set up API keys?

**Best practice: Environment variables**
```bash
export FRED_API_KEY="your_key_here"
export BEA_API_KEY="your_key_here"
export BLS_API_KEY="your_key_here"
export CENSUS_API_KEY="your_key_here"
```

**Alternative: Configuration file**
```bash
mkdir -p ~/.krl
cat > ~/.krl/apikeys << EOF
FRED API KEY: your_fred_key
BEA API KEY: your_bea_key
BLS API KEY: your_bls_key
CENSUS API: your_census_key
EOF
chmod 600 ~/.krl/apikeys
```

**For production: AWS Secrets Manager**
```python
# Automatic fallback to Secrets Manager if boto3 installed
fred = FREDConnector()  # Will check Secrets Manager if env var not set
```

See [API_KEY_SETUP.md](./API_KEY_SETUP.md) for detailed instructions.

### Do API keys cost money?

**No!** All supported data sources offer free API keys:
- FRED: Free, lifetime validity
- BEA: Free, lifetime validity
- BLS: Free, annual renewal
- Census: Free, lifetime validity
- HUD: Free (requires account creation)

There are no usage fees, just rate limits.

### What are the rate limits?

| Service | Without Key | With Key | Notes |
|---------|-------------|----------|-------|
| FRED | N/A | Unlimited | Key required |
| BEA | N/A | 1,000/day | Key required |
| BLS | 25/day | 500/day | Daily limit |
| Census | 500/day | 5,000/day | Per IP address |
| HUD | N/A | Not specified | Key required |

**Tip:** Enable caching to minimize API calls!

### Can I share my API keys with my team?

**Generally no.** Most API terms of service require individual keys. However:
- For institutional use, contact the data provider
- Some services offer organizational accounts
- Use AWS Secrets Manager for team access without sharing keys

---

## Data Access & Usage

### How do I get data for a specific state/region?

Each connector has geography-specific methods:

```python
# Census data for Rhode Island (FIPS code 44)
cbp = CountyBusinessPatternsConnector()
ri_data = cbp.get_state_data(year=2021, state='44')

# LEHD data for Rhode Island
lehd = LEHDConnector()
od_data = lehd.get_od_data(state='ri', year=2021)

# FRED state-level data
fred = FREDConnector()
ri_unemployment = fred.get_series("RIUR")  # RI unemployment rate
```

See connector-specific documentation for available geography options.

### How do I get historical time series data?

```python
# FRED: Specify date range
fred = FREDConnector()
data = fred.get_series(
    series_id="UNRATE",
    observation_start="2000-01-01",
    observation_end="2023-12-31"
)

# BLS: Specify year range
bls = BLSConnector()
data = bls.get_series(
    series_ids=['LASST440000000000003'],
    start_year=2000,
    end_year=2023
)

# County Business Patterns: Loop through years
cbp = CountyBusinessPatternsConnector()
all_years = []
for year in range(2010, 2024):
    data = cbp.get_state_data(year=year, state='44')
    all_years.append(data)
combined = pd.concat(all_years)
```

### What format is the data returned in?

All connectors return **pandas DataFrames** by default. This provides:
- Consistent interface across all sources
- Built-in data manipulation methods
- Easy export to CSV, Excel, SQL, etc.
- Integration with visualization libraries

```python
data = fred.get_series("UNRATE")
type(data)  # pandas.DataFrame

# Export to various formats
data.to_csv("unemployment.csv")
data.to_excel("unemployment.xlsx")
data.to_sql("unemployment", connection)
data.to_json("unemployment.json")
```

### How do I handle missing data?

```python
# Check for missing values
data.isnull().sum()

# Drop rows with any missing values
clean_data = data.dropna()

# Drop rows with missing values in specific columns
clean_data = data.dropna(subset=['value', 'date'])

# Fill missing values
data['value'].fillna(method='ffill')  # Forward fill
data['value'].fillna(0)  # Fill with zero
data['value'].fillna(data['value'].mean())  # Fill with mean
```

### Can I get metadata about the data?

Yes! Most connectors provide metadata methods:

```python
# FRED series information
fred = FREDConnector()
info = fred.get_series_info("UNRATE")
print(f"Title: {info['title']}")
print(f"Units: {info['units']}")
print(f"Frequency: {info['frequency']}")
print(f"Available: {info['observation_start']} to {info['observation_end']}")

# Census variable definitions
census = CensusACSConnector()
variables = census.get_variables(year=2021, dataset='acs5')
print(variables[['name', 'label', 'concept']])
```

---

## Performance & Caching

### How can I speed up data retrieval?

**1. Enable caching (automatic):**
```python
fred = FREDConnector(
    cache_dir="/tmp/fred_cache",
    cache_ttl=86400  # 24 hours
)

# First call: hits API (~5 seconds)
data1 = fred.get_series("UNRATE")

# Second call: hits cache (~0.1 seconds)
data2 = fred.get_series("UNRATE")
```

**2. Use batch requests when available:**
```python
# BLS supports up to 50 series at once
bls = BLSConnector()
data = bls.get_series(
    series_ids=['SERIES1', 'SERIES2', 'SERIES3'],
    start_year=2020,
    end_year=2023
)
```

**3. Request only needed columns:**
```python
cbp = CountyBusinessPatternsConnector()
data = cbp.get_state_data(
    year=2021,
    state='44',
    get='NAME,NAICS2017,ESTAB,EMP'  # Only these columns
)
```

### How does caching work?

Caching is **automatic** and **transparent**:

1. First request → Fetches from API → Saves to cache
2. Subsequent requests → Returns from cache (if not expired)
3. After TTL expires → Fetches fresh data → Updates cache

```python
# Configure caching
connector = FREDConnector(
    cache_dir="/tmp/my_cache",  # Where to store cache
    cache_ttl=3600,  # How long to cache (seconds)
)

# Check cache performance
stats = connector.cache.get_stats()
print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")
print(f"Hit rate: {stats['hit_rate']:.1f}%")

# Clear cache if needed
connector.cache.clear()
```

### Where is cached data stored?

**Default locations:**
- Linux/macOS: `/tmp/<connector_name>_cache/`
- Windows: `%TEMP%\<connector_name>_cache\`

**Custom location:**
```python
connector = FREDConnector(cache_dir="/my/custom/path")
```

**Important:** Cache is stored as files, not in memory, so it persists between Python sessions.

### How long is data cached?

**Default: 24 hours (86400 seconds)**

You can customize:
```python
# Cache for 1 hour
fred = FREDConnector(cache_ttl=3600)

# Cache for 1 week
fred = FREDConnector(cache_ttl=604800)

# Disable caching
fred = FREDConnector(cache_ttl=0)
```

### Can I use Redis for caching?

Not yet, but it's planned! Currently only file-based caching is supported. Redis support is in development.

---

## Troubleshooting

### I'm getting "API key not found" errors

See [API Keys & Authentication](#api-keys--authentication) above, or check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#api-key-problems).

### I'm getting connection timeout errors

```python
# Increase timeout
connector = FREDConnector(timeout=60)  # 60 seconds

# Check network
ping api.stlouisfed.org
```

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md#network--connection-errors) for more solutions.

### I'm getting rate limit errors

```python
# Enable caching to reduce API calls
connector = FREDConnector(cache_dir="/tmp/cache")

# Add delays between requests
import time
for item in items:
    data = connector.get_data(item)
    time.sleep(1)
```

### Data seems stale/outdated

```python
# Clear cache
connector.cache.clear()

# Or reduce cache TTL
connector = FREDConnector(cache_ttl=3600)  # 1 hour
```

### Getting empty DataFrames

Check if data exists for your parameters:
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Try request
data = connector.get_data(...)
```

See full [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) guide.

---

## Contributing

### How can I contribute?

We welcome contributions! Ways to help:

1. **Report bugs** - Use issue templates
2. **Request features** - Suggest new data sources
3. **Improve documentation** - Fix typos, add examples
4. **Write tests** - Increase coverage
5. **Add connectors** - Implement new data sources

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### I want to add a new data connector. How do I start?

1. **Check existing issues** - Someone may already be working on it
2. **Create a feature request** - Describe the data source
3. **Follow the connector template:**

```python
from krl_data_connectors import BaseConnector
import pandas as pd

class MyNewConnector(BaseConnector):
    """Connector for MyData API."""
    
    def __init__(self, api_key=None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.base_url = "https://api.mydata.gov"
    
    def get_data(self, ...):
        """Fetch data from MyData API."""
        # Implementation
        pass
```

4. **Write tests** - Aim for 80%+ coverage
5. **Add documentation** - Docstrings and quickstart notebook
6. **Submit PR** - Follow PR template

### Do I need to sign a CLA?

Yes. We require a Contributor License Agreement to protect the project and contributors. It's a simple online process.

See [CLA.md](./docs/CLA.md) for details.

---

## Commercial Use & Licensing

### Can I use this in commercial products?

**Yes!** KRL Data Connectors is licensed under Apache 2.0, which allows:
- Commercial use
- Modification
- Distribution
- Patent use
- Private use

**Requirements:**
- Include the original license
- State changes made to the code
- Include copyright notice

### Do I need to open-source my code if I use this?

**No.** Apache 2.0 is permissive - you can use this in proprietary software without releasing your source code.

### Can I sell products built with KRL Data Connectors?

Yes! You can build and sell commercial products. The only requirement is including the Apache 2.0 license notice.

### What about the data itself?

**Important:** While KRL Data Connectors is Apache 2.0, the *data* has its own terms:

- **Government data** (Census, BLS, FRED, etc.) - Generally public domain
- **Zillow data** - Check Zillow's terms for commercial use
- **Other sources** - Check each provider's terms

Always verify data licensing with the original provider.

### Who maintains this project?

KRL Data Connectors is maintained by **KR-Labs Foundation**, a non-profit dedicated to open-source socioeconomic analytics tools.

- **GitHub:** https://github.com/KR-Labs
- **Website:** https://krlabs.dev
- **Email:** info@krlabs.dev

---

## Still Have Questions?

- **Documentation:** https://krl-data-connectors.readthedocs.io
- **GitHub Issues:** https://github.com/KR-Labs/krl-data-connectors/issues
- **Discussions:** https://github.com/KR-Labs/krl-data-connectors/discussions
- **Email:** support@krlabs.dev

---

**Last Updated:** October 20, 2025  
**Version:** 1.0.0
