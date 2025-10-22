# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for OpportunityInsightsConnector.

Tests cover:
- Initialization with various configurations
- Connection establishment
- Data fetching and filtering
- Geographic aggregation
- Column normalization
- Error handling
- Edge cases

Target: 90%+ code coverage
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pandas as pd
import pytest
import requests

from krl_data_connectors.mobility import OpportunityInsightsConnector

# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def mock_cache_dir(tmp_path):
    """Create temporary cache directory."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return str(cache_dir)


@pytest.fixture
def connector(mock_cache_dir):
    """Create OpportunityInsightsConnector instance with test cache."""
    return OpportunityInsightsConnector(cache_dir=mock_cache_dir)


@pytest.fixture
def sample_stata_data():
    """Create sample STATA-format data for testing."""
    return pd.DataFrame(
        {
            "state": [44.0, 44.0, 44.0, 50.0, 50.0],
            "county": [1.0, 1.0, 7.0, 1.0, 3.0],
            "tract": [30100.0, 30200.0, 101.0, 10100.0, 20100.0],
            "cz": [20401.0, 20401.0, 20401.0, 23801.0, 23801.0],
            "czname": ["Providence", "Providence", "Providence", "Burlington", "Burlington"],
            "kfr_pooled_pooled_p25": [0.45, 0.48, 0.42, 0.52, 0.50],
            "kfr_pooled_pooled_p25_se": [0.01, 0.02, 0.015, 0.018, 0.012],
            "jail_pooled_pooled_p25": [0.005, 0.008, 0.012, 0.003, 0.004],
            "kfr_black_pooled_p25": [0.40, 0.43, None, None, None],
            "kfr_white_pooled_p25": [0.48, 0.51, 0.45, 0.54, 0.52],
            "pooled_pooled_count": [150, 200, 180, 120, 140],
        }
    )


@pytest.fixture
def normalized_data():
    """Create normalized data (after column name conversion)."""
    return pd.DataFrame(
        {
            "state": ["44", "44", "44", "50", "50"],
            "county": ["44001", "44001", "44007", "50001", "50003"],
            "tract": ["44001030100", "44001030200", "44007000101", "50001010100", "50003020100"],
            "cz": [20401.0, 20401.0, 20401.0, 23801.0, 23801.0],
            "czname": ["Providence", "Providence", "Providence", "Burlington", "Burlington"],
            "kfr_pooled_p25": [0.45, 0.48, 0.42, 0.52, 0.50],
            "kfr_pooled_p25_se": [0.01, 0.02, 0.015, 0.018, 0.012],
            "jail_pooled_p25": [0.005, 0.008, 0.012, 0.003, 0.004],
            "kfr_black_p25": [0.40, 0.43, None, None, None],
            "kfr_white_p25": [0.48, 0.51, 0.45, 0.54, 0.52],
            "pooled_pooled_count": [150, 200, 180, 120, 140],
        }
    )


# ============================================================
# INITIALIZATION TESTS
# ============================================================


class TestInitialization:
    """Test connector initialization."""

    def test_init_default_params(self):
        """Test initialization with default parameters."""
        oi = OpportunityInsightsConnector()
        assert str(oi.cache.cache_dir) == str(Path.home() / ".krl_cache" / "mobility")
        assert oi.data_version == "latest"
        assert oi.timeout == 60
        assert oi.max_retries == 3
        assert oi._atlas_data is None
        assert (
            oi._social_capital_data is None
        )  # Kept for backward compatibility, cache dict added later

    def test_init_custom_cache_dir(self, mock_cache_dir):
        """Test initialization with custom cache directory."""
        oi = OpportunityInsightsConnector(cache_dir=mock_cache_dir)
        assert str(oi.cache.cache_dir) == mock_cache_dir
        assert os.path.exists(mock_cache_dir)

    def test_init_custom_cache_ttl(self, mock_cache_dir):
        """Test initialization with custom cache TTL."""
        ttl = 86400  # 1 day
        oi = OpportunityInsightsConnector(cache_dir=mock_cache_dir, cache_ttl=ttl)
        assert oi.cache.default_ttl == ttl

    def test_init_custom_timeout(self, mock_cache_dir):
        """Test initialization with custom timeout."""
        oi = OpportunityInsightsConnector(cache_dir=mock_cache_dir, timeout=120)
        assert oi.timeout == 120

    def test_init_custom_data_version(self, mock_cache_dir):
        """Test initialization with custom data version."""
        oi = OpportunityInsightsConnector(cache_dir=mock_cache_dir, data_version="v2023")
        assert oi.data_version == "v2023"

    def test_init_creates_cache_directory(self, tmp_path):
        """Test that initialization creates cache directory if missing."""
        cache_dir = tmp_path / "new_cache"
        assert not cache_dir.exists()

        oi = OpportunityInsightsConnector(cache_dir=str(cache_dir))
        # Cache dir creation happens in parent class
        assert str(oi.cache.cache_dir) == str(cache_dir)


# ============================================================
# CONNECTION TESTS
# ============================================================


class TestConnection:
    """Test connection establishment."""

    def test_connect_success(self, connector):
        """Test successful connection."""
        connector.connect()
        assert connector.session is not None
        assert isinstance(connector.session, requests.Session)

    def test_connect_multiple_times(self, connector):
        """Test connecting multiple times (should be idempotent)."""
        connector.connect()
        session1 = connector.session

        connector.connect()
        session2 = connector.session

        # Should reuse or recreate session
        assert session1 is not None
        assert session2 is not None

    def test_get_api_key_returns_none(self, connector):
        """Test that get_api_key returns None (public data)."""
        assert connector._get_api_key() is None


# ============================================================
# COLUMN NORMALIZATION TESTS
# ============================================================


class TestColumnNormalization:
    """Test column name normalization."""

    def test_normalize_pooled_pooled_columns(self, connector, sample_stata_data):
        """Test normalization of double-pooled column names."""
        normalized = connector._normalize_column_names(sample_stata_data.copy())

        assert "kfr_pooled_p25" in normalized.columns
        assert "kfr_pooled_pooled_p25" not in normalized.columns
        assert "jail_pooled_p25" in normalized.columns
        assert "jail_pooled_pooled_p25" not in normalized.columns

    def test_normalize_race_columns(self, connector, sample_stata_data):
        """Test normalization of race-specific columns."""
        normalized = connector._normalize_column_names(sample_stata_data.copy())

        assert "kfr_black_p25" in normalized.columns
        assert "kfr_black_pooled_p25" not in normalized.columns
        assert "kfr_white_p25" in normalized.columns
        assert "kfr_white_pooled_p25" not in normalized.columns

    def test_normalize_preserves_other_columns(self, connector, sample_stata_data):
        """Test that normalization preserves non-target columns."""
        normalized = connector._normalize_column_names(sample_stata_data.copy())

        # Geographic columns should be unchanged
        assert "state" in normalized.columns
        assert "county" in normalized.columns
        assert "tract" in normalized.columns
        assert "cz" in normalized.columns
        assert "czname" in normalized.columns

        # Count columns should be unchanged
        assert "pooled_pooled_count" in normalized.columns

    def test_normalize_empty_dataframe(self, connector):
        """Test normalization of empty DataFrame."""
        empty_df = pd.DataFrame()
        normalized = connector._normalize_column_names(empty_df)
        assert len(normalized.columns) == 0
        assert len(normalized) == 0

    def test_normalize_no_matching_columns(self, connector):
        """Test normalization when no columns match patterns."""
        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6], "other_column": [7, 8, 9]})
        normalized = connector._normalize_column_names(df)

        # Should return unchanged
        assert list(normalized.columns) == list(df.columns)


# ============================================================
# FETCH METHOD TESTS
# ============================================================


class TestFetchMethod:
    """Test main fetch() method."""

    def test_fetch_atlas_product(self, connector):
        """Test fetch() with atlas data product."""
        with patch.object(connector, "fetch_opportunity_atlas") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({"col": [1, 2, 3]})

            result = connector.fetch(data_product="atlas", geography="tract", state="44")

            mock_fetch.assert_called_once_with(geography="tract", state="44")
            assert len(result) == 3

    def test_fetch_social_capital_product(self, connector):
        """Test fetch() with social_capital data product."""
        with patch.object(connector, "fetch_social_capital") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({"col": [1, 2]})

            result = connector.fetch(data_product="social_capital", geography="county")

            mock_fetch.assert_called_once_with(geography="county")
            assert len(result) == 2

    def test_fetch_economic_connectedness_product(self, connector):
        """Test fetch() with ec data product."""
        with patch.object(connector, "fetch_economic_connectedness") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame({"col": [1]})

            result = connector.fetch(data_product="ec", geography="zip")

            mock_fetch.assert_called_once_with(geography="zip")
            assert len(result) == 1

    def test_fetch_invalid_product(self, connector):
        """Test fetch() with invalid data product."""
        with pytest.raises(ValueError, match="Unknown data_product"):
            connector.fetch(data_product="invalid_product")

    def test_fetch_missing_product(self, connector):
        """Test fetch() without data_product parameter uses default 'atlas'."""
        # fetch() has default data_product='atlas', so this should NOT raise
        # It will try to fetch atlas data
        with patch.object(connector, "fetch_opportunity_atlas") as mock_fetch:
            mock_fetch.return_value = pd.DataFrame()
            connector.fetch(geography="tract")
            mock_fetch.assert_called_once_with(geography="tract")


# ============================================================
# DATA FILTERING TESTS
# ============================================================


class TestDataFiltering:
    """Test data filtering functionality."""

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_filter_by_state(self, mock_download, mock_read_stata, connector, sample_stata_data):
        """Test filtering data by state."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read_stata.return_value = sample_stata_data

        result = connector.fetch_opportunity_atlas(geography="tract", state="44")

        # Should only return Rhode Island (state=44)
        assert len(result) == 3
        assert all(result["state"] == "44")

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_filter_by_county(self, mock_download, mock_read_stata, connector, sample_stata_data):
        """Test filtering data by county."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read_stata.return_value = sample_stata_data

        result = connector.fetch_opportunity_atlas(geography="tract", county="44007")

        # Should only return Providence County
        assert len(result) == 1
        assert all(result["county"] == "44007")

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_filter_by_state_and_county(
        self, mock_download, mock_read_stata, connector, sample_stata_data
    ):
        """Test filtering by both state and county."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read_stata.return_value = sample_stata_data

        result = connector.fetch_opportunity_atlas(geography="tract", state="44", county="44001")

        # Should return only tracts in county 44001 within state 44
        assert len(result) == 2
        assert all(result["state"] == "44")
        assert all(result["county"] == "44001")

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_filter_by_metrics(self, mock_download, mock_read_stata, connector, sample_stata_data):
        """Test filtering by specific metrics."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read_stata.return_value = sample_stata_data

        metrics = ["kfr_pooled_p25", "jail_pooled_p25"]
        result = connector.fetch_opportunity_atlas(geography="tract", state="44", metrics=metrics)

        # Should include geographic columns + requested metrics
        expected_cols = {
            "tract",
            "county",
            "state",
            "cz",
            "czname",
            "kfr_pooled_p25",
            "jail_pooled_p25",
        }
        assert set(result.columns) == expected_cols

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_filter_nonexistent_state(
        self, mock_download, mock_read_stata, connector, sample_stata_data
    ):
        """Test filtering by state that doesn't exist in data."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read_stata.return_value = sample_stata_data

        result = connector.fetch_opportunity_atlas(geography="tract", state="99")

        # Should return empty DataFrame
        assert len(result) == 0


# ============================================================
# GEOGRAPHIC AGGREGATION TESTS
# ============================================================


class TestGeographicAggregation:
    """Test geographic aggregation methods."""

    def test_aggregate_to_county(self, connector, normalized_data):
        """Test aggregation from tract to county level."""
        result = connector.aggregate_to_county(normalized_data)

        # Should have fewer rows (grouped by county)
        assert len(result) < len(normalized_data)

        # Should have county as primary key
        assert "county" in result.columns

        # Should aggregate numeric columns
        assert "kfr_pooled_p25" in result.columns

    def test_aggregate_to_cz(self, connector, normalized_data):
        """Test aggregation to commuting zone level."""
        result = connector.aggregate_to_cz(normalized_data)

        # Should group by CZ
        assert len(result) <= len(normalized_data)
        assert "cz" in result.columns

    def test_aggregate_to_state(self, connector, normalized_data):
        """Test aggregation to state level."""
        result = connector.aggregate_to_state(normalized_data)

        # Should have very few rows (one per state)
        assert len(result) == 2  # RI and VT in sample data
        assert "state" in result.columns

    def test_aggregation_preserves_counts(self, connector, normalized_data):
        """Test that aggregation sums count columns correctly."""
        result = connector.aggregate_to_county(normalized_data)

        # Count columns should be summed
        if "pooled_pooled_count" in result.columns:
            # Sum should be preserved
            original_sum = normalized_data["pooled_pooled_count"].sum()
            aggregated_sum = result["pooled_pooled_count"].sum()
            assert aggregated_sum == original_sum


# ============================================================
# ERROR HANDLING TESTS
# ============================================================


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_geography(self, connector):
        """Test with invalid geography parameter."""
        with pytest.raises(ValueError, match="Invalid geography"):
            connector.fetch_opportunity_atlas(geography="invalid")

    def test_download_file_404_error(self, connector):
        """Test handling of 404 errors during download."""
        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.HTTPError("404")
            mock_session.get.return_value = mock_response

            connector.connect()

            with pytest.raises(requests.HTTPError):
                connector._download_file("https://example.com/nonexistent.dta", "test.dta")

    def test_download_file_network_error(self, connector):
        """Test handling of network errors during download."""
        with patch.object(connector, "session") as mock_session:
            mock_session.get.side_effect = requests.ConnectionError("Network error")

            connector.connect()

            with pytest.raises(requests.ConnectionError):
                connector._download_file("https://example.com/data.dta", "test.dta")

    def test_fetch_without_connect(self, connector):
        """Test fetching data without establishing connection first."""
        # fetch_opportunity_atlas should auto-connect if session is None
        # We need to let _download_file run to trigger auto-connect
        with patch("pandas.read_stata") as mock_read:
            mock_read.return_value = pd.DataFrame(
                {
                    "state": [44.0],
                    "county": [1.0],
                    "tract": [30100.0],
                    "cz": [20401.0],
                    "czname": ["Providence"],
                    "kfr_pooled_pooled_p25": [0.45],
                }
            )

            # Mock the actual HTTP download but let _download_file logic run
            with patch.object(
                connector.session if connector.session else requests.Session(), "get"
            ) as mock_get:
                mock_response = Mock()
                mock_response.headers = {"content-length": "100"}
                mock_response.iter_content = lambda chunk_size: [b"fake data"]
                mock_response.raise_for_status = Mock()
                mock_get.return_value = mock_response

                # Session is None initially
                assert connector.session is None

                # Should auto-connect during _download_file
                connector.fetch_opportunity_atlas(geography="tract", state="44")

                # Verify session was created (auto-connected)
                assert connector.session is not None


# ============================================================
# CACHING TESTS
# ============================================================


class TestCaching:
    """Test file caching functionality."""

    def test_download_file_caching(self, connector, tmp_path):
        """Test that files are cached after download."""
        test_file = tmp_path / "test_data.dta"
        test_file.write_text("test data")

        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.headers = {"content-length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"test data"]
            mock_session.get.return_value = mock_response

            connector.connect()

            # First download
            result1 = connector._download_file("https://example.com/data.dta", "cached_data.dta")

            # File should be cached
            assert result1.exists()

    def test_use_cached_file(self, connector, tmp_path):
        """Test that cached files are reused."""
        # Create a cached file
        cache_path = Path(str(connector.cache.cache_dir)) / "test.dta"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("cached data")

        # Set modification time to recent
        import time

        os.utime(cache_path, (time.time(), time.time()))

        with patch.object(connector, "session") as mock_session:
            connector.connect()

            # Should use cached file without downloading
            result = connector._download_file(
                "https://example.com/data.dta", "test.dta", force_download=False
            )

            # Should not have called session.get
            mock_session.get.assert_not_called()
            assert result == cache_path

    def test_force_download_bypasses_cache(self, connector):
        """Test that force_download bypasses cache."""
        # Create a cached file
        cache_path = Path(str(connector.cache.cache_dir)) / "test.dta"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("old cached data")

        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.headers = {"content-length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"new data"]
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response

            connector.connect()

            # Should download even though cached file exists
            result = connector._download_file(
                "https://example.com/data.dta", "test.dta", force_download=True
            )

            # Should have downloaded
            mock_session.get.assert_called_once()


# ============================================================
# EDGE CASE TESTS
# ============================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_dataframe_filtering(self, connector):
        """Test filtering on empty DataFrame."""
        empty_df = pd.DataFrame(columns=["state", "county", "tract"])

        # Should handle empty data gracefully
        connector._atlas_data = empty_df
        result = connector.fetch_opportunity_atlas(geography="tract", state="44")

        assert len(result) == 0
        assert isinstance(result, pd.DataFrame)

    def test_missing_geographic_columns(self, connector):
        """Test data with missing geographic columns."""
        df = pd.DataFrame(
            {
                "kfr_pooled_pooled_p25": [0.45, 0.48],
                # Missing state, county, tract
            }
        )

        with patch("pandas.read_stata") as mock_read:
            mock_read.return_value = df
            with patch.object(connector, "_download_file") as mock_download:
                mock_download.return_value = Path("/fake/path.dta")

                # Should handle missing columns
                result = connector.fetch_opportunity_atlas(geography="tract")
                assert isinstance(result, pd.DataFrame)

    def test_very_large_state_code(self, connector, sample_stata_data):
        """Test with invalid large state FIPS code."""
        with patch("pandas.read_stata") as mock_read:
            mock_read.return_value = sample_stata_data
            with patch.object(connector, "_download_file") as mock_download:
                mock_download.return_value = Path("/fake/path.dta")

                # State codes should be 01-56, test beyond range
                result = connector.fetch_opportunity_atlas(geography="tract", state="99")
                assert len(result) == 0

    def test_null_values_in_metrics(self, connector, sample_stata_data):
        """Test handling of null values in metric columns."""
        with patch("pandas.read_stata") as mock_read:
            mock_read.return_value = sample_stata_data
            with patch.object(connector, "_download_file") as mock_download:
                mock_download.return_value = Path("/fake/path.dta")

                result = connector.fetch_opportunity_atlas(
                    geography="tract", metrics=["kfr_black_p25"]  # Has nulls in sample data
                )

                # Should preserve nulls
                assert result["kfr_black_p25"].isna().any()


# ============================================================
# INTEGRATION-LIKE TESTS (using mocked data)
# ============================================================


class TestDataFlow:
    """Test complete data flow scenarios."""

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_complete_fetch_workflow(self, mock_download, mock_read, connector, sample_stata_data):
        """Test complete workflow from fetch to filtered result."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read.return_value = sample_stata_data

        # Complete workflow
        connector.connect()
        result = connector.fetch_opportunity_atlas(
            geography="tract", state="44", metrics=["kfr_pooled_p25", "jail_pooled_p25"]
        )

        # Verify complete flow
        assert connector.session is not None
        assert len(result) == 3  # 3 tracts in RI
        assert "kfr_pooled_p25" in result.columns
        assert "jail_pooled_p25" in result.columns
        assert all(result["state"] == "44")

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_aggregation_workflow(self, mock_download, mock_read, connector, sample_stata_data):
        """Test workflow with aggregation."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read.return_value = sample_stata_data

        # Fetch tract data
        tract_data = connector.fetch_opportunity_atlas(geography="tract", state="44")

        # Aggregate to county
        county_data = connector.aggregate_to_county(tract_data)

        # Verify aggregation
        assert len(county_data) < len(tract_data)
        assert "county" in county_data.columns


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=krl_data_connectors.mobility", "--cov-report=term-missing"])
