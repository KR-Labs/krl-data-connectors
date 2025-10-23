---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] - 2025-10-21 - 100% COMPLETION MILESTONE

### Major Achievement
**All 40 connectors complete!** This release achieves 100% completion of the planned connector suite, providing comprehensive coverage across 14 domains with production-ready quality standards.

### Added

#### **Week 22-24 Final Connectors (October 21, 2025)** - COMPLETION MILESTONE
- **EIAConnector** - Energy Information Administration
  - Energy production, consumption, and prices
  - 66 tests, 81.50% coverage, 11 contract tests
- **USGSConnector** - U.S. Geological Survey
  - Earthquake data, water resources, land use
  - 55 tests, 82.16% coverage, 9 contract tests
- **SSAConnector** - Social Security Administration
  - Benefits data, retirement statistics
  - 64 tests, 81.52% coverage, 10 contract tests
- **ACFConnector** - Administration for Children and Families
  - Child welfare, family assistance programs
  - 62 tests, 80.19% coverage, 10 contract tests
- **VAConnector** - Department of Veterans Affairs
  - VA facilities, benefits, healthcare, disability ratings
  - 70 tests, 83.04% coverage, 11 contract tests
- **NSFConnector** - National Science Foundation
  - Research awards, grants, funding
  - 70 tests, 85.59% coverage, 11 contract tests
- **NIHConnector** - National Institutes of Health
  - Research projects, grants, publications, clinical trials
  - 66 tests, 87.33% coverage, 11 contract tests

#### **Week 19-21 Connectors (October 21, 2025)**
- **SECConnector** - Securities and Exchange Commission
  - Company filings (10-K, 10-Q, 8-K), insider trading
  - 64 tests, 82.31% coverage, 11 contract tests
- **TreasuryConnector** - U.S. Department of Treasury
  - Treasury rates, fiscal data, debt statistics
  - 62 tests, 80.62% coverage, 10 contract tests
- **FDICConnector** - Federal Deposit Insurance Corporation
  - Bank financial data, failed bank list
  - 68 tests, 82.11% coverage, 11 contract tests
- **FDAConnector** - Food and Drug Administration
  - Drug approvals, recalls, medical device data
  - 64 tests, 81.60% coverage, 11 contract tests
- **OSHAConnector** - Occupational Safety and Health Administration
  - Workplace inspections, violations, citations
  - 68 tests, 82.91% coverage, 11 contract tests
- **FAAConnector** - Federal Aviation Administration
  - Airport data, flight delays, aircraft registry
  - 62 tests, 81.03% coverage, 10 contract tests

#### **Week 16-18 Connectors (October 20, 2025)**
- **SuperfundConnector** - EPA Superfund Sites
  - Hazardous waste sites, cleanup status
  - 38 tests, 80.37% coverage
- **WaterQualityConnector** - EPA Water Quality Data
  - Drinking water quality, violations
  - 42 tests, 81.85% coverage
- **NOAAClimateConnector** - NOAA Climate Data
  - Weather observations, climate normals
  - 40 tests, 76.04% coverage
- **IPEDSConnector** - Integrated Postsecondary Education Data System
  - Comprehensive college data
  - 44 tests, 84.19% coverage
- **BureauOfJusticeConnector** - Bureau of Justice Statistics
  - Criminal justice statistics
  - 34 tests, 85.51% coverage
- **VictimsOfCrimeConnector** - Office for Victims of Crime
  - Crime victimization data
  - 34 tests, 82.78% coverage

#### **Week 14-15 Connectors (October 20, 2025)**
- **USDAFoodAtlasConnector** - USDA Food Environment Atlas
- **USDANASSConnector** - USDA National Agricultural Statistics
- **OECDConnector** - OECD Better Life Index
- **WorldBankConnector** - World Bank Development Indicators
- **CollegeScorecardConnector** - College Scorecard
- **CDCWonderConnector** - CDC WONDER Database
- **CountyHealthRankingsConnector** - County Health Rankings

### Summary Statistics

**Total Connectors**: 40 (100% complete)
**Total Tests**: 2,800+ comprehensive tests
**Contract Tests**: 266 Phase 4 Layer 8 tests (100% passing)
**Average Coverage**: 82.5% (exceeds 80% target)
**Test Pass Rate**: 100% across all connectors

### Domain Coverage (14 domains)
- Economic & Financial Data: 8 connectors
- Demographic & Labor Data: 3 connectors
- Health & Wellbeing Data: 5 connectors
- Environmental & Climate Data: 5 connectors
- Education Data: 3 connectors
- Housing & Urban Data: 2 connectors
- Agricultural Data: 2 connectors
- Crime & Justice Data: 3 connectors
- Energy Data: 1 connector
- Science & Research Data: 2 connectors
- Transportation Data: 1 connector
- Labor Safety Data: 1 connector
- Social Services Data: 2 connectors
- Veterans Services Data: 1 connector

### Infrastructure Improvements
- Updated package version to 0.3.0
- Comprehensive __init__.py with all 40 connectors
- Updated documentation across all domains
- Enhanced README with complete connector catalog
- Updated ROADMAP to reflect 100% completion

---

## [0.1.0] - 2025-10-20

### Added
- **Week 13 Housing, Crime, and Education Connectors (October 20, 2025)**:
  - Zillow Research Data Connector: ZHVI/ZRI housing market data, inventory metrics, sales data, geographic filtering
  - HUD Fair Market Rents Connector: FMR data by bedroom count, affordability calculations, income limits, YoY comparisons
  - FBI Uniform Crime Reporting Connector: Violent/property crime statistics, crime rates per capita, trend analysis
  - NCES Connector: School directory, enrollment demographics, performance metrics, district finances, per-pupil spending
- **Comprehensive Test Coverage**:
  - 36 Zillow connector tests (coverage TBD)
  - 34 HUD FMR connector tests (coverage TBD)
  - 42 FBI UCR connector tests (coverage TBD)
  - 48 NCES connector tests (coverage TBD)
  - Total: 400+ tests passing across 16 connectors
- **Quickstart Notebooks**:
  - examples/zillow_quickstart.ipynb - Housing market analysis with ZHVI/ZRI data
  - examples/hud_fmr_quickstart.ipynb - Affordability calculations and FMR comparisons
  - examples/fbi_ucr_quickstart.ipynb - Crime statistics and trend analysis
  - examples/nces_quickstart.ipynb - Education data queries and per-pupil spending
- **Week 12 Health & Environment Connectors (October 20, 2025)**:
  - HRSA Connector: Health Professional Shortage Areas (HPSA), Medically Underserved Areas/Populations (MUA/P), Health Centers (FQHC)
  - County Health Rankings Connector: 30+ county-level health measures, trend data 2010-present, all ranking categories
  - EPA Air Quality / AirNow Connector: Real-time AQI, forecasts, historical data, 6 pollutants, 2,500+ monitoring stations
- **Week 12 Test Coverage**:
  - 45 HRSA connector tests (90.51% coverage)
  - 35 County Health Rankings connector tests
  - 49 Air Quality connector tests (83.82% coverage)
- **Week 12 Quickstart Notebooks**:
  - examples/hrsa_quickstart.ipynb - HPSA analysis and health center mapping
  - examples/chr_quickstart.ipynb - County health rankings and trend analysis  
  - examples/air_quality_quickstart.ipynb - Real-time AQI queries and forecasts
- **Documentation Updates**:
  - README updated with 16 production connectors
  - Comprehensive connector roadmap (24 additional planned connectors)
  - Development priorities and domain coverage table

### Changed
- Updated connector count badges: 14 live | 26 planned
- Enhanced README with complete Week 13 connector details
- Updated planned connectors section to reflect Week 13 completions
- Streamlined README structure for improved readability

### Infrastructure
- PyPI publishing workflow with trusted publisher support
- ReadTheDocs configuration for automated documentation builds
- GitHub issue and PR templates (bug reports, feature requests, questions)
- License compliance automation with SBOM generation

### Documentation
- Comprehensive FAQ (44 Q&A pairs across 8 categories)
- TROUBLESHOOTING guide (30+ problems with solutions)
- API_KEY_SETUP guide for all supported services
- Professional README with badges and data source comparison table

[Unreleased]: https://github.com/KR-Labs/krl-data-connectors/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/KR-Labs/krl-data-connectors/releases/tag/v0.1.0
