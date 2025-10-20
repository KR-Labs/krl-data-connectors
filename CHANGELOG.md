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

### Added
- **Week 12 Health & Environment Connectors (October 20, 2025)**:
  - HRSA Connector: Health Professional Shortage Areas (HPSA), Medically Underserved Areas/Populations (MUA/P), Health Centers (FQHC)
  - County Health Rankings Connector: 30+ county-level health measures, trend data 2010-present, all ranking categories
  - EPA Air Quality / AirNow Connector: Real-time AQI, forecasts, historical data, 6 pollutants, 2,500+ monitoring stations
- **Comprehensive Test Coverage**:
  - 45 HRSA connector tests (90.51% coverage)
  - 35 County Health Rankings connector tests (newly added)
  - 49 Air Quality connector tests (83.82% coverage)
  - Total: 240+ tests passing across 12 connectors
- **Quickstart Notebooks**:
  - examples/hrsa_quickstart.ipynb - HPSA analysis and health center mapping
  - examples/chr_quickstart.ipynb - County health rankings and trend analysis  
  - examples/air_quality_quickstart.ipynb - Real-time AQI queries and forecasts
- **Documentation Updates**:
  - README updated with all 12 production connectors
  - Comprehensive connector roadmap (28 additional planned connectors)
  - Development priorities and domain coverage table

### Changed
- Updated connector count badges: 12 live | 28 planned
- Enhanced README with roadmap section showing development priorities
- Improved citation format and footer styling

## [0.1.0] - 2025-10-19

### Added
- Initial release
- BaseConnector with caching, logging, and error handling
- FREDConnector for Federal Reserve Economic Data
- CensusConnector for U.S. Census Bureau data
- Full type hints and documentation
- Apache 2.0 license

[Unreleased]: https://github.com/KR-Labs/krl-data-connectors/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/KR-Labs/krl-data-connectors/releases/tag/v0.1.0
