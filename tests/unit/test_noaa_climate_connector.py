# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for NOAA Climate Data Connector (CDO API).

Test Coverage:
- Connector initialization
- Connection handling with API token
- Dataset queries
- Data category queries
- Data type queries
- Station queries
- Location queries
- Climate data observations
- Temperature and precipitation queries
- Contract tests (Phase 4 Layer 8)
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.environment.noaa_climate_connector import NOAAClimateConnector

# Fixtures


@pytest.fixture
def sample_dataset():
    """Sample NOAA dataset data."""
    return {
        "id": "GHCND",
        "name": "Global Historical Climatology Network - Daily",
        "datacoverage": 1.0,
        "mindate": "1763-01-01",
        "maxdate": "2024-10-20",
    }


@pytest.fixture
def sample_station():
    """Sample weather station data."""
    return {
        "id": "GHCND:USW00023174",
        "name": "SAN FRANCISCO DOWNTOWN, CA US",
        "latitude": 37.77,
        "longitude": -122.42,
        "elevation": 47.5,
        "mindate": "1945-01-01",
        "maxdate": "2024-10-20",
        "datacoverage": 1.0,
    }


@pytest.fixture
def sample_location():
    """Sample location data."""
    return {
        "id": "FIPS:06",
        "name": "California",
        "datacoverage": 1.0,
        "mindate": "1850-01-01",
        "maxdate": "2024-10-20",
    }


@pytest.fixture
def sample_data_type():
    """Sample data type."""
    return {
        "id": "TMAX",
        "name": "Maximum temperature",
        "datacoverage": 1.0,
        "mindate": "1763-01-01",
        "maxdate": "2024-10-20",
    }


@pytest.fixture
def sample_climate_data():
    """Sample climate observation data."""
    return {
        "date": "2024-01-15T00:00:00",
        "datatype": "TMAX",
        "station": "GHCND:USW00023174",
        "attributes": ",,W,",
        "value": 150,
    }


@pytest.fixture
def mock_response_datasets():
    """Mock datasets API response."""
    return {
        "metadata": {"resultset": {"count": 1}},
        "results": [
            {
                "id": "GHCND",
                "name": "Global Historical Climatology Network - Daily",
                "datacoverage": 1.0,
                "mindate": "1763-01-01",
                "maxdate": "2024-10-20",
            }
        ],
    }


@pytest.fixture
def mock_response_stations():
    """Mock stations API response."""
    return {
        "metadata": {"resultset": {"count": 1}},
        "results": [
            {
                "id": "GHCND:USW00023174",
                "name": "SAN FRANCISCO DOWNTOWN, CA US",
                "latitude": 37.77,
                "longitude": -122.42,
                "elevation": 47.5,
            }
        ],
    }


@pytest.fixture
def noaa_connector():
    """Create NOAAClimateConnector instance with mock API key."""
    return NOAAClimateConnector(api_key="test_token")


# Test Classes


class TestNOAAClimateConnectorInit:
    """Test connector initialization."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = NOAAClimateConnector(api_key="test_token")
        assert connector.base_url == NOAAClimateConnector.BASE_URL
        assert connector.api_key == "test_token"

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        connector = NOAAClimateConnector()
        # Should initialize but warn
        assert connector.base_url == NOAAClimateConnector.BASE_URL

    @patch.dict("os.environ", {"NOAA_CDO_TOKEN": "env_token"})
    def test_get_api_key_from_env(self):
        """Test getting API key from environment."""
        connector = NOAAClimateConnector()
        assert connector._get_api_key() == "env_token"

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = NOAAClimateConnector(api_key="test_token", timeout=60)
        assert connector.timeout == 60


class TestNOAAClimateConnectorConnection:
    """Test connection handling."""

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector._init_session"
    )
    def test_connect_success(self, mock_init_session):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_session.get.return_value = mock_response
        mock_init_session.return_value = mock_session

        connector = NOAAClimateConnector(api_key="test_token")
        connector.connect()

        assert connector.session is not None
        # Verify token header was set
        assert "token" in connector.session.headers

    def test_connect_without_api_key(self):
        """Test connection without API key raises error."""
        connector = NOAAClimateConnector()

        with pytest.raises(ValueError, match="API key required"):
            connector.connect()

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector._init_session"
    )
    def test_connect_already_connected(self, mock_init_session):
        """Test connect when already connected."""
        connector = NOAAClimateConnector(api_key="test_token")
        connector.session = MagicMock()

        connector.connect()

        # Should not call _init_session again
        mock_init_session.assert_not_called()


class TestNOAAClimateConnectorGetDatasets:
    """Test get_datasets method."""

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_datasets_success(self, mock_fetch, mock_response_datasets):
        """Test successful retrieval of datasets."""
        mock_fetch.return_value = mock_response_datasets

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_datasets()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["id"].iloc[0] == "GHCND"

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_datasets_specific_id(self, mock_fetch, sample_dataset):
        """Test retrieval of specific dataset."""
        mock_fetch.return_value = sample_dataset

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_datasets(dataset_id="GHCND")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_datasets_empty(self, mock_fetch):
        """Test datasets query with no results."""
        mock_fetch.return_value = {}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_datasets()

        assert isinstance(result, pd.DataFrame)


class TestNOAAClimateConnectorGetDataCategories:
    """Test get_data_categories method."""

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_categories_success(self, mock_fetch):
        """Test successful retrieval of data categories."""
        mock_fetch.return_value = {"results": [{"id": "TEMP", "name": "Air Temperature"}]}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_data_categories()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_categories_specific_id(self, mock_fetch):
        """Test retrieval of specific category."""
        mock_fetch.return_value = {"id": "TEMP", "name": "Air Temperature"}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_data_categories(category_id="TEMP")

        assert isinstance(result, pd.DataFrame)


class TestNOAAClimateConnectorGetDataTypes:
    """Test get_data_types method."""

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_data_types_success(self, mock_fetch, sample_data_type):
        """Test successful retrieval of data types."""
        mock_fetch.return_value = {"results": [sample_data_type]}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_data_types()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_data_types_with_dataset_filter(self, mock_fetch, sample_data_type):
        """Test data types query with dataset filter."""
        mock_fetch.return_value = {"results": [sample_data_type]}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_data_types(dataset_id="GHCND")

        assert isinstance(result, pd.DataFrame)


class TestNOAAClimateConnectorGetStations:
    """Test get_stations method."""

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_stations_success(self, mock_fetch, mock_response_stations):
        """Test successful retrieval of stations."""
        mock_fetch.return_value = mock_response_stations

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_stations()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["id"].iloc[0] == "GHCND:USW00023174"

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_stations_with_location(self, mock_fetch, mock_response_stations):
        """Test stations query with location filter."""
        mock_fetch.return_value = mock_response_stations

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_stations(locationid="FIPS:06")

        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_stations_specific_id(self, mock_fetch, sample_station):
        """Test retrieval of specific station."""
        mock_fetch.return_value = sample_station

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_stations(station_id="GHCND:USW00023174")

        assert isinstance(result, pd.DataFrame)


class TestNOAAClimateConnectorGetLocations:
    """Test get_locations method."""

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_locations_success(self, mock_fetch, sample_location):
        """Test successful retrieval of locations."""
        mock_fetch.return_value = {"results": [sample_location]}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_locations()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_locations_with_category(self, mock_fetch, sample_location):
        """Test locations query with category filter."""
        mock_fetch.return_value = {"results": [sample_location]}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_locations(locationcategoryid="ST")

        assert isinstance(result, pd.DataFrame)


class TestNOAAClimateConnectorGetClimateData:
    """Test get_climate_data method."""

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_climate_data_success(self, mock_fetch, sample_climate_data):
        """Test successful retrieval of climate data."""
        mock_fetch.return_value = {"results": [sample_climate_data]}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_climate_data(
            dataset_id="GHCND", start_date="2024-01-01", end_date="2024-01-31"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "date" in result.columns

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_climate_data_with_filters(self, mock_fetch, sample_climate_data):
        """Test climate data query with multiple filters."""
        mock_fetch.return_value = {"results": [sample_climate_data]}

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_climate_data(
            dataset_id="GHCND",
            start_date="2024-01-01",
            end_date="2024-01-31",
            datatype_id="TMAX",
            stationid="GHCND:USW00023174",
        )

        assert isinstance(result, pd.DataFrame)


class TestNOAAClimateConnectorGetStates:
    """Test get_states method."""

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.get_locations"
    )
    def test_get_states_success(self, mock_get_locations, sample_location):
        """Test successful retrieval of states."""
        mock_get_locations.return_value = pd.DataFrame([sample_location])

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_states()

        assert isinstance(result, pd.DataFrame)
        # Verify it called get_locations with correct params
        mock_get_locations.assert_called_once_with(
            locationcategoryid="ST", limit=NOAAClimateConnector.MAX_LIMIT
        )


class TestNOAAClimateConnectorGetTemperatureData:
    """Test get_temperature_data method."""

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.get_climate_data"
    )
    def test_get_temperature_data_success(self, mock_get_climate_data, sample_climate_data):
        """Test successful retrieval of temperature data."""
        mock_get_climate_data.return_value = pd.DataFrame([sample_climate_data])

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_temperature_data(
            start_date="2024-01-01", end_date="2024-01-31", stationid="GHCND:USW00023174"
        )

        assert isinstance(result, pd.DataFrame)
        # Verify it called get_climate_data with correct params
        assert mock_get_climate_data.called


class TestNOAAClimateConnectorGetPrecipitationData:
    """Test get_precipitation_data method."""

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.get_climate_data"
    )
    def test_get_precipitation_data_success(self, mock_get_climate_data, sample_climate_data):
        """Test successful retrieval of precipitation data."""
        mock_get_climate_data.return_value = pd.DataFrame([sample_climate_data])

        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_precipitation_data(
            start_date="2024-01-01", end_date="2024-01-31", locationid="FIPS:06"
        )

        assert isinstance(result, pd.DataFrame)
        # Verify datatype_id was set to PRCP
        call_kwargs = mock_get_climate_data.call_args[1]
        assert call_kwargs.get("datatype_id") == "PRCP"


class TestNOAAClimateConnectorClose:
    """Test close method."""

    def test_close_closes_session(self):
        """Test that close properly closes session."""
        connector = NOAAClimateConnector()
        mock_session = MagicMock()
        connector.session = mock_session

        connector.close()

        mock_session.close.assert_called_once()
        assert connector.session is None

    def test_close_when_no_session(self):
        """Test close when session is None."""
        connector = NOAAClimateConnector(api_key="test_token")
        connector.session = None

        # Should not raise error
        connector.close()


# Phase 4 Layer 8: Contract Tests


class TestNOAAClimateConnectorTypeContracts:
    """Contract tests for return types (Phase 4 Layer 8)."""

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_datasets_returns_dataframe(self, mock_fetch):
        """Contract: get_datasets returns DataFrame."""
        mock_fetch.return_value = {}
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_datasets()
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_data_categories_returns_dataframe(self, mock_fetch):
        """Contract: get_data_categories returns DataFrame."""
        mock_fetch.return_value = {}
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_data_categories()
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_data_types_returns_dataframe(self, mock_fetch):
        """Contract: get_data_types returns DataFrame."""
        mock_fetch.return_value = {}
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_data_types()
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_stations_returns_dataframe(self, mock_fetch):
        """Contract: get_stations returns DataFrame."""
        mock_fetch.return_value = {}
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_stations()
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_locations_returns_dataframe(self, mock_fetch):
        """Contract: get_locations returns DataFrame."""
        mock_fetch.return_value = {}
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_locations()
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.fetch")
    def test_get_climate_data_returns_dataframe(self, mock_fetch):
        """Contract: get_climate_data returns DataFrame."""
        mock_fetch.return_value = {}
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_climate_data(
            dataset_id="GHCND", start_date="2024-01-01", end_date="2024-01-31"
        )
        assert isinstance(result, pd.DataFrame)

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.get_locations"
    )
    def test_get_states_returns_dataframe(self, mock_get_locations):
        """Contract: get_states returns DataFrame."""
        mock_get_locations.return_value = pd.DataFrame()
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_states()
        assert isinstance(result, pd.DataFrame)

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.get_climate_data"
    )
    def test_get_temperature_data_returns_dataframe(self, mock_get_climate_data):
        """Contract: get_temperature_data returns DataFrame."""
        mock_get_climate_data.return_value = pd.DataFrame()
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_temperature_data(start_date="2024-01-01", end_date="2024-01-31")
        assert isinstance(result, pd.DataFrame)

    @patch(
        "krl_data_connectors.environment.noaa_climate_connector.NOAAClimateConnector.get_climate_data"
    )
    def test_get_precipitation_data_returns_dataframe(self, mock_get_climate_data):
        """Contract: get_precipitation_data returns DataFrame."""
        mock_get_climate_data.return_value = pd.DataFrame()
        connector = NOAAClimateConnector(api_key="test_token")
        result = connector.get_precipitation_data(start_date="2024-01-01", end_date="2024-01-31")
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
