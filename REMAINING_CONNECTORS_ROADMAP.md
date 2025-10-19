# KRL Data Connectors - Remaining Implementation Roadmap

**Created**: October 19, 2025  
**Status**: 6/40 connectors complete (15%)  
**Target Completion**: Week 16 (per KRL_DEVELOPMENT_TODO.md)

---

## 📊 Current Status

### ✅ Completed Connectors (6/40)

| Connector | Module | API Key Required | Status | Tests | Examples |
|-----------|--------|------------------|--------|-------|----------|
| **BEA** | `bea_connector.py` | ✅ Yes | ✅ Complete | ✅ Yes | ✅ Yes |
| **BLS** | `bls_connector.py` | ✅ Yes | ✅ Complete | ✅ Yes | ✅ Yes |
| **CBP** | `cbp_connector.py` | ✅ Yes | ✅ Complete | ✅ Yes | ✅ Yes |
| **Census ACS** | `census_connector.py` | ✅ Yes | ✅ Complete | ✅ Yes | ✅ No |
| **FRED** | `fred_connector.py` | ✅ Yes | ✅ Complete | ✅ Yes | ✅ Yes |
| **LEHD** | `lehd_connector.py` | ❌ No | ✅ Complete | ✅ Yes | ✅ Yes |

**Achievements:**
- ✅ Portable configuration system implemented
- ✅ 137/137 tests passing
- ✅ Security audit: 100/100
- ✅ Public repository published
- ✅ 6 example notebooks with portable config

---

## 🎯 Remaining Connectors (34/40)

### Week 12: Health & Environment (7 connectors)

#### 🏥 Health Data Connectors (3)

**1. CDC WONDER Connector** ⏳ HIGH PRIORITY
- **Purpose**: Mortality, natality, cancer, and population data
- **API**: Public API, no key required
- **Domains**: D04 (Health), D25 (Food & Nutrition), D28 (Mental Health)
- **Data Types**: Mortality rates, life expectancy, cause of death
- **Geographic Levels**: National, state, county
- **Implementation Priority**: HIGH
- **Estimated Time**: 8-12 hours

```python
# Proposed interface
from krl_connectors.health import CDCWonderConnector

cdc = CDCWonderConnector()
mortality_data = cdc.get_mortality_data(
    year=2022,
    geo_level='county',
    cause='cardiovascular'
)
```

**2. HRSA Connector (Health Resources & Services Administration)** ⏳ MEDIUM PRIORITY
- **Purpose**: Healthcare provider locations, health professional shortage areas
- **API**: Open data, no key required
- **Domains**: D04 (Health)
- **Data Types**: Hospital locations, HPSA designations, provider counts
- **Geographic Levels**: County, ZIP code
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 6-8 hours

**3. County Health Rankings Connector** ⏳ MEDIUM PRIORITY
- **Purpose**: Comprehensive county health metrics
- **API**: CSV downloads, no key required
- **Domains**: D04 (Health), D24 (Environmental Justice)
- **Data Types**: Health outcomes, clinical care, social factors
- **Geographic Levels**: County
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 4-6 hours

#### 🌍 Environmental Connectors (4)

**4. EPA EJScreen Connector** ⏳ HIGH PRIORITY
- **Purpose**: Environmental justice screening and mapping
- **API**: REST API, no key required
- **Domains**: D12 (Environmental Economics), D24 (Environmental Justice)
- **Data Types**: Pollution exposure, demographic indicators, EJ indexes
- **Geographic Levels**: Block group, tract, county
- **Implementation Priority**: HIGH
- **Estimated Time**: 10-14 hours

```python
# Proposed interface
from krl_connectors.environment import EJScreenConnector

ej = EJScreenConnector()
environmental_data = ej.get_environmental_indicators(
    geo_level='tract',
    state='CA',
    year=2023
)
```

**5. EPA Air Quality Connector** ⏳ MEDIUM PRIORITY
- **Purpose**: Air quality index, pollutant concentrations
- **API**: AirNow API, key required
- **Domains**: D12 (Environmental Economics), D04 (Health)
- **Data Types**: AQI, PM2.5, ozone, CO, NO2
- **Geographic Levels**: Monitoring stations, ZIP code
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 6-8 hours

**6. EPA Superfund Sites Connector** ⏳ LOW PRIORITY
- **Purpose**: Hazardous waste site locations and status
- **API**: Open data, no key required
- **Domains**: D24 (Environmental Justice)
- **Implementation Priority**: LOW
- **Estimated Time**: 4-6 hours

**7. NOAA Climate Data Connector** ⏳ LOW PRIORITY
- **Purpose**: Temperature, precipitation, climate normals
- **API**: NOAA NCDC API, key required
- **Domains**: D12 (Environmental Economics), D17 (Food & Agriculture)
- **Implementation Priority**: LOW
- **Estimated Time**: 8-10 hours

---

### Week 13: Housing, Crime & Education (9 connectors)

#### 🏠 Housing Connectors (2)

**8. Zillow Open Data Connector** ⏳ HIGH PRIORITY
- **Purpose**: Housing prices, rents, inventory, forecasts
- **API**: CSV downloads, no key required
- **Domains**: D05 (Housing), D27 (Housing Affordability)
- **Data Types**: ZHVI, Zillow Rent Index, home values, forecasts
- **Geographic Levels**: National, metro, county, ZIP, neighborhood
- **Implementation Priority**: HIGH
- **Estimated Time**: 6-8 hours

```python
# Proposed interface
from krl_connectors.housing import ZillowConnector

zillow = ZillowConnector()
home_values = zillow.get_home_values(
    geo_level='county',
    metric='ZHVI',
    frequency='monthly'
)
```

**9. HUD Fair Market Rents Connector** ⏳ MEDIUM PRIORITY
- **Purpose**: HUD Fair Market Rents, income limits
- **API**: HUD USER API, no key required
- **Domains**: D05 (Housing), D18 (Social Services), D27 (Housing Affordability)
- **Data Types**: FMR, income limits by household size
- **Geographic Levels**: Metro area, county
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 4-6 hours

#### 🚔 Crime & Safety Connectors (2)

**10. FBI UCR Connector (Uniform Crime Reporting)** ⏳ HIGH PRIORITY
- **Purpose**: Crime statistics, arrest data, law enforcement
- **API**: FBI Crime Data API, no key required
- **Domains**: D13 (Crime & Public Safety), D26 (Public Safety)
- **Data Types**: Violent crime, property crime, arrests by type
- **Geographic Levels**: National, state, agency
- **Implementation Priority**: HIGH
- **Estimated Time**: 10-12 hours

```python
# Proposed interface
from krl_connectors.crime import FBIUCRConnector

fbi = FBIUCRConnector()
crime_data = fbi.get_crime_statistics(
    state='CA',
    year=2022,
    crime_type='violent'
)
```

**11. Gun Violence Archive Connector** ⏳ LOW PRIORITY
- **Purpose**: Gun violence incidents, mass shootings
- **API**: Web scraping or CSV
- **Domains**: D13 (Crime & Public Safety), D26 (Public Safety)
- **Implementation Priority**: LOW
- **Estimated Time**: 6-8 hours

#### 🎓 Education Connectors (5)

**12. NCES (National Center for Education Statistics) Connector** ⏳ HIGH PRIORITY
- **Purpose**: School demographics, performance, financing
- **API**: Multiple NCES APIs, no key required
- **Domains**: D03 (Education)
- **Data Types**: Enrollment, test scores, graduation rates, spending
- **Geographic Levels**: National, state, district, school
- **Implementation Priority**: HIGH
- **Estimated Time**: 12-16 hours

```python
# Proposed interface
from krl_connectors.education import NCESConnector

nces = NCESConnector()
school_data = nces.get_school_demographics(
    state='MA',
    year=2023
)
```

**13. College Scorecard Connector** ⏳ MEDIUM PRIORITY
- **Purpose**: College costs, outcomes, debt
- **API**: College Scorecard API, key required
- **Domains**: D03 (Education), D10 (Social Mobility)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 6-8 hours

**14. IPEDS Connector (Integrated Postsecondary Education)** ⏳ MEDIUM PRIORITY
- **Purpose**: Higher education institutional data
- **API**: NCES IPEDS API
- **Domains**: D03 (Education)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 8-10 hours

**15. Stanford Education Data Archive** ⏳ LOW PRIORITY
- **Purpose**: K-12 test score data
- **API**: CSV downloads
- **Domains**: D03 (Education), D06 (Inequality)
- **Implementation Priority**: LOW
- **Estimated Time**: 4-6 hours

**16. EdGap Connector** ⏳ LOW PRIORITY
- **Purpose**: Education opportunity gaps
- **API**: CSV downloads
- **Domains**: D03 (Education), D06 (Inequality)
- **Implementation Priority**: LOW
- **Estimated Time**: 4-6 hours

---

### Week 14-15: Food, International & Specialty (18 connectors)

#### 🌾 Food & Agriculture Connectors (4)

**17. USDA Food Environment Atlas Connector** ⏳ HIGH PRIORITY
- **Purpose**: Food access, food insecurity, local food systems
- **API**: CSV downloads, no key required
- **Domains**: D17 (Food & Agriculture), D25 (Food & Nutrition)
- **Data Types**: Food deserts, SNAP participation, food insecurity
- **Geographic Levels**: County
- **Implementation Priority**: HIGH
- **Estimated Time**: 6-8 hours

```python
# Proposed interface
from krl_connectors.food import USDAFoodAtlasConnector

usda = USDAFoodAtlasConnector()
food_access = usda.get_food_access_indicators(
    state='MS',
    year=2020
)
```

**18. USDA NASS Connector (National Agricultural Statistics)** ⏳ MEDIUM PRIORITY
- **Purpose**: Crop production, livestock, farm economics
- **API**: NASS QuickStats API, key required
- **Domains**: D17 (Food & Agriculture)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 8-10 hours

**19. USDA SNAP Connector** ⏳ MEDIUM PRIORITY
- **Purpose**: SNAP participation, benefits
- **API**: USDA FNS data
- **Domains**: D17 (Food & Agriculture), D18 (Social Services), D25 (Food & Nutrition)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 4-6 hours

**20. Feeding America Connector** ⏳ LOW PRIORITY
- **Purpose**: Food insecurity county-level estimates
- **API**: MAP the Meal Gap data
- **Domains**: D25 (Food & Nutrition)
- **Implementation Priority**: LOW
- **Estimated Time**: 4-6 hours

#### 🌐 International Data Connectors (6)

**21. OECD Connector** ⏳ HIGH PRIORITY
- **Purpose**: Cross-country economic, social, environmental indicators
- **API**: OECD.Stat API, no key required
- **Domains**: D30 (Subjective Well-Being), D31 (Civic Trust), D32 (Freedom), D33 (Gender)
- **Data Types**: Better Life Index, inequality, governance, gender gaps
- **Geographic Levels**: Country
- **Implementation Priority**: HIGH
- **Estimated Time**: 10-14 hours

```python
# Proposed interface
from krl_connectors.global_data import OECDConnector

oecd = OECDConnector()
wellbeing = oecd.get_better_life_index(
    countries=['USA', 'CAN', 'MEX'],
    year=2023
)
```

**22. World Bank Connector** ⏳ HIGH PRIORITY
- **Purpose**: Global development indicators
- **API**: World Bank API, no key required
- **Domains**: D30-D33 (Subjective Well-Being, Trust, Freedom, Gender)
- **Implementation Priority**: HIGH
- **Estimated Time**: 8-10 hours

**23. WHO Connector (World Health Organization)** ⏳ MEDIUM PRIORITY
- **Purpose**: Global health indicators
- **API**: WHO GHO API, no key required
- **Domains**: D04 (Health), D30 (Well-Being)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 6-8 hours

**24. WEF Connector (World Economic Forum)** ⏳ MEDIUM PRIORITY
- **Purpose**: Global Competitiveness, Gender Gap reports
- **API**: CSV downloads
- **Domains**: D33 (Gender Equality)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 4-6 hours

**25. Freedom House Connector** ⏳ MEDIUM PRIORITY
- **Purpose**: Freedom in the World, civil liberties
- **API**: CSV downloads
- **Domains**: D32 (Freedom & Civil Liberties)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 4-6 hours

**26. UN Data Connector** ⏳ LOW PRIORITY
- **Purpose**: UN statistical databases
- **API**: UNdata API
- **Domains**: D30-D33
- **Implementation Priority**: LOW
- **Estimated Time**: 8-10 hours

#### 🎭 Culture & Civic Connectors (5)

**27. IRS 990 Connector (Nonprofit Data)** ⏳ HIGH PRIORITY
- **Purpose**: Nonprofit financial data, Form 990
- **API**: IRS Tax Exempt Organization Search, no key required
- **Domains**: D11 (Cultural Economics), D22 (Cultural Consumption), D21 (Social Capital)
- **Data Types**: Revenue, expenses, programs, governance
- **Geographic Levels**: Organization-level (geocoded)
- **Implementation Priority**: HIGH
- **Estimated Time**: 10-12 hours

```python
# Proposed interface
from krl_connectors.culture import IRS990Connector

irs = IRS990Connector()
nonprofit_data = irs.get_nonprofit_financials(
    state='CA',
    ntee_code='A',  # Arts, culture
    year=2022
)
```

**28. NEA Connector (National Endowment for the Arts)** ⏳ MEDIUM PRIORITY
- **Purpose**: Arts participation, cultural engagement
- **API**: NEA data downloads
- **Domains**: D11 (Cultural Economics), D22 (Cultural Consumption)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 4-6 hours

**29. IMLS Connector (Institute of Museum and Library Services)** ⏳ MEDIUM PRIORITY
- **Purpose**: Library and museum data
- **API**: IMLS data files
- **Domains**: D11 (Cultural Economics), D22 (Cultural Consumption)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 4-6 hours

**30. MIT Election Lab Connector** ⏳ MEDIUM PRIORITY
- **Purpose**: Election results, turnout, voting laws
- **API**: CSV downloads, no key required
- **Domains**: D19 (Civic & Political), D31 (Civic Trust)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 6-8 hours

**31. Volunteering in America Connector** ⏳ LOW PRIORITY
- **Purpose**: Volunteer rates, civic engagement
- **API**: AmeriCorps data
- **Domains**: D21 (Social Capital), D19 (Civic)
- **Implementation Priority**: LOW
- **Estimated Time**: 4-6 hours

#### 🚗 Transportation & Infrastructure (3)

**32. NHTS Connector (National Household Travel Survey)** ⏳ MEDIUM PRIORITY
- **Purpose**: Travel behavior, commuting patterns
- **API**: CSV downloads
- **Domains**: D14 (Transportation), D23 (Transport Equity)
- **Implementation Priority**: MEDIUM
- **Estimated Time**: 6-8 hours

**33. FTA Connector (Federal Transit Administration)** ⏳ LOW PRIORITY
- **Purpose**: Public transit ridership, service data
- **API**: National Transit Database
- **Domains**: D14 (Transportation), D23 (Transport Equity)
- **Implementation Priority**: LOW
- **Estimated Time**: 6-8 hours

**34. DOT Fatal Accident Connector** ⏳ LOW PRIORITY
- **Purpose**: Traffic fatality data
- **API**: FARS API
- **Domains**: D14 (Transportation), D26 (Public Safety)
- **Implementation Priority**: LOW
- **Estimated Time**: 4-6 hours

---

## 🗓️ Implementation Schedule

### Week 12: Health & Environment (Oct 21-27, 2025)

**Monday-Tuesday: CDC WONDER** (12 hours)
- Day 1: Connector implementation + basic tests
- Day 2: Advanced features + example notebook

**Wednesday: HRSA** (8 hours)
- Connector implementation + tests + example

**Thursday: County Health Rankings** (6 hours)
- Connector implementation + tests

**Friday: EPA EJScreen** (14 hours across 2 days)
- Day 1: Core implementation
- Carry over to Monday

**Target**: 4-5 connectors complete

---

### Week 13: Housing, Crime & Education (Oct 28 - Nov 3, 2025)

**Monday: EPA EJScreen (continued)** (6 hours)
- Complete tests + example notebook

**Tuesday: Zillow** (8 hours)
- Connector implementation + tests

**Wednesday: HUD FMR** (6 hours)
- Connector implementation + tests

**Thursday-Friday: FBI UCR** (12 hours)
- Complex API, multiple endpoints
- Tests + example notebook

**Monday (Week 14): NCES** (16 hours across 2 days)
- Most complex education connector
- Multiple data products

**Target**: 4-5 connectors complete

---

### Week 14-15: Food, International & Specialty (Nov 4-17, 2025)

**HIGH PRIORITY (Complete first):**
- USDA Food Atlas (8 hours)
- OECD (14 hours)
- World Bank (10 hours)
- IRS 990 (12 hours)

**MEDIUM PRIORITY:**
- USDA NASS (10 hours)
- WHO (8 hours)
- WEF (6 hours)
- Freedom House (6 hours)
- NEA (6 hours)
- IMLS (6 hours)
- MIT Election Lab (8 hours)
- NHTS (8 hours)

**LOW PRIORITY (if time permits):**
- Remaining specialty connectors

**Target**: 10-15 connectors complete

---

## 🎯 Priority Matrix

### Immediate (Week 12) - 5 connectors
1. **CDC WONDER** - Critical for health domains
2. **EPA EJScreen** - Essential for environmental justice
3. **HRSA** - Healthcare access analysis
4. **County Health Rankings** - Comprehensive health metrics
5. **EPA Air Quality** - Pollution data

### High Priority (Week 13) - 4 connectors
6. **Zillow** - Housing market analysis
7. **FBI UCR** - Crime data
8. **NCES** - Education system data
9. **HUD FMR** - Rental market

### Medium Priority (Week 14-15) - 12 connectors
10-21: USDA connectors, International data, Culture & civic

### Low Priority (As time allows) - 13 connectors
22-34: Specialty, niche data sources

---

## 📝 Implementation Template

For each connector, follow this workflow:

### 1. Research Phase (30-60 min)
- [ ] Review API documentation
- [ ] Test API endpoints manually
- [ ] Document data schema
- [ ] Identify rate limits and restrictions
- [ ] Check if API key is required

### 2. Implementation Phase (2-6 hours)
- [ ] Create connector class inheriting from `BaseConnector`
- [ ] Implement authentication (if required)
- [ ] Implement main data fetching methods
- [ ] Add error handling and retries
- [ ] Add logging
- [ ] Implement caching
- [ ] Add docstrings

### 3. Testing Phase (1-2 hours)
- [ ] Write unit tests for each method
- [ ] Test error conditions
- [ ] Test with mock data
- [ ] Test rate limiting
- [ ] Aim for 80%+ coverage

### 4. Documentation Phase (1-2 hours)
- [ ] Create quickstart notebook
- [ ] Add usage examples
- [ ] Document domain mappings
- [ ] Update README

### 5. Integration Phase (30 min)
- [ ] Update `__init__.py` exports
- [ ] Add to connector registry
- [ ] Update main documentation
- [ ] Commit and push

---

## 🚀 Quick Start for Next Connector

```bash
# Create new connector file
cd /Users/bcdelo/KR-Labs/krl-data-connectors
touch src/krl_data_connectors/health/cdc_connector.py
touch tests/unit/test_cdc_connector.py
touch examples/cdc_quickstart.ipynb

# Start implementation
code src/krl_data_connectors/health/cdc_connector.py
```

---

## 📊 Success Metrics

- **Quality**: 80%+ test coverage per connector
- **Security**: 100/100 security audit score maintained
- **Documentation**: Every connector has example notebook
- **Performance**: < 1 second for cached queries
- **Portability**: All connectors use portable configuration
- **Completeness**: 40/40 connectors by Week 16

---

## 🎓 Learning Resources

- **API Best Practices**: [API Design Patterns](https://www.api-design-patterns.com/)
- **Python Testing**: [pytest documentation](https://docs.pytest.org/)
- **Data Connectors**: Review existing 6 connectors as templates
- **Rate Limiting**: [ratelimit library](https://pypi.org/project/ratelimit/)

---

**Next Action**: Start with CDC WONDER connector (highest priority, no API key required, immediate impact on 3 domains)

**Command to begin**:
```bash
cd /Users/bcdelo/KR-Labs/krl-data-connectors
mkdir -p src/krl_data_connectors/health
touch src/krl_data_connectors/health/__init__.py
```
