# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for Bureau of Justice Statistics (BJS) Connector.

Test Coverage:
- Connector initialization
- Connection handling
- Crime statistics queries
- Prison population queries
- Recidivism data queries
- Court sentencing queries
- Law enforcement data queries
- Victimization data queries
- Probation/parole queries
- Federal justice statistics
- Crime trend analysis
- Contract tests (Phase 4 Layer 8)
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.crime.bjs_connector import BureauOfJusticeConnector


# Fixtures

@pytest.fixture
def bjs_connector():
    """Create BureauOfJusticeConnector instance."""
    return BureauOfJusticeConnector()


# Test Classes

class TestBJSConnectorInit:
    """Test connector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = BureauOfJusticeConnector()
        assert connector.base_url == BureauOfJusticeConnector.BASE_URL
        assert connector.api_url == BureauOfJusticeConnector.API_BASE_URL
        assert connector.api_key is None

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = BureauOfJusticeConnector(timeout=60)
        assert connector.timeout == 60

    def test_get_api_key_returns_none(self):
        """Test that _get_api_key returns None (no auth required)."""
        connector = BureauOfJusticeConnector()
        assert connector._get_api_key() is None


class TestBJSConnectorConnection:
    """Test connection handling."""

    @patch('krl_data_connectors.crime.bjs_connector.BureauOfJusticeConnector._init_session')
    def test_connect_success(self, mock_init_session):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        connector = BureauOfJusticeConnector()
        connector.connect()

        assert connector.session is not None
        mock_init_session.assert_called_once()

    @patch('krl_data_connectors.crime.bjs_connector.BureauOfJusticeConnector._init_session')
    def test_connect_already_connected(self, mock_init_session):
        """Test connect when already connected."""
        connector = BureauOfJusticeConnector()
        connector.session = MagicMock()

        connector.connect()

        # Should not call _init_session again
        mock_init_session.assert_not_called()


class TestBJSConnectorGetCrimeStatistics:
    """Test get_crime_statistics method."""

    def test_get_crime_statistics_returns_dataframe(self, bjs_connector):
        """Test that get_crime_statistics returns DataFrame."""
        result = bjs_connector.get_crime_statistics()
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_statistics_with_year(self, bjs_connector):
        """Test crime statistics query with year filter."""
        result = bjs_connector.get_crime_statistics(year=2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_statistics_with_state(self, bjs_connector):
        """Test crime statistics query with state filter."""
        result = bjs_connector.get_crime_statistics(state="CA")
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_statistics_with_crime_type(self, bjs_connector):
        """Test crime statistics query with crime type."""
        result = bjs_connector.get_crime_statistics(crime_type="VIOLENT")
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_statistics_cached(self, bjs_connector):
        """Test that cached data is returned on second call."""
        # First call
        result1 = bjs_connector.get_crime_statistics(year=2023)
        
        # Second call - should use cache
        result2 = bjs_connector.get_crime_statistics(year=2023)

        assert result1.equals(result2)


class TestBJSConnectorGetPrisonPopulation:
    """Test get_prison_population method."""

    def test_get_prison_population_returns_dataframe(self, bjs_connector):
        """Test that get_prison_population returns DataFrame."""
        result = bjs_connector.get_prison_population()
        assert isinstance(result, pd.DataFrame)

    def test_get_prison_population_with_filters(self, bjs_connector):
        """Test prison population query with filters."""
        result = bjs_connector.get_prison_population(year=2023, facility_type="PRISON")
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetRecidivismRates:
    """Test get_recidivism_rates method."""

    def test_get_recidivism_rates_returns_dataframe(self, bjs_connector):
        """Test that get_recidivism_rates returns DataFrame."""
        result = bjs_connector.get_recidivism_rates()
        assert isinstance(result, pd.DataFrame)

    def test_get_recidivism_rates_with_year(self, bjs_connector):
        """Test recidivism query with year."""
        result = bjs_connector.get_recidivism_rates(year=2023)
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetCourtSentencing:
    """Test get_court_sentencing method."""

    def test_get_court_sentencing_returns_dataframe(self, bjs_connector):
        """Test that get_court_sentencing returns DataFrame."""
        result = bjs_connector.get_court_sentencing()
        assert isinstance(result, pd.DataFrame)

    def test_get_court_sentencing_with_filters(self, bjs_connector):
        """Test sentencing query with filters."""
        result = bjs_connector.get_court_sentencing(year=2023, state="NY")
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetLawEnforcementData:
    """Test get_law_enforcement_data method."""

    def test_get_law_enforcement_data_returns_dataframe(self, bjs_connector):
        """Test that get_law_enforcement_data returns DataFrame."""
        result = bjs_connector.get_law_enforcement_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_law_enforcement_data_with_filters(self, bjs_connector):
        """Test law enforcement query with filters."""
        result = bjs_connector.get_law_enforcement_data(year=2023, state="TX")
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetVictimizationData:
    """Test get_victimization_data method."""

    def test_get_victimization_data_returns_dataframe(self, bjs_connector):
        """Test that get_victimization_data returns DataFrame."""
        result = bjs_connector.get_victimization_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_victimization_data_with_filters(self, bjs_connector):
        """Test victimization query with filters."""
        result = bjs_connector.get_victimization_data(year=2023, crime_type="VIOLENT")
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetProbationParole:
    """Test get_probation_parole method."""

    def test_get_probation_parole_returns_dataframe(self, bjs_connector):
        """Test that get_probation_parole returns DataFrame."""
        result = bjs_connector.get_probation_parole()
        assert isinstance(result, pd.DataFrame)

    def test_get_probation_parole_with_filters(self, bjs_connector):
        """Test probation/parole query with filters."""
        result = bjs_connector.get_probation_parole(year=2023, supervision_type="PROBATION")
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetFederalJusticeStatistics:
    """Test get_federal_justice_statistics method."""

    def test_get_federal_justice_statistics_returns_dataframe(self, bjs_connector):
        """Test that get_federal_justice_statistics returns DataFrame."""
        result = bjs_connector.get_federal_justice_statistics()
        assert isinstance(result, pd.DataFrame)

    def test_get_federal_justice_statistics_with_filters(self, bjs_connector):
        """Test federal justice query with filters."""
        result = bjs_connector.get_federal_justice_statistics(year=2023, category="sentencing")
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetCrimeTrends:
    """Test get_crime_trends method."""

    def test_get_crime_trends_returns_dataframe(self, bjs_connector):
        """Test that get_crime_trends returns DataFrame."""
        result = bjs_connector.get_crime_trends(2015, 2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_trends_with_filters(self, bjs_connector):
        """Test crime trends with filters."""
        result = bjs_connector.get_crime_trends(2015, 2023, crime_type="VIOLENT", state="CA")
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorGetCrimeByState:
    """Test get_crime_by_state method."""

    def test_get_crime_by_state_returns_dataframe(self, bjs_connector):
        """Test that get_crime_by_state returns DataFrame."""
        result = bjs_connector.get_crime_by_state("CA")
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_by_state_with_year(self, bjs_connector):
        """Test crime by state with year filter."""
        result = bjs_connector.get_crime_by_state("CA", year=2023)
        assert isinstance(result, pd.DataFrame)


class TestBJSConnectorClose:
    """Test close method."""

    def test_close_closes_session(self):
        """Test that close properly closes session."""
        connector = BureauOfJusticeConnector()
        connector.session = MagicMock()

        connector.close()

        connector.session.close.assert_called_once()
        assert connector.session is None

    def test_close_when_no_session(self):
        """Test close when session is None."""
        connector = BureauOfJusticeConnector()
        connector.session = None

        # Should not raise error
        connector.close()


# Phase 4 Layer 8: Contract Tests

class TestBJSConnectorTypeContracts:
    """Contract tests for return types (Phase 4 Layer 8)."""

    def test_get_crime_statistics_returns_dataframe(self, bjs_connector):
        """Contract: get_crime_statistics returns DataFrame."""
        result = bjs_connector.get_crime_statistics()
        assert isinstance(result, pd.DataFrame)

    def test_get_prison_population_returns_dataframe(self, bjs_connector):
        """Contract: get_prison_population returns DataFrame."""
        result = bjs_connector.get_prison_population()
        assert isinstance(result, pd.DataFrame)

    def test_get_recidivism_rates_returns_dataframe(self, bjs_connector):
        """Contract: get_recidivism_rates returns DataFrame."""
        result = bjs_connector.get_recidivism_rates()
        assert isinstance(result, pd.DataFrame)

    def test_get_court_sentencing_returns_dataframe(self, bjs_connector):
        """Contract: get_court_sentencing returns DataFrame."""
        result = bjs_connector.get_court_sentencing()
        assert isinstance(result, pd.DataFrame)

    def test_get_law_enforcement_data_returns_dataframe(self, bjs_connector):
        """Contract: get_law_enforcement_data returns DataFrame."""
        result = bjs_connector.get_law_enforcement_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_victimization_data_returns_dataframe(self, bjs_connector):
        """Contract: get_victimization_data returns DataFrame."""
        result = bjs_connector.get_victimization_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_probation_parole_returns_dataframe(self, bjs_connector):
        """Contract: get_probation_parole returns DataFrame."""
        result = bjs_connector.get_probation_parole()
        assert isinstance(result, pd.DataFrame)

    def test_get_federal_justice_statistics_returns_dataframe(self, bjs_connector):
        """Contract: get_federal_justice_statistics returns DataFrame."""
        result = bjs_connector.get_federal_justice_statistics()
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_trends_returns_dataframe(self, bjs_connector):
        """Contract: get_crime_trends returns DataFrame."""
        result = bjs_connector.get_crime_trends(2015, 2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_crime_by_state_returns_dataframe(self, bjs_connector):
        """Contract: get_crime_by_state returns DataFrame."""
        result = bjs_connector.get_crime_by_state("CA")
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
