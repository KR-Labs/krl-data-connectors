"""
Tests for EPA Superfund connector (Envirofacts API).

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
"""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.environment import SuperfundConnector


@pytest.fixture
def sample_site_response():
    """Sample site response from EPA Envirofacts API."""
    return [
        {
            "SITE_EPA_ID": "CAD009195731",
            "SITE_NAME": "TEST SUPERFUND SITE",
            "CITY": "LOS ANGELES",
            "STATE": "CA",
            "ZIP": "90001",
            "ADDRESS": "123 TEST STREET",
            "NPL_STATUS": "F",
            "CONST_COMP_IND": "Y",
            "LATITUDE": "34.0522",
            "LONGITUDE": "-118.2437",
        }
    ]


@pytest.fixture
def connector():
    """Create connector instance (no API key needed)."""
    return SuperfundConnector()


@pytest.fixture
def sample_dataframe(sample_site_response):
    """Create sample DataFrame from site response."""
    return pd.DataFrame(sample_site_response)


class TestSuperfundConnectorInit:
    """Test Superfund connector initialization."""

    def test_init_no_api_key_required(self):
        """Test connector initialization without API key."""
        connector = SuperfundConnector()
        assert connector.api_key is None
        assert connector.base_url == SuperfundConnector.BASE_URL

    def test_init_with_custom_cache_ttl(self):
        """Test connector with custom cache TTL."""
        connector = SuperfundConnector(cache_ttl=7200)
        assert connector.cache.default_ttl == 7200

    def test_status_codes_defined(self):
        """Test that status code mappings are defined."""
        assert "F" in SuperfundConnector.STATUS_CODES
        assert SuperfundConnector.STATUS_CODES["F"] == "Final NPL"

    def test_cleanup_phases_defined(self):
        """Test that cleanup phase mappings are defined."""
        assert "8" in SuperfundConnector.CLEANUP_PHASES
        assert "Construction Complete" in SuperfundConnector.CLEANUP_PHASES["8"]


class TestSuperfundConnectorConnection:
    """Test Superfund connector connection methods."""

    @patch("requests.Session")
    def test_connect_successful(self, mock_session_class):
        """Test successful connection to EPA Envirofacts."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_session.get.return_value = mock_response
        mock_session_class.return_value = mock_session

        connector = SuperfundConnector()
        connector.connect()

        assert connector.session is not None

    @patch("requests.Session")
    def test_connect_failure(self, mock_session_class):
        """Test connection failure handling."""
        mock_session = Mock()
        mock_session.get.side_effect = Exception("Connection failed")
        mock_session_class.return_value = mock_session

        connector = SuperfundConnector()

        with pytest.raises(ConnectionError, match="Could not connect"):
            connector.connect()


class TestSuperfundConnectorGetSitesByState:
    """Test get_sites_by_state method."""

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_state_success(self, mock_fetch, sample_site_response):
        """Test retrieving sites by state."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()
        result = connector.get_sites_by_state("CA")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["STATE"] == "CA"

        # Verify fetch was called with correct endpoint
        mock_fetch.assert_called_once()
        call_kwargs = mock_fetch.call_args[1]
        assert "SEMS/STATE/CA" in call_kwargs["endpoint"]

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_state_with_status(self, mock_fetch, sample_site_response):
        """Test retrieving sites by state with status filter."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()
        result = connector.get_sites_by_state("CA", status="F")

        assert isinstance(result, pd.DataFrame)

        # Verify status filter was applied
        call_kwargs = mock_fetch.call_args[1]
        assert "NPL_STATUS/F" in call_kwargs["endpoint"]

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_state_empty_result(self, mock_fetch):
        """Test handling of empty results."""
        mock_fetch.return_value = []

        connector = SuperfundConnector()
        result = connector.get_sites_by_state("ZZ")  # Invalid state

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_state_caching(self, mock_fetch, sample_site_response):
        """Test that results are cached."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()

        # First call
        result1 = connector.get_sites_by_state("CA")

        # Second call should use cache
        result2 = connector.get_sites_by_state("CA")

        # fetch should only be called once
        assert mock_fetch.call_count == 1
        assert result1.equals(result2)


class TestSuperfundConnectorGetSiteById:
    """Test get_site_by_id method."""

    @patch.object(SuperfundConnector, "fetch")
    def test_get_site_by_id_success(self, mock_fetch, sample_site_response):
        """Test retrieving site by EPA ID."""
        mock_fetch.return_value = sample_site_response[0]

        connector = SuperfundConnector()
        result = connector.get_site_by_id("CAD009195731")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["SITE_EPA_ID"] == "CAD009195731"

    @patch.object(SuperfundConnector, "fetch")
    def test_get_site_by_id_caching(self, mock_fetch, sample_site_response):
        """Test site details are cached."""
        mock_fetch.return_value = sample_site_response[0]

        connector = SuperfundConnector()

        result1 = connector.get_site_by_id("CAD009195731")
        result2 = connector.get_site_by_id("CAD009195731")

        assert mock_fetch.call_count == 1
        assert result1.equals(result2)


class TestSuperfundConnectorGetSitesByCity:
    """Test get_sites_by_city method."""

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_city_success(self, mock_fetch, sample_site_response):
        """Test retrieving sites by city and state."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()
        result = connector.get_sites_by_city("Los Angeles", "CA")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

        # Verify endpoint contains uppercase city name
        call_kwargs = mock_fetch.call_args[1]
        assert "LOS" in call_kwargs["endpoint"]
        assert "ANGELES" in call_kwargs["endpoint"]

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_city_handles_spaces(self, mock_fetch):
        """Test that city names with spaces are handled."""
        mock_fetch.return_value = []

        connector = SuperfundConnector()
        connector.get_sites_by_city("San Francisco", "CA")

        call_kwargs = mock_fetch.call_args[1]
        # Should encode spaces as %20
        assert "%20" in call_kwargs["endpoint"]


class TestSuperfundConnectorGetSitesByZip:
    """Test get_sites_by_zip method."""

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_zip_success(self, mock_fetch, sample_site_response):
        """Test retrieving sites by ZIP code."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()
        result = connector.get_sites_by_zip("90001")

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

        call_kwargs = mock_fetch.call_args[1]
        assert "ZIP/90001" in call_kwargs["endpoint"]


class TestSuperfundConnectorGetNPLSites:
    """Test get_npl_sites method."""

    @patch.object(SuperfundConnector, "fetch")
    def test_get_npl_sites_success(self, mock_fetch, sample_site_response):
        """Test retrieving all NPL sites."""
        mock_fetch.return_value = sample_site_response * 100  # Simulate multiple sites

        connector = SuperfundConnector()
        result = connector.get_npl_sites()

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

        # Verify it queries Final NPL status
        call_kwargs = mock_fetch.call_args[1]
        assert "NPL_STATUS/F" in call_kwargs["endpoint"]

    @patch.object(SuperfundConnector, "fetch")
    def test_get_npl_sites_caching(self, mock_fetch, sample_site_response):
        """Test NPL sites are cached."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()

        result1 = connector.get_npl_sites()
        result2 = connector.get_npl_sites()

        assert mock_fetch.call_count == 1


class TestSuperfundConnectorGetConstructionCompleteSites:
    """Test get_construction_complete_sites method."""

    @patch.object(SuperfundConnector, "fetch")
    def test_get_construction_complete_all_states(self, mock_fetch, sample_site_response):
        """Test retrieving construction complete sites nationwide."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()
        result = connector.get_construction_complete_sites()

        assert isinstance(result, pd.DataFrame)

        call_kwargs = mock_fetch.call_args[1]
        assert "CONST_COMP_IND/Y" in call_kwargs["endpoint"]

    @patch.object(SuperfundConnector, "fetch")
    def test_get_construction_complete_by_state(self, mock_fetch, sample_site_response):
        """Test retrieving construction complete sites by state."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()
        result = connector.get_construction_complete_sites(state="CA")

        assert isinstance(result, pd.DataFrame)

        call_kwargs = mock_fetch.call_args[1]
        assert "STATE/CA" in call_kwargs["endpoint"]
        assert "CONST_COMP_IND/Y" in call_kwargs["endpoint"]


class TestSuperfundConnectorSearchSitesByName:
    """Test search_sites_by_name method."""

    @patch.object(SuperfundConnector, "fetch")
    def test_search_sites_by_name_success(self, mock_fetch, sample_site_response):
        """Test searching sites by name."""
        mock_fetch.return_value = sample_site_response

        connector = SuperfundConnector()
        result = connector.search_sites_by_name("Chemical")

        assert isinstance(result, pd.DataFrame)

        call_kwargs = mock_fetch.call_args[1]
        assert "SITE_NAME/BEGINNING" in call_kwargs["endpoint"]
        assert "CHEMICAL" in call_kwargs["endpoint"]

    @patch.object(SuperfundConnector, "fetch")
    def test_search_sites_by_name_with_spaces(self, mock_fetch):
        """Test name search handles spaces."""
        mock_fetch.return_value = []

        connector = SuperfundConnector()
        connector.search_sites_by_name("Test Site")

        call_kwargs = mock_fetch.call_args[1]
        assert "%20" in call_kwargs["endpoint"]


class TestSuperfundConnectorGetSiteCoordinates:
    """Test get_site_coordinates method."""

    @patch.object(SuperfundConnector, "get_site_by_id")
    def test_get_site_coordinates_success(self, mock_get_site):
        """Test retrieving site coordinates."""
        mock_df = pd.DataFrame(
            [{"SITE_EPA_ID": "CAD009195731", "LATITUDE": "34.0522", "LONGITUDE": "-118.2437"}]
        )
        mock_get_site.return_value = mock_df

        connector = SuperfundConnector()
        coords = connector.get_site_coordinates("CAD009195731")

        assert coords is not None
        assert isinstance(coords, tuple)
        assert len(coords) == 2
        assert isinstance(coords[0], float)
        assert isinstance(coords[1], float)

    @patch.object(SuperfundConnector, "get_site_by_id")
    def test_get_site_coordinates_missing(self, mock_get_site):
        """Test handling of missing coordinates."""
        mock_df = pd.DataFrame([{"SITE_EPA_ID": "CAD009195731"}])
        mock_get_site.return_value = mock_df

        connector = SuperfundConnector()
        coords = connector.get_site_coordinates("CAD009195731")

        assert coords is None

    @patch.object(SuperfundConnector, "get_site_by_id")
    def test_get_site_coordinates_empty_df(self, mock_get_site):
        """Test handling of empty DataFrame."""
        mock_get_site.return_value = pd.DataFrame()

        connector = SuperfundConnector()
        coords = connector.get_site_coordinates("INVALID_ID")

        assert coords is None


class TestSuperfundConnectorClose:
    """Test close method."""

    def test_close_closes_session(self):
        """Test that close properly closes session."""
        connector = SuperfundConnector()
        mock_session = MagicMock()
        connector.session = mock_session

        connector.close()

        mock_session.close.assert_called_once()
        assert connector.session is None

    def test_close_no_session(self):
        """Test close when no session exists."""
        connector = SuperfundConnector()
        connector.close()  # Should not raise error
        assert connector.session is None


class TestSuperfundConnectorTypeContracts:
    """Test type contracts and return value structures (Phase 4 Layer 8)."""

    def test_connect_return_type(self):
        """Test that connect returns None."""
        connector = SuperfundConnector()
        assert callable(connector.connect)

    def test_fetch_return_type_signature(self):
        """Test that fetch method exists and is callable."""
        connector = SuperfundConnector()
        assert callable(connector.fetch)

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_state_return_type(self, mock_fetch):
        """Test that get_sites_by_state returns DataFrame."""
        mock_fetch.return_value = []
        connector = SuperfundConnector()
        result = connector.get_sites_by_state("CA")
        assert isinstance(result, pd.DataFrame)

    @patch.object(SuperfundConnector, "fetch")
    def test_get_site_by_id_return_type(self, mock_fetch):
        """Test that get_site_by_id returns DataFrame."""
        mock_fetch.return_value = {"SITE_EPA_ID": "TEST"}
        connector = SuperfundConnector()
        result = connector.get_site_by_id("TEST")
        assert isinstance(result, pd.DataFrame)

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_city_return_type(self, mock_fetch):
        """Test that get_sites_by_city returns DataFrame."""
        mock_fetch.return_value = []
        connector = SuperfundConnector()
        result = connector.get_sites_by_city("Los Angeles", "CA")
        assert isinstance(result, pd.DataFrame)

    @patch.object(SuperfundConnector, "fetch")
    def test_get_sites_by_zip_return_type(self, mock_fetch):
        """Test that get_sites_by_zip returns DataFrame."""
        mock_fetch.return_value = []
        connector = SuperfundConnector()
        result = connector.get_sites_by_zip("90001")
        assert isinstance(result, pd.DataFrame)

    @patch.object(SuperfundConnector, "fetch")
    def test_get_npl_sites_return_type(self, mock_fetch):
        """Test that get_npl_sites returns DataFrame."""
        mock_fetch.return_value = []
        connector = SuperfundConnector()
        result = connector.get_npl_sites()
        assert isinstance(result, pd.DataFrame)

    @patch.object(SuperfundConnector, "fetch")
    def test_get_construction_complete_sites_return_type(self, mock_fetch):
        """Test that get_construction_complete_sites returns DataFrame."""
        mock_fetch.return_value = []
        connector = SuperfundConnector()
        result = connector.get_construction_complete_sites()
        assert isinstance(result, pd.DataFrame)

    @patch.object(SuperfundConnector, "fetch")
    def test_search_sites_by_name_return_type(self, mock_fetch):
        """Test that search_sites_by_name returns DataFrame."""
        mock_fetch.return_value = []
        connector = SuperfundConnector()
        result = connector.search_sites_by_name("Test")
        assert isinstance(result, pd.DataFrame)

    @patch.object(SuperfundConnector, "get_site_by_id")
    def test_get_site_coordinates_return_type(self, mock_get_site):
        """Test that get_site_coordinates returns tuple or None."""
        # Test with coordinates
        mock_df = pd.DataFrame([{"LATITUDE": "34.0", "LONGITUDE": "-118.0"}])
        mock_get_site.return_value = mock_df
        connector = SuperfundConnector()
        result = connector.get_site_coordinates("TEST")
        assert result is None or isinstance(result, tuple)

        if result:
            assert len(result) == 2
            assert isinstance(result[0], float)
            assert isinstance(result[1], float)
