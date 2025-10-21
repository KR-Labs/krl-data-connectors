# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for Zillow connector.

Tests the ZillowConnector for Zillow Research Data access.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.housing import ZillowConnector


@pytest.fixture
def zillow_connector():
    """Create a ZillowConnector instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector = ZillowConnector(cache_dir=tmpdir)
        yield connector


@pytest.fixture
def sample_zhvi_data():
    """Create sample ZHVI data for testing."""
    return pd.DataFrame(
        {
            "RegionID": [1, 2, 3],
            "RegionName": ["New York", "Los Angeles", "Chicago"],
            "State": ["NY", "CA", "IL"],
            "Metro": [
                "New York-Newark-Jersey City",
                "Los Angeles-Long Beach-Anaheim",
                "Chicago-Naperville-Elgin",
            ],
            "CountyName": ["New York County", "Los Angeles County", "Cook County"],
            "2023-01-31": [500000, 750000, 300000],
            "2023-02-28": [505000, 755000, 302000],
            "2023-03-31": [510000, 760000, 305000],
        }
    )


@pytest.fixture
def sample_zri_data():
    """Create sample ZRI data for testing."""
    return pd.DataFrame(
        {
            "RegionID": [1, 2, 3],
            "RegionName": ["New York", "Los Angeles", "Chicago"],
            "State": ["NY", "CA", "IL"],
            "Metro": [
                "New York-Newark-Jersey City",
                "Los Angeles-Long Beach-Anaheim",
                "Chicago-Naperville-Elgin",
            ],
            "2023-01-31": [2500, 3000, 1800],
            "2023-02-28": [2520, 3020, 1820],
            "2023-03-31": [2540, 3040, 1840],
        }
    )


class TestZillowConnectorInit:
    """Test ZillowConnector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = ZillowConnector()
        assert connector is not None
        # Check that connector has the expected methods
        assert hasattr(connector, "load_zhvi_data")
        assert hasattr(connector, "get_time_series")

    def test_init_custom_cache(self):
        """Test initialization with custom cache settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            connector = ZillowConnector(cache_dir=tmpdir)
            assert connector is not None
            assert hasattr(connector, "load_zhvi_data")


class TestDataLoading:
    """Test data loading methods."""

    def test_load_zhvi_data(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test loading ZHVI data from file."""
        # Create temporary CSV
        filepath = tmp_path / "zhvi.csv"
        sample_zhvi_data.to_csv(filepath, index=False)

        # Load data
        data = zillow_connector.load_zhvi_data(filepath)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 3
        assert "RegionName" in data.columns
        assert "State" in data.columns

    def test_load_zri_data(self, zillow_connector, sample_zri_data, tmp_path):
        """Test loading ZRI data from file."""
        filepath = tmp_path / "zri.csv"
        sample_zri_data.to_csv(filepath, index=False)

        data = zillow_connector.load_zri_data(filepath)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 3
        assert "2023-01-31" in data.columns

    def test_load_inventory_data(self, zillow_connector, tmp_path):
        """Test loading inventory data."""
        inventory_data = pd.DataFrame(
            {
                "RegionID": [1, 2],
                "RegionName": ["Boston", "Seattle"],
                "State": ["MA", "WA"],
                "2023-01-31": [500, 600],
            }
        )

        filepath = tmp_path / "inventory.csv"
        inventory_data.to_csv(filepath, index=False)

        data = zillow_connector.load_inventory_data(filepath)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 2

    def test_load_sales_data(self, zillow_connector, tmp_path):
        """Test loading sales data."""
        sales_data = pd.DataFrame(
            {
                "RegionID": [1, 2],
                "RegionName": ["Boston", "Seattle"],
                "State": ["MA", "WA"],
                "2023-01-31": [450000, 550000],
            }
        )

        filepath = tmp_path / "sales.csv"
        sales_data.to_csv(filepath, index=False)

        data = zillow_connector.load_sales_data(filepath)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 2


class TestGeographicFiltering:
    """Test geographic filtering methods."""

    def test_get_state_data_single(self, zillow_connector, sample_zhvi_data):
        """Test filtering by single state."""
        result = zillow_connector.get_state_data(sample_zhvi_data, "NY")

        assert len(result) == 1
        assert result.iloc[0]["State"] == "NY"
        assert result.iloc[0]["RegionName"] == "New York"

    def test_get_state_data_multiple(self, zillow_connector, sample_zhvi_data):
        """Test filtering by multiple states."""
        result = zillow_connector.get_state_data(sample_zhvi_data, ["NY", "CA"])

        assert len(result) == 2
        assert set(result["State"].unique()) == {"NY", "CA"}

    def test_get_state_data_case_insensitive(self, zillow_connector, sample_zhvi_data):
        """Test case-insensitive state filtering."""
        result = zillow_connector.get_state_data(sample_zhvi_data, "ny")

        assert len(result) == 1
        assert result.iloc[0]["State"] == "NY"

    def test_get_metro_data(self, zillow_connector, sample_zhvi_data):
        """Test filtering by metro area."""
        result = zillow_connector.get_metro_data(sample_zhvi_data, "Los Angeles-Long Beach-Anaheim")

        assert len(result) == 1
        assert result.iloc[0]["RegionName"] == "Los Angeles"

    def test_get_county_data(self, zillow_connector, sample_zhvi_data):
        """Test filtering by county."""
        result = zillow_connector.get_county_data(sample_zhvi_data, "Cook County")

        assert len(result) == 1
        assert result.iloc[0]["RegionName"] == "Chicago"

    def test_get_zip_data(self, zillow_connector):
        """Test filtering by ZIP code."""
        zip_data = pd.DataFrame(
            {
                "RegionID": [1, 2, 3],
                "RegionName": ["02903", "02906", "90210"],
                "State": ["RI", "RI", "CA"],
                "2023-01-31": [300000, 320000, 850000],
            }
        )

        result = zillow_connector.get_zip_data(zip_data, ["02903", "02906"])

        assert len(result) == 2
        assert set(result["RegionName"].values) == {"02903", "02906"}


class TestTimeSeriesOperations:
    """Test time series conversion and analysis."""

    def test_get_time_series(self, zillow_connector, sample_zhvi_data):
        """Test converting wide format to long format time series."""
        result = zillow_connector.get_time_series(sample_zhvi_data)

        assert "Date" in result.columns
        assert "Value" in result.columns
        assert len(result) == 9  # 3 regions × 3 months

    def test_get_latest_values(self, zillow_connector, sample_zhvi_data):
        """Test getting most recent N periods."""
        # First convert to time series format (with Date column)
        ts_data = zillow_connector.get_time_series(sample_zhvi_data)

        # Get latest 2 periods
        result = zillow_connector.get_latest_values(ts_data, n=2)

        assert len(result) > 0  # Should have some data
        assert "Date" in result.columns
        # With 3 regions and n=2, we expect 6 rows max
        assert len(result) <= 6


class TestGrowthCalculations:
    """Test growth rate calculations."""

    def test_calculate_yoy_growth(self, zillow_connector, sample_zhvi_data):
        """Test year-over-year growth calculation."""
        # First convert to time series format
        ts_data = zillow_connector.get_time_series(sample_zhvi_data)

        # Calculate YoY growth
        result = zillow_connector.calculate_yoy_growth(ts_data)

        assert "YoY_Growth" in result.columns
        assert len(result) > 0

    def test_calculate_mom_growth(self, zillow_connector, sample_zhvi_data):
        """Test month-over-month growth calculation."""
        # First convert to time series format
        ts_data = zillow_connector.get_time_series(sample_zhvi_data)

        # Calculate MoM growth
        result = zillow_connector.calculate_mom_growth(ts_data)

        assert "MoM_Growth" in result.columns
        assert len(result) > 0


class TestStatisticalAnalysis:
    """Test statistical analysis methods."""

    def test_calculate_summary_statistics(self, zillow_connector, sample_zhvi_data):
        """Test summary statistics calculation."""
        # First convert to time series format with Date and Value columns
        ts_data = zillow_connector.get_time_series(sample_zhvi_data)

        # Calculate summary statistics
        result = zillow_connector.calculate_summary_statistics(ts_data)

        # Result should be a dictionary with statistical measures
        assert isinstance(result, dict)
        assert "mean" in result
        assert "median" in result
        assert "std" in result
        assert "min" in result
        assert "max" in result
        assert "count" in result


class TestExport:
    """Test data export functionality."""

    def test_export_to_csv(self, zillow_connector, sample_zhvi_data, tmp_path):
        """Test exporting data to CSV."""
        output_file = tmp_path / "export.csv"

        zillow_connector.export_to_csv(sample_zhvi_data, output_file)

        assert output_file.exists()

        # Verify exported data
        exported = pd.read_csv(output_file)
        assert len(exported) == len(sample_zhvi_data)
        assert list(exported.columns) == list(sample_zhvi_data.columns)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self, zillow_connector):
        """Test handling empty DataFrame."""
        empty_df = pd.DataFrame()
        result = zillow_connector.get_state_data(empty_df, "NY")

        assert len(result) == 0

    def test_missing_state_column(self, zillow_connector):
        """Test handling missing State column."""
        data = pd.DataFrame(
            {
                "RegionName": ["Boston"],
                "2023-01-31": [400000],
            }
        )

        result = zillow_connector.get_state_data(data, "MA")
        assert len(result) == 0

    def test_nonexistent_state(self, zillow_connector, sample_zhvi_data):
        """Test filtering by nonexistent state."""
        result = zillow_connector.get_state_data(sample_zhvi_data, "ZZ")

        assert len(result) == 0


class TestZillowConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    def test_connect_return_type(self):
        """Test that connect returns None."""
        zillow = ZillowConnector()
        result = zillow.connect()
        assert result is None

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_fetch_return_type(self, mock_read_csv, mock_exists):
        """Test that fetch returns DataFrame."""
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({
            "RegionName": ["Providence"],
            "State": ["RI"],
            "2023-01-31": [300000]
        })
        zillow = ZillowConnector()
        result = zillow.fetch(filepath="test.csv", data_type="zhvi")
        assert isinstance(result, pd.DataFrame)

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_load_zhvi_data_return_type(self, mock_read_csv, mock_exists):
        """Test that load_zhvi_data returns DataFrame."""
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({
            "RegionName": ["Providence"],
            "State": ["RI"],
            "2023-01-31": [300000]
        })
        zillow = ZillowConnector()
        result = zillow.load_zhvi_data("test.csv")
        assert isinstance(result, pd.DataFrame)

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_load_zri_data_return_type(self, mock_read_csv, mock_exists):
        """Test that load_zri_data returns DataFrame."""
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({
            "RegionName": ["Providence"],
            "State": ["RI"],
            "2023-01-31": [1500]
        })
        zillow = ZillowConnector()
        result = zillow.load_zri_data("test.csv")
        assert isinstance(result, pd.DataFrame)

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_load_inventory_data_return_type(self, mock_read_csv, mock_exists):
        """Test that load_inventory_data returns DataFrame."""
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({
            "RegionName": ["Providence"],
            "State": ["RI"],
            "2023-01-31": [250]
        })
        zillow = ZillowConnector()
        result = zillow.load_inventory_data("test.csv")
        assert isinstance(result, pd.DataFrame)

    def test_get_state_data_return_type(self):
        """Test that get_state_data returns DataFrame."""
        zillow = ZillowConnector()
        df = pd.DataFrame({
            "RegionName": ["Providence", "Boston"],
            "State": ["RI", "MA"],
            "2023-01-31": [300000, 500000]
        })
        result = zillow.get_state_data(df, "RI")
        assert isinstance(result, pd.DataFrame)

    def test_get_metro_data_return_type(self):
        """Test that get_metro_data returns DataFrame."""
        zillow = ZillowConnector()
        df = pd.DataFrame({
            "RegionName": ["Providence-Warwick", "Boston"],
            "State": ["RI", "MA"],
            "2023-01-31": [300000, 500000]
        })
        result = zillow.get_metro_data(df, "Providence")
        assert isinstance(result, pd.DataFrame)

    def test_get_county_data_return_type(self):
        """Test that get_county_data returns DataFrame."""
        zillow = ZillowConnector()
        df = pd.DataFrame({
            "RegionName": ["Providence County", "Kent County"],
            "State": ["RI", "RI"],
            "2023-01-31": [300000, 280000]
        })
        result = zillow.get_county_data(df, "Providence")
        assert isinstance(result, pd.DataFrame)

    def test_get_zip_data_return_type(self):
        """Test that get_zip_data returns DataFrame."""
        zillow = ZillowConnector()
        df = pd.DataFrame({
            "RegionName": [2903, 2906],
            "State": ["RI", "RI"],
            "2023-01-31": [320000, 290000]
        })
        result = zillow.get_zip_data(df, "02903")
        assert isinstance(result, pd.DataFrame)

    def test_calculate_yoy_growth_return_type(self):
        """Test that calculate_yoy_growth returns DataFrame."""
        zillow = ZillowConnector()
        df = pd.DataFrame({
            "Date": ["2022-01", "2023-01"],
            "Value": [280000, 300000]
        })
        result = zillow.calculate_yoy_growth(df)
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
