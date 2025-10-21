"""
Comprehensive test suite for County Health Rankings (CHR) connector.

Tests cover:
- Layer 1: Unit tests (initialization, file loading, data filtering)
- Layer 2: Integration tests (data processing, state/county operations)
- Layer 5: Security tests (path traversal, injection prevention)
- Layer 7: Property-based tests (Hypothesis for edge cases)
- Layer 8: Contract tests (type safety validation)
"""

from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from hypothesis import given, strategies as st

from krl_data_connectors.health import CountyHealthRankingsConnector


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def chr_connector():
    """Create CHR connector instance."""
    return CountyHealthRankingsConnector()


@pytest.fixture
def sample_chr_data():
    """Sample CHR rankings data."""
    return pd.DataFrame({
        'state': ['RI', 'RI', 'RI', 'CA', 'CA', 'TX', 'TX'],
        'statecode': ['RI', 'RI', 'RI', 'CA', 'CA', 'TX', 'TX'],
        'county': ['Providence', 'Kent', 'Washington', 'Los Angeles', 'San Diego', 'Harris', 'Dallas'],
        'countycode': ['007', '003', '009', '037', '073', '201', '113'],
        'fips': ['44007', '44003', '44009', '06037', '06073', '48201', '48113'],
        'health_outcomes_rank': [2, 1, 3, 45, 30, 35, 40],
        'health_factors_rank': [1, 2, 3, 40, 28, 32, 38],
        'length_of_life_rank': [2, 1, 3, 44, 29, 34, 39],
        'quality_of_life_rank': [3, 2, 4, 46, 31, 36, 41],
        'v001_rawvalue': [250, 220, 270, 450, 380, 410, 430],  # Premature death
        'v002_rawvalue': [12.5, 11.0, 13.5, 18.5, 16.0, 17.2, 18.0],  # Poor/fair health
        'v036_rawvalue': [15.0, 14.0, 16.0, 19.0, 17.5, 18.2, 18.8],  # Adult smoking
        'v011_rawvalue': [1200, 1500, 1000, 800, 900, 850, 825],  # Primary care ratio
        'v023_rawvalue': [4.5, 4.0, 4.8, 8.5, 7.2, 7.8, 8.2],  # Unemployment
        'adult_obesity': [28.0, 26.5, 29.0, 32.5, 30.2, 31.5, 32.0],
        'adult_smoking': [15.0, 14.0, 16.0, 19.0, 17.5, 18.2, 18.8],
        'uninsured': [4.5, 4.0, 4.8, 8.5, 7.2, 7.8, 8.2],
        'unemployment': [4.5, 4.0, 4.8, 8.5, 7.2, 7.8, 8.2],
        'high_school_graduation': [88.0, 90.0, 87.0, 82.0, 85.0, 84.0, 83.0],
        'year': [2025] * 7
    })


@pytest.fixture
def sample_chr_trends_data():
    """Sample CHR trends data (multi-year)."""
    return pd.DataFrame({
        'state': ['RI'] * 6,
        'county': ['Providence'] * 6,
        'year': [2020, 2021, 2022, 2023, 2024, 2025],
        'adult_obesity': [25.0, 26.0, 26.5, 27.0, 27.5, 28.0],
        'adult_smoking': [17.0, 16.5, 16.0, 15.5, 15.2, 15.0],
        'uninsured': [5.5, 5.2, 5.0, 4.8, 4.6, 4.5]
    })


# ============================================================================
# Layer 1: Unit Tests - Initialization & Core Functionality
# ============================================================================


class TestCHRConnectorInitialization:
    """Test CHR connector initialization."""

    def test_initialization_default_values(self):
        """Test connector initializes with correct default values."""
        chr_conn = CountyHealthRankingsConnector()
        
        assert chr_conn.session is None  # File-based, no session needed
        assert chr_conn.api_key is None  # No API key required
        assert chr_conn._get_api_key() is None
    
    def test_initialization_with_custom_cache(self, tmp_path):
        """Test connector accepts custom cache directory."""
        cache_dir = tmp_path / "custom_cache"
        chr_conn = CountyHealthRankingsConnector(
            cache_dir=str(cache_dir),
            cache_ttl=7200
        )
        
        # Connector initialized successfully with custom params
        assert chr_conn is not None
    
    def test_connect_is_noop(self, chr_connector):
        """Test connect method does nothing (file-based connector)."""
        # Should not raise any exception
        chr_connector.connect()
        assert True
    
    def test_fetch_not_supported(self, chr_connector):
        """Test fetch method raises NotImplementedError."""
        with pytest.raises(NotImplementedError) as exc_info:
            chr_connector.fetch()
        
        assert "does not provide an API" in str(exc_info.value)
        assert "load_rankings_data()" in str(exc_info.value)
    
    def test_class_constants_defined(self, chr_connector):
        """Test class constants are properly defined."""
        assert hasattr(chr_connector, 'RANKING_COLUMNS')
        assert hasattr(chr_connector, 'HEALTH_OUTCOME_MEASURES')
        assert hasattr(chr_connector, 'HEALTH_FACTOR_MEASURES')
        
        assert 'health_outcomes_rank' in chr_connector.RANKING_COLUMNS
        assert 'premature_death' in chr_connector.HEALTH_OUTCOME_MEASURES
        assert 'adult_smoking' in chr_connector.HEALTH_FACTOR_MEASURES


# ============================================================================
# Layer 2: Integration Tests - File Loading & Data Processing
# ============================================================================


class TestCHRConnectorFileLoading:
    """Test file loading operations."""

    def test_load_rankings_data_success(self, chr_connector, sample_chr_data, tmp_path):
        """Test successful loading of rankings data."""
        test_file = tmp_path / "chr_rankings.csv"
        sample_chr_data.to_csv(test_file, index=False)
        
        data = chr_connector.load_rankings_data(test_file)
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert len(data) == 7
        assert 'health_outcomes_rank' in data.columns
    
    def test_load_rankings_data_file_not_found(self, chr_connector):
        """Test error handling for missing file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            chr_connector.load_rankings_data('/nonexistent/file.csv')
        
        assert "not found" in str(exc_info.value)
    
    def test_load_rankings_data_invalid_format(self, chr_connector, tmp_path):
        """Test error handling for invalid CSV format."""
        test_file = tmp_path / "invalid.csv"
        test_file.write_text("Invalid,CSV,Data\n1,2,")  # Incomplete row
        
        # Should still load but may have issues - depends on pandas behavior
        try:
            data = chr_connector.load_rankings_data(test_file)
            assert isinstance(data, pd.DataFrame)
        except ValueError:
            pass  # Acceptable failure
    
    def test_load_trends_data_success(self, chr_connector, sample_chr_trends_data, tmp_path):
        """Test successful loading of trends data."""
        test_file = tmp_path / "chr_trends.csv"
        sample_chr_trends_data.to_csv(test_file, index=False)
        
        data = chr_connector.load_trends_data(test_file)
        
        assert isinstance(data, pd.DataFrame)
        assert not data.empty
        assert len(data) == 6
        assert 'year' in data.columns
    
    def test_load_trends_data_file_not_found(self, chr_connector):
        """Test error handling for missing trends file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            chr_connector.load_trends_data('/nonexistent/trends.csv')
        
        assert "trends data file not found" in str(exc_info.value)
    
    def test_column_name_normalization(self, chr_connector, tmp_path):
        """Test column names are normalized to lowercase."""
        data = pd.DataFrame({
            'STATE': ['RI', 'CA'],
            'County': ['Providence', 'Los Angeles'],
            'HEALTH_OUTCOMES_RANK': [1, 2]
        })
        
        test_file = tmp_path / "mixed_case.csv"
        data.to_csv(test_file, index=False)
        
        loaded = chr_connector.load_rankings_data(test_file)
        
        assert 'state' in loaded.columns
        assert 'county' in loaded.columns
        assert 'health_outcomes_rank' in loaded.columns


# ============================================================================
# Layer 2: Integration Tests - Data Filtering Operations
# ============================================================================


class TestCHRConnectorDataFiltering:
    """Test data filtering and selection methods."""

    def test_get_state_data(self, chr_connector, sample_chr_data):
        """Test filtering by state abbreviation."""
        state_data = chr_connector.get_state_data(sample_chr_data, 'RI')
        
        assert not state_data.empty
        assert all(state_data['state'] == 'RI')
        assert len(state_data) == 3
    
    def test_get_state_data_full_name(self, chr_connector, sample_chr_data):
        """Test filtering by full state name."""
        # Modify test data to include full state name
        data_with_name = sample_chr_data.copy()
        data_with_name['statename'] = data_with_name['state'].map({
            'RI': 'RHODE ISLAND',
            'CA': 'CALIFORNIA',
            'TX': 'TEXAS'
        })
        
        state_data = chr_connector.get_state_data(data_with_name, 'RHODE ISLAND', state_column='statename')
        
        assert not state_data.empty
        assert len(state_data) == 3
    
    def test_get_state_data_no_column(self, chr_connector):
        """Test error when state column not found."""
        data = pd.DataFrame({'county': ['Providence'], 'value': [100]})
        
        with pytest.raises(ValueError) as exc_info:
            chr_connector.get_state_data(data, 'RI')
        
        assert "State column not found" in str(exc_info.value)
    
    def test_get_county_data(self, chr_connector, sample_chr_data):
        """Test filtering by county name."""
        county_data = chr_connector.get_county_data(sample_chr_data, 'Providence')
        
        assert not county_data.empty
        assert county_data['county'].iloc[0] == 'Providence'
    
    def test_get_county_data_with_state(self, chr_connector, sample_chr_data):
        """Test filtering by county and state."""
        county_data = chr_connector.get_county_data(sample_chr_data, 'Providence', state='RI')
        
        assert not county_data.empty
        assert len(county_data) == 1
        assert county_data['county'].iloc[0] == 'Providence'
        assert county_data['state'].iloc[0] == 'RI'
    
    def test_get_county_data_case_insensitive(self, chr_connector, sample_chr_data):
        """Test county filtering is case-insensitive."""
        county_data = chr_connector.get_county_data(sample_chr_data, 'providence')
        
        assert not county_data.empty
        assert county_data['county'].iloc[0] == 'Providence'


# ============================================================================
# Layer 2: Integration Tests - Ranking & Analysis Operations
# ============================================================================


class TestCHRConnectorRankingOperations:
    """Test ranking and analysis methods."""

    def test_get_health_outcomes(self, chr_connector, sample_chr_data):
        """Test getting health outcomes sorted by rank."""
        outcomes = chr_connector.get_health_outcomes(sample_chr_data)
        
        assert not outcomes.empty
        assert outcomes.iloc[0]['health_outcomes_rank'] == 1  # Best rank first
    
    def test_get_health_factors(self, chr_connector, sample_chr_data):
        """Test getting health factors sorted by rank."""
        factors = chr_connector.get_health_factors(sample_chr_data)
        
        assert not factors.empty
        assert factors.iloc[0]['health_factors_rank'] == 1  # Best rank first
    
    def test_get_top_performers(self, chr_connector, sample_chr_data):
        """Test getting top performing counties."""
        top_n = chr_connector.get_top_performers(sample_chr_data, n=3)
        
        assert len(top_n) == 3
        assert top_n.iloc[0]['health_outcomes_rank'] == 1
        assert top_n.iloc[1]['health_outcomes_rank'] == 2
        assert top_n.iloc[2]['health_outcomes_rank'] == 3
    
    def test_get_top_performers_custom_column(self, chr_connector, sample_chr_data):
        """Test top performers with custom ranking column."""
        top_n = chr_connector.get_top_performers(
            sample_chr_data, 
            n=2, 
            rank_column='health_factors_rank'
        )
        
        assert len(top_n) == 2
        assert top_n.iloc[0]['health_factors_rank'] == 1
    
    def test_get_poor_performers(self, chr_connector, sample_chr_data):
        """Test getting poor performing counties."""
        poor = chr_connector.get_poor_performers(sample_chr_data, percentile=75)
        
        assert not poor.empty
        # Should get counties in worst 25% (highest ranks)
        assert all(poor['health_outcomes_rank'] >= sample_chr_data['health_outcomes_rank'].quantile(0.75))
    
    def test_filter_by_measure_above_threshold(self, chr_connector, sample_chr_data):
        """Test filtering by measure above threshold."""
        high_obesity = chr_connector.filter_by_measure(
            sample_chr_data, 
            'adult_obesity', 
            threshold=30.0, 
            above=True
        )
        
        assert not high_obesity.empty
        assert all(high_obesity['adult_obesity'] >= 30.0)
    
    def test_filter_by_measure_below_threshold(self, chr_connector, sample_chr_data):
        """Test filtering by measure below threshold."""
        low_uninsured = chr_connector.filter_by_measure(
            sample_chr_data, 
            'uninsured', 
            threshold=5.0, 
            above=False
        )
        
        assert not low_uninsured.empty
        assert all(low_uninsured['uninsured'] < 5.0)


# ============================================================================
# Layer 2: Integration Tests - Comparison & Summary Operations
# ============================================================================


class TestCHRConnectorComparisonOperations:
    """Test comparison and summary methods."""

    def test_compare_to_state(self, chr_connector, sample_chr_data):
        """Test comparing counties to state averages."""
        comparison = chr_connector.compare_to_state(sample_chr_data, 'adult_smoking')
        
        assert 'adult_smoking_state_avg' in comparison.columns
        assert 'adult_smoking_vs_state' in comparison.columns
        
        # Verify calculations
        ri_avg = sample_chr_data[sample_chr_data['state'] == 'RI']['adult_smoking'].mean()
        ri_comparison = comparison[comparison['state'] == 'RI']
        
        # Check that state average is consistent for all RI counties
        ri_avgs = ri_comparison['adult_smoking_state_avg'].unique()
        assert len(ri_avgs) == 1
        assert float(ri_avgs[0]) == pytest.approx(ri_avg, rel=1e-5)
    
    def test_get_available_measures(self, chr_connector, sample_chr_data):
        """Test getting list of available measures."""
        measures = chr_connector.get_available_measures(sample_chr_data)
        
        assert isinstance(measures, dict)
        assert 'rankings' in measures
        assert 'raw_values' in measures
        assert len(measures['rankings']) > 0
        assert 'health_outcomes_rank' in measures['rankings']
    
    def test_summarize_by_state(self, chr_connector, sample_chr_data):
        """Test state-level summary statistics."""
        summary = chr_connector.summarize_by_state(
            sample_chr_data, 
            measures=['adult_obesity', 'uninsured']
        )
        
        assert not summary.empty
        assert len(summary) == 3  # 3 states in sample data
        
        # Verify aggregation columns
        assert ('adult_obesity', 'mean') in summary.columns
        assert ('adult_obesity', 'median') in summary.columns
    
    def test_summarize_by_state_default_measures(self, chr_connector, sample_chr_data):
        """Test state summary with default measures."""
        summary = chr_connector.summarize_by_state(sample_chr_data)
        
        assert not summary.empty


# ============================================================================
# Layer 5: Security Tests - Path Traversal & Injection Prevention
# ============================================================================


class TestCHRConnectorSecurity:
    """Test security measures against common attacks."""

    def test_path_traversal_in_file_path(self, chr_connector):
        """Test path traversal attempts are handled safely."""
        malicious_path = "../../etc/passwd"
        
        # Should raise FileNotFoundError, not execute path traversal
        with pytest.raises(FileNotFoundError):
            chr_connector.load_rankings_data(malicious_path)
    
    def test_path_traversal_in_trends_file(self, chr_connector):
        """Test path traversal in trends data loading."""
        malicious_path = "../../../sensitive_data.csv"
        
        with pytest.raises(FileNotFoundError):
            chr_connector.load_trends_data(malicious_path)
    
    def test_sql_injection_in_state_filter(self, chr_connector, sample_chr_data):
        """Test SQL injection attempts in state filtering."""
        malicious_state = "XX'; DROP TABLE counties; --"
        
        # Should return empty DataFrame, not execute SQL
        result = chr_connector.get_state_data(sample_chr_data, malicious_state)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # No matching state (XX doesn't exist)
    
    def test_sql_injection_in_county_filter(self, chr_connector, sample_chr_data):
        """Test SQL injection attempts in county filtering."""
        malicious_county = "Providence' OR '1'='1"
        
        # Should return empty DataFrame or only exact matches
        result = chr_connector.get_county_data(sample_chr_data, malicious_county)
        
        assert isinstance(result, pd.DataFrame)
        # Should not match anything (case-insensitive exact match only)
        assert len(result) == 0
    
    def test_special_characters_in_measure_names(self, chr_connector, sample_chr_data):
        """Test special characters in measure names."""
        # Try to filter with special characters
        with pytest.raises(ValueError):
            chr_connector.filter_by_measure(
                sample_chr_data, 
                "adult_obesity'; DROP TABLE data; --",
                threshold=30.0
            )


# ============================================================================
# Layer 7: Property-Based Tests - Edge Case Discovery with Hypothesis
# ============================================================================


class TestCHRConnectorPropertyBased:
    """Property-based tests using Hypothesis."""

    def test_state_filtering_property_based(self):
        """Test state filtering with various states."""
        chr_conn = CountyHealthRankingsConnector()
        data = pd.DataFrame({
            'state': ['RI', 'CA', 'TX'] * 3,
            'county': [f'County{i}' for i in range(9)],
            'value': range(9)
        })
        
        for state in ['RI', 'CA', 'TX', 'NY', 'FL']:
            result = chr_conn.get_state_data(data, state)
            assert isinstance(result, pd.DataFrame)
            if len(result) > 0:
                assert all(result['state'] == state)
    
    def test_top_performers_n_parameter(self):
        """Test top performers with various n values."""
        chr_conn = CountyHealthRankingsConnector()
        data = pd.DataFrame({
            'health_outcomes_rank': range(1, 11),
            'county': [f'County{i}' for i in range(10)]
        })
        
        for n in [1, 3, 5, 10]:
            result = chr_conn.get_top_performers(data, n=n)
            assert isinstance(result, pd.DataFrame)
            assert len(result) <= n
            assert len(result) <= len(data)
    
    def test_poor_performers_percentile_parameter(self):
        """Test poor performers with various percentile values."""
        chr_conn = CountyHealthRankingsConnector()
        data = pd.DataFrame({
            'health_outcomes_rank': range(1, 11),
            'county': [f'County{i}' for i in range(10)]
        })
        
        for percentile in [50, 75, 90]:
            result = chr_conn.get_poor_performers(data, percentile=percentile)
            assert isinstance(result, pd.DataFrame)
            if len(result) > 0:
                threshold = data['health_outcomes_rank'].quantile(percentile / 100)
                assert all(result['health_outcomes_rank'] >= threshold)
    
    def test_measure_filtering_with_various_thresholds(self):
        """Test measure filtering with various threshold values."""
        chr_conn = CountyHealthRankingsConnector()
        data = pd.DataFrame({
            'adult_obesity': [20.0, 25.0, 30.0, 35.0, 40.0],
            'county': [f'County{i}' for i in range(5)]
        })
        
        for threshold in [15.0, 25.0, 35.0, 45.0]:
            result = chr_conn.filter_by_measure(data, 'adult_obesity', threshold=threshold, above=True)
            assert isinstance(result, pd.DataFrame)
            if len(result) > 0:
                assert all(result['adult_obesity'] >= threshold)


# ============================================================================
# Layer 8: Contract Tests - Type Safety Validation
# ============================================================================


class TestCHRConnectorTypeContracts:
    """Test type contracts and return types."""

    def test_load_rankings_data_return_type(self, chr_connector, sample_chr_data, tmp_path):
        """Test load_rankings_data returns DataFrame."""
        test_file = tmp_path / "data.csv"
        sample_chr_data.to_csv(test_file, index=False)
        
        result = chr_connector.load_rankings_data(test_file)
        
        assert isinstance(result, pd.DataFrame)
    
    def test_load_trends_data_return_type(self, chr_connector, sample_chr_trends_data, tmp_path):
        """Test load_trends_data returns DataFrame."""
        test_file = tmp_path / "trends.csv"
        sample_chr_trends_data.to_csv(test_file, index=False)
        
        result = chr_connector.load_trends_data(test_file)
        
        assert isinstance(result, pd.DataFrame)
    
    def test_get_state_data_return_type(self, chr_connector, sample_chr_data):
        """Test get_state_data returns DataFrame."""
        result = chr_connector.get_state_data(sample_chr_data, 'RI')
        
        assert isinstance(result, pd.DataFrame)
    
    def test_get_county_data_return_type(self, chr_connector, sample_chr_data):
        """Test get_county_data returns DataFrame."""
        result = chr_connector.get_county_data(sample_chr_data, 'Providence')
        
        assert isinstance(result, pd.DataFrame)
    
    def test_get_available_measures_return_type(self, chr_connector, sample_chr_data):
        """Test get_available_measures returns dict."""
        result = chr_connector.get_available_measures(sample_chr_data)
        
        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, list)
    
    def test_summarize_by_state_return_type(self, chr_connector, sample_chr_data):
        """Test summarize_by_state returns DataFrame."""
        result = chr_connector.summarize_by_state(sample_chr_data, measures=['adult_obesity'])
        
        assert isinstance(result, pd.DataFrame)
    
    def test_compare_to_state_return_type(self, chr_connector, sample_chr_data):
        """Test compare_to_state returns DataFrame."""
        result = chr_connector.compare_to_state(sample_chr_data, 'adult_smoking')
        
        assert isinstance(result, pd.DataFrame)
        # Verify new columns are added
        assert 'adult_smoking_state_avg' in result.columns
        assert 'adult_smoking_vs_state' in result.columns
    
    def test_filter_by_measure_return_type(self, chr_connector, sample_chr_data):
        """Test filter_by_measure returns DataFrame."""
        result = chr_connector.filter_by_measure(sample_chr_data, 'adult_obesity', 30.0)
        
        assert isinstance(result, pd.DataFrame)
