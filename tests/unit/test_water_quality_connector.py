# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for EPA Water Quality Connector (ECHO API).

Test Coverage:
- Connector initialization
- Connection handling
- Water system queries (by state, city, ZIP, ID)
- Violation queries
- Enforcement action queries
- Population served retrieval
- Contract tests (Phase 4 Layer 8)
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.environment.water_quality_connector import WaterQualityConnector

# Fixtures


@pytest.fixture(autouse=True)
def clear_connector_cache():
    """Clear connector cache before and after each test."""
    temp_conn = WaterQualityConnector()
    temp_conn.cache.clear()
    yield
    temp_conn.cache.clear()


@pytest.fixture
def sample_water_system():
    """Sample water system data."""
    return {
        "PWSID": "CA1234567",
        "PWS_NAME": "San Francisco Water System",
        "CITY_NAME": "SAN FRANCISCO",
        "ZIP_CODE": "94102",
        "PRIMACY_AGENCY_CODE": "CA",
        "PWS_TYPE_CODE": "CWS",
        "POPULATION_SERVED_COUNT": 850000,
        "PRIMARY_SOURCE_CODE": "SW",
        "PRIMACY_TYPE": "EPA",
    }


@pytest.fixture
def sample_violation():
    """Sample SDWA violation data."""
    return {
        "PWSID": "CA1234567",
        "VIOLATION_ID": "VIO123",
        "VIOLATION_CODE": "MCL",
        "VIOLATION_DESC": "Maximum Contaminant Level Violation",
        "IS_HEALTH_BASED_IND": "Y",
        "COMPL_STATUS": "O",
        "COMPLIANCE_STATUS_DATE": "2024-01-15",
        "CONTAMINANT_CODE": "1040",
        "CONTAMINANT_NAME": "LEAD",
    }


@pytest.fixture
def sample_enforcement():
    """Sample enforcement action data."""
    return {
        "PWSID": "CA1234567",
        "ENFORCEMENT_ID": "ENF456",
        "ENFORCEMENT_DATE": "2024-02-01",
        "ENFORCEMENT_TYPE": "FO",
        "ENFORCEMENT_ACTION_TYPE_DESC": "Formal Order",
    }


@pytest.fixture
def mock_response_success():
    """Mock successful API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = [{"PWSID": "CA1234567", "PWS_NAME": "Test System"}]
    return mock


@pytest.fixture
def mock_response_empty():
    """Mock empty API response."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = []
    return mock


@pytest.fixture
def water_quality_connector():
    """Create WaterQualityConnector instance."""
    return WaterQualityConnector()


# Test Classes


class TestWaterQualityConnectorInit:
    """Test connector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = WaterQualityConnector()
        assert connector.base_url == WaterQualityConnector.BASE_URL
        assert connector.echo_url == WaterQualityConnector.ECHO_BASE_URL
        assert connector.api_key is None

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = WaterQualityConnector(timeout=60)
        assert connector.timeout == 60

    def test_init_with_cache(self):
        """Test initialization with cache enabled."""
        connector = WaterQualityConnector(cache_ttl=1800)
        assert connector.cache is not None

    def test_get_api_key_returns_none(self):
        """Test that _get_api_key returns None (no auth required)."""
        connector = WaterQualityConnector()
        assert connector._get_api_key() is None


class TestWaterQualityConnectorConnection:
    """Test connection handling."""

    @patch(
        "krl_data_connectors.environment.water_quality_connector.WaterQualityConnector._init_session"
    )
    def test_connect_success(self, mock_init_session):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        mock_init_session.return_value = mock_session

        connector = WaterQualityConnector()
        connector.connect()

        assert connector.session is not None
        mock_init_session.assert_called_once()

    @patch(
        "krl_data_connectors.environment.water_quality_connector.WaterQualityConnector._init_session"
    )
    def test_connect_already_connected(self, mock_init_session):
        """Test connect when already connected."""
        connector = WaterQualityConnector()
        connector.session = MagicMock()

        connector.connect()

        # Should not call _init_session again
        mock_init_session.assert_not_called()


class TestWaterQualityConnectorGetSystemsByState:
    """Test get_water_systems_by_state method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_state_success(self, mock_fetch, sample_water_system):
        """Test successful retrieval of systems by state."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_water_systems_by_state("CA")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["PWSID"].iloc[0] == "CA1234567"
        mock_fetch.assert_called_once()

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_state_with_type_filter(self, mock_fetch, sample_water_system):
        """Test systems query with system type filter."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_water_systems_by_state("CA", system_type="CWS")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_fetch.assert_called_once()

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_state_empty(self, mock_fetch):
        """Test systems query with no results."""
        mock_fetch.return_value = []

        connector = WaterQualityConnector()
        result = connector.get_water_systems_by_state("XX")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_state_cached(self, mock_fetch, sample_water_system):
        """Test that cached data is returned on second call."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()

        # First call - should fetch
        result1 = connector.get_water_systems_by_state("CA")

        # Second call - should use cache
        result2 = connector.get_water_systems_by_state("CA")

        assert result1.equals(result2)
        # fetch should only be called once
        assert mock_fetch.call_count == 1


class TestWaterQualityConnectorGetSystemById:
    """Test get_system_by_id method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_system_by_id_success(self, mock_fetch, sample_water_system):
        """Test successful retrieval of system by ID."""
        mock_fetch.return_value = sample_water_system

        connector = WaterQualityConnector()
        result = connector.get_system_by_id("CA1234567")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["PWSID"].iloc[0] == "CA1234567"
        assert result["PWS_NAME"].iloc[0] == "San Francisco Water System"

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_system_by_id_list_response(self, mock_fetch, sample_water_system):
        """Test system query with list response."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_system_by_id("CA1234567")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


class TestWaterQualityConnectorGetViolations:
    """Test get_violations_by_system method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_violations_success(self, mock_fetch, sample_violation):
        """Test successful retrieval of violations."""
        mock_fetch.return_value = [sample_violation]

        connector = WaterQualityConnector()
        result = connector.get_violations_by_system("CA1234567")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["VIOLATION_CODE"].iloc[0] == "MCL"

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_violations_empty(self, mock_fetch):
        """Test violations query with no results."""
        mock_fetch.return_value = []

        connector = WaterQualityConnector()
        result = connector.get_violations_by_system("CA9999999")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestWaterQualityConnectorGetSystemsByCity:
    """Test get_systems_by_city method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_city_success(self, mock_fetch, sample_water_system):
        """Test successful retrieval of systems by city."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_systems_by_city("San Francisco", "CA")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["CITY_NAME"].iloc[0] == "SAN FRANCISCO"

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_city_with_spaces(self, mock_fetch, sample_water_system):
        """Test city query with spaces in name."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_systems_by_city("Los Angeles", "CA")

        assert isinstance(result, pd.DataFrame)


class TestWaterQualityConnectorGetSystemsByZip:
    """Test get_systems_by_zip method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_zip_success(self, mock_fetch, sample_water_system):
        """Test successful retrieval of systems by ZIP."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_systems_by_zip("94102")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["ZIP_CODE"].iloc[0] == "94102"


class TestWaterQualityConnectorGetCWS:
    """Test get_community_water_systems method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_cws_with_state(self, mock_fetch, sample_water_system):
        """Test CWS query with state filter."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_community_water_systems(state="CA")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["PWS_TYPE_CODE"].iloc[0] == "CWS"

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_cws_no_state(self, mock_fetch, sample_water_system):
        """Test CWS query without state filter."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.get_community_water_systems()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


class TestWaterQualityConnectorGetHealthViolations:
    """Test get_health_based_violations method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_health_violations_success(self, mock_fetch, sample_violation):
        """Test successful retrieval of health-based violations."""
        mock_fetch.return_value = [sample_violation]

        connector = WaterQualityConnector()
        result = connector.get_health_based_violations("CA")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["IS_HEALTH_BASED_IND"].iloc[0] == "Y"


class TestWaterQualityConnectorSearchByName:
    """Test search_systems_by_name method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_search_by_name_success(self, mock_fetch, sample_water_system):
        """Test successful system name search."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.search_systems_by_name("San Francisco")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_search_by_name_with_state(self, mock_fetch, sample_water_system):
        """Test system name search with state filter."""
        mock_fetch.return_value = [sample_water_system]

        connector = WaterQualityConnector()
        result = connector.search_systems_by_name("Municipal", state="CA")

        assert isinstance(result, pd.DataFrame)


class TestWaterQualityConnectorGetEnforcement:
    """Test get_enforcement_actions method."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_enforcement_success(self, mock_fetch, sample_enforcement):
        """Test successful retrieval of enforcement actions."""
        mock_fetch.return_value = [sample_enforcement]

        connector = WaterQualityConnector()
        result = connector.get_enforcement_actions("CA1234567")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result["ENFORCEMENT_TYPE"].iloc[0] == "FO"


class TestWaterQualityConnectorGetPopulation:
    """Test get_system_population_served method."""

    @patch(
        "krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.get_system_by_id"
    )
    def test_get_population_success(self, mock_get_system, sample_water_system):
        """Test successful population retrieval."""
        mock_get_system.return_value = pd.DataFrame([sample_water_system])

        connector = WaterQualityConnector()
        result = connector.get_system_population_served("CA1234567")

        assert result == 850000

    @patch(
        "krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.get_system_by_id"
    )
    def test_get_population_empty(self, mock_get_system):
        """Test population retrieval with no data."""
        mock_get_system.return_value = pd.DataFrame()

        connector = WaterQualityConnector()
        result = connector.get_system_population_served("CA9999999")

        assert result is None

    @patch(
        "krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.get_system_by_id"
    )
    def test_get_population_none(self, mock_get_system):
        """Test population retrieval when field is None."""
        mock_get_system.return_value = pd.DataFrame([{"PWSID": "CA1234567"}])

        connector = WaterQualityConnector()
        result = connector.get_system_population_served("CA1234567")

        assert result is None


class TestWaterQualityConnectorClose:
    """Test close method."""

    def test_close_closes_session(self):
        """Test that close() closes the session."""
        connector = WaterQualityConnector()
        mock_session = MagicMock()
        connector.session = mock_session

        connector.close()

        mock_session.close.assert_called_once()
        assert connector.session is None

    def test_close_when_no_session(self):
        """Test close when session is None."""
        connector = WaterQualityConnector()
        connector.session = None

        # Should not raise error
        connector.close()


# Phase 4 Layer 8: Contract Tests


class TestWaterQualityConnectorTypeContracts:
    """Contract tests for return types (Phase 4 Layer 8)."""

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_state_returns_dataframe(self, mock_fetch):
        """Contract: get_water_systems_by_state returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.get_water_systems_by_state("CA")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_system_by_id_returns_dataframe(self, mock_fetch):
        """Contract: get_system_by_id returns DataFrame."""
        mock_fetch.return_value = {}
        connector = WaterQualityConnector()
        result = connector.get_system_by_id("CA1234567")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_violations_returns_dataframe(self, mock_fetch):
        """Contract: get_violations_by_system returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.get_violations_by_system("CA1234567")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_city_returns_dataframe(self, mock_fetch):
        """Contract: get_systems_by_city returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.get_systems_by_city("San Francisco", "CA")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_systems_by_zip_returns_dataframe(self, mock_fetch):
        """Contract: get_systems_by_zip returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.get_systems_by_zip("94102")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_cws_returns_dataframe(self, mock_fetch):
        """Contract: get_community_water_systems returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.get_community_water_systems()
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_health_violations_returns_dataframe(self, mock_fetch):
        """Contract: get_health_based_violations returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.get_health_based_violations("CA")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_search_by_name_returns_dataframe(self, mock_fetch):
        """Contract: search_systems_by_name returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.search_systems_by_name("Municipal")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.fetch")
    def test_get_enforcement_returns_dataframe(self, mock_fetch):
        """Contract: get_enforcement_actions returns DataFrame."""
        mock_fetch.return_value = []
        connector = WaterQualityConnector()
        result = connector.get_enforcement_actions("CA1234567")
        assert isinstance(result, pd.DataFrame)

    @patch(
        "krl_data_connectors.environment.water_quality_connector.WaterQualityConnector.get_system_by_id"
    )
    def test_get_population_returns_int_or_none(self, mock_get_system):
        """Contract: get_system_population_served returns int or None."""
        mock_get_system.return_value = pd.DataFrame([{"POPULATION_SERVED_COUNT": 100000}])
        connector = WaterQualityConnector()
        result = connector.get_system_population_served("CA1234567")
        assert isinstance(result, int) or result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
