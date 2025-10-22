---
© 2025 KR-Labs. All rights reserved.  
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
---

# OpportunityInsightsConnector Development Specification
**Date**: October 22, 2025  
**Priority**: 🔴 CRITICAL - Phase 4, Week 1-3  
**Complexity**: Tier 1 - Highest Complexity  
**Estimated Effort**: 3 weeks development + 1 week testing

---

## Executive Summary

The **OpportunityInsightsConnector** is the most complex connector in Phase 4-8, providing access to three major Opportunity Insights data products:

1. **Opportunity Atlas** - Intergenerational mobility by neighborhood
2. **Social Capital Atlas** - Economic connectedness and social capital
3. **Economic Connectedness** - Cross-class friendships and economic outcomes

**Domain Impact**: 
- D10 (Social Mobility) - 0% → 100% coverage
- D21 (Social Capital) - 0% → 100% coverage

**Why Build First**: Establishes architectural patterns for:
- Multi-source data integration
- Complex geographic aggregations (tract → county → CZ → metro)
- Large dataset handling (100GB+ total)
- Multi-level parent/child income quintile matrices

---

## Data Sources

### 1. Opportunity Atlas
**URL**: https://opportunityinsights.org/data/  
**Data**: Intergenerational mobility outcomes by census tract  
**Geographic Coverage**: ~74,000 census tracts  
**Years**: Children born 1978-1983, outcomes measured in 2014-15  
**File Format**: CSV files  
**Dataset Size**: ~2GB compressed, ~10GB uncompressed

**Key Metrics**:
- Household income ranks by parental income percentile
- Employment rates
- Incarceration rates
- College attendance rates
- Teen birth rates
- Marriage rates

**Geographic Levels**:
- Census tract (primary)
- County
- Commuting zone (CZ)
- State

### 2. Social Capital Atlas
**URL**: https://socialcapital.org/  
**Data**: Facebook friendship networks and economic connectedness  
**Geographic Coverage**: ZIP code, county, college  
**Years**: 2022  
**File Format**: CSV files  
**Dataset Size**: ~500MB

**Key Metrics**:
- Economic connectedness (EC)
- Cohesiveness
- Civic engagement
- Volunteering rates
- Clustering coefficient

**Geographic Levels**:
- ZIP code
- County
- College (institution-level)

### 3. Economic Connectedness (Raj Chetty et al.)
**URL**: https://data.humdata.org/dataset/social-capital-atlas  
**Data**: Cross-class friendships  
**Geographic Coverage**: County, ZIP code  
**Years**: 2022  
**File Format**: CSV files  
**Dataset Size**: ~200MB

---

## API Architecture

### Data Access Pattern
**Note**: Opportunity Insights does NOT have a REST API. Data access is via:
1. Direct CSV downloads from public URLs
2. Data stored on AWS S3 (public bucket)
3. Manual file management and caching

### Connector Design Pattern
```python
class OpportunityInsightsConnector(BaseConnector):
    """
    Connector for Opportunity Insights data products.
    
    Unlike most connectors, this does not use an API key.
    Instead, it downloads and caches CSV files from public URLs.
    """
    
    def _get_api_key(self) -> Optional[str]:
        # No API key required for public data
        return None
    
    def connect(self):
        # Initialize HTTP session for file downloads
        pass
    
    def fetch_opportunity_atlas(
        self,
        geography: str = "tract",
        metrics: Optional[List[str]] = None,
        state: Optional[str] = None,
        county: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch Opportunity Atlas mobility data."""
        pass
    
    def fetch_social_capital(
        self,
        geography: str = "county",
        metrics: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """Fetch Social Capital Atlas data."""
        pass
    
    def fetch_economic_connectedness(
        self,
        geography: str = "county"
    ) -> pd.DataFrame:
        """Fetch Economic Connectedness data."""
        pass
```

---

## Implementation Plan

### Week 1: Foundation & Opportunity Atlas (40 hours)

**Day 1-2: Research & Setup (16 hours)**
- [ ] Review all Opportunity Insights documentation
- [ ] Download sample datasets for testing
- [ ] Map CSV file structure and schemas
- [ ] Identify geographic aggregation requirements
- [ ] Create data dictionary for all metrics

**Day 3-5: Core Implementation (24 hours)**
- [ ] Create `social/` subdirectory in `src/krl_data_connectors/`
- [ ] Implement `OpportunityInsightsConnector` base class
- [ ] Implement file download and caching mechanism
- [ ] Implement `fetch_opportunity_atlas()` method
- [ ] Add geographic filtering (state, county, tract)
- [ ] Add metric selection functionality

### Week 2: Social Capital & Economic Connectedness (40 hours)

**Day 1-2: Social Capital Atlas (16 hours)**
- [ ] Implement `fetch_social_capital()` method
- [ ] Handle ZIP code geography
- [ ] Handle county geography
- [ ] Handle college-level data
- [ ] Implement metric selection

**Day 3-4: Economic Connectedness (16 hours)**
- [ ] Implement `fetch_economic_connectedness()` method
- [ ] Cross-validate with Social Capital data
- [ ] Implement data merging capabilities

**Day 5: Integration & Utilities (8 hours)**
- [ ] Create utility methods for geographic aggregation
- [ ] Implement `aggregate_to_county()` method
- [ ] Implement `aggregate_to_cz()` method
- [ ] Implement `aggregate_to_state()` method

### Week 3: Testing & Documentation (40 hours)

**Day 1-2: Unit Tests (16 hours)**
- [ ] Write unit tests for all methods (90%+ coverage target)
- [ ] Mock file downloads for testing
- [ ] Test geographic filtering
- [ ] Test metric selection
- [ ] Test aggregation methods

**Day 3: Integration Tests (8 hours)**
- [ ] Test end-to-end data retrieval
- [ ] Test caching behavior
- [ ] Test error handling
- [ ] Test large dataset performance

**Day 4: Contract Tests (Phase 4 Layer 8) (8 hours)**
- [ ] Write 11 contract tests minimum
- [ ] Test method signatures
- [ ] Test return types
- [ ] Test error conditions
- [ ] Test data validation

**Day 5: Documentation (8 hours)**
- [ ] Write comprehensive docstrings
- [ ] Create quickstart notebook
- [ ] Add to Sphinx documentation
- [ ] Update README with examples
- [ ] Create data dictionary documentation

### Week 4: Testing & QA (40 hours)

**Integration & Performance Testing**
- [ ] Load testing with full datasets
- [ ] Memory profiling and optimization
- [ ] Cache performance validation
- [ ] Cross-platform testing (macOS, Linux, Windows)

**Code Review & Refinement**
- [ ] Peer code review
- [ ] Address feedback
- [ ] Security scan
- [ ] Final documentation review

---

## Technical Challenges

### 1. Large Dataset Handling
**Challenge**: Opportunity Atlas is ~10GB uncompressed  
**Solution**: 
- Chunked file downloads
- On-demand loading by geography
- Efficient data filtering before loading full dataset
- Parquet conversion for faster loading

### 2. Geographic Aggregations
**Challenge**: Census tract → County → CZ → State aggregations  
**Solution**:
- Use Census tract-to-county crosswalk files
- Use CZ definition files from Opportunity Insights
- Implement weighted aggregations by population
- Cache aggregation results

### 3. Multi-Source Integration
**Challenge**: Three separate data products with different schemas  
**Solution**:
- Unified geographic identifier system (FIPS codes)
- Common data structure with metadata
- Clear separation of concerns (one method per data product)
- Standardized column naming conventions

### 4. No API Key Management
**Challenge**: Public data, no authentication  
**Solution**:
- Override `_get_api_key()` to return None
- Implement HTTP session for file downloads
- Add user-agent headers for tracking
- Implement rate limiting on downloads

### 5. Data Version Management
**Challenge**: Data updates infrequently, need to track versions  
**Solution**:
- Add `data_version` parameter to methods
- Store version metadata in cache
- Implement version checking on download
- Document data vintage in responses

---

## Data Schema

### Opportunity Atlas Schema (Simplified)
```python
{
    "tract": str,          # Census tract FIPS code (11 digits)
    "county": str,         # County FIPS code (5 digits)
    "state": str,          # State FIPS code (2 digits)
    "cz": int,             # Commuting zone ID
    "czname": str,         # Commuting zone name
    
    # Household income ranks by parent percentile
    "kfr_pooled_p25": float,  # Mean kid rank (pooled) for parents at p25
    "kfr_pooled_p50": float,
    "kfr_pooled_p75": float,
    
    # Employment rates
    "emp_rate_pooled": float,
    
    # Incarceration rates
    "jail_pooled": float,
    
    # College attendance
    "frac_coll_plus_pooled": float,
    
    # Marriage rates
    "married_pooled": float,
}
```

### Social Capital Atlas Schema
```python
{
    "zip": str,              # ZIP code (5 digits)
    "county": str,           # County FIPS (5 digits)
    
    # Economic connectedness
    "ec_zip": float,         # Economic connectedness at ZIP level
    "ec_se": float,          # Standard error
    
    # Network metrics
    "clustering_zip": float, # Local clustering coefficient
    "support_ratio_zip": float,
    "volunteering_rate_zip": float,
}
```

---

## Testing Strategy

### Unit Tests (~30 tests)
- File download and caching
- Geographic filtering
- Metric selection
- Data validation
- Error handling

### Integration Tests (~10 tests)
- End-to-end data retrieval
- Multi-source integration
- Performance benchmarks
- Cache behavior

### Contract Tests (11 minimum)
- Method signature validation
- Return type checking
- Error condition handling
- Data structure validation

**Target Coverage**: 90%+

---

## Success Criteria

### Functional Requirements
- [ ] All three data products accessible
- [ ] Geographic filtering works correctly
- [ ] Metric selection implemented
- [ ] Aggregation methods functional
- [ ] Caching reduces redundant downloads

### Performance Requirements
- [ ] First download: < 5 minutes for full dataset
- [ ] Cached access: < 5 seconds
- [ ] Memory usage: < 2GB for typical queries
- [ ] Supports 100+ concurrent users (via caching)

### Quality Requirements
- [ ] 90%+ test coverage
- [ ] 100% Phase 4 Layer 8 contract tests passing
- [ ] Security scan clean
- [ ] Documentation complete
- [ ] Example notebook functional

### Domain Coverage
- [ ] D10 (Social Mobility): 0% → 100% ✅
- [ ] D21 (Social Capital): 0% → 100% ✅

---

## Example Usage

```python
from krl_data_connectors import OpportunityInsightsConnector

# Initialize connector (no API key needed)
oi = OpportunityInsightsConnector()

# Fetch Opportunity Atlas data for California
ca_mobility = oi.fetch_opportunity_atlas(
    geography="tract",
    state="06",  # California FIPS code
    metrics=["kfr_pooled_p25", "kfr_pooled_p50", "kfr_pooled_p75"]
)

# Fetch Social Capital data at county level
social_capital = oi.fetch_social_capital(
    geography="county",
    metrics=["ec_zip", "clustering_zip"]
)

# Aggregate tract data to county level
county_mobility = oi.aggregate_to_county(ca_mobility)

# Fetch Economic Connectedness
ec_data = oi.fetch_economic_connectedness(geography="county")
```

---

## File Structure

```
src/krl_data_connectors/
├── social/
│   ├── __init__.py
│   ├── opportunity_insights_connector.py  (main connector)
│   └── utils.py  (geographic aggregation utilities)
├── ...

tests/
├── unit/
│   └── social/
│       ├── test_opportunity_insights_connector.py
│       └── test_social_utils.py
├── integration/
│   └── social/
│       └── test_opportunity_insights_integration.py
└── contract/
    └── social/
        └── test_opportunity_insights_contract.py

examples/
└── quickstart_opportunity_insights.ipynb

docs/
└── connectors/
    └── social/
        └── opportunity_insights.rst
```

---

## Dependencies

### New Dependencies (add to pyproject.toml)
```toml
[project.optional-dependencies]
social = [
    "pandas>=2.0.0",
    "geopandas>=0.13.0",  # for geographic operations
    "pyarrow>=12.0.0",     # for Parquet file support
]
```

### Existing Dependencies (already included)
- requests (HTTP downloads)
- krl-core (caching, logging, config)

---

## Data Sources & URLs

### Opportunity Atlas
- Main site: https://opportunityinsights.org/data/
- Data download: https://opportunityinsights.org/wp-content/uploads/2018/10/atlas.csv
- Codebook: https://opportunityinsights.org/wp-content/uploads/2018/10/atlas_codebook.pdf

### Social Capital Atlas
- Main site: https://socialcapital.org/
- Data download: https://data.humdata.org/dataset/social-capital-atlas
- Paper: Nature (2022) - "Social capital I: measurement and associations with economic mobility"

### Economic Connectedness
- Paper: Nature (2022) - Chetty et al.
- Data: Included in Social Capital Atlas

---

## Risk Assessment

### High Risk
- **Dataset size**: 10GB+ could cause memory issues → Mitigation: Chunked loading
- **Data updates**: Infrequent updates, hard to detect → Mitigation: Version tracking

### Medium Risk
- **Geographic complexity**: Tract→County→CZ aggregations → Mitigation: Use official crosswalks
- **Schema changes**: Data structure might change → Mitigation: Schema validation

### Low Risk
- **Download failures**: Large files → Mitigation: Resume capability, retries
- **Cache management**: Large cache size → Mitigation: Configurable TTL

---

## Next Steps (Immediate)

1. **Create GitHub Issue**: "Implement OpportunityInsightsConnector (Phase 4)"
2. **Set up branch**: `git checkout -b feature/opportunity-insights-connector`
3. **Download sample data**: Get small samples for initial development
4. **Create directory structure**: `src/krl_data_connectors/social/`
5. **Begin implementation**: Start with base class and file download mechanism

---

**Status**: 📋 Specification Complete - Ready to Build  
**Estimated Start**: October 22, 2025  
**Estimated Completion**: November 12, 2025 (3 weeks)  
**Owner**: KR-Labs Development Team
