# KRL Data Connectors - Comprehensive Tutorial

This notebook demonstrates how to use all the data connectors in the KRL Data Connectors package.

## Setup

First, install the package and import the connectors:

```python
# Install the package (if not already installed)
# pip install krl-data-connectors

# Import connectors
from krl_data_connectors import (
    CensusConnector,
    LEHDConnector,
    CountyBusinessPatternsConnector,
    FREDConnector,
    BLSConnector,
    BEAConnector
)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set up plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
```

## 1. Census American Community Survey (ACS) Connector

The Census ACS connector provides access to demographic and socioeconomic data.

```python
# Initialize the connector
census = CensusConnector()

# Get population and median income for California counties
variables = ['B01003_001E', 'B19013_001E']  # Total population, Median household income
ca_data = census.get_acs_data(
    variables=variables,
    geography='county',
    state='06',  # California
    year=2021
)

print("California Counties - Population and Income:")
print(ca_data.head())

# Visualize
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

# Top 10 counties by population
top_pop = ca_data.nlargest(10, 'B01003_001E')
ax1.barh(top_pop['NAME'], top_pop['B01003_001E'])
ax1.set_xlabel('Population')
ax1.set_title('Top 10 California Counties by Population')

# Top 10 counties by median income
top_income = ca_data.nlargest(10, 'B19013_001E')
ax2.barh(top_income['NAME'], top_income['B19013_001E'])
ax2.set_xlabel('Median Household Income ($)')
ax2.set_title('Top 10 California Counties by Median Income')

plt.tight_layout()
plt.show()
```

## 2. LEHD Origin-Destination Employment Statistics

The LEHD connector provides detailed employment flow data showing where people live and work.

```python
# Initialize the connector
lehd = LEHDConnector()

# Get origin-destination data for California in 2019
# This shows worker flows between home and work locations
od_data = lehd.get_od_data(
    state='ca',
    year=2019,
    part='main',
    job_type='JT00',  # All jobs
    segment='S000'     # All workers
)

print("Sample OD Data:")
print(od_data.head())

# Aggregate to county level for visualization
county_work = lehd.aggregate_to_county(od_data, geocode_col='w_geocode')
county_home = lehd.aggregate_to_county(od_data, geocode_col='h_geocode')

print("\nTop 5 Counties by Workplace Jobs:")
print(county_work.nlargest(5, 'S000')[['w_county', 'S000']])

# Get Residence Area Characteristics (where workers live)
rac_data = lehd.get_rac_data(
    state='ca',
    year=2019,
    segment='SE03'  # High earners ($3333+ per month)
)

print("\nHigh Earner Residential Distribution (sample):")
print(rac_data.head())
```

## 3. County Business Patterns

The CBP connector provides establishment and employment data by industry and geography.

```python
# Initialize the connector
cbp = CountyBusinessPatternsConnector()

# Get county-level data for all counties in 2021
county_data = cbp.get_county_data(
    year=2021,
    variables=['ESTAB', 'EMP', 'PAYANN'],
)

print("Sample County Business Patterns:")
print(county_data.head())

# Get state totals
state_data = cbp.get_state_data(year=2021)

print("\nTop 10 States by Establishments:")
top_states = state_data.nlargest(10, 'ESTAB')
print(top_states[['NAME', 'ESTAB', 'EMP', 'PAYANN']])

# Visualize
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

ax1.barh(top_states['NAME'], top_states['ESTAB'].astype(float))
ax1.set_xlabel('Number of Establishments')
ax1.set_title('Top 10 States by Establishments (2021)')

ax2.barh(top_states['NAME'], top_states['EMP'].astype(float))
ax2.set_xlabel('Employment')
ax2.set_title('Top 10 States by Employment (2021)')

plt.tight_layout()
plt.show()

# Get NAICS sector totals
naics_totals = cbp.get_naics_totals(county_data, level=2)  # 2-digit sectors
print("\nEmployment by NAICS Sector:")
print(naics_totals.head())
```

## 4. Federal Reserve Economic Data (FRED)

The FRED connector provides access to 800,000+ economic time series.

```python
# Initialize the connector (requires API key)
fred = FREDConnector(api_key='your_fred_api_key')

# Get GDP data
gdp = fred.get_series('GDP', start_date='2015-01-01', end_date='2023-12-31')

# Get unemployment rate
unemployment = fred.get_series('UNRATE', start_date='2015-01-01', end_date='2023-12-31')

# Get CPI (inflation indicator)
cpi = fred.get_series('CPIAUCSL', start_date='2015-01-01', end_date='2023-12-31')

# Plot economic indicators
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

gdp.plot(x='date', y='value', ax=ax1, title='US GDP (Billions of Dollars)', legend=False)
ax1.set_ylabel('Billions $')

unemployment.plot(x='date', y='value', ax=ax2, title='US Unemployment Rate (%)', legend=False, color='red')
ax2.set_ylabel('Percent')

cpi.plot(x='date', y='value', ax=ax3, title='Consumer Price Index (All Items)', legend=False, color='green')
ax3.set_ylabel('Index')

plt.tight_layout()
plt.show()

# Search for series
search_results = fred.search_series('housing starts', limit=5)
print("\nSearch Results for 'housing starts':")
print(search_results[['id', 'title', 'frequency']])

# Get series information
gdp_info = fred.get_series_info('GDP')
print("\nGDP Series Information:")
print(f"Title: {gdp_info.get('title')}")
print(f"Units: {gdp_info.get('units')}")
print(f"Frequency: {gdp_info.get('frequency')}")
print(f"Last Updated: {gdp_info.get('last_updated')}")
```

## 5. Bureau of Labor Statistics (BLS)

The BLS connector provides employment, unemployment, and price index data.

```python
# Initialize the connector (API key optional but recommended)
bls = BLSConnector(api_key='your_bls_api_key')

# Get national unemployment rate
unemployment = bls.get_unemployment_rate(start_year=2019, end_year=2023)

print("National Unemployment Rate:")
print(unemployment[['year', 'period', 'periodName', 'value', 'date']].head(10))

# Get Consumer Price Index (all items)
cpi = bls.get_cpi(item='SA0', start_year=2019, end_year=2023)

print("\nConsumer Price Index (All Items):")
print(cpi[['year', 'period', 'periodName', 'value', 'date']].head(10))

# Get multiple series at once
series_ids = [
    'LNS14000000',  # Unemployment rate
    'LNS12000000',  # Employment level
    'LNS11000000',  # Labor force
]
multi_data = bls.get_multiple_series(series_ids, start_year=2020, end_year=2023)

print("\nMultiple Series Retrieved:")
for series_id, df in multi_data.items():
    print(f"{series_id}: {len(df)} observations")

# Visualize unemployment and CPI trends
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

unemployment_plot = unemployment.dropna(subset=['date', 'value'])
ax1.plot(unemployment_plot['date'], unemployment_plot['value'])
ax1.set_title('US Unemployment Rate (2019-2023)')
ax1.set_ylabel('Percent')
ax1.grid(True)

cpi_plot = cpi.dropna(subset=['date', 'value'])
ax2.plot(cpi_plot['date'], cpi_plot['value'], color='orange')
ax2.set_title('Consumer Price Index (2019-2023)')
ax2.set_ylabel('Index')
ax2.grid(True)

plt.tight_layout()
plt.show()
```

## 6. Bureau of Economic Analysis (BEA)

The BEA connector provides GDP, personal income, and other economic accounts data.

```python
# Initialize the connector (requires API key)
bea = BEAConnector(api_key='your_bea_api_key')

# Get available datasets
datasets = bea.get_dataset_list()
print("Available BEA Datasets:")
print(datasets[['DatasetName', 'DatasetDescription']].head())

# Get GDP data (NIPA Table 1.1.1)
gdp_data = bea.get_nipa_data(
    table_name='T10101',
    frequency='Q',  # Quarterly
    year='2020,2021,2022,2023'
)

print("\nGDP Data (Quarterly):")
print(gdp_data.head())

# Get state personal income
state_income = bea.get_regional_data(
    table_name='SAINC1',  # Personal income summary
    line_code='1',        # Personal income
    geo_fips='STATE',
    year='LAST5'
)

print("\nState Personal Income:")
print(state_income.head())

# Get GDP by industry
gdp_industry = bea.get_gdp_by_industry(
    industry='ALL',
    year='2020,2021,2022',
    frequency='A'
)

print("\nGDP by Industry:")
print(gdp_industry.head())

# Visualize top states by personal income (most recent year)
latest_year = state_income['TimePeriod'].max()
latest_data = state_income[state_income['TimePeriod'] == latest_year]
top_10 = latest_data.nlargest(10, 'DataValue')

plt.figure(figsize=(12, 6))
plt.barh(top_10['GeoName'], top_10['DataValue'])
plt.xlabel('Personal Income (Millions $)')
plt.title(f'Top 10 States by Personal Income ({latest_year})')
plt.tight_layout()
plt.show()
```

## 7. Combining Multiple Data Sources

Here's an example combining multiple connectors for comprehensive analysis:

```python
# Example: Analyze economic conditions for a specific state (California)

# 1. Get demographic data from Census
census = CensusConnector()
ca_demo = census.get_acs_data(
    variables=['B01003_001E', 'B19013_001E'],  # Population, Median income
    geography='state',
    state='06',
    year=2021
)

# 2. Get employment data from BLS (California unemployment)
bls = BLSConnector(api_key='your_bls_api_key')
ca_unemployment = bls.get_unemployment_rate(area_code='06', start_year=2019, end_year=2023)

# 3. Get state GDP from BEA
bea = BEAConnector(api_key='your_bea_api_key')
ca_gdp = bea.get_regional_data(
    table_name='SAGDP2',  # GDP by state
    line_code='1',
    geo_fips='06',  # California
    year='LAST5'
)

# 4. Get business patterns from CBP
cbp = CountyBusinessPatternsConnector()
ca_business = cbp.get_state_data(year=2021, state='06')

# Create a comprehensive report
print("California Economic Profile")
print("=" * 50)
print(f"\nPopulation (2021): {ca_demo['B01003_001E'].iloc[0]:,.0f}")
print(f"Median Household Income (2021): ${ca_demo['B19013_001E'].iloc[0]:,.0f}")
print(f"\nEstablishments (2021): {int(ca_business['ESTAB'].iloc[0]):,}")
print(f"Employment (2021): {int(ca_business['EMP'].iloc[0]):,}")
print(f"\nUnemployment Rate (Latest): {ca_unemployment['value'].iloc[-1]:.1f}%")
print(f"GDP (Latest): ${ca_gdp['DataValue'].iloc[-1]:,.0f}M")
```

## Best Practices

### 1. API Key Management

Store API keys securely:

```python
# Option 1: Environment variables
import os
fred_key = os.getenv('FRED_API_KEY')
bls_key = os.getenv('BLS_API_KEY')
bea_key = os.getenv('BEA_API_KEY')

# Option 2: Configuration file
from krl_data_connectors import BaseConnector
connector = BaseConnector()
config = connector.config
```

### 2. Caching

Enable caching to improve performance:

```python
# Specify a cache directory
fred = FREDConnector(api_key='your_key', cache_dir='/path/to/cache')
```

### 3. Error Handling

Always handle potential errors:

```python
try:
    data = fred.get_series('GDP')
except ValueError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Rate Limiting

Be aware of API rate limits:
- **FRED**: 1000 requests/day (no key), unlimited (with key)
- **BLS**: 25 queries/day (no key), 500 queries/day (with key)
- **Census**: 500 requests/day per IP
- **BEA**: No strict limit, but be respectful

### 5. Data Validation

Always validate data before analysis:

```python
# Check for missing values
print(f"Missing values: {data.isnull().sum()}")

# Check data types
print(data.dtypes)

# Check date ranges
print(f"Date range: {data['date'].min()} to {data['date'].max()}")
```

## Next Steps

- Explore the [API documentation](https://krl-data-connectors.readthedocs.io/)
- Check out specific connector tutorials for advanced features
- Join our community for support and updates

## Additional Resources

- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/)
- [Census API Documentation](https://www.census.gov/data/developers/guidance.html)
- [BLS API Documentation](https://www.bls.gov/developers/)
- [BEA API Documentation](https://apps.bea.gov/api/)
