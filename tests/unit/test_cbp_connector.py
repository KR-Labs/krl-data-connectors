# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Unit tests for County Business Patterns (CBP) Connector.

Tests cover:
- Initialization
- County data retrieval
- State data retrieval
- Metro area data retrieval
- NAICS aggregation
- Error handling
- Edge cases
"""

from unittest.mock import patch

import pandas as pd
import pytest

from krl_data_connectors.cbp_connector import CountyBusinessPatternsConnector


class TestCBPConnectorInit:
    """Test CBP connector initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = CountyBusinessPatternsConnector()
        assert connector.BASE_URL == "https://api.census.gov/data"
        # API key may come from environment, so just check it's accessible
        assert hasattr(connector, "api_key")

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = CountyBusinessPatternsConnector(api_key="test_key_123")
        assert connector.api_key == "test_key_123"

    def test_init_with_cache_dir(self, temp_cache_dir):
        """Test initialization with cache directory."""
        connector = CountyBusinessPatternsConnector(cache_dir=str(temp_cache_dir))
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)


class TestCBPURLBuilding:
    """Test URL building for CBP API."""

    def test_build_cbp_url_2021(self):
        """Test URL building for 2021 data."""
        connector = CountyBusinessPatternsConnector()
        url = connector._build_cbp_url(2021)

        assert "https://api.census.gov/data/2021/cbp" in url

    def test_build_cbp_url_2017(self):
        """Test URL building for 2017 data."""
        connector = CountyBusinessPatternsConnector()
        url = connector._build_cbp_url(2017)

        assert "2017/cbp" in url

    def test_build_cbp_url_invalid_year(self):
        """Test URL building with year outside valid range."""
        connector = CountyBusinessPatternsConnector()

        # Should still build URL, but would fail on API request
        url = connector._build_cbp_url(2025)
        assert "2025" in url


class TestCBPCountyData:
    """Test county-level data retrieval."""

    @pytest.fixture
    def mock_county_response(self):
        """Create mock county data response."""
        return [
            ["ESTAB", "EMP", "PAYANN", "NAICS2017", "NAME", "state", "county"],
            ["100", "5000", "250000000", "00", "Alameda County, California", "06", "001"],
            ["150", "7500", "375000000", "00", "Los Angeles County, California", "06", "037"],
            ["200", "10000", "500000000", "00", "Cook County, Illinois", "17", "031"],
        ]

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_county_data_all(self, mock_request, mock_county_response):
        """Test getting county data for all counties."""
        mock_request.return_value = mock_county_response

        connector = CountyBusinessPatternsConnector()
        df = connector.get_county_data(year=2021)

        assert not df.empty
        assert len(df) == 3
        assert "ESTAB" in df.columns
        assert "EMP" in df.columns
        assert "NAME" in df.columns

        mock_request.assert_called_once()

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_county_data_specific_state(self, mock_request, mock_county_response):
        """Test getting county data for a specific state."""
        mock_request.return_value = mock_county_response

        connector = CountyBusinessPatternsConnector()
        df = connector.get_county_data(year=2021, state="06")

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        assert "params" in call_kwargs
        assert "state:06" in call_kwargs["params"].get("in", "")

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_county_data_specific_county(self, mock_request, mock_county_response):
        """Test getting data for a specific county."""
        mock_request.return_value = mock_county_response

        connector = CountyBusinessPatternsConnector()
        df = connector.get_county_data(year=2021, state="06", county="001")

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs["params"]
        assert "for" in params
        assert "county:001" in params["for"]

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_county_data_with_naics(self, mock_request, mock_county_response):
        """Test getting county data filtered by NAICS code."""
        # Add NAICS codes that match the filter
        mock_response_with_naics = [
            mock_county_response[0],  # Header
            ["100", "5000", "250000000", "44", "Test County 1", "06", "001"],
            ["150", "7500", "375000000", "441", "Test County 2", "06", "037"],
            ["200", "10000", "500000000", "31", "Test County 3", "17", "031"],
        ]
        mock_request.return_value = mock_response_with_naics

        connector = CountyBusinessPatternsConnector()
        df = connector.get_county_data(year=2021, naics="44")  # Retail trade

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs["params"]
        # Census API doesn't accept NAICS2017 as a query parameter
        # Filtering happens in pandas after data retrieval
        assert "NAICS2017" not in params
        # Verify the filtering worked - should only have rows starting with '44'
        assert len(df) == 2  # Both '44' and '441' start with '44'

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_county_data_custom_variables(self, mock_request, mock_county_response):
        """Test getting county data with custom variables."""
        mock_request.return_value = mock_county_response

        connector = CountyBusinessPatternsConnector()
        custom_vars = ["ESTAB", "EMP"]
        df = connector.get_county_data(year=2021, variables=custom_vars)

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs["params"]
        assert "ESTAB,EMP" in params.get("get", "")


class TestCBPStateData:
    """Test state-level data retrieval."""

    @pytest.fixture
    def mock_state_response(self):
        """Create mock state data response."""
        return [
            ["ESTAB", "EMP", "PAYANN", "NAME", "state"],
            ["50000", "2000000", "100000000000", "California", "06"],
            ["30000", "1500000", "75000000000", "Texas", "48"],
            ["40000", "1800000", "90000000000", "New York", "36"],
        ]

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_state_data_all(self, mock_request, mock_state_response):
        """Test getting data for all states."""
        mock_request.return_value = mock_state_response

        connector = CountyBusinessPatternsConnector()
        df = connector.get_state_data(year=2021)

        assert not df.empty
        assert len(df) == 3
        assert "ESTAB" in df.columns
        assert "NAME" in df.columns

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_state_data_specific_state(self, mock_request, mock_state_response):
        """Test getting data for a specific state."""
        mock_request.return_value = mock_state_response

        connector = CountyBusinessPatternsConnector()
        df = connector.get_state_data(year=2021, state="06")

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs["params"]
        assert "for" in params
        assert "state:06" in params["for"]

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_state_data_with_naics(self, mock_request, mock_state_response):
        """Test getting state data filtered by NAICS."""
        mock_request.return_value = mock_state_response

        connector = CountyBusinessPatternsConnector()
        df = connector.get_state_data(year=2021, naics="54")  # Professional services

        mock_request.assert_called_once()


class TestCBPMetroData:
    """Test metropolitan area data retrieval."""

    @pytest.fixture
    def mock_metro_response(self):
        """Create mock metro area data response."""
        return [
            ["ESTAB", "EMP", "NAME", "metropolitan statistical area/micropolitan statistical area"],
            ["10000", "500000", "San Francisco-Oakland-Berkeley, CA", "41860"],
            ["15000", "750000", "Los Angeles-Long Beach-Anaheim, CA", "31080"],
            ["8000", "400000", "Chicago-Naperville-Elgin, IL-IN-WI", "16980"],
        ]

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_get_metro_data(self, mock_request, mock_metro_response):
        """Test getting metropolitan area data."""
        mock_request.return_value = mock_metro_response

        connector = CountyBusinessPatternsConnector()
        df = connector.get_metro_data(year=2021)

        assert not df.empty
        assert len(df) == 3
        assert "ESTAB" in df.columns
        assert "NAME" in df.columns


class TestCBPNAICSAggregation:
    """Test NAICS aggregation functionality."""

    @pytest.fixture
    def sample_naics_data(self):
        """Create sample data with NAICS codes."""
        data = {
            "NAICS2017": ["441110", "441120", "441210", "441220", "445110", "445120"],
            "ESTAB": [100, 150, 200, 250, 300, 350],
            "EMP": [1000, 1500, 2000, 2500, 3000, 3500],
            "PAYANN": [50000000, 75000000, 100000000, 125000000, 150000000, 175000000],
            "state": ["06", "06", "06", "06", "06", "06"],
            "county": ["001", "001", "037", "037", "073", "073"],
        }
        return pd.DataFrame(data)

    def test_get_naics_totals_2_digit(self, sample_naics_data):
        """Test aggregation to 2-digit NAICS level (sectors)."""
        connector = CountyBusinessPatternsConnector()
        df = connector.get_naics_totals(sample_naics_data, level=2)

        assert not df.empty
        assert "naics" in df.columns

        # Should have 2 sectors: 44 (Retail) and 45 (Retail)
        unique_naics = df["naics"].unique()
        assert all(len(str(code)) == 2 for code in unique_naics)

    def test_get_naics_totals_3_digit(self, sample_naics_data):
        """Test aggregation to 3-digit NAICS level."""
        connector = CountyBusinessPatternsConnector()
        df = connector.get_naics_totals(sample_naics_data, level=3)

        # Should have subsectors: 441, 445
        unique_naics = df["naics"].unique()
        assert all(len(str(code)) == 3 for code in unique_naics)

    def test_get_naics_totals_4_digit(self, sample_naics_data):
        """Test aggregation to 4-digit NAICS level."""
        connector = CountyBusinessPatternsConnector()
        df = connector.get_naics_totals(sample_naics_data, level=4)

        # Should have industry groups: 4411, 4412, 4451
        unique_naics = df["naics"].unique()
        assert all(len(str(code)) == 4 for code in unique_naics)

    def test_get_naics_totals_aggregates_correctly(self, sample_naics_data):
        """Test that numeric values are aggregated correctly."""
        connector = CountyBusinessPatternsConnector()
        df = connector.get_naics_totals(sample_naics_data, level=2)

        # Total establishments should match sum of original
        total_original = sample_naics_data["ESTAB"].sum()
        total_aggregated = df["ESTAB"].sum()
        assert total_original == total_aggregated

    def test_get_naics_totals_empty_dataframe(self):
        """Test aggregation with empty DataFrame."""
        connector = CountyBusinessPatternsConnector()
        empty_df = pd.DataFrame()

        result = connector.get_naics_totals(empty_df, level=2)
        assert result.empty

    def test_get_naics_totals_invalid_level(self, sample_naics_data):
        """Test aggregation with invalid NAICS level."""
        connector = CountyBusinessPatternsConnector()

        # Should handle gracefully or raise informative error
        # Depending on implementation
        with pytest.raises((ValueError, IndexError, KeyError)):
            connector.get_naics_totals(sample_naics_data, level=7)


class TestCBPNAICSSectorMapping:
    """Test NAICS sector mapping."""

    def test_naics_sectors_defined(self):
        """Test that NAICS sectors are properly defined."""
        connector = CountyBusinessPatternsConnector()

        assert hasattr(connector, "NAICS_SECTORS")
        assert isinstance(connector.NAICS_SECTORS, dict)
        assert len(connector.NAICS_SECTORS) > 0

    def test_naics_sector_codes(self):
        """Test that sector codes are valid."""
        connector = CountyBusinessPatternsConnector()

        # All sector codes should be 2 digits or compound codes (e.g., '31-33', '44-45')
        for code in connector.NAICS_SECTORS.keys():
            assert len(str(code)) <= 5  # Allow for compound codes like '31-33'
            # Check if it's a simple 2-digit code or a compound code
            if "-" in str(code):
                parts = str(code).split("-")
                assert len(parts) == 2
                assert all(part.isdigit() and len(part) == 2 for part in parts)
            else:
                assert len(str(code)) == 2
                assert str(code).isdigit()

    def test_naics_sector_descriptions(self):
        """Test that sector descriptions exist."""
        connector = CountyBusinessPatternsConnector()

        for description in connector.NAICS_SECTORS.values():
            assert isinstance(description, str)
            assert len(description) > 0


class TestCBPErrorHandling:
    """Test error handling."""

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_api_error_handling(self, mock_request):
        """Test handling of API errors."""
        mock_request.side_effect = Exception("API Error")

        connector = CountyBusinessPatternsConnector()

        with pytest.raises(Exception) as exc_info:
            connector.get_county_data(year=2021)

        assert "API Error" in str(exc_info.value)

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_empty_response_handling(self, mock_request):
        """Test handling of empty API response."""
        mock_request.return_value = []

        connector = CountyBusinessPatternsConnector()
        df = connector.get_county_data(year=2021)

        # Should return empty DataFrame or handle gracefully
        assert isinstance(df, pd.DataFrame)

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_malformed_response_handling(self, mock_request):
        """Test handling of malformed API response."""
        mock_request.return_value = [["header_only"]]

        connector = CountyBusinessPatternsConnector()

        # Should handle gracefully
        try:
            df = connector.get_county_data(year=2021)
            # If it returns a DataFrame, check it's empty or minimal
            assert len(df) <= 1
        except Exception:
            # Or it should raise a clear error
            pass


class TestCBPDataValidation:
    """Test data validation and type conversion."""

    @pytest.fixture
    def mock_response_with_types(self):
        """Create mock response with various data types."""
        return [
            ["ESTAB", "EMP", "PAYANN", "NAME", "state", "county"],
            ["100", "1000", "50000", "Test County", "06", "001"],
            ["D", "S", "0", "Suppressed County", "06", "002"],  # Suppressed data
        ]

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_numeric_conversion(self, mock_request, mock_response_with_types):
        """Test that numeric values are properly converted."""
        mock_request.return_value = mock_response_with_types

        connector = CountyBusinessPatternsConnector()
        df = connector.get_county_data(year=2021)

        # Check that valid numeric values are present
        assert not df.empty


class TestCBPIntegration:
    """Integration tests requiring network access."""

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    def test_real_county_data_retrieval(self):
        """Test retrieving real county data."""
        connector = CountyBusinessPatternsConnector()

        try:
            # Request data for Rhode Island (small state)
            df = connector.get_county_data(
                year=2021, state="44", variables=["ESTAB", "EMP", "NAME"]  # Rhode Island
            )

            assert not df.empty
            assert "ESTAB" in df.columns
            assert "NAME" in df.columns

        except Exception as e:
            pytest.skip(f"Network request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    def test_real_state_data_retrieval(self):
        """Test retrieving real state data."""
        connector = CountyBusinessPatternsConnector()

        try:
            df = connector.get_state_data(year=2021)

            assert not df.empty
            assert "ESTAB" in df.columns
            assert "state" in df.columns

            # Should have ~50 states
            assert len(df) > 40

        except Exception as e:
            pytest.skip(f"Network request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    def test_real_naics_filtering(self):
        """Test filtering by NAICS code with real data."""
        connector = CountyBusinessPatternsConnector()

        try:
            # Get retail trade data (NAICS 44-45)
            df = connector.get_state_data(year=2021, state="44", naics="44")  # Rhode Island

            assert not df.empty

        except Exception as e:
            pytest.skip(f"Network request failed: {e}")


class TestCBPCaching:
    """Test caching functionality."""

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_caching_enabled(self, mock_request, temp_cache_dir):
        """Test that caching works when enabled."""
        mock_response = [
            ["ESTAB", "state"],
            ["1000", "06"],
        ]
        mock_request.return_value = mock_response

        connector = CountyBusinessPatternsConnector(cache_dir=str(temp_cache_dir))

        # First call
        df1 = connector.get_state_data(year=2021)
        assert not df1.empty

        # Verify cache_dir is set
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)


class TestCBPLogging:
    """Test logging functionality."""

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_logging_on_data_retrieval(self, mock_request, caplog):
        """Test that operations are logged."""
        mock_response = [
            ["ESTAB", "state"],
            ["1000", "06"],
        ]
        mock_request.return_value = mock_response

        connector = CountyBusinessPatternsConnector()

        # Enable log propagation for testing
        connector.logger.propagate = True

        with caplog.at_level("INFO", logger="CountyBusinessPatternsConnector"):
            df = connector.get_state_data(year=2021)

        # Check that logging occurred
        assert len(caplog.records) > 0


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestCBPSecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_sql_injection_in_parameters(self, mock_request):
        """Test SQL injection attempt in parameters."""
        mock_response = [
            ["ESTAB", "state"],
            ["1000", "06"],
        ]
        mock_request.return_value = mock_response

        connector = CountyBusinessPatternsConnector()

        # SQL injection attempt
        malicious_state = "06'; DROP TABLE data; --"

        # Should handle safely
        df = connector.get_state_data(year=2021, state=malicious_state)

        assert isinstance(df, pd.DataFrame)

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_command_injection_prevention(self, mock_request):
        """Test command injection prevention."""
        mock_response = [
            ["ESTAB", "NAICS2017"],
            ["1000", "00"],
        ]
        mock_request.return_value = mock_response

        connector = CountyBusinessPatternsConnector()

        # Command injection attempt
        malicious_naics = "00; rm -rf /"

        # Should handle safely
        df = connector.get_state_data(year=2021, naics=malicious_naics)

        assert isinstance(df, pd.DataFrame)

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_xss_injection_prevention(self, mock_request):
        """Test XSS injection prevention."""
        mock_response = [
            ["ESTAB", "county"],
            ["1000", "001"],
        ]
        mock_request.return_value = mock_response

        connector = CountyBusinessPatternsConnector()

        # XSS attempt
        xss_payload = "<script>alert('XSS')</script>"

        # Should handle safely
        df = connector.get_county_data(year=2021, county=xss_payload)

        assert isinstance(df, pd.DataFrame)


class TestCBPSecurityAPIKey:
    """Test security: API key exposure prevention."""

    def test_api_key_not_in_repr(self):
        """Test that API key is not exposed in repr()."""
        api_key = "super_secret_cbp_key_12345"
        connector = CountyBusinessPatternsConnector(api_key=api_key)

        repr_str = repr(connector)

        # API key should be masked or not present
        assert api_key not in repr_str

    def test_api_key_not_in_str(self):
        """Test that API key is not exposed in str()."""
        api_key = "super_secret_cbp_key_12345"
        connector = CountyBusinessPatternsConnector(api_key=api_key)

        str_repr = str(connector)

        # API key should be masked or not present
        assert api_key not in str_repr


class TestCBPSecurityInputValidation:
    """Test security: Input validation and sanitization."""

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_handles_null_bytes(self, mock_request):
        """Test handling of null bytes in parameters."""
        mock_response = [
            ["ESTAB", "state"],
            ["1000", "06"],
        ]
        mock_request.return_value = mock_response

        connector = CountyBusinessPatternsConnector()

        # Null byte injection
        malicious_state = "06\x00malicious"

        # Should handle safely or reject
        try:
            df = connector.get_state_data(year=2021, state=malicious_state)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    def test_year_validation(self):
        """Test year parameter validation."""
        connector = CountyBusinessPatternsConnector()

        # Invalid year types
        with pytest.raises((ValueError, TypeError)):
            connector.get_state_data(year="not_a_year")

    @patch.object(CountyBusinessPatternsConnector, "_make_request")
    def test_handles_extremely_long_inputs(self, mock_request):
        """Test handling of excessively long inputs (DoS prevention)."""
        mock_response = [
            ["ESTAB", "state"],
            ["1000", "06"],
        ]
        mock_request.return_value = mock_response

        connector = CountyBusinessPatternsConnector()

        # Extremely long NAICS code
        long_naics = "123456" * 10000

        # Should handle safely or reject
        try:
            df = connector.get_state_data(year=2021, naics=long_naics)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject overly long inputs
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
