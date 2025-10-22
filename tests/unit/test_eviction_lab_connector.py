# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for EvictionLabConnector.

Layer 8: Contract Testing - Type validation and basic interface contracts.

These tests ensure the connector meets the interface contract defined by BaseConnector
and returns data in expected formats. They DO NOT validate data accuracy or business logic.
"""

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import pytest

from krl_data_connectors.housing.eviction_lab_connector import EvictionLabConnector


class TestEvictionLabConnectorContracts:
    """Contract tests verifying EvictionLabConnector interface compliance."""

    @pytest.fixture
    def connector(self):
        """Create connector instance for testing."""
        return EvictionLabConnector()

    @pytest.fixture
    def sample_tract_data(self, tmp_path):
        """Create sample tract-level CSV data."""
        csv_path = tmp_path / "test_tracts.csv"
        csv_path.write_text(
            "GEOID,year,name,parent-location,eviction-filings,evictions,eviction-rate,"
            "eviction-filing-rate,renter-occupied-households,pct-renter-occupied,"
            "median-gross-rent,median-household-income,poverty-rate,pct-white,pct-african-american\n"
            "06037206100,2016,Census Tract 2061,Los Angeles County,150,50,5.2,15.6,962,65.3,1200,45000,18.5,25.0,35.0\n"
            "06037206100,2017,Census Tract 2061,Los Angeles County,145,48,5.0,15.1,960,65.5,1250,46000,17.8,24.5,35.5\n"
            "06037206100,2018,Census Tract 2061,Los Angeles County,140,45,4.7,14.6,958,65.8,1300,47000,17.0,24.0,36.0\n"
            "17031010100,2016,Census Tract 101,Cook County,200,75,7.5,20.0,1000,70.0,950,38000,22.0,15.0,60.0\n"
            "17031010100,2017,Census Tract 101,Cook County,195,72,7.2,19.5,1000,70.2,980,39000,21.5,14.5,60.5\n"
        )
        return csv_path

    @pytest.fixture
    def sample_county_data(self, tmp_path):
        """Create sample county-level CSV data."""
        csv_path = tmp_path / "test_counties.csv"
        csv_path.write_text(
            "GEOID,year,name,eviction-filings,evictions,eviction-rate,"
            "eviction-filing-rate,renter-occupied-households\n"
            "06037,2016,Los Angeles County,125000,42000,4.5,13.4,933333\n"
            "06037,2017,Los Angeles County,120000,40000,4.3,12.9,930000\n"
            "06037,2018,Los Angeles County,115000,38000,4.1,12.4,927000\n"
            "17031,2016,Cook County,85000,32000,6.4,17.0,500000\n"
            "17031,2017,Cook County,82000,30000,6.0,16.4,500000\n"
        )
        return csv_path

    def test_connect_return_type(self, connector):
        """
        Verify connect() returns None and doesn't raise unexpected errors.

        Contract: connect() should complete successfully and return None.
        Layer 8: Contract testing - interface validation.
        """
        result = connector.connect()
        assert result is None, "connect() should return None"

    def test_load_tract_data_return_type(self, connector, sample_tract_data):
        """
        Verify load_tract_data() returns DataFrame with correct structure.

        Contract: load_tract_data() should return pandas DataFrame with
        expected columns when given valid CSV file.

        Layer 8: Contract testing - return type validation.
        """
        connector.connect()
        result = connector.load_tract_data(sample_tract_data)

        # Verify return type
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"

        # Verify expected columns exist
        expected_columns = [
            "GEOID",
            "year",
            "name",
            "parent-location",
            "eviction-filings",
            "evictions",
            "eviction-rate",
            "eviction-filing-rate",
            "renter-occupied-households",
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"

        # Verify data loaded
        assert len(result) == 5, "Should load 5 test records"

        # Verify GEOID preserved as string
        assert result["GEOID"].dtype == "object", "GEOID should be string type"

    def test_load_county_data_return_type(self, connector, sample_county_data):
        """
        Verify load_county_data() returns DataFrame with correct structure.

        Contract: load_county_data() should return DataFrame with county-level
        eviction data.

        Layer 8: Contract testing - method interface validation.
        """
        connector.connect()
        result = connector.load_county_data(sample_county_data)

        assert isinstance(result, pd.DataFrame), "Should return DataFrame"

        # Verify key columns
        expected_columns = [
            "GEOID",
            "year",
            "name",
            "eviction-filings",
            "evictions",
            "eviction-rate",
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"

        assert len(result) == 5, "Should load 5 county-year observations"
        assert result["GEOID"].dtype == "object", "GEOID should be string"

    def test_get_eviction_by_geography_return_type(self, connector, sample_tract_data):
        """
        Verify get_eviction_by_geography() returns filtered DataFrame.

        Contract: get_eviction_by_geography() should return DataFrame with
        data for specified geography.

        Layer 8: Contract testing - filtering logic validation.
        """
        connector.connect()
        connector.load_tract_data(sample_tract_data)

        # Test tract-level query
        result = connector.get_eviction_by_geography(geoid="06037206100", level="tract")

        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        assert len(result) == 3, "Should return 3 years for this tract"
        assert all(result["GEOID"] == "06037206100"), "All records should match GEOID"

        # Test year filtering
        result_2018 = connector.get_eviction_by_geography(
            geoid="06037206100", level="tract", year=2018
        )
        assert len(result_2018) == 1, "Should return 1 record for 2018"
        assert result_2018.iloc[0]["year"] == 2018, "Year should be 2018"

    def test_get_eviction_trends_return_type(self, connector, sample_tract_data):
        """
        Verify get_eviction_trends() returns time series DataFrame.

        Contract: get_eviction_trends() should return DataFrame with
        year and eviction metrics sorted chronologically.

        Layer 8: Contract testing - time series output validation.
        """
        connector.connect()
        connector.load_tract_data(sample_tract_data)

        result = connector.get_eviction_trends(geoid="06037206100", level="tract")

        assert isinstance(result, pd.DataFrame), "Should return DataFrame"

        # Verify expected columns
        expected_columns = [
            "year",
            "evictions",
            "eviction-filings",
            "eviction-rate",
            "eviction-filing-rate",
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"

        # Verify chronological order
        years = result["year"].tolist()
        assert years == sorted(years), "Years should be in chronological order"

        # Verify data for LA tract
        assert len(result) == 3, "Should have 3 years of data"
        assert result.iloc[0]["year"] == 2016, "First year should be 2016"
        assert result.iloc[-1]["year"] == 2018, "Last year should be 2018"

    def test_get_high_eviction_areas_return_type(self, connector, sample_tract_data):
        """
        Verify get_high_eviction_areas() returns filtered DataFrame.

        Contract: get_high_eviction_areas() should return DataFrame of
        geographies exceeding eviction rate threshold.

        Layer 8: Contract testing - threshold filtering validation.
        """
        connector.connect()
        connector.load_tract_data(sample_tract_data)

        # Test with 5% threshold (should find Cook County tract)
        result = connector.get_high_eviction_areas(threshold=5.0, level="tract")

        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        assert "eviction-rate" in result.columns, "Should include eviction-rate"

        # Verify all returned areas meet threshold
        assert all(result["eviction-rate"] >= 5.0), "All areas should meet 5% threshold"

        # Verify Cook County tract included (7.2% in most recent year)
        cook_tracts = result[result["GEOID"] == "17031010100"]
        assert len(cook_tracts) > 0, "Cook County tract should be in high eviction areas"

        # Test with higher threshold (should find fewer areas)
        result_high = connector.get_high_eviction_areas(threshold=7.0, level="tract")
        assert len(result_high) <= len(result), "Higher threshold should return fewer areas"

    def test_get_eviction_statistics_return_type(self, connector, sample_county_data):
        """
        Verify get_eviction_statistics() returns Dict with summary stats.

        Contract: get_eviction_statistics() should return dictionary with
        mean, median, std, and totals for eviction metrics.

        Layer 8: Contract testing - aggregation output validation.
        """
        connector.connect()
        connector.load_county_data(sample_county_data)

        result = connector.get_eviction_statistics(level="county", year=2016)

        assert isinstance(result, dict), "Should return dictionary"

        # Verify expected keys
        expected_keys = [
            "mean_eviction_rate",
            "median_eviction_rate",
            "std_eviction_rate",
            "total_evictions",
            "total_filings",
            "observations",
        ]
        for key in expected_keys:
            assert key in result, f"Missing expected key: {key}"

        # Verify types (accept numpy types too)
        assert isinstance(
            result["mean_eviction_rate"], (float, int, np.number)
        ), "Mean should be numeric"
        assert isinstance(
            result["median_eviction_rate"], (float, int, np.number)
        ), "Median should be numeric"
        assert isinstance(
            result["total_evictions"], (float, int, np.number)
        ), "Total should be numeric"
        assert isinstance(result["observations"], (int, np.integer)), "Observations should be int"

        # Verify 2016 data
        assert result["observations"] == 2, "Should have 2 counties in 2016"
        assert result["total_evictions"] == 74000, "Should sum evictions (42000 + 32000)"
