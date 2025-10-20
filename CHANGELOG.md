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
