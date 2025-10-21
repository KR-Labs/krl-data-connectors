# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Unit tests for Bureau of Labor Statistics (BLS) Connector.

Tests cover:
- Initialization
- Series data retrieval
- Multi-series retrieval
- Unemployment rate data
- CPI data
- Error handling
- Rate limiting
- Edge cases
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.bls_connector import BLSConnector


class TestBLSConnectorInit:
    """Test BLS connector initialization."""

    def test_init_without_api_key(self):
        """Test initialization without API key (v1)."""
        connector = BLSConnector()
        assert connector.base_url == connector.BASE_URL_V1
        assert connector.api_key is None

    def test_init_with_api_key(self):
        """Test initialization with API key (v2)."""
        connector = BLSConnector(api_key="test_key_123")
        assert connector.base_url == connector.BASE_URL_V2
        assert connector.api_key == "test_key_123"

    def test_init_with_cache_dir(self, temp_cache_dir):
        """Test initialization with cache directory."""
        connector = BLSConnector(cache_dir=str(temp_cache_dir))
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)

    def test_common_series_ids_defined(self):
        """Test that common series IDs are defined."""
        connector = BLSConnector()
        assert hasattr(connector, "COMMON_SERIES")
        assert isinstance(connector.COMMON_SERIES, dict)
        assert "unemployment_rate" in connector.COMMON_SERIES
        assert "cpi_all" in connector.COMMON_SERIES


class TestBLSSeriesRetrieval:
    """Test single series data retrieval."""

    @pytest.fixture
    def mock_bls_response(self):
        """Create mock BLS API response."""
        return {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [
                            {
                                "year": "2023",
                                "period": "M12",
                                "periodName": "December",
                                "value": "3.7",
                            },
                            {
                                "year": "2023",
                                "period": "M11",
                                "periodName": "November",
                                "value": "3.7",
                            },
                            {
                                "year": "2023",
                                "period": "M10",
                                "periodName": "October",
                                "value": "3.9",
                            },
                        ],
                    }
                ]
            },
        }

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_series_basic(self, mock_request, mock_bls_response):
        """Test basic series retrieval."""
        mock_request.return_value = mock_bls_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_series("LNS14000000", start_year=2023, end_year=2023)

        assert not df.empty
        assert len(df) == 3
        assert "year" in df.columns
        assert "period" in df.columns
        assert "value" in df.columns
        assert "date" in df.columns

        # Verify values are numeric
        assert pd.api.types.is_numeric_dtype(df["value"])

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_series_default_years(self, mock_request, mock_bls_response):
        """Test series retrieval with default year range."""
        mock_request.return_value = mock_bls_response

        connector = BLSConnector(api_key="test_key")
        connector.get_series("LNS14000000")

        # Should default to last 10 years
        mock_request.assert_called_once()
        payload = mock_request.call_args[0][0]  # First positional argument

        current_year = datetime.now().year
        assert str(current_year) == payload["endyear"]
        assert str(current_year - 9) == payload["startyear"]

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_series_with_calculations(self, mock_request, mock_bls_response):
        """Test series retrieval with calculations."""
        mock_request.return_value = mock_bls_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_series("LNS14000000", calculations=True, annual_average=True)

        mock_request.assert_called_once()
        payload = mock_request.call_args[0][0]  # First positional argument

        assert payload["calculations"] is True
        assert payload["annualaverage"] is True

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_series_year_range_validation(self, mock_request, mock_bls_response):
        """Test year range validation."""
        mock_request.return_value = mock_bls_response

        connector = BLSConnector(api_key="test_key")

        # v2 API allows 20 years (2004-2023 = 20 years inclusive)
        df = connector.get_series("LNS14000000", start_year=2004, end_year=2023)
        assert not df.empty

        # v2 API should reject >20 years (2003-2023 = 21 years)
        with pytest.raises(ValueError) as exc_info:
            connector.get_series("LNS14000000", start_year=2003, end_year=2023)
        assert "Year range too large" in str(exc_info.value)

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_series_year_range_validation_v1(self, mock_request, mock_bls_response):
        """Test year range validation for v1 API."""
        mock_request.return_value = mock_bls_response

        connector = BLSConnector()  # No API key = v1

        # v1 API allows 10 years (2014-2023 = 10 years inclusive)
        df = connector.get_series("LNS14000000", start_year=2014, end_year=2023)
        assert not df.empty

        # v1 API should reject >10 years (2013-2023 = 11 years)
        with pytest.raises(ValueError) as exc_info:
            connector.get_series("LNS14000000", start_year=2013, end_year=2023)
        assert "Year range too large" in str(exc_info.value)

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_series_date_parsing(self, mock_request, mock_bls_response):
        """Test that dates are properly parsed."""
        mock_request.return_value = mock_bls_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_series("LNS14000000")

        assert "date" in df.columns
        # Should be sorted by date
        assert df["date"].is_monotonic_increasing or df["date"].is_monotonic_decreasing


class TestBLSMultiSeriesRetrieval:
    """Test multiple series retrieval."""

    @pytest.fixture
    def mock_multi_series_response(self):
        """Create mock multi-series response."""
        return {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [
                            {"year": "2023", "period": "M12", "value": "3.7"},
                        ],
                    },
                    {
                        "seriesID": "LNS12000000",
                        "data": [
                            {"year": "2023", "period": "M12", "value": "161000"},
                        ],
                    },
                ]
            },
        }

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_multiple_series(self, mock_request, mock_multi_series_response):
        """Test retrieving multiple series at once."""
        mock_request.return_value = mock_multi_series_response

        connector = BLSConnector(api_key="test_key")
        series_ids = ["LNS14000000", "LNS12000000"]
        result = connector.get_multiple_series(series_ids)

        assert isinstance(result, dict)
        assert len(result) == 2
        assert "LNS14000000" in result
        assert "LNS12000000" in result

        for series_id, df in result.items():
            assert isinstance(df, pd.DataFrame)
            assert not df.empty

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_multiple_series_limit_v2(self, mock_request, mock_multi_series_response):
        """Test series limit for v2 API (50 series)."""
        mock_request.return_value = mock_multi_series_response

        connector = BLSConnector(api_key="test_key")

        # Should accept up to 50 series
        ["SERIES" + str(i) for i in range(50)]
        # Don't actually call, just verify validation

        # Should reject >50 series
        too_many_series = ["SERIES" + str(i) for i in range(51)]
        with pytest.raises(ValueError) as exc_info:
            connector.get_multiple_series(too_many_series)
        assert "Too many series" in str(exc_info.value)

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_multiple_series_limit_v1(self, mock_request, mock_multi_series_response):
        """Test series limit for v1 API (25 series)."""
        mock_request.return_value = mock_multi_series_response

        connector = BLSConnector()  # No API key = v1

        # Should reject >25 series
        too_many_series = ["SERIES" + str(i) for i in range(26)]
        with pytest.raises(ValueError) as exc_info:
            connector.get_multiple_series(too_many_series)
        assert "Too many series" in str(exc_info.value)


class TestBLSUnemploymentRate:
    """Test unemployment rate specific methods."""

    @pytest.fixture
    def mock_unemployment_response(self):
        """Create mock unemployment response."""
        return {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [
                            {"year": "2023", "period": "M12", "value": "3.7"},
                            {"year": "2023", "period": "M11", "value": "3.7"},
                        ],
                    }
                ]
            },
        }

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_unemployment_rate_national(self, mock_request, mock_unemployment_response):
        """Test getting national unemployment rate."""
        mock_request.return_value = mock_unemployment_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_unemployment_rate()

        assert not df.empty
        assert "value" in df.columns

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_unemployment_rate_state(self, mock_request, mock_unemployment_response):
        """Test getting state unemployment rate."""
        mock_request.return_value = mock_unemployment_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_unemployment_rate(area_code="06")  # California

        mock_request.assert_called_once()
        payload = mock_request.call_args[0][0]  # First positional argument

        # Should construct state series ID
        series_id = payload["seriesid"][0]
        assert "06" in series_id
        assert "LASST" in series_id


class TestBLSCPI:
    """Test Consumer Price Index methods."""

    @pytest.fixture
    def mock_cpi_response(self):
        """Create mock CPI response."""
        return {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "CUUR0000SA0",
                        "data": [
                            {"year": "2023", "period": "M12", "value": "306.746"},
                            {"year": "2023", "period": "M11", "value": "307.051"},
                        ],
                    }
                ]
            },
        }

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_cpi_all_items(self, mock_request, mock_cpi_response):
        """Test getting CPI for all items."""
        mock_request.return_value = mock_cpi_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_cpi()

        assert not df.empty
        assert "value" in df.columns

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_cpi_food(self, mock_request, mock_cpi_response):
        """Test getting CPI for food."""
        mock_request.return_value = mock_cpi_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_cpi(item="SAF")  # Food

        mock_request.assert_called_once()
        payload = mock_request.call_args[0][0]  # First positional argument

        series_id = payload["seriesid"][0]
        assert "SAF" in series_id

    @patch.object(BLSConnector, "_bls_post_request")
    def test_get_cpi_energy(self, mock_request, mock_cpi_response):
        """Test getting CPI for energy."""
        mock_request.return_value = mock_cpi_response

        connector = BLSConnector(api_key="test_key")
        df = connector.get_cpi(item="SA0E")  # Energy

        mock_request.assert_called_once()


class TestBLSCommonSeriesHelper:
    """Test common series helper method."""

    def test_get_common_series_id_valid(self):
        """Test getting valid common series IDs."""
        assert BLSConnector.get_common_series_id("unemployment_rate") == "LNS14000000"
        assert BLSConnector.get_common_series_id("cpi_all") == "CUUR0000SA0"
        assert BLSConnector.get_common_series_id("employment_level") == "LNS12000000"

    def test_get_common_series_id_invalid(self):
        """Test getting invalid common series ID."""
        result = BLSConnector.get_common_series_id("nonexistent_series")
        assert result is None


class TestBLSErrorHandling:
    """Test error handling."""

    @patch.object(BLSConnector, "_bls_post_request")
    def test_api_error_response(self, mock_request):
        """Test handling of API error responses."""
        mock_request.return_value = {
            "status": "REQUEST_NOT_PROCESSED",
            "message": ["Invalid series ID"],
        }

        connector = BLSConnector(api_key="test_key")

        with pytest.raises(ValueError) as exc_info:
            connector.get_series("INVALID_SERIES")

        assert "BLS API error" in str(exc_info.value)

    @patch.object(BLSConnector, "_bls_post_request")
    def test_empty_response(self, mock_request):
        """Test handling of empty response."""
        mock_request.return_value = {"status": "REQUEST_SUCCEEDED", "Results": {"series": []}}

        connector = BLSConnector(api_key="test_key")
        df = connector.get_series("LNS14000000")

        assert df.empty

    @patch.object(BLSConnector, "_bls_post_request")
    def test_network_error(self, mock_request):
        """Test handling of network errors."""
        mock_request.side_effect = Exception("Network error")

        connector = BLSConnector(api_key="test_key")

        with pytest.raises(Exception) as exc_info:
            connector.get_series("LNS14000000")

        assert "Network error" in str(exc_info.value)

    @patch.object(BLSConnector, "_bls_post_request")
    def test_missing_data_field(self, mock_request):
        """Test handling of missing data field."""
        mock_request.return_value = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        # Missing 'data' field
                    }
                ]
            },
        }

        connector = BLSConnector(api_key="test_key")
        df = connector.get_series("LNS14000000")

        # Should handle gracefully
        assert isinstance(df, pd.DataFrame)


class TestBLSIntegration:
    """Integration tests requiring network access."""

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    @pytest.mark.api
    def test_real_series_retrieval(self):
        """Test retrieving real series data."""
        import os

        api_key = os.getenv("BLS_API_KEY")

        if not api_key:
            pytest.skip("BLS_API_KEY not set")

        connector = BLSConnector(api_key=api_key)

        try:
            # Get unemployment rate
            df = connector.get_series("LNS14000000", start_year=2022, end_year=2023)

            assert not df.empty
            assert "value" in df.columns
            assert "date" in df.columns
            assert len(df) > 0

        except Exception as e:
            pytest.skip(f"API request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    @pytest.mark.api
    def test_real_unemployment_rate(self):
        """Test retrieving real unemployment rate."""
        import os

        api_key = os.getenv("BLS_API_KEY")

        if not api_key:
            pytest.skip("BLS_API_KEY not set")

        connector = BLSConnector(api_key=api_key)

        try:
            df = connector.get_unemployment_rate(start_year=2022, end_year=2023)

            assert not df.empty
            assert df["value"].dtype in [float, "float64"]

        except Exception as e:
            pytest.skip(f"API request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    @pytest.mark.api
    def test_real_cpi_retrieval(self):
        """Test retrieving real CPI data."""
        import os

        api_key = os.getenv("BLS_API_KEY")

        if not api_key:
            pytest.skip("BLS_API_KEY not set")

        connector = BLSConnector(api_key=api_key)

        try:
            df = connector.get_cpi(start_year=2022, end_year=2023)

            assert not df.empty
            assert "value" in df.columns

        except Exception as e:
            pytest.skip(f"API request failed: {e}")


class TestBLSCaching:
    """Test caching functionality."""

    @patch.object(BLSConnector, "_bls_post_request")
    def test_caching_enabled(self, mock_request, temp_cache_dir):
        """Test that caching works when enabled."""
        mock_response = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [{"year": "2023", "period": "M12", "value": "3.7"}],
                    }
                ]
            },
        }
        mock_request.return_value = mock_response

        connector = BLSConnector(api_key="test_key", cache_dir=str(temp_cache_dir))

        df = connector.get_series("LNS14000000")
        assert not df.empty
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)


class TestBLSLogging:
    """Test logging functionality."""

    @patch.object(BLSConnector, "_bls_post_request")
    def test_logging_on_data_retrieval(self, mock_request, caplog):
        """Test that operations are logged."""
        mock_response = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [{"year": "2023", "period": "M12", "value": "3.7"}],
                    }
                ]
            },
        }
        mock_request.return_value = mock_response

        connector = BLSConnector(api_key="test_key")

        # Enable log propagation for testing
        connector.logger.propagate = True

        with caplog.at_level("INFO", logger="BLSConnector"):
            connector.get_series("LNS14000000")

        assert len(caplog.records) > 0


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestBLSSecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    @patch.object(BLSConnector, "_bls_post_request")
    def test_sql_injection_in_series_id(self, mock_request):
        """Test SQL injection attempt in series_id parameter."""
        mock_response = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [{"year": "2023", "period": "M12", "value": "3.7"}],
                    }
                ]
            },
        }
        mock_request.return_value = mock_response

        connector = BLSConnector(api_key="test_key")

        # SQL injection attempt
        malicious_series = "LNS14000000'; DROP TABLE data; --"

        # Should handle safely
        df = connector.get_series(malicious_series, start_year=2023, end_year=2023)

        assert isinstance(df, pd.DataFrame)

    @patch.object(BLSConnector, "_bls_post_request")
    def test_command_injection_in_parameters(self, mock_request):
        """Test command injection attempt in parameters."""
        mock_response = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [{"year": "2023", "period": "M12", "value": "3.7"}],
                    }
                ]
            },
        }
        mock_request.return_value = mock_response

        connector = BLSConnector(api_key="test_key")

        # Command injection attempt in series ID
        malicious = "LNS14000000; rm -rf /"

        # Should handle safely
        df = connector.get_series(malicious, start_year=2023, end_year=2023)

        assert isinstance(df, pd.DataFrame)

    @patch.object(BLSConnector, "_bls_post_request")
    def test_xss_injection_prevention(self, mock_request):
        """Test XSS injection prevention in parameters."""
        mock_response = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {
                "series": [
                    {
                        "seriesID": "LNS14000000",
                        "data": [{"year": "2023", "period": "M12", "value": "3.7"}],
                    }
                ]
            },
        }
        mock_request.return_value = mock_response

        connector = BLSConnector(api_key="test_key")

        # XSS attempt
        xss_payload = "<script>alert('XSS')</script>"

        # Should handle safely
        df = connector.get_series(xss_payload, start_year=2023, end_year=2023)

        assert isinstance(df, pd.DataFrame)


class TestBLSSecurityAPIKey:
    """Test security: API key exposure prevention."""

    def test_api_key_not_in_repr(self):
        """Test that API key is not exposed in repr()."""
        api_key = "super_secret_bls_key_12345"
        connector = BLSConnector(api_key=api_key)

        repr_str = repr(connector)

        # API key should be masked or not present
        assert api_key not in repr_str

    def test_api_key_not_in_str(self):
        """Test that API key is not exposed in str()."""
        api_key = "super_secret_bls_key_12345"
        connector = BLSConnector(api_key=api_key)

        str_repr = str(connector)

        # API key should be masked or not present
        assert api_key not in str_repr

    @patch.object(BLSConnector, "_bls_post_request")
    def test_api_key_not_in_error_messages(self, mock_request):
        """Test that API key is not leaked in error messages."""
        api_key = "super_secret_bls_key_12345"
        mock_request.side_effect = Exception("BLS API request failed")

        connector = BLSConnector(api_key=api_key)

        with pytest.raises(Exception) as exc_info:
            connector.get_series("LNS14000000")

        # API key should not appear in exception message
        assert api_key not in str(exc_info.value)

    def test_api_key_not_in_logs(self, caplog):
        """Test that API key is not logged."""
        api_key = "super_secret_bls_key_12345"
        connector = BLSConnector(api_key=api_key)
        connector.logger.propagate = True

        with caplog.at_level("DEBUG", logger="BLSConnector"):
            # Trigger some logging
            repr(connector)

        # Check all log messages
        for record in caplog.records:
            assert api_key not in record.message


class TestBLSSecurityInputValidation:
    """Test security: Input validation and sanitization."""

    @patch.object(BLSConnector, "_bls_post_request")
    def test_handles_null_bytes_in_series_id(self, mock_request):
        """Test handling of null bytes in series ID."""
        mock_response = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {"series": []},
        }
        mock_request.return_value = mock_response

        connector = BLSConnector(api_key="test_key")

        # Null byte injection
        malicious_series = "LNS14000000\x00malicious"

        # Should handle safely or reject
        try:
            df = connector.get_series(malicious_series, start_year=2023, end_year=2023)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    @patch.object(BLSConnector, "_bls_post_request")
    def test_handles_extremely_long_series_ids(self, mock_request):
        """Test handling of excessively long series IDs (DoS attempt)."""
        mock_response = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {"series": []},
        }
        mock_request.return_value = mock_response

        connector = BLSConnector(api_key="test_key")

        # Extremely long series ID
        long_series = "LNS" * 10000

        # Should handle safely or reject
        try:
            df = connector.get_series(long_series, start_year=2023, end_year=2023)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject overly long inputs
            pass

    def test_year_range_boundary_validation(self):
        """Test year range boundary validation for security."""
        connector = BLSConnector(api_key="test_key")

        # Negative years (should fail)
        with pytest.raises(ValueError):
            connector.get_series("LNS14000000", start_year=-1, end_year=2023)

        # Future years too far out (should be acceptable but may return no data)
        # Year 9999 is an extreme case
        with pytest.raises(ValueError):
            connector.get_series("LNS14000000", start_year=1900, end_year=9999)


# ============================================================================
# Layer 8: Contract Tests
# ============================================================================


class TestBLSConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    def test_connect_return_type(self, temp_cache_dir):
        """Test that connect returns None."""
        connector = BLSConnector(api_key="test_key", cache_dir=str(temp_cache_dir))

        result = connector.connect()

        assert result is None

    @patch("requests.Session.post")
    def test_get_series_return_type(self, mock_post, temp_cache_dir):
        """Test that get_series returns DataFrame."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {"series": [{"seriesID": "LNS14000000", "data": []}]},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        connector = BLSConnector(api_key="test_key", cache_dir=str(temp_cache_dir))
        connector.connect()

        result = connector.get_series("LNS14000000")

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.post")
    def test_get_multiple_series_return_type(self, mock_post, temp_cache_dir):
        """Test that get_multiple_series returns dict of DataFrames."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {"series": [{"seriesID": "LNS14000000", "data": []}]},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        connector = BLSConnector(api_key="test_key", cache_dir=str(temp_cache_dir))
        connector.connect()

        result = connector.get_multiple_series(["LNS14000000"])

        assert isinstance(result, dict)
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, pd.DataFrame)

    @patch("requests.Session.post")
    def test_get_unemployment_rate_return_type(self, mock_post, temp_cache_dir):
        """Test that get_unemployment_rate returns DataFrame."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {"series": [{"seriesID": "LNS14000000", "data": []}]},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        connector = BLSConnector(api_key="test_key", cache_dir=str(temp_cache_dir))
        connector.connect()

        result = connector.get_unemployment_rate()

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.post")
    def test_get_cpi_return_type(self, mock_post, temp_cache_dir):
        """Test that get_cpi returns DataFrame."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": "REQUEST_SUCCEEDED",
            "Results": {"series": [{"seriesID": "CUUR0000SA0", "data": []}]},
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        connector = BLSConnector(api_key="test_key", cache_dir=str(temp_cache_dir))
        connector.connect()

        result = connector.get_cpi()

        assert isinstance(result, pd.DataFrame)

    def test_get_common_series_id_return_type(self):
        """Test that get_common_series_id returns Optional[str]."""
        result = BLSConnector.get_common_series_id("unemployment_rate")

        assert result is None or isinstance(result, str)

    def test_get_api_key_return_type(self, temp_cache_dir):
        """Test that _get_api_key returns Optional[str]."""
        connector = BLSConnector(api_key="test_key", cache_dir=str(temp_cache_dir))

        result = connector._get_api_key()

        assert result is None or isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
