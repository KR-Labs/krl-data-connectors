---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# Troubleshooting Guide

This guide covers common issues and solutions when using KRL Data Connectors.

## Table of Contents

- [Installation Issues](#installation-issues)
- [API Key Problems](#api-key-problems)
- [Network & Connection Errors](#network--connection-errors)
- [Data Quality Issues](#data-quality-issues)
- [Performance Problems](#performance-problems)
- [Caching Issues](#caching-issues)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Installation Issues

### Problem: pip install fails with dependency conflicts

**Symptoms:**
```bash
ERROR: Cannot install krl-data-connectors because these package versions have conflicting dependencies.
```

**Solutions:**

1. **Use a fresh virtual environment:**
```bash
python -m venv krl_env
source krl_env/bin/activate  # On Windows: krl_env\Scripts\activate
pip install --upgrade pip
pip install krl-data-connectors
```

2. **Install with specific dependency versions:**
```bash
pip install krl-data-connectors --no-deps
pip install pandas requests pyyaml
```

3. **Use conda instead:**
```bash
conda create -n krl python=3.11
conda activate krl
pip install krl-data-connectors
```

### Problem: ModuleNotFoundError after installation

**Symptoms:**
```python
ModuleNotFoundError: No module named 'krl_data_connectors'
```

**Solutions:**

1. **Verify installation:**
```bash
pip list | grep krl
python -c "import krl_data_connectors; print(krl_data_connectors.__version__)"
```

2. **Check Python environment:**
```bash
which python  # Ensure you're using the right Python
pip show krl-data-connectors  # Verify install location
```

3. **Reinstall package:**
```bash
pip uninstall krl-data-connectors
pip install krl-data-connectors
```

---

## API Key Problems

### Problem: "API key not found" error

**Symptoms:**
```python
ValueError: API key not found. Set FRED_API_KEY environment variable or provide api_key parameter.
```

**Solutions:**

**Option 1: Environment Variables (Recommended)**
```bash
# Linux/macOS
export FRED_API_KEY="your_key_here"

# Windows (Command Prompt)
set FRED_API_KEY=your_key_here

# Windows (PowerShell)
$env:FRED_API_KEY="your_key_here"

# Verify it's set
echo $FRED_API_KEY  # Linux/macOS
echo %FRED_API_KEY%  # Windows
```

**Option 2: Configuration File**
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

**Option 3: Direct in Code (Development Only)**
```python
from krl_data_connectors import FREDConnector

fred = FREDConnector(api_key="your_key_here")
```

### Problem: "Invalid API key" or 401 Unauthorized

**Symptoms:**
```python
requests.exceptions.HTTPError: 401 Client Error: Unauthorized
```

**Solutions:**

1. **Verify key is correct:**
```bash
# Test FRED API key
curl "https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key=YOUR_KEY&file_type=json"
```

2. **Check key hasn't expired:**
   - FRED keys: Lifetime validity
   - BLS keys: Check https://www.bls.gov/developers/
   - Census keys: Check https://api.census.gov/data/key_signup.html

3. **Regenerate key:**
   - Most services allow regenerating keys
   - Update key in all locations (env vars, config files)

### Problem: "Rate limit exceeded"

**Symptoms:**
```python
requests.exceptions.HTTPError: 429 Client Error: Too Many Requests
```

**Solutions:**

1. **Enable caching** (automatic retry after rate limit):
```python
from krl_data_connectors import FREDConnector

fred = FREDConnector(
    cache_dir="/tmp/fred_cache",
    cache_ttl=86400  # 24 hours
)
```

2. **Add delays between requests:**
```python
import time
for series_id in series_list:
    data = fred.get_series(series_id)
    time.sleep(1)  # Wait 1 second between requests
```

3. **Get a registered API key:**
   - BLS: 25 requests/day (no key) vs 500 requests/day (with key)
   - Census: 500 requests/day (no key) vs 5,000 requests/day (with key)

---

## Network & Connection Errors

### Problem: "Connection timeout" errors

**Symptoms:**
```python
requests.exceptions.ConnectTimeout: HTTPSConnectionPool(host='api.stlouisfed.org', port=443): Max retries exceeded
```

**Solutions:**

1. **Increase timeout:**
```python
from krl_data_connectors import FREDConnector

fred = FREDConnector(timeout=60)  # Increase to 60 seconds
```

2. **Check network connectivity:**
```bash
ping api.stlouisfed.org
curl -I https://api.stlouisfed.org
```

3. **Check firewall/proxy:**
```bash
# Set proxy if needed
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

### Problem: SSL Certificate errors

**Symptoms:**
```python
requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**

1. **Update certificates:**
```bash
pip install --upgrade certifi
```

2. **On macOS, install certificates:**
```bash
/Applications/Python\ 3.11/Install\ Certificates.command
```

3. **Temporary workaround (NOT recommended for production):**
```python
import requests
from krl_data_connectors import FREDConnector

# Disable SSL verification (DEVELOPMENT ONLY)
fred = FREDConnector()
fred.session.verify = False
```

---

## Data Quality Issues

### Problem: Empty DataFrame returned

**Symptoms:**
```python
data = connector.get_data(...)
print(len(data))  # 0
```

**Diagnosis:**

1. **Check if data exists for parameters:**
```python
# Example: LEHD data might not exist for all states/years
lehd = LEHDConnector()
try:
    data = lehd.get_od_data(state='ri', year=2021)
    if data.empty:
        print("No data available for RI 2021")
except Exception as e:
    print(f"Error: {e}")
```

2. **Verify parameters:**
```python
# Check valid values
fred = FREDConnector()
info = fred.get_series_info("GNPCA")
print(f"Available from {info['observation_start']} to {info['observation_end']}")
```

3. **Enable debug logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now connector will show detailed logs
fred = FREDConnector()
data = fred.get_series("GNPCA")
```

### Problem: Missing columns in DataFrame

**Symptoms:**
```python
KeyError: 'ESTAB'  # Expected column not found
```

**Solutions:**

1. **Check API documentation** for available fields
2. **Use `.columns` to see what's returned:**
```python
data = cbp.get_state_data(year=2021, state='44')
print("Available columns:", data.columns.tolist())
```

3. **Different years may have different fields:**
```python
# Older data might have different schema
data_2021 = cbp.get_state_data(year=2021, state='44')
data_2010 = cbp.get_state_data(year=2010, state='44')
print("2021 columns:", set(data_2021.columns))
print("2010 columns:", set(data_2010.columns))
```

### Problem: Data types are incorrect

**Symptoms:**
```python
TypeError: unsupported operand type(s) for /: 'str' and 'int'
```

**Solutions:**

1. **Convert data types explicitly:**
```python
data['ESTAB'] = pd.to_numeric(data['ESTAB'], errors='coerce')
data['EMP'] = pd.to_numeric(data['EMP'], errors='coerce')
```

2. **Check for missing values:**
```python
print(data.isnull().sum())
data = data.dropna(subset=['ESTAB', 'EMP'])
```

---

## Performance Problems

### Problem: Slow data retrieval

**Symptoms:**
- Requests taking >30 seconds
- Repeated API calls for same data

**Solutions:**

1. **Enable caching:**
```python
from krl_data_connectors import FREDConnector

fred = FREDConnector(
    cache_dir="/tmp/fred_cache",
    cache_ttl=86400  # 24 hours
)

# First call: hits API (~5 seconds)
data1 = fred.get_series("GNPCA")

# Second call: hits cache (~0.1 seconds)
data2 = fred.get_series("GNPCA")

# Check cache performance
stats = fred.cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.1f}%")
```

2. **Use batch requests when available:**
```python
# BLS supports batch requests (up to 50 series)
bls = BLSConnector()
data = bls.get_series(
    series_ids=['LASST060000000000003', 'LASST440000000000003'],
    start_year=2020,
    end_year=2023
)
```

3. **Filter data at API level:**
```python
# Get only specific columns/rows
cbp = CountyBusinessPatternsConnector()
data = cbp.get_state_data(
    year=2021,
    state='44',
    naics='44',  # Only retail trade
    get='NAME,NAICS2017,ESTAB,EMP'  # Only these columns
)
```

### Problem: High memory usage

**Symptoms:**
- Process uses >2GB RAM
- Out of memory errors

**Solutions:**

1. **Process data in chunks:**
```python
# Instead of loading all years at once
years = range(2010, 2023)
for year in years:
    data = cbp.get_state_data(year=year, state='44')
    # Process and save
    data.to_csv(f"cbp_{year}.csv")
    del data  # Free memory
```

2. **Use categorical data types:**
```python
data['NAICS2017'] = data['NAICS2017'].astype('category')
data['NAME'] = data['NAME'].astype('category')
```

3. **Select specific columns:**
```python
# Don't load unnecessary columns
data = data[['NAICS2017', 'ESTAB', 'EMP', 'PAYANN']]
```

---

## Caching Issues

### Problem: Stale cached data

**Symptoms:**
- Data hasn't updated despite API changes
- Getting old data when expecting new

**Solutions:**

1. **Clear cache:**
```python
fred = FREDConnector()
fred.cache.clear()
```

2. **Reduce cache TTL:**
```python
# Set shorter cache expiration
fred = FREDConnector(cache_ttl=3600)  # 1 hour instead of 24
```

3. **Disable cache for specific requests:**
```python
# Temporarily bypass cache
fred.cache.enabled = False
fresh_data = fred.get_series("GNPCA")
fred.cache.enabled = True
```

### Problem: Cache directory permission denied

**Symptoms:**
```python
PermissionError: [Errno 13] Permission denied: '/tmp/fred_cache'
```

**Solutions:**

1. **Use user-writable directory:**
```python
import os
from pathlib import Path

cache_dir = Path.home() / ".krl_cache"
fred = FREDConnector(cache_dir=str(cache_dir))
```

2. **Fix permissions:**
```bash
chmod 755 /tmp/fred_cache
```

---

## Platform-Specific Issues

### macOS: Certificate Issues

**Problem:**
```python
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solution:**
```bash
# Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command

# Or update certifi
pip install --upgrade certifi
```

### Windows: Path Issues

**Problem:**
```python
FileNotFoundError: [Errno 2] No such file or directory: '~/.krl/apikeys'
```

**Solution:**
```python
# Use full path on Windows
from pathlib import Path
config_path = Path.home() / ".krl" / "apikeys"
```

### Linux: Missing System Dependencies

**Problem:**
```bash
ImportError: libssl.so.1.1: cannot open shared object file
```

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install libssl-dev

# CentOS/RHEL
sudo yum install openssl-devel
```

---

## Getting Help

If you're still experiencing issues:

1. **Check the logs:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Search existing issues:**
   - GitHub Issues: https://github.com/KR-Labs/krl-data-connectors/issues

3. **Create a new issue:**
   - Use our bug report template
   - Include: Python version, OS, error messages, code to reproduce

4. **Community support:**
   - Discussions: https://github.com/KR-Labs/krl-data-connectors/discussions
   - Email: support@krlabs.dev

---

## Quick Diagnostic Script

Run this to check your environment:

```python
import sys
import platform
import os

print("=== KRL Data Connectors Diagnostics ===")
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.machine()}")

try:
    import krl_data_connectors
    print(f"KRL Data Connectors: {krl_data_connectors.__version__}")
except ImportError as e:
    print(f"KRL Data Connectors: NOT INSTALLED ({e})")

# Check API keys
keys = {
    'FRED_API_KEY': os.getenv('FRED_API_KEY'),
    'BEA_API_KEY': os.getenv('BEA_API_KEY'),
    'BLS_API_KEY': os.getenv('BLS_API_KEY'),
    'CENSUS_API_KEY': os.getenv('CENSUS_API_KEY'),
}

print("\n=== API Keys ===")
for key, value in keys.items():
    status = " SET" if value else " NOT SET"
    print(f"{key}: {status}")

# Check network
import requests
print("\n=== Network Connectivity ===")
endpoints = {
    'FRED': 'https://api.stlouisfed.org',
    'Census': 'https://api.census.gov',
    'BLS': 'https://api.bls.gov',
    'BEA': 'https://apps.bea.gov',
}

for name, url in endpoints.items():
    try:
        r = requests.get(url, timeout=5)
        print(f"{name}:  REACHABLE (status {r.status_code})")
    except Exception as e:
        print(f"{name}:  UNREACHABLE ({e})")

print("\n=== Diagnostics Complete ===")
```

---

**Last Updated:** October 20, 2025  
**Version:** 1.0.0
