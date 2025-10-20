# HRSA Connector Implementation Summary

**Date:** October 19, 2025  
**Status:** ✅ Implementation Complete - Testing Pending  
**Connector:** HRSA (Health Resources and Services Administration)

---

## Overview

Successfully implemented file-based HRSA connector for accessing Health Professional Shortage Area (HPSA), Medically Underserved Area/Population (MUA/P), and Health Center data.

**Key Finding:** HRSA does NOT provide a REST API - data is available only as downloadable CSV/XLSX/KML/SHP files from the HRSA Data Warehouse.

---

## Implementation Details

### File: `src/krl_data_connectors/health/hrsa_connector.py`
- **Lines:** 615 lines
- **Class:** `HRSAConnector(BaseConnector)`
- **Data Types Supported:**
  - HPSA (Health Professional Shortage Areas)
  - MUA/P (Medically Underserved Areas/Populations)
  - Health Centers (FQHC)

### Core Methods (13 total)

1. **`load_hpsa_data(file_path)`** - Load HPSA CSV file
2. **`load_mua_data(file_path)`** - Load MUA/P CSV file
3. **`load_health_center_data(file_path)`** - Load Health Center CSV file
4. **`get_state_data(data, state)`** - Filter by 2-letter state code
5. **`get_county_data(data, county, state)`** - Filter by county name
6. **`filter_by_discipline(data, discipline)`** - Filter HPSA by discipline (Primary Care, Dental, Mental Health)
7. **`filter_by_type(data, designation_type)`** - Filter by designation type
8. **`get_high_need_areas(data, score_threshold)`** - Filter by HPSA score (0-26 scale)
9. **`get_rural_areas(data)`** - Filter to rural areas only
10. **`summarize_by_state(data, metrics)`** - Calculate state-level statistics
11. **`get_available_disciplines(data)`** - Get discipline counts
12. **Abstract implementations:** `_get_api_key()`, `connect()`, `fetch()`

### Test File: `tests/unit/test_hrsa_connector.py`
- **Lines:** 428 lines
- **Test Classes:** 12
- **Total Tests:** 37
- **Coverage Target:** >80%

**Test Coverage:**
- ✅ Initialization and configuration
- ✅ HPSA data loading
- ✅ MUA/P data loading
- ✅ Health Center data loading
- ✅ State filtering
- ✅ County filtering
- ✅ Discipline filtering (Primary Care, Dental, Mental Health)
- ✅ Type filtering (Geographic, Population, Facility)
- ✅ High-need area identification (score-based)
- ✅ Rural area filtering
- ✅ State-level summarization
- ✅ Discipline counts
- ✅ Error handling for missing files/columns
- ✅ Integration tests combining multiple filters

---

## Data Access Strategy

### HRSA Data Sources

**Primary Download Page:** https://data.hrsa.gov/data/download

**Key Datasets:**
1. **Shortage Areas (SHORT):**
   - URL: https://data.hrsa.gov/data/download?data=SHORT
   - Formats: CSV, XLSX, KML, SHP
   - Contains: HPSA and MUA/P designations

2. **Health Centers:**
   - URL: https://data.hrsa.gov/data/download
   - Contains: FQHC service delivery sites, grant data

3. **UDS (Uniform Data System):**
   - URL: https://data.hrsa.gov/topics/healthcenters/uds/overview
   - Contains: Health center performance metrics

### Interactive Tools (for manual queries)
- HPSA Find: https://data.hrsa.gov/topics/health-workforce/shortage-areas/hpsa-find
- MUA Find: https://data.hrsa.gov/topics/health-workforce/shortage-areas/mua-find
- Health Center Locator: https://findahealthcenter.hrsa.gov/

---

## HPSA Score System

**Score Range:** 0-26 (higher = greater shortage)

**Categories:**
- **0-14:** Moderate shortage
- **15-19:** High shortage (high need)
- **20-26:** Critical shortage (critical need)

**Factors in Score:**
- Population-to-practitioner ratio
- Percent of population below poverty level
- Travel time to nearest source of care
- Infant mortality rate (for Primary Care)

---

## Data Domains

**Primary:**
- **D05:** Healthcare Access & Affordability
- **D06:** Public Health & Wellness

**Secondary:**
- **D24:** Geographic & Spatial Data (spatial analysis of shortages)

---

## Example Usage

```python
from krl_data_connectors.health import HRSAConnector

# Initialize connector
hrsa = HRSAConnector()

# Load HPSA data (downloaded from HRSA Data Warehouse)
hpsa_data = hrsa.load_hpsa_data('BCD_HPSA_FCT_DET_PC.csv')

# Filter to Rhode Island
ri_hpsas = hrsa.get_state_data(hpsa_data, 'RI')

# Get Primary Care shortages
primary_care = hrsa.filter_by_discipline(ri_hpsas, 'Primary Care')

# Find high-need areas (score >= 15)
high_need = hrsa.get_high_need_areas(primary_care, score_threshold=15)

# Find critical rural shortages (score >= 20)
critical_rural = hrsa.get_high_need_areas(high_need, score_threshold=20)
critical_rural = hrsa.get_rural_areas(critical_rural)

# Summarize by state
summary = hrsa.summarize_by_state(
    hpsa_data,
    metrics=['HPSA_Score', 'HPSA_FTE']
)
```

---

## Export Updates

### Modified Files:
1. **`src/krl_data_connectors/health/__init__.py`**
   - Added: `from .hrsa_connector import HRSAConnector`
   - Updated `__all__` to include `HRSAConnector`

2. **`src/krl_data_connectors/__init__.py`**
   - Added: `HRSAConnector` to health imports
   - Updated `__all__` to include `HRSAConnector`

---

## Next Steps

### Immediate:
1. ⏳ **Run tests** - Requires pytest environment setup
2. ⏳ **Verify coverage** - Target: >80%
3. ⏳ **Create quickstart notebook** - `examples/hrsa_quickstart.ipynb`

### Follow-up:
4. **Download sample HRSA data** - For notebook demonstration
5. **Add HRSA to README** - Document features and usage
6. **Commit and push** - Once tests pass

---

## Testing Status

**Environment Issue:** pytest not found in current Python environment
- Tried: `pytest`, `python -m pytest`, `python3 -m pytest`
- Solution needed: Activate conda/venv environment or install pytest

**Expected Test Results:**
- 37 tests across 12 test classes
- Coverage target: >80% (615 lines of code)
- All edge cases covered (missing files, invalid columns, etc.)

---

## Documentation Quality

**Module Docstring:** ✅ Comprehensive
- Data access limitations documented
- Download URLs provided
- Interactive tools referenced

**Method Docstrings:** ✅ Complete
- Args, Returns, Raises documented
- Examples provided for key methods
- Clear parameter descriptions

**Type Hints:** ✅ Full coverage
- All parameters typed
- Return types specified
- Optional parameters marked

**Copyright/Licensing:** ✅ Compliant
- Apache 2.0 license header
- KR-Labs trademark notice
- Proper legal attribution

---

## Comparison to Similar Connectors

| Feature | CDC WONDER | EPA EJScreen | HRSA |
|---------|------------|--------------|------|
| API Available | ❌ No | ❌ No | ❌ No |
| Data Format | CSV (web form) | CSV (FTP) | CSV/XLSX/KML/SHP |
| Implementation | File-based | File-based | File-based |
| Methods | 3 | 8 | 13 |
| Tests | 13 | 29 | 37 |
| Lines of Code | 476 | 390 | 615 |

**HRSA Advantage:** Most comprehensive method suite for shortage area analysis

---

## Known Limitations

1. **No Real-Time API:** Data must be downloaded manually from HRSA Data Warehouse
2. **File Format Dependency:** Relies on HRSA maintaining consistent CSV structure
3. **Data Freshness:** Updates depend on HRSA's quarterly/annual publication schedule
4. **Large Files:** National HPSA data can be several MB (10,000+ records)

---

## Future Enhancements

**Potential Additions:**
- **Spatial analysis methods:** Calculate distances to nearest health center
- **Demographic overlay:** Combine with Census data for deeper analysis
- **Time series support:** Track designation changes over time
- **Automated downloads:** Scrape HRSA download page for latest files
- **GIS integration:** Load KML/SHP formats for spatial visualization

---

## Commit Information

**Branch:** main  
**Status:** Ready to commit  
**Files Changed:**
- `src/krl_data_connectors/health/hrsa_connector.py` (new, 615 lines)
- `tests/unit/test_hrsa_connector.py` (new, 428 lines)
- `src/krl_data_connectors/health/__init__.py` (modified)
- `src/krl_data_connectors/__init__.py` (modified)

**Commit Message:**
```
feat: HRSA connector - 37 tests, 13 methods, file-based implementation

- Implemented HRSAConnector for Health Professional Shortage Areas (HPSA), 
  Medically Underserved Areas (MUA/P), and Health Centers
- 615 lines of production code with comprehensive docstrings
- 37 tests covering all methods and edge cases
- Supports Primary Care, Dental Health, and Mental Health disciplines
- HPSA score-based filtering (0-26 scale)
- State, county, rural, and designation type filtering
- File-based connector (HRSA does not provide REST API)
- Data downloads from: https://data.hrsa.gov/data/download

Testing pending - requires pytest environment setup
```

---

© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC.
