# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for HUD Fair Market Rents connector.

Tests the HUDFMRConnector for HUD FMR data access.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.housing import HUDFMRConnector


@pytest.fixture
def hud_connector():
    """Create a HUDFMRConnector instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield HUDFMRConnector(api_key="test_key", cache_dir=tmpdir)


@pytest.fixture
def sample_fmr_data():
    """Create sample FMR data for testing."""
    return pd.DataFrame({
        'state_alpha': ['RI', 'RI', 'MA', 'MA'],
        'countyname': ['Providence County', 'Newport County', 'Suffolk County', 'Middlesex County'],
        'metro_name': ['Providence', 'Providence', 'Boston', 'Boston'],
        'fmr_0br': [850, 900, 1200, 1150],
        'fmr_1br': [950, 1000, 1400, 1350],
        'fmr_2br': [1150, 1200, 1700, 1650],
        'fmr_3br': [1450, 1500, 2100, 2050],
        'fmr_4br': [1700, 1750, 2500, 2450],
        'year': [2023, 2023, 2023, 2023],
    })


class TestHUDFMRConnectorInit:
    """Test HUDFMRConnector initialization."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = HUDFMRConnector(api_key="test_key")
        assert connector is not None
        assert connector.base_url == "https://www.huduser.gov/hudapi/public"

    def test_init_default(self):
        """Test default initialization."""
        connector = HUDFMRConnector()
        assert connector is not None
        assert connector.cache_ttl == 2592000  # 30 days


class TestDataLoading:
    """Test data loading methods."""

    def test_load_fmr_data_csv(self, hud_connector, sample_fmr_data, tmp_path):
        """Test loading FMR data from CSV."""
        filepath = tmp_path / "fmr.csv"
        sample_fmr_data.to_csv(filepath, index=False)
        
        data = hud_connector.load_fmr_data(filepath)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4
        assert 'fmr_0br' in data.columns

    def test_load_fmr_data_excel(self, hud_connector, sample_fmr_data, tmp_path):
        """Test loading FMR data from Excel."""
        filepath = tmp_path / "fmr.xlsx"
        sample_fmr_data.to_excel(filepath, index=False)
        
        data = hud_connector.load_fmr_data(filepath)
        
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4


class TestStateFiltering:
    """Test state-level FMR retrieval."""

    def test_get_state_fmrs_from_data(self, hud_connector, sample_fmr_data):
        """Test getting state FMRs from loaded data."""
        result = hud_connector.get_state_fmrs(
            'RI',
            year=2023,
            data=sample_fmr_data,
            use_api=False
        )
        
        assert len(result) == 2
        assert all(result['state_alpha'] == 'RI')

    @patch('requests.get')
    def test_get_state_fmrs_api(self, mock_get, hud_connector):
        """Test getting state FMRs via API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'fmr_data': [
                    {'county': 'Providence', 'fmr_0br': 850, 'fmr_1br': 950}
                ]
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = hud_connector._api_get_state_fmrs('RI', 2023)
        
        assert isinstance(result, pd.DataFrame)

    def test_get_state_fmrs_multiple_states(self, hud_connector, sample_fmr_data):
        """Test filtering multiple states."""
        result_ri = hud_connector.get_state_fmrs('RI', 2023, sample_fmr_data, False)
        result_ma = hud_connector.get_state_fmrs('MA', 2023, sample_fmr_data, False)
        
        assert len(result_ri) == 2
        assert len(result_ma) == 2


class TestMetroFiltering:
    """Test metro-level FMR retrieval."""

    def test_get_metro_fmrs(self, hud_connector, sample_fmr_data):
        """Test getting metro area FMRs."""
        result = hud_connector.get_metro_fmrs(sample_fmr_data, 'Boston')
        
        assert len(result) == 2
        assert all(result['metro_name'] == 'Boston')

    def test_get_metro_fmrs_case_insensitive(self, hud_connector, sample_fmr_data):
        """Test case-insensitive metro filtering."""
        result = hud_connector.get_metro_fmrs(sample_fmr_data, 'boston')
        
        assert len(result) == 2


class TestCountyFiltering:
    """Test county-level FMR retrieval."""

    def test_get_county_fmrs_single(self, hud_connector, sample_fmr_data):
        """Test getting FMRs for single county."""
        result = hud_connector.get_county_fmrs(sample_fmr_data, 'Providence County')
        
        assert len(result) == 1
        assert result.iloc[0]['countyname'] == 'Providence County'

    def test_get_county_fmrs_multiple(self, hud_connector, sample_fmr_data):
        """Test getting FMRs for multiple counties."""
        result = hud_connector.get_county_fmrs(
            sample_fmr_data,
            ['Providence County', 'Newport County']
        )
        
        assert len(result) == 2


class TestBedroomFiltering:
    """Test bedroom-specific FMR queries."""

    def test_get_fmr_by_bedrooms_0br(self, hud_connector, sample_fmr_data):
        """Test getting 0-bedroom FMRs."""
        result = hud_connector.get_fmr_by_bedrooms(sample_fmr_data, 0)
        
        assert 'fmr_0br' in result.columns
        assert 'fmr_1br' not in result.columns

    def test_get_fmr_by_bedrooms_2br(self, hud_connector, sample_fmr_data):
        """Test getting 2-bedroom FMRs."""
        result = hud_connector.get_fmr_by_bedrooms(sample_fmr_data, 2)
        
        assert 'fmr_2br' in result.columns
        assert 'fmr_0br' not in result.columns

    def test_get_fmr_by_bedrooms_invalid(self, hud_connector, sample_fmr_data):
        """Test invalid bedroom count."""
        result = hud_connector.get_fmr_by_bedrooms(sample_fmr_data, 5)
        
        assert result.empty or 'fmr_5br' not in result.columns


class TestAffordabilityCalculations:
    """Test affordability analysis."""

    def test_calculate_affordability_affordable(self, hud_connector):
        """Test affordability when rent is affordable."""
        result = hud_connector.calculate_affordability(
            household_income=60000,
            fmr_value=1500,
            income_threshold=0.30
        )
        
        assert 'max_affordable_rent' in result
        assert 'rent_to_income_ratio' in result
        assert 'affordable' in result
        assert result['max_affordable_rent'] == 1500.0
        assert result['affordable'] is True

    def test_calculate_affordability_unaffordable(self, hud_connector):
        """Test affordability when rent is too high."""
        result = hud_connector.calculate_affordability(
            household_income=40000,
            fmr_value=1500,
            income_threshold=0.30
        )
        
        assert result['affordable'] is False
        assert result['surplus_deficit'] < 0

    def test_calculate_affordability_custom_threshold(self, hud_connector):
        """Test affordability with custom income threshold."""
        result = hud_connector.calculate_affordability(
            household_income=60000,
            fmr_value=2000,
            income_threshold=0.35
        )
        
        # 60000 * 0.35 / 12 = 1750
        assert result['max_affordable_rent'] == 1750.0


class TestIncomeData:
    """Test income limit retrieval."""

    @patch('requests.get')
    def test_get_income_limits_api(self, mock_get, hud_connector):
        """Test getting income limits via API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': [
                {'income_limit': 'very_low', 'household_1': 30000},
                {'income_limit': 'low', 'household_1': 48000},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        result = hud_connector.get_income_limits('RI', 2023)
        
        assert isinstance(result, pd.DataFrame)


class TestComparisons:
    """Test FMR comparison methods."""

    def test_compare_fmrs(self, hud_connector, sample_fmr_data):
        """Test comparing FMRs across regions."""
        regions = ['Providence County', 'Suffolk County']
        result = hud_connector.compare_fmrs(sample_fmr_data, regions, bedroom_count=2)
        
        assert len(result) == 2
        assert 'fmr_2br' in result.columns
        assert set(result['countyname'].values) == set(regions)

    def test_compare_fmrs_all_bedrooms(self, hud_connector, sample_fmr_data):
        """Test comparing FMRs with all bedroom counts."""
        regions = ['Providence County', 'Newport County']
        result = hud_connector.compare_fmrs(sample_fmr_data, regions)
        
        assert 'fmr_0br' in result.columns
        assert 'fmr_4br' in result.columns


class TestYoYAnalysis:
    """Test year-over-year change calculations."""

    def test_calculate_yoy_change(self, hud_connector):
        """Test YoY FMR change calculation."""
        current_year = pd.DataFrame({
            'countyname': ['Providence County', 'Suffolk County'],
            'fmr_2br': [1150, 1700],
        })
        
        previous_year = pd.DataFrame({
            'countyname': ['Providence County', 'Suffolk County'],
            'fmr_2br': [1100, 1650],
        })
        
        result = hud_connector.calculate_yoy_change(
            current_year,
            previous_year,
            'fmr_2br'
        )
        
        assert 'yoy_change' in result.columns
        assert 'yoy_change_pct' in result.columns
        # Providence: (1150 - 1100) / 1100 * 100 = 4.54%
        assert abs(result.iloc[0]['yoy_change_pct'] - 4.54) < 0.1


class TestExport:
    """Test data export functionality."""

    def test_export_to_csv(self, hud_connector, sample_fmr_data, tmp_path):
        """Test exporting FMR data to CSV."""
        output_file = tmp_path / "export.csv"
        
        hud_connector.export_to_csv(sample_fmr_data, output_file)
        
        assert output_file.exists()
        
        exported = pd.read_csv(output_file)
        assert len(exported) == len(sample_fmr_data)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self, hud_connector):
        """Test handling empty DataFrame."""
        empty_df = pd.DataFrame()
        result = hud_connector.get_state_fmrs('RI', 2023, empty_df, False)
        
        assert len(result) == 0

    def test_missing_bedroom_column(self, hud_connector):
        """Test handling missing bedroom columns."""
        data = pd.DataFrame({
            'countyname': ['Providence County'],
            'fmr_2br': [1150],
        })
        
        result = hud_connector.get_fmr_by_bedrooms(data, 3)
        # Should return empty or handle gracefully
        assert result.empty or 'fmr_3br' not in result.columns

    def test_nonexistent_state(self, hud_connector, sample_fmr_data):
        """Test filtering by nonexistent state."""
        result = hud_connector.get_state_fmrs('ZZ', 2023, sample_fmr_data, False)
        
        assert len(result) == 0
