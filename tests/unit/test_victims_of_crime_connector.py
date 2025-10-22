# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for Office for Victims of Crime (OVC) Connector.

Test Coverage:
- Connector initialization
- Connection handling
- Compensation data queries
- Assistance program queries
- Victim demographics queries
- Service utilization queries
- Grant funding queries
- State performance queries
- Victim rights queries
- Trend analysis
- Contract tests (Phase 4 Layer 8)
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.crime.victims_of_crime_connector import VictimsOfCrimeConnector

# Fixtures


@pytest.fixture
def ovc_connector():
    """Create VictimsOfCrimeConnector instance."""
    return VictimsOfCrimeConnector()


# Test Classes


class TestOVCConnectorInit:
    """Test connector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = VictimsOfCrimeConnector()
        assert connector.base_url == VictimsOfCrimeConnector.BASE_URL
        assert connector.api_url == VictimsOfCrimeConnector.API_BASE_URL
        assert connector.api_key is None

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = VictimsOfCrimeConnector(timeout=60)
        assert connector.timeout == 60

    def test_get_api_key_returns_none(self):
        """Test that _get_api_key returns None (no auth required)."""
        connector = VictimsOfCrimeConnector()
        assert connector._get_api_key() is None


class TestOVCConnectorConnection:
    """Test connection handling."""

    @patch(
        "krl_data_connectors.crime.victims_of_crime_connector.VictimsOfCrimeConnector._init_session"
    )
    def test_connect_success(self, mock_init_session):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        connector = VictimsOfCrimeConnector()
        connector.connect()

        assert connector.session is not None
        mock_init_session.assert_called_once()

    @patch(
        "krl_data_connectors.crime.victims_of_crime_connector.VictimsOfCrimeConnector._init_session"
    )
    def test_connect_already_connected(self, mock_init_session):
        """Test connect when already connected."""
        connector = VictimsOfCrimeConnector()
        connector.session = MagicMock()

        connector.connect()

        # Should not call _init_session again
        mock_init_session.assert_not_called()


class TestOVCConnectorGetCompensationData:
    """Test get_compensation_data method."""

    def test_get_compensation_data_returns_dataframe(self, ovc_connector):
        """Test that get_compensation_data returns DataFrame."""
        result = ovc_connector.get_compensation_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_data_with_year(self, ovc_connector):
        """Test compensation query with year filter."""
        result = ovc_connector.get_compensation_data(year=2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_data_with_state(self, ovc_connector):
        """Test compensation query with state filter."""
        result = ovc_connector.get_compensation_data(state="CA")
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_data_with_crime_type(self, ovc_connector):
        """Test compensation query with crime type."""
        result = ovc_connector.get_compensation_data(crime_type="VIOLENT")
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_data_cached(self, ovc_connector):
        """Test that cached data is returned on second call."""
        # First call
        result1 = ovc_connector.get_compensation_data(year=2023)

        # Second call - should use cache
        result2 = ovc_connector.get_compensation_data(year=2023)

        assert result1.equals(result2)


class TestOVCConnectorGetAssistancePrograms:
    """Test get_assistance_programs method."""

    def test_get_assistance_programs_returns_dataframe(self, ovc_connector):
        """Test that get_assistance_programs returns DataFrame."""
        result = ovc_connector.get_assistance_programs()
        assert isinstance(result, pd.DataFrame)

    def test_get_assistance_programs_with_state(self, ovc_connector):
        """Test assistance programs query with state."""
        result = ovc_connector.get_assistance_programs(state="NY")
        assert isinstance(result, pd.DataFrame)

    def test_get_assistance_programs_with_service_type(self, ovc_connector):
        """Test assistance programs query with service type."""
        result = ovc_connector.get_assistance_programs(service_type="COUNSELING")
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetVictimDemographics:
    """Test get_victim_demographics method."""

    def test_get_victim_demographics_returns_dataframe(self, ovc_connector):
        """Test that get_victim_demographics returns DataFrame."""
        result = ovc_connector.get_victim_demographics()
        assert isinstance(result, pd.DataFrame)

    def test_get_victim_demographics_with_filters(self, ovc_connector):
        """Test demographics query with filters."""
        result = ovc_connector.get_victim_demographics(year=2023, state="TX")
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetServiceUtilization:
    """Test get_service_utilization method."""

    def test_get_service_utilization_returns_dataframe(self, ovc_connector):
        """Test that get_service_utilization returns DataFrame."""
        result = ovc_connector.get_service_utilization()
        assert isinstance(result, pd.DataFrame)

    def test_get_service_utilization_with_filters(self, ovc_connector):
        """Test service utilization query with filters."""
        result = ovc_connector.get_service_utilization(year=2023, service_type="LEGAL")
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetGrantFunding:
    """Test get_grant_funding method."""

    def test_get_grant_funding_returns_dataframe(self, ovc_connector):
        """Test that get_grant_funding returns DataFrame."""
        result = ovc_connector.get_grant_funding()
        assert isinstance(result, pd.DataFrame)

    def test_get_grant_funding_with_filters(self, ovc_connector):
        """Test grant funding query with filters."""
        result = ovc_connector.get_grant_funding(year=2023, state="FL")
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetStatePerformance:
    """Test get_state_performance method."""

    def test_get_state_performance_returns_dataframe(self, ovc_connector):
        """Test that get_state_performance returns DataFrame."""
        result = ovc_connector.get_state_performance("CA")
        assert isinstance(result, pd.DataFrame)

    def test_get_state_performance_with_year(self, ovc_connector):
        """Test state performance query with year."""
        result = ovc_connector.get_state_performance("CA", year=2023)
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetCompensationByType:
    """Test get_compensation_by_type method."""

    def test_get_compensation_by_type_returns_dataframe(self, ovc_connector):
        """Test that get_compensation_by_type returns DataFrame."""
        result = ovc_connector.get_compensation_by_type("MEDICAL")
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_by_type_with_filters(self, ovc_connector):
        """Test compensation by type query with filters."""
        result = ovc_connector.get_compensation_by_type("MEDICAL", year=2023, state="NY")
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetVictimRightsData:
    """Test get_victim_rights_data method."""

    def test_get_victim_rights_data_returns_dataframe(self, ovc_connector):
        """Test that get_victim_rights_data returns DataFrame."""
        result = ovc_connector.get_victim_rights_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_victim_rights_data_with_filters(self, ovc_connector):
        """Test victim rights query with filters."""
        result = ovc_connector.get_victim_rights_data(year=2023, state="IL")
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetCompensationTrends:
    """Test get_compensation_trends method."""

    def test_get_compensation_trends_returns_dataframe(self, ovc_connector):
        """Test that get_compensation_trends returns DataFrame."""
        result = ovc_connector.get_compensation_trends(2015, 2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_trends_with_filters(self, ovc_connector):
        """Test compensation trends with filters."""
        result = ovc_connector.get_compensation_trends(2015, 2023, state="WA", crime_type="VIOLENT")
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorGetServicesByState:
    """Test get_services_by_state method."""

    def test_get_services_by_state_returns_dataframe(self, ovc_connector):
        """Test that get_services_by_state returns DataFrame."""
        result = ovc_connector.get_services_by_state("TX")
        assert isinstance(result, pd.DataFrame)

    def test_get_services_by_state_with_year(self, ovc_connector):
        """Test services by state with year filter."""
        result = ovc_connector.get_services_by_state("TX", year=2023)
        assert isinstance(result, pd.DataFrame)


class TestOVCConnectorClose:
    """Test close method."""

    def test_close_closes_session(self):
        """Test that close properly closes session."""
        connector = VictimsOfCrimeConnector()
        connector.session = MagicMock()

        connector.close()

        connector.session.close.assert_called_once()
        assert connector.session is None

    def test_close_when_no_session(self):
        """Test close when session is None."""
        connector = VictimsOfCrimeConnector()
        connector.session = None

        # Should not raise error
        connector.close()


# Phase 4 Layer 8: Contract Tests


class TestOVCConnectorTypeContracts:
    """Contract tests for return types (Phase 4 Layer 8)."""

    def test_get_compensation_data_returns_dataframe(self, ovc_connector):
        """Contract: get_compensation_data returns DataFrame."""
        result = ovc_connector.get_compensation_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_assistance_programs_returns_dataframe(self, ovc_connector):
        """Contract: get_assistance_programs returns DataFrame."""
        result = ovc_connector.get_assistance_programs()
        assert isinstance(result, pd.DataFrame)

    def test_get_victim_demographics_returns_dataframe(self, ovc_connector):
        """Contract: get_victim_demographics returns DataFrame."""
        result = ovc_connector.get_victim_demographics()
        assert isinstance(result, pd.DataFrame)

    def test_get_service_utilization_returns_dataframe(self, ovc_connector):
        """Contract: get_service_utilization returns DataFrame."""
        result = ovc_connector.get_service_utilization()
        assert isinstance(result, pd.DataFrame)

    def test_get_grant_funding_returns_dataframe(self, ovc_connector):
        """Contract: get_grant_funding returns DataFrame."""
        result = ovc_connector.get_grant_funding()
        assert isinstance(result, pd.DataFrame)

    def test_get_state_performance_returns_dataframe(self, ovc_connector):
        """Contract: get_state_performance returns DataFrame."""
        result = ovc_connector.get_state_performance("CA")
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_by_type_returns_dataframe(self, ovc_connector):
        """Contract: get_compensation_by_type returns DataFrame."""
        result = ovc_connector.get_compensation_by_type("MEDICAL")
        assert isinstance(result, pd.DataFrame)

    def test_get_victim_rights_data_returns_dataframe(self, ovc_connector):
        """Contract: get_victim_rights_data returns DataFrame."""
        result = ovc_connector.get_victim_rights_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_compensation_trends_returns_dataframe(self, ovc_connector):
        """Contract: get_compensation_trends returns DataFrame."""
        result = ovc_connector.get_compensation_trends(2015, 2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_services_by_state_returns_dataframe(self, ovc_connector):
        """Contract: get_services_by_state returns DataFrame."""
        result = ovc_connector.get_services_by_state("TX")
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
