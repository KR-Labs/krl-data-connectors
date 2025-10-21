# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for FBI Uniform Crime Reporting connector.

Tests the FBIUCRConnector for FBI UCR crime data access.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.crime import FBIUCRConnector


@pytest.fixture
def fbi_connector():
    """Create a FBIUCRConnector instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield FBIUCRConnector(cache_dir=tmpdir)


@pytest.fixture
def sample_crime_data():
    """Create sample crime data for testing."""
    return pd.DataFrame({
        'state': ['RI', 'RI', 'MA', 'MA'],
        'agency': ['Providence PD', 'Newport PD', 'Boston PD', 'Cambridge PD'],
        'year': [2023, 2023, 2023, 2023],
        'population': [180000, 25000, 675000, 118000],
        'violent_crime': [500, 45, 2500, 180],
        'murder': [10, 1, 50, 3],
        'rape': [50, 5, 200, 15],
        'robbery': [150, 15, 800, 50],
        'aggravated_assault': [290, 24, 1450, 112],
        'property_crime': [2500, 300, 10000, 800],
        'burglary': [400, 50, 1500, 120],
        'larceny': [1800, 220, 7500, 600],
        'motor_vehicle_theft': [300, 30, 1000, 80],
    })


class TestFBIUCRConnectorInit:
    """Test FBIUCRConnector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = FBIUCRConnector()
        assert connector is not None
        assert connector.base_url == "https://api.usa.gov/crime/fbi/cde"

    def test_init_custom_cache(self):
        """Test initialization with custom cache settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            connector = FBIUCRConnector(cache_dir=tmpdir)
            assert connector is not None
            assert hasattr(connector, 'load_crime_data')


class TestDataLoading:
    """Test data loading methods."""

    def test_load_crime_data(self, fbi_connector, sample_crime_data, tmp_path):
        """Test loading crime data from file."""
        filepath = tmp_path / "ucr.csv"
        sample_crime_data.to_csv(filepath, index=False)
        
        data = fbi_connector.load_crime_data(filepath)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4
        assert 'violent_crime' in data.columns


class TestStateData:
    """Test state-level crime data retrieval."""

    @patch('requests.get')
    def test_get_state_crime_data_api(self, mock_get, fbi_connector):
        """Test getting state crime data via API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'state': 'RI', 'year': 2023, 'violent_crime': 500}
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = fbi_connector.get_state_crime_data('RI', 2023)
        
        assert isinstance(result, pd.DataFrame)

    def test_get_state_crime_data_no_api(self, fbi_connector):
        """Test getting state crime data without API."""
        result = fbi_connector.get_state_crime_data('RI', 2023, use_api=False)
        
        assert result.empty


class TestCrimeTypeFiltering:
    """Test filtering by crime type."""

    def test_get_violent_crime(self, fbi_connector, sample_crime_data):
        """Test extracting violent crime data."""
        result = fbi_connector.get_violent_crime(sample_crime_data)
        
        assert 'violent_crime' in result.columns
        assert 'murder' in result.columns
        assert 'rape' in result.columns
        assert 'robbery' in result.columns
        assert 'aggravated_assault' in result.columns

    def test_get_property_crime(self, fbi_connector, sample_crime_data):
        """Test extracting property crime data."""
        result = fbi_connector.get_property_crime(sample_crime_data)
        
        assert 'property_crime' in result.columns
        assert 'burglary' in result.columns
        assert 'larceny' in result.columns
        assert 'motor_vehicle_theft' in result.columns

    def test_violent_crime_no_columns(self, fbi_connector):
        """Test violent crime extraction with no relevant columns."""
        data = pd.DataFrame({
            'state': ['RI'],
            'year': [2023],
            'total_arrests': [1000],
        })
        
        result = fbi_connector.get_violent_crime(data)
        assert result.empty


class TestRateCalculations:
    """Test crime rate calculations."""

    def test_calculate_crime_rate_default(self, fbi_connector, sample_crime_data):
        """Test crime rate calculation per 100,000."""
        result = fbi_connector.calculate_crime_rate(
            sample_crime_data,
            'violent_crime',
            'population'
        )
        
        assert 'violent_crime_rate' in result.columns
        # Providence: 500 / 180000 * 100000 = 277.78
        assert abs(result.iloc[0]['violent_crime_rate'] - 277.78) < 1.0

    def test_calculate_crime_rate_custom_per_capita(self, fbi_connector, sample_crime_data):
        """Test crime rate with custom per capita value."""
        result = fbi_connector.calculate_crime_rate(
            sample_crime_data,
            'murder',
            'population',
            per_capita=1000
        )
        
        assert 'murder_rate' in result.columns
        # Providence: 10 / 180000 * 1000 = 0.056
        assert abs(result.iloc[0]['murder_rate'] - 0.056) < 0.01

    def test_calculate_crime_rate_missing_column(self, fbi_connector):
        """Test rate calculation with missing column."""
        data = pd.DataFrame({
            'state': ['RI'],
            'violent_crime': [500],
        })
        
        result = fbi_connector.calculate_crime_rate(data, 'violent_crime', 'population')
        assert 'violent_crime_rate' not in result.columns


class TestStateComparisons:
    """Test comparing crime across states."""

    @patch.object(FBIUCRConnector, 'get_state_crime_data')
    def test_compare_states_all_crime(self, mock_get_state, fbi_connector):
        """Test comparing all crime types across states."""
        mock_get_state.side_effect = [
            pd.DataFrame({'state': ['RI'], 'violent_crime': [500], 'property_crime': [2500]}),
            pd.DataFrame({'state': ['MA'], 'violent_crime': [2500], 'property_crime': [10000]}),
        ]
        
        result = fbi_connector.compare_states(['RI', 'MA'], 2023)
        
        assert len(result) == 2
        assert set(result['state'].unique()) == {'RI', 'MA'}

    @patch.object(FBIUCRConnector, 'get_state_crime_data')
    def test_compare_states_violent_only(self, mock_get_state, fbi_connector):
        """Test comparing violent crime across states."""
        mock_get_state.side_effect = [
            pd.DataFrame({'state': ['RI'], 'violent_crime': [500], 'property_crime': [2500]}),
            pd.DataFrame({'state': ['MA'], 'violent_crime': [2500], 'property_crime': [10000]}),
        ]
        
        result = fbi_connector.compare_states(['RI', 'MA'], 2023, crime_type='violent')
        
        assert 'violent_crime' in result.columns
        assert 'property_crime' not in result.columns

    @patch.object(FBIUCRConnector, 'get_state_crime_data')
    def test_compare_states_property_only(self, mock_get_state, fbi_connector):
        """Test comparing property crime across states."""
        mock_get_state.side_effect = [
            pd.DataFrame({'state': ['RI'], 'violent_crime': [500], 'property_crime': [2500]}),
            pd.DataFrame({'state': ['MA'], 'violent_crime': [2500], 'property_crime': [10000]}),
        ]
        
        result = fbi_connector.compare_states(['RI', 'MA'], 2023, crime_type='property')
        
        assert 'property_crime' in result.columns
        assert 'violent_crime' not in result.columns


class TestYoYAnalysis:
    """Test year-over-year crime change."""

    def test_calculate_yoy_change(self, fbi_connector):
        """Test YoY crime change calculation."""
        current_year = pd.DataFrame({
            'state': ['RI', 'MA'],
            'violent_crime': [500, 2500],
        })
        
        previous_year = pd.DataFrame({
            'state': ['RI', 'MA'],
            'violent_crime': [450, 2400],
        })
        
        result = fbi_connector.calculate_yoy_change(
            current_year,
            previous_year,
            'violent_crime'
        )
        
        assert 'yoy_change' in result.columns
        assert 'yoy_change_pct' in result.columns
        # RI: (500 - 450) / 450 * 100 = 11.11%
        assert abs(result.iloc[0]['yoy_change_pct'] - 11.11) < 0.1

    def test_calculate_yoy_change_missing_column(self, fbi_connector):
        """Test YoY change with missing column."""
        current_year = pd.DataFrame({'state': ['RI'], 'violent_crime': [500]})
        previous_year = pd.DataFrame({'state': ['RI'], 'robbery': [150]})
        
        result = fbi_connector.calculate_yoy_change(
            current_year,
            previous_year,
            'violent_crime'
        )
        
        assert result.empty


class TestTrendData:
    """Test multi-year trend analysis."""

    @patch.object(FBIUCRConnector, 'get_state_crime_data')
    def test_get_trend_data(self, mock_get_state, fbi_connector):
        """Test getting multi-year trend data."""
        mock_get_state.side_effect = [
            pd.DataFrame({'state': ['RI'], 'violent_crime': [450]}),
            pd.DataFrame({'state': ['RI'], 'violent_crime': [480]}),
            pd.DataFrame({'state': ['RI'], 'violent_crime': [500]}),
        ]
        
        result = fbi_connector.get_trend_data('RI', 2021, 2023)
        
        assert len(result) == 3
        assert 'year' in result.columns
        assert set(result['year'].unique()) == {2021, 2022, 2023}

    @patch.object(FBIUCRConnector, 'get_state_crime_data')
    def test_get_trend_data_empty(self, mock_get_state, fbi_connector):
        """Test trend data when no data available."""
        mock_get_state.return_value = pd.DataFrame()
        
        result = fbi_connector.get_trend_data('RI', 2020, 2022)
        
        assert result.empty


class TestExport:
    """Test data export functionality."""

    def test_export_to_csv(self, fbi_connector, sample_crime_data, tmp_path):
        """Test exporting crime data to CSV."""
        output_file = tmp_path / "export.csv"
        
        fbi_connector.export_to_csv(sample_crime_data, output_file)
        
        assert output_file.exists()
        
        exported = pd.read_csv(output_file)
        assert len(exported) == len(sample_crime_data)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self, fbi_connector):
        """Test handling empty DataFrame."""
        empty_df = pd.DataFrame()
        result = fbi_connector.get_violent_crime(empty_df)
        
        assert result.empty

    def test_missing_state_column(self, fbi_connector):
        """Test handling missing state column."""
        data = pd.DataFrame({
            'agency': ['Providence PD'],
            'violent_crime': [500],
        })
        
        result = fbi_connector.get_violent_crime(data)
        assert len(result) == 1

    @patch('requests.get')
    def test_api_request_failure(self, mock_get, fbi_connector):
        """Test handling API request failure."""
        mock_get.side_effect = Exception("API Error")
        
        # Implementation raises exception instead of returning empty DataFrame
        with pytest.raises(Exception, match="API Error"):
            fbi_connector.get_state_crime_data('RI', 2023)


class TestCrimeCategories:
    """Test crime category definitions."""

    def test_violent_crime_list(self, fbi_connector):
        """Test violent crime categories."""
        assert 'murder' in fbi_connector.violent_crimes
        assert 'rape' in fbi_connector.violent_crimes
        assert 'robbery' in fbi_connector.violent_crimes
        assert 'aggravated-assault' in fbi_connector.violent_crimes

    def test_property_crime_list(self, fbi_connector):
        """Test property crime categories."""
        assert 'burglary' in fbi_connector.property_crimes
        assert 'larceny' in fbi_connector.property_crimes
        assert 'motor-vehicle-theft' in fbi_connector.property_crimes
        assert 'arson' in fbi_connector.property_crimes
