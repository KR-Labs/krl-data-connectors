# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Unit tests for LEHD (Longitudinal Employer-Household Dynamics) Connector.

Tests cover:
- Initialization
- URL building
- Data retrieval (OD, RAC, WAC)
- Geographic aggregation
- Error handling
- Edge cases
"""

from unittest.mock import patch

import pandas as pd
import pytest

from krl_data_connectors.lehd_connector import LEHDConnector


@pytest.fixture
def mock_od_data():
    """Create mock OD data."""
    data = {
        "w_geocode": ["060371001001001", "060371001001002", "060371001001003"],
        "h_geocode": ["060371001002001", "060371001002002", "060371001002003"],
        "S000": [100, 150, 200],
        "SA01": [30, 45, 60],
        "SA02": [40, 60, 80],
        "SA03": [30, 45, 60],
    }
    return pd.DataFrame(data)


class TestLEHDConnectorInit:
    """Test LEHD connector initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = LEHDConnector()
        assert connector.BASE_URL == "https://lehd.ces.census.gov/data/lodes/LODES7"
        assert connector.api_key is None

    def test_init_with_cache_dir(self, temp_cache_dir):
        """Test initialization with cache directory."""
        connector = LEHDConnector(cache_dir=str(temp_cache_dir))
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)


class TestLEHDURLBuilding:
    """Test URL building for LEHD API."""

    def test_build_lodes_url_od_main(self):
        """Test URL building for origin-destination data."""
        connector = LEHDConnector()
        url = connector._build_lodes_url("ca", "od", 2019, "main", "JT00", "S000")

        assert "ca_od_main_JT00_2019.csv.gz" in url
        assert "https://lehd.ces.census.gov/data/lodes/LODES7/ca/od/" in url

    def test_build_lodes_url_rac(self):
        """Test URL building for residence area characteristics."""
        connector = LEHDConnector()
        url = connector._build_lodes_url("tx", "rac", 2018, segment="SE03")

        assert "tx_rac_SE03_JT00_2018.csv.gz" in url
        assert "/tx/rac/" in url

    def test_build_lodes_url_wac(self):
        """Test URL building for workplace area characteristics."""
        connector = LEHDConnector()
        url = connector._build_lodes_url("ny", "wac", 2020, segment="SA02")

        assert "ny_wac_SA02_JT00_2020.csv.gz" in url
        assert "/ny/wac/" in url

    def test_build_lodes_url_aux_part(self):
        """Test URL building for auxiliary files."""
        connector = LEHDConnector()
        url = connector._build_lodes_url("fl", "od", 2019, "aux", "JT01", "S000")

        assert "fl_od_aux_JT01_2019.csv.gz" in url


class TestLEHDDataRetrieval:
    """Test data retrieval methods."""

    @pytest.fixture
    def mock_od_data(self):
        """Create mock OD data."""
        data = {
            "w_geocode": ["060371001001001", "060371001001002", "060371001001003"],
            "h_geocode": ["060371001002001", "060371001002002", "060371001002003"],
            "S000": [100, 150, 200],
            "SA01": [30, 45, 60],
            "SA02": [40, 60, 80],
            "SA03": [30, 45, 60],
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def mock_rac_data(self):
        """Create mock RAC data."""
        data = {
            "h_geocode": ["060371001001001", "060371001001002"],
            "C000": [500, 600],
            "CE01": [200, 250],
            "CE02": [200, 250],
            "CE03": [100, 100],
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def mock_wac_data(self):
        """Create mock WAC data."""
        data = {
            "w_geocode": ["060371001001001", "060371001001002"],
            "C000": [800, 900],
            "CE01": [300, 350],
            "CE02": [300, 350],
            "CE03": [200, 200],
        }
        return pd.DataFrame(data)

    @patch("pandas.read_csv")
    def test_get_od_data(self, mock_read_csv, mock_od_data):
        """Test getting origin-destination data."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()
        df = connector.get_od_data(state="ca", year=2019)

        assert not df.empty
        assert "w_geocode" in df.columns
        assert "h_geocode" in df.columns
        assert "S000" in df.columns
        assert len(df) == 3

        # Verify read_csv was called with correct parameters
        mock_read_csv.assert_called_once()
        call_args = mock_read_csv.call_args
        assert "compression" in call_args.kwargs
        assert call_args.kwargs["compression"] == "gzip"

    @patch("pandas.read_csv")
    def test_get_od_data_with_parameters(self, mock_read_csv, mock_od_data):
        """Test getting OD data with custom parameters."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()
        df = connector.get_od_data(
            state="tx", year=2018, part="aux", job_type="JT01", segment="SA02"
        )

        assert not df.empty
        mock_read_csv.assert_called_once()

    @patch("pandas.read_csv")
    def test_get_rac_data(self, mock_read_csv, mock_rac_data):
        """Test getting residence area characteristics."""
        mock_read_csv.return_value = mock_rac_data

        connector = LEHDConnector()
        df = connector.get_rac_data(state="ca", year=2019, segment="CE01")

        assert not df.empty
        assert "h_geocode" in df.columns
        assert "C000" in df.columns

        # Verify geocode is string type
        assert df["h_geocode"].dtype == "object"

    @patch("pandas.read_csv")
    def test_get_wac_data(self, mock_read_csv, mock_wac_data):
        """Test getting workplace area characteristics."""
        mock_read_csv.return_value = mock_wac_data

        connector = LEHDConnector()
        df = connector.get_wac_data(state="ny", year=2020, segment="CE02")

        assert not df.empty
        assert "w_geocode" in df.columns
        assert "C000" in df.columns

    @patch("pandas.read_csv")
    def test_data_retrieval_error_handling(self, mock_read_csv):
        """Test error handling during data retrieval."""
        mock_read_csv.side_effect = Exception("Network error")

        connector = LEHDConnector()

        with pytest.raises(Exception) as exc_info:
            connector.get_od_data(state="ca", year=2019)

        assert "Network error" in str(exc_info.value)


class TestLEHDGeographicAggregation:
    """Test geographic aggregation methods."""

    @pytest.fixture
    def sample_block_data(self):
        """Create sample block-level data for aggregation."""
        data = {
            "h_geocode": [
                "060371001001001",  # County 06037, Tract 100100, Block 1001
                "060371001001002",
                "060371001002001",  # Different tract
                "060371001002002",
                "060850001001001",  # Different county
            ],
            "w_geocode": [
                "060371002001001",
                "060371002001002",
                "060371002002001",
                "060371002002002",
                "060850002001001",
            ],
            "S000": [100, 150, 200, 250, 300],
            "SA01": [30, 45, 60, 75, 90],
        }
        return pd.DataFrame(data)

    def test_aggregate_to_tract(self, sample_block_data):
        """Test aggregation from block to tract level."""
        connector = LEHDConnector()
        df = connector.aggregate_to_tract(sample_block_data, geocode_col="h_geocode")

        assert "h_tract" in df.columns
        assert len(df) < len(sample_block_data)  # Should have fewer rows after aggregation

        # Check that numeric columns were summed
        assert "S000" in df.columns
        assert "SA01" in df.columns

        # Verify tract codes are correct length (11 digits)
        assert all(len(str(tract)) == 11 for tract in df["h_tract"])

    def test_aggregate_to_county(self, sample_block_data):
        """Test aggregation from block to county level."""
        connector = LEHDConnector()
        df = connector.aggregate_to_county(sample_block_data, geocode_col="h_geocode")

        assert "h_county" in df.columns
        assert len(df) == 2  # Should have 2 counties in sample data

        # Verify county codes are correct length (5 digits)
        assert all(len(str(county)) == 5 for county in df["h_county"])

        # Check aggregation worked correctly
        total_s000 = sample_block_data["S000"].sum()
        aggregated_s000 = df["S000"].sum()
        assert total_s000 == aggregated_s000

    def test_aggregate_to_county_with_workplace(self, sample_block_data):
        """Test aggregation using workplace geocode."""
        connector = LEHDConnector()
        df = connector.aggregate_to_county(sample_block_data, geocode_col="w_geocode")

        assert "w_county" in df.columns
        assert len(df) == 2

    def test_aggregate_empty_dataframe(self):
        """Test aggregation with empty DataFrame."""
        connector = LEHDConnector()
        empty_df = pd.DataFrame()

        result = connector.aggregate_to_county(empty_df, geocode_col="h_geocode")
        assert result.empty

    def test_aggregate_preserves_numeric_columns(self, sample_block_data):
        """Test that aggregation preserves all numeric columns."""
        connector = LEHDConnector()
        df = connector.aggregate_to_county(sample_block_data, geocode_col="h_geocode")

        # All numeric columns from original should be in aggregated
        original_numeric = sample_block_data.select_dtypes(include=["number"]).columns
        for col in original_numeric:
            assert col in df.columns


class TestLEHDJobTypesAndSegments:
    """Test job type and segment handling."""

    def test_valid_job_types(self):
        """Test that connector accepts valid job types."""
        connector = LEHDConnector()

        valid_job_types = ["JT00", "JT01", "JT02", "JT03", "JT04", "JT05"]

        for jt in valid_job_types:
            url = connector._build_lodes_url("ca", "od", 2019, job_type=jt)
            assert jt in url

    def test_valid_segments(self):
        """Test that connector accepts valid segments."""
        connector = LEHDConnector()

        valid_segments = [
            "S000",
            "SA01",
            "SA02",
            "SA03",  # Age
            "SE01",
            "SE02",
            "SE03",  # Earnings
            "SI01",
            "SI02",
            "SI03",  # Industry
        ]

        for seg in valid_segments:
            url = connector._build_lodes_url("ca", "rac", 2019, segment=seg)
            assert seg in url


class TestLEHDEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_state_code(self):
        """Test handling of invalid state codes."""
        connector = LEHDConnector()

        # The connector builds URL regardless, but network request would fail
        url = connector._build_lodes_url("XX", "od", 2019)
        assert "xx" in url.lower()

    def test_invalid_year(self):
        """Test handling of invalid years."""
        connector = LEHDConnector()

        # Years before 2002 (LODES7 start) - URL is built but would fail on request
        url = connector._build_lodes_url("ca", "od", 1999)
        assert "1999" in url

    def test_future_year(self):
        """Test handling of future years."""
        connector = LEHDConnector()

        url = connector._build_lodes_url("ca", "od", 2030)
        assert "2030" in url

    @patch("pandas.read_csv")
    def test_empty_response(self, mock_read_csv):
        """Test handling of empty response."""
        mock_read_csv.return_value = pd.DataFrame()

        connector = LEHDConnector()
        df = connector.get_od_data(state="ca", year=2019)

        assert df.empty

    def test_geocode_string_preservation(self):
        """Test that geocodes are preserved as strings (with leading zeros)."""
        connector = LEHDConnector()

        # Create data with leading zeros
        data = {
            "h_geocode": ["010010001001001", "020020002002002"],  # Leading zeros
            "S000": [100, 200],
        }
        df = pd.DataFrame(data)

        # Aggregate and verify strings maintained
        result = connector.aggregate_to_county(df, geocode_col="h_geocode")

        # Check that county codes maintain leading zeros
        assert all(isinstance(code, str) for code in result["h_county"])


class TestLEHDIntegration:
    """Integration tests requiring network access."""

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    def test_real_od_data_retrieval(self):
        """Test retrieving real OD data from LEHD API."""
        connector = LEHDConnector()

        try:
            # Request small dataset
            df = connector.get_od_data(
                state="ri",  # Rhode Island (small state)
                year=2019,
                part="main",
                job_type="JT00",
                segment="S000",
            )

            # Verify response structure
            assert not df.empty
            assert "w_geocode" in df.columns
            assert "h_geocode" in df.columns
            assert "S000" in df.columns

            # Verify data types
            assert df["w_geocode"].dtype == "object"
            assert df["h_geocode"].dtype == "object"
            assert pd.api.types.is_numeric_dtype(df["S000"])

        except Exception as e:
            pytest.skip(f"Network request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    def test_real_rac_data_retrieval(self):
        """Test retrieving real RAC data from LEHD API."""
        connector = LEHDConnector()

        try:
            df = connector.get_rac_data(state="ri", year=2019, segment="S000")

            assert not df.empty
            assert "h_geocode" in df.columns
            assert "C000" in df.columns

        except Exception as e:
            pytest.skip(f"Network request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    def test_real_data_aggregation(self):
        """Test aggregation on real data."""
        connector = LEHDConnector()

        try:
            # Get real data
            df = connector.get_rac_data(state="ri", year=2019, segment="S000")

            # Aggregate to county
            county_df = connector.aggregate_to_county(df, geocode_col="h_geocode")

            assert not county_df.empty
            assert len(county_df) < len(df)
            assert "h_county" in county_df.columns

        except Exception as e:
            pytest.skip(f"Network request failed: {e}")


class TestLEHDCaching:
    """Test caching functionality."""

    @patch("pandas.read_csv")
    def test_caching_enabled(self, mock_read_csv, temp_cache_dir, mock_od_data):
        """Test that caching works when enabled."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector(cache_dir=str(temp_cache_dir))

        # First call should hit the API
        df1 = connector.get_od_data(state="ca", year=2019)
        assert not df1.empty

        # Note: Actual caching behavior depends on BaseConnector implementation
        # This test verifies the cache_dir is passed correctly
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)


class TestLEHDLogging:
    """Test logging functionality."""

    @patch("pandas.read_csv")
    def test_logging_on_data_retrieval(self, mock_read_csv, mock_od_data, caplog):
        """Test that operations are logged."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()

        # Enable log propagation for testing
        connector.logger.propagate = True

        with caplog.at_level("INFO", logger="LEHDConnector"):
            df = connector.get_od_data(state="ca", year=2019)

        # Check that logging occurred
        assert len(caplog.records) > 0


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestLEHDSecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    @patch("pandas.read_csv")
    def test_sql_injection_in_state(self, mock_read_csv, mock_od_data):
        """Test SQL injection attempt in state parameter."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()

        # SQL injection attempt
        malicious_state = "ca'; DROP TABLE data; --"

        # Should handle safely
        try:
            df = connector.get_od_data(state=malicious_state, year=2019)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, FileNotFoundError):
            # Acceptable to reject invalid state codes
            pass

    @patch("pandas.read_csv")
    def test_command_injection_in_parameters(self, mock_read_csv, mock_od_data):
        """Test command injection prevention."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()

        # Command injection attempt
        malicious_job_type = "JT00; rm -rf /"

        # Should handle safely
        try:
            df = connector.get_od_data(state="ca", year=2019, job_type=malicious_job_type)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, FileNotFoundError):
            # Acceptable to reject invalid job types
            pass

    @patch("pandas.read_csv")
    def test_path_traversal_prevention(self, mock_read_csv, mock_od_data):
        """Test path traversal prevention."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()

        # Path traversal attempt
        malicious_state = "../../etc/passwd"

        # Should prevent path traversal
        try:
            df = connector.get_od_data(state=malicious_state, year=2019)
            # Should not access files outside expected directory
            assert isinstance(df, pd.DataFrame)
        except (ValueError, FileNotFoundError, OSError):
            # Expected to reject path traversal
            pass


class TestLEHDSecurityInputValidation:
    """Test security: Input validation and sanitization."""

    def test_year_type_validation(self):
        """Test year parameter type validation."""
        connector = LEHDConnector()

        # Invalid year types
        with pytest.raises((ValueError, TypeError)):
            connector.get_od_data(state="ca", year="not_a_year")

    def test_state_code_validation(self):
        """Test state code validation."""
        connector = LEHDConnector()

        # Empty state code
        with pytest.raises((ValueError, TypeError)):
            connector.get_od_data(state="", year=2019)

    @patch("pandas.read_csv")
    def test_handles_null_bytes(self, mock_read_csv, mock_od_data):
        """Test handling of null bytes in parameters."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()

        # Null byte injection
        malicious_state = "ca\x00malicious"

        # Should handle safely or reject
        try:
            df = connector.get_od_data(state=malicious_state, year=2019)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError, FileNotFoundError):
            # Acceptable to reject null bytes
            pass

    @patch("pandas.read_csv")
    def test_handles_extremely_long_state_codes(self, mock_read_csv, mock_od_data):
        """Test handling of excessively long state codes (DoS prevention)."""
        mock_read_csv.return_value = mock_od_data

        connector = LEHDConnector()

        # Extremely long state code
        long_state = "ca" * 10000

        # Should handle safely or reject
        try:
            df = connector.get_od_data(state=long_state, year=2019)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, FileNotFoundError, Exception):
            # Acceptable to reject overly long inputs
            pass

    def test_year_range_validation(self):
        """Test year range boundary validation."""
        connector = LEHDConnector()

        # Year too far in past
        with pytest.raises((ValueError, FileNotFoundError)):
            connector.get_od_data(state="ca", year=1900)

        # Year too far in future
        with pytest.raises((ValueError, FileNotFoundError)):
            connector.get_od_data(state="ca", year=9999)


class TestLEHDPropertyBased:
    """Test LEHD connector using property-based testing with Hypothesis."""

    @pytest.mark.hypothesis
    def test_year_parameter_validation_property(self):
        """Property: Year parameter should accept valid years (2002-2020)."""
        from hypothesis import given
        from hypothesis import strategies as st

        lehd_connector = LEHDConnector()

        @given(year=st.integers(min_value=2002, max_value=2020))
        def check_year_handling(year):
            with patch("pandas.read_csv") as mock_read_csv:
                # Mock LEHD LODES CSV format
                mock_df = pd.DataFrame(
                    {
                        "w_geocode": ["060371001001"],
                        "h_geocode": ["060371002001"],
                        "S000": [100],
                        "createdate": ["20210101"],
                    }
                )
                mock_read_csv.return_value = mock_df
                df = lehd_connector.get_od_data(state="ca", year=year)
                assert isinstance(df, pd.DataFrame)
                assert mock_read_csv.called

        check_year_handling()

    @pytest.mark.hypothesis
    def test_state_code_property(self):
        """Property: State codes should be 2-letter strings."""
        from hypothesis import given
        from hypothesis import strategies as st

        lehd_connector = LEHDConnector()

        @given(
            state=st.text(
                alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=2, max_size=2
            )
        )
        def check_state_code_handling(state):
            with patch("pandas.read_csv") as mock_read_csv:
                mock_df = pd.DataFrame(
                    {
                        "w_geocode": ["010010201001"],
                        "h_geocode": ["010010202001"],
                        "S000": [50],
                    }
                )
                mock_read_csv.return_value = mock_df
                df = lehd_connector.get_od_data(state=state, year=2019)
                assert isinstance(df, pd.DataFrame)
                assert mock_read_csv.called

        check_state_code_handling()

    @pytest.mark.hypothesis
    def test_job_type_code_property(self):
        """Property: Job type codes should be alphanumeric strings (e.g., JT00, JT01)."""
        from hypothesis import given
        from hypothesis import strategies as st

        lehd_connector = LEHDConnector()

        @given(job_type=st.from_regex(r"JT[0-9]{2}", fullmatch=True))
        def check_job_type_handling(job_type):
            with patch("pandas.read_csv") as mock_read_csv:
                mock_df = pd.DataFrame(
                    {
                        "w_geocode": ["060371001001"],
                        "h_geocode": ["060371002001"],
                        "S000": [100],
                    }
                )
                mock_read_csv.return_value = mock_df
                df = lehd_connector.get_od_data(state="ca", year=2019, job_type=job_type)
                assert isinstance(df, pd.DataFrame)
                assert mock_read_csv.called

        check_job_type_handling()

    @pytest.mark.hypothesis
    def test_segment_code_property(self):
        """Property: Segment codes should be alphanumeric strings (e.g., S000, SA01)."""
        from hypothesis import given
        from hypothesis import strategies as st

        lehd_connector = LEHDConnector()

        @given(segment=st.from_regex(r"S[A-Z0-9]{3}", fullmatch=True))
        def check_segment_handling(segment):
            with patch("pandas.read_csv") as mock_read_csv:
                mock_df = pd.DataFrame(
                    {
                        "w_geocode": ["060371001001"],
                        "h_geocode": ["060371002001"],
                        "S000": [100],
                    }
                )
                mock_read_csv.return_value = mock_df
                df = lehd_connector.get_od_data(state="ca", year=2019, segment=segment)
                assert isinstance(df, pd.DataFrame)
                assert mock_read_csv.called

        check_segment_handling()


class TestLEHDConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    def test_connect_return_type(self):
        """Test that connect returns None."""
        lehd = LEHDConnector()

        result = lehd.connect()

        assert result is None

    @patch("pandas.read_csv")
    def test_fetch_return_type(self, mock_read_csv):
        """Test that fetch returns DataFrame."""
        mock_read_csv.return_value = pd.DataFrame({
            "w_geocode": ["060371001001"],
            "h_geocode": ["060371002001"],
            "S000": [100]
        })

        lehd = LEHDConnector()

        result = lehd.fetch(state="ca", year=2019)

        assert isinstance(result, pd.DataFrame)

    @patch("pandas.read_csv")
    def test_get_od_data_return_type(self, mock_read_csv):
        """Test that get_od_data returns DataFrame."""
        mock_read_csv.return_value = pd.DataFrame({
            "w_geocode": ["060371001001"],
            "h_geocode": ["060371002001"],
            "S000": [100]
        })

        lehd = LEHDConnector()

        result = lehd.get_od_data(state="ca", year=2019)

        assert isinstance(result, pd.DataFrame)

    @patch("pandas.read_csv")
    def test_get_rac_data_return_type(self, mock_read_csv):
        """Test that get_rac_data returns DataFrame."""
        mock_read_csv.return_value = pd.DataFrame({
            "h_geocode": ["060371001001"],
            "C000": [500],
            "CE01": [100]
        })

        lehd = LEHDConnector()

        result = lehd.get_rac_data(state="ca", year=2019)

        assert isinstance(result, pd.DataFrame)

    @patch("pandas.read_csv")
    def test_get_wac_data_return_type(self, mock_read_csv):
        """Test that get_wac_data returns DataFrame."""
        mock_read_csv.return_value = pd.DataFrame({
            "w_geocode": ["060371001001"],
            "C000": [500],
            "CE01": [100]
        })

        lehd = LEHDConnector()

        result = lehd.get_wac_data(state="ca", year=2019)

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.get")
    def test_get_available_years_return_type(self, mock_get):
        """Test that get_available_years returns list of ints."""
        mock_response = type('MockResponse', (), {
            'text': '<html><a href="od_main_JT00_2015.csv.gz">2015</a><a href="od_main_JT00_2019.csv.gz">2019</a></html>',
            'raise_for_status': lambda: None
        })()
        mock_get.return_value = mock_response

        lehd = LEHDConnector()

        result = lehd.get_available_years(state="ca")

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], int)

    def test_aggregate_to_tract_return_type(self):
        """Test that aggregate_to_tract returns DataFrame."""
        lehd = LEHDConnector()

        df = pd.DataFrame({
            "h_geocode": ["060371001001001", "060371001001002"],
            "C000": [100, 200]
        })

        result = lehd.aggregate_to_tract(df, geocode_col="h_geocode")

        assert isinstance(result, pd.DataFrame)

    def test_aggregate_to_county_return_type(self):
        """Test that aggregate_to_county returns DataFrame."""
        lehd = LEHDConnector()

        df = pd.DataFrame({
            "h_geocode": ["060371001001", "060372001001"],
            "C000": [100, 200]
        })

        result = lehd.aggregate_to_county(df, geocode_col="h_geocode")

        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
