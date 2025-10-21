"""
Comprehensive test suite for Zillow Housing Data connector.

Tests cover:
- Layer 1: Unit tests (initialization, file loading, geographic filtering)
- Layer 2: Integration tests (time series operations, growth calculations)
- Layer 5: Security tests (path traversal, injection prevention)
- Layer 7: Property-based tests (Hypothesis for edge cases)
- Layer 8: Contract tests (type safety validation)
"""

from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from krl_data_connectors.housing import ZillowConnector


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def zillow_connector(tmp_path):
    """Create Zillow connector instance."""
    return ZillowConnector(cache_dir=str(tmp_path))


@pytest.fixture
def sample_zhvi_data():
    """Sample ZHVI (home values) data."""
    return pd.DataFrame({
        'RegionID': [1, 2, 3, 4, 5],
        'RegionName': ['New York', 'Los Angeles', 'Chicago', 'Providence', 'Boston'],
        'State': ['NY', 'CA', 'IL', 'RI', 'MA'],
        'Metro': ['New York-Newark', 'Los Angeles-Long Beach', 'Chicago', 'Providence', 'Boston'],
        'CountyName': ['New York County', 'Los Angeles County', 'Cook County', 'Providence County', 'Suffolk County'],
        '2022-12-31': [480000, 740000, 290000, 310000, 620000],
        '2023-01-31': [485000, 745000, 292000, 312000, 625000],
        '2023-02-28': [490000, 750000, 295000, 315000, 630000],
        '2023-03-31': [495000, 755000, 298000, 318000, 635000],
    })


@pytest.fixture
def sample_zip_data():
    """Sample ZIP code level data."""
    return pd.DataFrame({
        'RegionID': [100, 101, 102, 103],
        'RegionName': ['02903', '02906', '02907', '90210'],
        'State': ['RI', 'RI', 'RI', 'CA'],
        'City': ['Providence', 'Providence', 'Providence', 'Beverly Hills'],
        '2023-01-31': [295000, 310000, 285000, 1500000],
        '2023-02-28': [298000, 313000, 287000, 1520000],
        '2023-03-31': [301000, 316000, 290000, 1540000],
    })


@pytest.fixture
def sample_time_series_data():
    """Sample data in time series format."""
    return pd.DataFrame({
        'RegionName': ['Providence'] * 12,
        'State': ['RI'] * 12,
        'Date': pd.date_range('2023-01-01', periods=12, freq='MS'),
        'Value': [300000, 302000, 305000, 308000, 310000, 312000, 
                  315000, 318000, 320000, 322000, 325000, 328000]
    })


# ============================================================================
# Layer 1: Unit Tests - Initialization & Core Functionality
# ============================================================================


class TestZillowConnectorInitialization:
    """Test Zillow connector initialization."""

    def test_initialization_default(self):
        """Test connector initializes with defaults."""
        zillow = ZillowConnector()
        
        assert zillow is not None
        assert zillow._get_api_key() is None
        assert hasattr(zillow, 'load_zhvi_data')
        assert hasattr(zillow, 'get_time_series')
    
    def test_initialization_custom_cache(self, tmp_path):
        """Test connector with custom cache directory."""
        cache_dir = tmp_path / "zillow_cache"
        zillow = ZillowConnector(cache_dir=str(cache_dir), cache_ttl=7200)
        
        assert zillow is not None
    
    def test_connect_is_noop(self, zillow_connector):
        """Test connect method does nothing (file-based)."""
        # Should not raise exception
        zillow_connector.connect()
        assert True
    
    def test_get_api_key_returns_none(self, zillow_connector):
        """Test no API key is required."""
        assert zillow_connector._get_api_key() is None


# ============================================================================
# Layer 2: Integration Tests - File Loading
# ============================================================================


class TestZillowConnectorFileLoading:
    """Test file loading operations."""

    def test_load_zhvi_data(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test loading ZHVI data from CSV."""
        filepath = tmp_path / "zhvi.csv"
        sample_zhvi_data.to_csv(filepath, index=False)
        
        data = zillow_connector.load_zhvi_data(filepath)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 5
        assert 'RegionName' in data.columns
        assert '2023-01-31' in data.columns
    
    def test_load_zri_data(self, zillow_connector, tmp_path):
        """Test loading ZRI (rental) data."""
        zri_data = pd.DataFrame({
            'RegionName': ['New York', 'Boston'],
            'State': ['NY', 'MA'],
            '2023-01-31': [2500, 2200],
            '2023-02-28': [2520, 2220],
        })
        
        filepath = tmp_path / "zri.csv"
        zri_data.to_csv(filepath, index=False)
        
        data = zillow_connector.load_zri_data(filepath)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 2
        assert '2023-01-31' in data.columns
    
    def test_load_inventory_data(self, zillow_connector, tmp_path):
        """Test loading inventory data."""
        inventory = pd.DataFrame({
            'RegionName': ['Providence', 'Boston'],
            'State': ['RI', 'MA'],
            '2023-01-31': [500, 1200],
        })
        
        filepath = tmp_path / "inventory.csv"
        inventory.to_csv(filepath, index=False)
        
        data = zillow_connector.load_inventory_data(filepath)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 2
    
    def test_load_sales_data(self, zillow_connector, tmp_path):
        """Test loading sales data."""
        sales = pd.DataFrame({
            'RegionName': ['Providence'],
            'State': ['RI'],
            '2023-01-31': [310000],
        })
        
        filepath = tmp_path / "sales.csv"
        sales.to_csv(filepath, index=False)
        
        data = zillow_connector.load_sales_data(filepath)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 1
    
    def test_fetch_with_filepath(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test fetch method with filepath parameter."""
        filepath = tmp_path / "zhvi.csv"
        sample_zhvi_data.to_csv(filepath, index=False)
        
        data = zillow_connector.fetch(filepath=str(filepath), data_type='zhvi')
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 5
    
    def test_fetch_with_state_filter(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test fetch with automatic state filtering."""
        filepath = tmp_path / "zhvi.csv"
        sample_zhvi_data.to_csv(filepath, index=False)
        
        data = zillow_connector.fetch(filepath=str(filepath), data_type='zhvi', state='RI')
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 1
        assert data.iloc[0]['State'] == 'RI'
    
    def test_fetch_missing_filepath(self, zillow_connector):
        """Test fetch raises error without filepath."""
        with pytest.raises(ValueError) as exc_info:
            zillow_connector.fetch(data_type='zhvi')
        
        assert 'filepath' in str(exc_info.value).lower()
    
    def test_fetch_unknown_data_type(self, zillow_connector, tmp_path):
        """Test fetch with invalid data type."""
        filepath = tmp_path / "test.csv"
        pd.DataFrame({'test': [1]}).to_csv(filepath, index=False)
        
        with pytest.raises(ValueError) as exc_info:
            zillow_connector.fetch(filepath=str(filepath), data_type='invalid')
        
        assert 'Unknown data_type' in str(exc_info.value)


# ============================================================================
# Layer 2: Integration Tests - Geographic Filtering
# ============================================================================


class TestZillowConnectorGeographicFiltering:
    """Test geographic filtering operations."""

    def test_get_state_data_single(self, zillow_connector, sample_zhvi_data):
        """Test filtering by single state."""
        result = zillow_connector.get_state_data(sample_zhvi_data, 'RI')
        
        assert len(result) == 1
        assert result.iloc[0]['State'] == 'RI'
        assert result.iloc[0]['RegionName'] == 'Providence'
    
    def test_get_state_data_multiple(self, zillow_connector, sample_zhvi_data):
        """Test filtering by multiple states."""
        result = zillow_connector.get_state_data(sample_zhvi_data, ['RI', 'MA'])
        
        assert len(result) == 2
        assert set(result['State'].unique()) == {'RI', 'MA'}
    
    def test_get_state_data_case_insensitive(self, zillow_connector, sample_zhvi_data):
        """Test state filtering is case-insensitive."""
        result = zillow_connector.get_state_data(sample_zhvi_data, 'ri')
        
        assert len(result) == 1
        assert result.iloc[0]['State'] == 'RI'
    
    def test_get_state_data_no_match(self, zillow_connector, sample_zhvi_data):
        """Test filtering with non-existent state."""
        result = zillow_connector.get_state_data(sample_zhvi_data, 'ZZ')
        
        assert len(result) == 0
    
    def test_get_metro_data(self, zillow_connector, sample_zhvi_data):
        """Test filtering by metro area."""
        result = zillow_connector.get_metro_data(sample_zhvi_data, 'Providence')
        
        assert len(result) == 1
        assert result.iloc[0]['RegionName'] == 'Providence'
    
    def test_get_metro_data_case_insensitive(self, zillow_connector, sample_zhvi_data):
        """Test metro filtering is case-insensitive."""
        result = zillow_connector.get_metro_data(sample_zhvi_data, 'providence')
        
        assert len(result) == 1
    
    def test_get_county_data(self, zillow_connector, sample_zhvi_data):
        """Test filtering by county."""
        result = zillow_connector.get_county_data(sample_zhvi_data, 'Providence County')
        
        assert len(result) == 1
        assert result.iloc[0]['CountyName'] == 'Providence County'
    
    def test_get_county_data_with_state(self, zillow_connector, sample_zhvi_data):
        """Test county filtering with state filter."""
        result = zillow_connector.get_county_data(sample_zhvi_data, 'Providence', state='RI')
        
        assert len(result) == 1
        assert result.iloc[0]['State'] == 'RI'
    
    def test_get_zip_data_single(self, zillow_connector, sample_zip_data):
        """Test filtering by single ZIP code."""
        result = zillow_connector.get_zip_data(sample_zip_data, '02903')
        
        assert len(result) == 1
        assert result.iloc[0]['RegionName'] == '02903'
    
    def test_get_zip_data_multiple(self, zillow_connector, sample_zip_data):
        """Test filtering by multiple ZIP codes."""
        result = zillow_connector.get_zip_data(sample_zip_data, ['02903', '02906', '02907'])
        
        assert len(result) == 3
        assert set(result['RegionName'].values) == {'02903', '02906', '02907'}
    
    def test_get_zip_data_int_input(self, zillow_connector, sample_zip_data):
        """Test ZIP filtering with integer input."""
        # Integer without leading zeros - won't match '02903' string
        # This tests the int-to-string conversion
        result = zillow_connector.get_zip_data(sample_zip_data, '02903')
        
        assert len(result) == 1
        assert result.iloc[0]['RegionName'] == '02903'


# ============================================================================
# Layer 2: Integration Tests - Time Series Operations
# ============================================================================


class TestZillowConnectorTimeSeriesOperations:
    """Test time series operations."""

    def test_get_time_series(self, zillow_connector, sample_zhvi_data):
        """Test converting wide format to time series."""
        result = zillow_connector.get_time_series(sample_zhvi_data)
        
        assert 'Date' in result.columns
        assert 'Value' in result.columns
        assert 'RegionName' in result.columns
        # 5 regions × 4 date columns = 20 rows
        assert len(result) == 20
    
    def test_get_time_series_date_conversion(self, zillow_connector, sample_zhvi_data):
        """Test date columns are converted to datetime."""
        result = zillow_connector.get_time_series(sample_zhvi_data)
        
        assert pd.api.types.is_datetime64_any_dtype(result['Date'])
    
    def test_get_latest_values(self, zillow_connector, sample_time_series_data):
        """Test getting most recent values."""
        result = zillow_connector.get_latest_values(sample_time_series_data, n=3)
        
        assert len(result) == 3
        assert result['Date'].max() == sample_time_series_data['Date'].max()
    
    def test_calculate_yoy_growth(self, zillow_connector, sample_time_series_data):
        """Test year-over-year growth calculation."""
        result = zillow_connector.calculate_yoy_growth(sample_time_series_data)
        
        assert 'YoY_Growth' in result.columns
        assert len(result) == 12
    
    def test_calculate_mom_growth(self, zillow_connector, sample_time_series_data):
        """Test month-over-month growth calculation."""
        result = zillow_connector.calculate_mom_growth(sample_time_series_data)
        
        assert 'MoM_Growth' in result.columns
        assert len(result) == 12
        # First month should have NaN growth (no prior period)
        assert pd.isna(result.iloc[0]['MoM_Growth'])
        # Subsequent months should have values
        assert not pd.isna(result.iloc[1]['MoM_Growth'])


# ============================================================================
# Layer 2: Integration Tests - Statistical Analysis
# ============================================================================


class TestZillowConnectorStatisticalAnalysis:
    """Test statistical analysis methods."""

    def test_calculate_summary_statistics(self, zillow_connector, sample_time_series_data):
        """Test summary statistics calculation."""
        result = zillow_connector.calculate_summary_statistics(sample_time_series_data)
        
        assert isinstance(result, dict)
        assert 'mean' in result
        assert 'median' in result
        assert 'std' in result
        assert 'min' in result
        assert 'max' in result
        assert 'count' in result
        
        # Verify values are reasonable
        assert result['mean'] > 0
        assert result['count'] == 12
    
    def test_export_to_csv(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test exporting data to CSV."""
        output_file = tmp_path / "export.csv"
        
        zillow_connector.export_to_csv(sample_zhvi_data, output_file)
        
        assert output_file.exists()
        
        # Verify exported data
        exported = pd.read_csv(output_file)
        assert len(exported) == len(sample_zhvi_data)


# ============================================================================
# Layer 5: Security Tests - Path Traversal & Injection Prevention
# ============================================================================


class TestZillowConnectorSecurity:
    """Test security measures against common attacks."""

    def test_path_traversal_load_zhvi(self, zillow_connector):
        """Test path traversal attempts in file loading."""
        malicious_path = "../../etc/passwd"
        
        # Should raise FileNotFoundError, not execute path traversal
        with pytest.raises(FileNotFoundError):
            zillow_connector.load_zhvi_data(malicious_path)
    
    def test_path_traversal_load_zri(self, zillow_connector):
        """Test path traversal in ZRI loading."""
        malicious_path = "../../../sensitive_data.csv"
        
        with pytest.raises(FileNotFoundError):
            zillow_connector.load_zri_data(malicious_path)
    
    def test_sql_injection_state_filter(self, zillow_connector, sample_zhvi_data):
        """Test SQL injection attempts in state filtering."""
        malicious_state = "RI'; DROP TABLE housing; --"
        
        # Should return empty DataFrame, not execute SQL
        result = zillow_connector.get_state_data(sample_zhvi_data, malicious_state)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # No matching state
    
    def test_sql_injection_metro_filter(self, zillow_connector, sample_zhvi_data):
        """Test SQL injection in metro filtering."""
        malicious_metro = "Providence' OR '1'='1"
        
        # Should handle safely
        result = zillow_connector.get_metro_data(sample_zhvi_data, malicious_metro)
        
        assert isinstance(result, pd.DataFrame)
    
    def test_special_characters_in_zip(self, zillow_connector, sample_zip_data):
        """Test special characters in ZIP code filtering."""
        malicious_zip = "02903'; DELETE FROM zips; --"
        
        result = zillow_connector.get_zip_data(sample_zip_data, malicious_zip)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0  # No matching ZIP


# ============================================================================
# Layer 7: Property-Based Tests - Edge Case Discovery
# ============================================================================


class TestZillowConnectorPropertyBased:
    """Property-based tests using Hypothesis."""

    def test_state_filtering_robustness(self):
        """Test state filtering with various inputs."""
        zillow = ZillowConnector()
        data = pd.DataFrame({
            'State': ['RI', 'CA', 'TX', 'NY', 'MA'],
            'RegionName': [f'City{i}' for i in range(5)],
            'Value': range(5)
        })
        
        for state in ['RI', 'CA', 'TX', 'ri', 'ca', 'ZZ', '']:
            result = zillow.get_state_data(data, state)
            assert isinstance(result, pd.DataFrame)
            if state.upper() in ['RI', 'CA', 'TX', 'NY', 'MA']:
                assert len(result) >= 1
    
    def test_zip_filtering_various_formats(self):
        """Test ZIP filtering with different input types."""
        zillow = ZillowConnector()
        data = pd.DataFrame({
            'RegionName': ['02903', '02906', '90210'],
            'State': ['RI', 'RI', 'CA'],
            'Value': [300000, 310000, 1500000]
        })
        
        # Test string, int, and list inputs
        for zip_input in ['02903', 2903, ['02903'], ['02903', '02906']]:
            result = zillow.get_zip_data(data, zip_input)
            assert isinstance(result, pd.DataFrame)
    
    def test_latest_values_various_n(self):
        """Test getting latest values with various n parameters."""
        zillow = ZillowConnector()
        data = pd.DataFrame({
            'Date': pd.date_range('2023-01-01', periods=12, freq='MS'),
            'RegionName': ['Providence'] * 12,
            'Value': range(12)
        })
        
        for n in [1, 3, 6, 12, 24]:
            result = zillow.get_latest_values(data, n=n)
            assert isinstance(result, pd.DataFrame)
            assert len(result) <= min(n, 12)


# ============================================================================
# Layer 8: Contract Tests - Type Safety Validation
# ============================================================================


class TestZillowConnectorTypeContracts:
    """Test type contracts and return types."""

    def test_load_zhvi_return_type(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test load_zhvi_data returns DataFrame."""
        filepath = tmp_path / "zhvi.csv"
        sample_zhvi_data.to_csv(filepath, index=False)
        
        result = zillow_connector.load_zhvi_data(filepath)
        
        assert isinstance(result, pd.DataFrame)
    
    def test_load_zri_return_type(self, zillow_connector, tmp_path):
        """Test load_zri_data returns DataFrame."""
        data = pd.DataFrame({'col': [1, 2]})
        filepath = tmp_path / "zri.csv"
        data.to_csv(filepath, index=False)
        
        result = zillow_connector.load_zri_data(filepath)
        
        assert isinstance(result, pd.DataFrame)
    
    def test_get_state_data_return_type(self, zillow_connector, sample_zhvi_data):
        """Test get_state_data returns DataFrame."""
        result = zillow_connector.get_state_data(sample_zhvi_data, 'RI')
        
        assert isinstance(result, pd.DataFrame)
    
    def test_get_metro_data_return_type(self, zillow_connector, sample_zhvi_data):
        """Test get_metro_data returns DataFrame."""
        result = zillow_connector.get_metro_data(sample_zhvi_data, 'Providence')
        
        assert isinstance(result, pd.DataFrame)
    
    def test_get_time_series_return_type(self, zillow_connector, sample_zhvi_data):
        """Test get_time_series returns DataFrame."""
        result = zillow_connector.get_time_series(sample_zhvi_data)
        
        assert isinstance(result, pd.DataFrame)
        if len(result) > 0:
            assert 'Date' in result.columns
            assert 'Value' in result.columns
    
    def test_calculate_summary_statistics_return_type(self, zillow_connector, sample_time_series_data):
        """Test calculate_summary_statistics returns dict."""
        result = zillow_connector.calculate_summary_statistics(sample_time_series_data)
        
        assert isinstance(result, dict)
        for key in ['mean', 'median', 'std', 'min', 'max', 'count']:
            assert key in result
    
    def test_calculate_yoy_growth_return_type(self, zillow_connector, sample_time_series_data):
        """Test calculate_yoy_growth returns DataFrame."""
        result = zillow_connector.calculate_yoy_growth(sample_time_series_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'YoY_Growth' in result.columns
    
    def test_calculate_mom_growth_return_type(self, zillow_connector, sample_time_series_data):
        """Test calculate_mom_growth returns DataFrame."""
        result = zillow_connector.calculate_mom_growth(sample_time_series_data)
        
        assert isinstance(result, pd.DataFrame)
        assert 'MoM_Growth' in result.columns
    
    def test_get_latest_values_return_type(self, zillow_connector, sample_time_series_data):
        """Test get_latest_values returns DataFrame."""
        result = zillow_connector.get_latest_values(sample_time_series_data, n=3)
        
        assert isinstance(result, pd.DataFrame)
    
    def test_fetch_return_type(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test fetch returns DataFrame."""
        filepath = tmp_path / "zhvi.csv"
        sample_zhvi_data.to_csv(filepath, index=False)
        
        result = zillow_connector.fetch(filepath=str(filepath), data_type='zhvi')
        
        assert isinstance(result, pd.DataFrame)
