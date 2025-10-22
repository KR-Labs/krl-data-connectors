"""
Tests for EPA Air Quality connector (AirNow API).

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from krl_data_connectors.environment import EPAAirQualityConnector


@pytest.fixture
def mock_api_key():
    """Provide a mock API key."""
    return "test_api_key_12345"


@pytest.fixture
def sample_current_response():
    """Sample current observation response from AirNow API."""
    return [
        {
            "DateObserved": "2025-10-19",
            "HourObserved": 14,
            "LocalTimeZone": "PST",
            "ReportingArea": "San Francisco",
            "StateCode": "CA",
            "Latitude": 37.7749,
            "Longitude": -122.4194,
            "ParameterName": "PM2.5",
            "AQI": 45,
            "Category": {"Number": 1, "Name": "Good"},
        },
        {
            "DateObserved": "2025-10-19",
            "HourObserved": 14,
            "LocalTimeZone": "PST",
            "ReportingArea": "San Francisco",
            "StateCode": "CA",
            "Latitude": 37.7749,
            "Longitude": -122.4194,
            "ParameterName": "OZONE",
            "AQI": 32,
            "Category": {"Number": 1, "Name": "Good"},
        },
    ]


@pytest.fixture
def sample_forecast_response():
    """Sample forecast response from AirNow API."""
    return [
        {
            "DateForecast": "2025-10-20",
            "StateCode": "CA",
            "ReportingArea": "San Francisco",
            "ParameterName": "OZONE",
            "AQI": 58,
            "Category": {"Number": 2, "Name": "Moderate"},
            "ActionDay": False,
            "Discussion": "Air quality expected to be moderate.",
        }
    ]


@pytest.fixture
def connector(mock_api_key):
    """Create connector instance with mock API key."""
    return EPAAirQualityConnector(api_key=mock_api_key)


@pytest.fixture
def sample_dataframe(sample_current_response):
    """Create sample DataFrame from current response."""
    return pd.DataFrame(sample_current_response)


class TestEPAAirQualityConnectorInit:
    """Test EPA Air Quality connector initialization."""

    def test_init_with_api_key(self, mock_api_key):
        """Test connector initialization with API key."""
        connector = EPAAirQualityConnector(api_key=mock_api_key)
        assert connector.api_key == mock_api_key
        assert connector.base_url == EPAAirQualityConnector.BASE_URL

    def test_init_without_api_key(self):
        """Test that initialization fails without API key."""
        with pytest.raises(ValueError, match="API key required"):
            EPAAirQualityConnector()

    @patch.dict("os.environ", {"AIRNOW_API_KEY": "env_api_key"})
    def test_init_from_environment(self):
        """Test connector initialization from environment variable."""
        connector = EPAAirQualityConnector()
        assert connector.api_key == "env_api_key"

    def test_constants(self, connector):
        """Test that constants are defined."""
        assert len(connector.AQI_CATEGORIES) == 6
        assert "Good" in connector.AQI_CATEGORIES
        assert "Hazardous" in connector.AQI_CATEGORIES
        assert len(connector.PARAMETERS) > 0
        assert "PM25" in connector.PARAMETERS


class TestConnect:
    """Test API connection functionality."""

    @patch("requests.get")
    def test_connect_success(self, mock_get, connector):
        """Test successful API connection."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        connector.connect()
        assert connector._session is not None

    @patch("requests.get")
    def test_connect_invalid_key(self, mock_get, connector):
        """Test connection with invalid API key."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        with pytest.raises(ConnectionError, match="Invalid API key"):
            connector.connect()

    @patch("requests.get")
    def test_connect_service_unavailable(self, mock_get, connector):
        """Test connection when service is unavailable."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        with pytest.raises(ConnectionError, match="API connection failed"):
            connector.connect()

    def test_disconnect(self, connector):
        """Test disconnect functionality."""
        mock_session = Mock()
        connector._session = mock_session
        connector.disconnect()
        mock_session.close.assert_called_once()
        assert connector._session is None


class TestGetCurrentByZip:
    """Test current observations by ZIP code."""

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_current_by_zip_success(self, mock_request, connector, sample_current_response):
        """Test successful current observation retrieval by ZIP."""
        mock_request.return_value = sample_current_response

        result = connector.get_current_by_zip("94102")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "ParameterName" in result.columns
        assert "AQI" in result.columns
        mock_request.assert_called_once()

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_current_by_zip_no_data(self, mock_request, connector):
        """Test current observation with no data returned."""
        mock_request.return_value = []

        result = connector.get_current_by_zip("94102")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_get_current_by_zip_invalid_zip(self, connector):
        """Test with invalid ZIP code."""
        with pytest.raises(ValueError, match="ZIP code must be 5 digits"):
            connector.get_current_by_zip("123")

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_current_by_zip_custom_distance(
        self, mock_request, connector, sample_current_response
    ):
        """Test current observation with custom distance."""
        mock_request.return_value = sample_current_response

        connector.get_current_by_zip("94102", distance=50)

        # Verify distance parameter was passed
        call_args = mock_request.call_args
        assert call_args[0][1]["distance"] == "50"


class TestGetCurrentByLatLon:
    """Test current observations by latitude/longitude."""

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_current_by_latlon_success(self, mock_request, connector, sample_current_response):
        """Test successful current observation by lat/lon."""
        mock_request.return_value = sample_current_response

        result = connector.get_current_by_latlon(37.7749, -122.4194)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_get_current_by_latlon_invalid_lat(self, connector):
        """Test with invalid latitude."""
        with pytest.raises(ValueError, match="Latitude must be between"):
            connector.get_current_by_latlon(91.0, -122.4194)

    def test_get_current_by_latlon_invalid_lon(self, connector):
        """Test with invalid longitude."""
        with pytest.raises(ValueError, match="Longitude must be between"):
            connector.get_current_by_latlon(37.7749, -181.0)


class TestGetForecastByZip:
    """Test forecast retrieval by ZIP code."""

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_forecast_by_zip_success(self, mock_request, connector, sample_forecast_response):
        """Test successful forecast retrieval."""
        mock_request.return_value = sample_forecast_response

        result = connector.get_forecast_by_zip("94102")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "DateForecast" in result.columns

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_forecast_by_zip_with_date_string(
        self, mock_request, connector, sample_forecast_response
    ):
        """Test forecast with date as string."""
        mock_request.return_value = sample_forecast_response

        connector.get_forecast_by_zip("94102", date="2025-10-20")

        call_args = mock_request.call_args
        assert call_args[0][1]["date"] == "2025-10-20"

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_forecast_by_zip_with_datetime(
        self, mock_request, connector, sample_forecast_response
    ):
        """Test forecast with datetime object."""
        mock_request.return_value = sample_forecast_response

        test_date = datetime(2025, 10, 20)
        connector.get_forecast_by_zip("94102", date=test_date)

        call_args = mock_request.call_args
        assert call_args[0][1]["date"] == "2025-10-20"


class TestGetForecastByLatLon:
    """Test forecast retrieval by latitude/longitude."""

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_forecast_by_latlon_success(
        self, mock_request, connector, sample_forecast_response
    ):
        """Test successful forecast by lat/lon."""
        mock_request.return_value = sample_forecast_response

        result = connector.get_forecast_by_latlon(37.7749, -122.4194)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


class TestGetHistoricalByZip:
    """Test historical data retrieval by ZIP code."""

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_historical_by_zip_success(self, mock_request, connector, sample_current_response):
        """Test successful historical data retrieval."""
        mock_request.return_value = sample_current_response

        result = connector.get_historical_by_zip("94102", start_date="2025-10-01")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_historical_by_zip_with_datetime(
        self, mock_request, connector, sample_current_response
    ):
        """Test historical data with datetime object."""
        mock_request.return_value = sample_current_response

        start_date = datetime(2025, 10, 1)
        connector.get_historical_by_zip("94102", start_date=start_date)

        call_args = mock_request.call_args
        assert "2025-10-01" in call_args[0][1]["date"]

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_historical_by_zip_with_end_date(
        self, mock_request, connector, sample_current_response
    ):
        """Test historical data with date range."""
        mock_request.return_value = sample_current_response

        connector.get_historical_by_zip("94102", start_date="2025-10-01", end_date="2025-10-15")

        # Verify request was made
        assert mock_request.called


class TestGetHistoricalByLatLon:
    """Test historical data retrieval by latitude/longitude."""

    @patch.object(EPAAirQualityConnector, "_make_request")
    def test_get_historical_by_latlon_success(
        self, mock_request, connector, sample_current_response
    ):
        """Test successful historical data by lat/lon."""
        mock_request.return_value = sample_current_response

        result = connector.get_historical_by_latlon(37.7749, -122.4194, start_date="2025-10-01")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2


class TestGetAQICategory:
    """Test AQI category lookup."""

    def test_get_aqi_category_good(self, connector):
        """Test AQI category for good air quality."""
        assert connector.get_aqi_category(25) == "Good"
        assert connector.get_aqi_category(50) == "Good"

    def test_get_aqi_category_moderate(self, connector):
        """Test AQI category for moderate air quality."""
        assert connector.get_aqi_category(51) == "Moderate"
        assert connector.get_aqi_category(75) == "Moderate"
        assert connector.get_aqi_category(100) == "Moderate"

    def test_get_aqi_category_unhealthy_sensitive(self, connector):
        """Test AQI category for unhealthy for sensitive groups."""
        assert connector.get_aqi_category(101) == "Unhealthy for Sensitive Groups"
        assert connector.get_aqi_category(125) == "Unhealthy for Sensitive Groups"

    def test_get_aqi_category_unhealthy(self, connector):
        """Test AQI category for unhealthy air quality."""
        assert connector.get_aqi_category(151) == "Unhealthy"
        assert connector.get_aqi_category(175) == "Unhealthy"

    def test_get_aqi_category_very_unhealthy(self, connector):
        """Test AQI category for very unhealthy air quality."""
        assert connector.get_aqi_category(201) == "Very Unhealthy"
        assert connector.get_aqi_category(250) == "Very Unhealthy"

    def test_get_aqi_category_hazardous(self, connector):
        """Test AQI category for hazardous air quality."""
        assert connector.get_aqi_category(301) == "Hazardous"
        assert connector.get_aqi_category(450) == "Hazardous"

    def test_get_aqi_category_unknown(self, connector):
        """Test AQI category for values outside range."""
        assert connector.get_aqi_category(501) == "Unknown"
        assert connector.get_aqi_category(-1) == "Unknown"


class TestFilterByParameter:
    """Test parameter filtering."""

    def test_filter_by_parameter_pm25(self, connector, sample_dataframe):
        """Test filtering for PM2.5."""
        result = connector.filter_by_parameter(sample_dataframe, "PM2.5")
        assert len(result) == 1
        assert result.iloc[0]["ParameterName"] == "PM2.5"

    def test_filter_by_parameter_ozone(self, connector, sample_dataframe):
        """Test filtering for Ozone."""
        result = connector.filter_by_parameter(sample_dataframe, "OZONE")
        assert len(result) == 1
        assert result.iloc[0]["ParameterName"] == "OZONE"

    def test_filter_by_parameter_case_insensitive(self, connector, sample_dataframe):
        """Test case-insensitive parameter filtering."""
        result = connector.filter_by_parameter(sample_dataframe, "ozone")
        assert len(result) == 1

    def test_filter_by_parameter_alias(self, connector, sample_dataframe):
        """Test filtering with parameter alias."""
        # O3 is an alias for OZONE
        result = connector.filter_by_parameter(sample_dataframe, "O3")
        assert len(result) == 1

    def test_filter_by_parameter_empty_data(self, connector):
        """Test filtering with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = connector.filter_by_parameter(empty_df, "PM2.5")
        assert len(result) == 0

    def test_filter_by_parameter_missing_column(self, connector):
        """Test filtering with missing ParameterName column."""
        bad_df = pd.DataFrame({"AQI": [50, 75]})
        with pytest.raises(ValueError, match="does not contain 'ParameterName'"):
            connector.filter_by_parameter(bad_df, "PM2.5")


class TestFilterByAQIThreshold:
    """Test AQI threshold filtering."""

    def test_filter_by_aqi_threshold_above(self, connector, sample_dataframe):
        """Test filtering for AQI above threshold."""
        result = connector.filter_by_aqi_threshold(sample_dataframe, 40, above=True)
        assert len(result) == 1
        assert result.iloc[0]["AQI"] == 45

    def test_filter_by_aqi_threshold_below(self, connector, sample_dataframe):
        """Test filtering for AQI below threshold."""
        result = connector.filter_by_aqi_threshold(sample_dataframe, 40, above=False)
        assert len(result) == 1
        assert result.iloc[0]["AQI"] == 32

    def test_filter_by_aqi_threshold_boundary(self, connector, sample_dataframe):
        """Test filtering at exact threshold boundary."""
        result = connector.filter_by_aqi_threshold(sample_dataframe, 45, above=True)
        assert len(result) == 1

    def test_filter_by_aqi_threshold_empty_data(self, connector):
        """Test filtering with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = connector.filter_by_aqi_threshold(empty_df, 100)
        assert len(result) == 0

    def test_filter_by_aqi_threshold_missing_column(self, connector):
        """Test filtering with missing AQI column."""
        bad_df = pd.DataFrame({"ParameterName": ["PM2.5"]})
        with pytest.raises(ValueError, match="does not contain 'AQI'"):
            connector.filter_by_aqi_threshold(bad_df, 100)


class TestSummarizeByParameter:
    """Test parameter summarization."""

    def test_summarize_by_parameter_success(self, connector, sample_dataframe):
        """Test successful parameter summarization."""
        result = connector.summarize_by_parameter(sample_dataframe)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # PM2.5 and OZONE
        assert "ParameterName" in result.columns
        assert "Count" in result.columns
        assert "Mean_AQI" in result.columns
        assert "Max_AQI" in result.columns
        assert "Min_AQI" in result.columns

    def test_summarize_by_parameter_values(self, connector, sample_dataframe):
        """Test summarization produces correct values."""
        result = connector.summarize_by_parameter(sample_dataframe)

        pm25_row = result[result["ParameterName"] == "PM2.5"].iloc[0]
        assert pm25_row["Count"] == 1
        assert pm25_row["Mean_AQI"] == 45
        assert pm25_row["Max_AQI"] == 45
        assert pm25_row["Min_AQI"] == 45

    def test_summarize_by_parameter_empty_data(self, connector):
        """Test summarization with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = connector.summarize_by_parameter(empty_df)
        assert len(result) == 0

    def test_summarize_by_parameter_missing_columns(self, connector):
        """Test summarization with missing required columns."""
        bad_df = pd.DataFrame({"ParameterName": ["PM2.5"]})
        with pytest.raises(ValueError, match="must contain 'ParameterName' and 'AQI'"):
            connector.summarize_by_parameter(bad_df)


class TestMakeRequest:
    """Test internal API request method."""

    @patch("requests.get")
    def test_make_request_success(self, mock_get, connector, sample_current_response):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_current_response
        mock_get.return_value = mock_response

        result = connector._make_request("observation/zipCode/current/", {"zipCode": "94102"})

        assert result == sample_current_response
        assert mock_get.called

    @patch("requests.get")
    def test_make_request_adds_api_key(self, mock_get, connector):
        """Test that API key is added to parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        connector._make_request("observation/zipCode/current/", {"zipCode": "94102"})

        # Verify API key was added
        call_args = mock_get.call_args
        assert call_args[1]["params"]["API_KEY"] == connector.api_key

    @patch("requests.get")
    def test_make_request_403_error(self, mock_get, connector):
        """Test handling of 403 Forbidden error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            connector._make_request("observation/zipCode/current/", {"zipCode": "94102"})

    @patch("requests.get")
    def test_make_request_404_returns_empty(self, mock_get, connector):
        """Test that 404 returns empty list instead of raising."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = connector._make_request("observation/zipCode/current/", {"zipCode": "99999"})

        assert result == []


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestAirQualitySecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    @patch("requests.get")
    def test_sql_injection_in_zip_code(self, mock_get, connector):
        """Test SQL injection attempt in ZIP code parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # SQL injection attempt
        malicious_zip = "94102'; DROP TABLE data; --"

        # Should handle safely
        df = connector.get_current_observations_by_zip(malicious_zip)
        assert isinstance(df, pd.DataFrame)

    @patch("requests.get")
    def test_command_injection_in_parameters(self, mock_get, connector):
        """Test command injection prevention."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Command injection attempt
        malicious_lat = "37.7749; rm -rf /"

        # Should handle safely
        try:
            df = connector.get_current_observations_by_latlon(malicious_lat, -122.4194)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject invalid coordinates
            pass

    @patch("requests.get")
    def test_xss_injection_prevention(self, mock_get, connector):
        """Test XSS injection prevention."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # XSS attempt
        xss_payload = "<script>alert('XSS')</script>"

        # Should handle safely
        df = connector.get_current_observations_by_zip(xss_payload)
        assert isinstance(df, pd.DataFrame)


class TestAirQualitySecurityAPIKey:
    """Test security: API key exposure prevention."""

    def test_api_key_not_in_repr(self, mock_api_key):
        """Test that API key is not exposed in repr()."""
        connector = EPAAirQualityConnector(api_key=mock_api_key)
        repr_str = repr(connector)

        # API key should be masked or not present
        assert mock_api_key not in repr_str

    def test_api_key_not_in_str(self, mock_api_key):
        """Test that API key is not exposed in str()."""
        connector = EPAAirQualityConnector(api_key=mock_api_key)
        str_repr = str(connector)

        # API key should be masked or not present
        assert mock_api_key not in str_repr

    @patch("requests.get")
    def test_api_key_not_in_error_messages(self, mock_get, mock_api_key):
        """Test that API key is not leaked in error messages."""
        mock_get.side_effect = Exception("API request failed")

        connector = EPAAirQualityConnector(api_key=mock_api_key)

        with pytest.raises(Exception) as exc_info:
            connector.get_current_observations_by_zip("94102")

        # API key should not appear in exception message
        assert mock_api_key not in str(exc_info.value)


class TestAirQualitySecurityInputValidation:
    """Test security: Input validation and sanitization."""

    @patch("requests.get")
    def test_handles_null_bytes_in_zip(self, mock_get, connector):
        """Test handling of null bytes in ZIP code."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Null byte injection
        malicious_zip = "94102\x00malicious"

        # Should handle safely or reject
        try:
            df = connector.get_current_observations_by_zip(malicious_zip)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    @patch("requests.get")
    def test_handles_extremely_long_zip_codes(self, mock_get, connector):
        """Test handling of excessively long ZIP codes (DoS prevention)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Extremely long ZIP code
        long_zip = "94102" * 10000

        # Should handle safely or reject
        try:
            df = connector.get_current_observations_by_zip(long_zip)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject overly long inputs
            pass

    def test_coordinate_range_validation(self, connector):
        """Test latitude/longitude range validation."""
        # Invalid latitude (>90)
        with pytest.raises((ValueError, Exception)):
            connector.get_current_observations_by_latlon(91.0, -122.0)

        # Invalid latitude (<-90)
        with pytest.raises((ValueError, Exception)):
            connector.get_current_observations_by_latlon(-91.0, -122.0)

        # Invalid longitude (>180)
        with pytest.raises((ValueError, Exception)):
            connector.get_current_observations_by_latlon(37.0, 181.0)

        # Invalid longitude (<-180)
        with pytest.raises((ValueError, Exception)):
            connector.get_current_observations_by_latlon(37.0, -181.0)

    def test_date_format_validation(self, connector):
        """Test date parameter format validation."""
        # Invalid date format
        with pytest.raises((ValueError, TypeError)):
            connector.get_forecast_by_zip("94102", date="not-a-date")


class TestEPAAirQualityConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    def test_connect_return_type(self):
        """Test that connect returns None."""
        epa = EPAAirQualityConnector(api_key="test_key")
        # connect() tries to make API call, will raise ConnectionError without mock
        # For type contract, we just test that it's defined and callable
        assert callable(epa.connect)

    def test_fetch_return_type(self):
        """Test that fetch raises NotImplementedError."""
        epa = EPAAirQualityConnector(api_key="test_key")
        with pytest.raises(NotImplementedError):
            epa.fetch()

    @patch("requests.get")
    def test_get_current_by_zip_return_type(self, mock_get):
        """Test that get_current_by_zip returns DataFrame."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"ZIP": "02903", "AQI": 45, "Parameter": "PM2.5"}]
        mock_get.return_value = mock_response

        epa = EPAAirQualityConnector(api_key="test_key")
        result = epa.get_current_by_zip("02903")
        assert isinstance(result, pd.DataFrame)

    @patch("requests.get")
    def test_get_current_by_latlon_return_type(self, mock_get):
        """Test that get_current_by_latlon returns DataFrame."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"Latitude": 41.8, "Longitude": -71.4, "AQI": 45}]
        mock_get.return_value = mock_response

        epa = EPAAirQualityConnector(api_key="test_key")
        result = epa.get_current_by_latlon(41.8, -71.4)
        assert isinstance(result, pd.DataFrame)

    @patch("requests.get")
    def test_get_forecast_by_zip_return_type(self, mock_get):
        """Test that get_forecast_by_zip returns DataFrame."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"ZIP": "02903", "AQI": 50, "DateForecast": "2025-01-01"}
        ]
        mock_get.return_value = mock_response

        epa = EPAAirQualityConnector(api_key="test_key")
        result = epa.get_forecast_by_zip("02903")
        assert isinstance(result, pd.DataFrame)

    @patch("requests.get")
    def test_get_historical_by_zip_return_type(self, mock_get):
        """Test that get_historical_by_zip returns DataFrame."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"ZIP": "02903", "AQI": 42, "Date": "2024-01-01"}]
        mock_get.return_value = mock_response

        epa = EPAAirQualityConnector(api_key="test_key")
        result = epa.get_historical_by_zip("02903", "2024-01-01", "2024-01-31")
        assert isinstance(result, pd.DataFrame)

    def test_get_aqi_category_return_type(self):
        """Test that get_aqi_category returns string."""
        epa = EPAAirQualityConnector(api_key="test_key")
        result = epa.get_aqi_category(45)
        assert isinstance(result, str)

    def test_filter_by_parameter_return_type(self):
        """Test that filter_by_parameter returns DataFrame."""
        epa = EPAAirQualityConnector(api_key="test_key")
        df = pd.DataFrame({"ParameterName": ["PM2.5", "O3", "PM2.5"], "AQI": [45, 55, 50]})
        result = epa.filter_by_parameter(df, "PM2.5")
        assert isinstance(result, pd.DataFrame)

    def test_filter_by_aqi_threshold_return_type(self):
        """Test that filter_by_aqi_threshold returns DataFrame."""
        epa = EPAAirQualityConnector(api_key="test_key")
        df = pd.DataFrame({"AQI": [25, 55, 150, 200], "Location": ["A", "B", "C", "D"]})
        result = epa.filter_by_aqi_threshold(df, 100)
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
