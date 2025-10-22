# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for IPEDS Connector (Integrated Postsecondary Education Data System).

Test Coverage:
- Connector initialization
- Connection handling
- Institution queries
- Enrollment data queries
- Graduation rates queries
- Financial aid queries
- Tuition and fees queries
- Institutional finances queries
- Completions/degrees queries
- Search functionality
- Contract tests (Phase 4 Layer 8)
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.education.ipeds_connector import IPEDSConnector

# Fixtures


@pytest.fixture
def sample_institution():
    """Sample institution data."""
    return {
        "unitid": 110635,
        "institution_name": "University of California-Berkeley",
        "city": "Berkeley",
        "state": "CA",
        "zip": "94720",
        "control": 1,
        "level": 1,
        "degree_granting": 1,
        "carnegie_basic": 15,
        "website": "www.berkeley.edu",
        "enrollment_total": 45000,
        "Founded": 1868,
    }


@pytest.fixture
def sample_enrollment():
    """Sample enrollment data."""
    return {
        "unitid": 110635,
        "institution_name": "University of California-Berkeley",
        "year": 2023,
        "total_enrollment": 45000,
        "full_time": 40000,
        "part_time": 5000,
        "undergraduate": 32000,
        "graduate": 13000,
        "male": 22000,
        "female": 23000,
    }


@pytest.fixture
def sample_graduation():
    """Sample graduation rate data."""
    return {
        "unitid": 110635,
        "institution_name": "University of California-Berkeley",
        "cohort_year": 2020,
        "cohort_size": 8000,
        "grad_rate_4yr": 75.5,
        "grad_rate_6yr": 92.3,
    }


@pytest.fixture
def sample_financial_aid():
    """Sample financial aid data."""
    return {
        "unitid": 110635,
        "institution_name": "University of California-Berkeley",
        "year": 2023,
        "percent_receiving_aid": 65.5,
        "avg_net_price": 15000,
        "avg_grant_amount": 20000,
    }


@pytest.fixture
def sample_tuition():
    """Sample tuition data."""
    return {
        "unitid": 110635,
        "institution_name": "University of California-Berkeley",
        "year": 2024,
        "in_state_tuition": 14000,
        "out_state_tuition": 44000,
        "room_board": 18000,
    }


@pytest.fixture
def ipeds_connector():
    """Create IPEDSConnector instance."""
    return IPEDSConnector()


# Test Classes


class TestIPEDSConnectorInit:
    """Test connector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = IPEDSConnector()
        assert connector.base_url == IPEDSConnector.BASE_URL
        assert connector.api_url == IPEDSConnector.API_BASE_URL
        assert connector.api_key is None

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = IPEDSConnector(timeout=60)
        assert connector.timeout == 60

    def test_get_api_key_returns_none(self):
        """Test that _get_api_key returns None (no auth required)."""
        connector = IPEDSConnector()
        assert connector._get_api_key() is None


class TestIPEDSConnectorConnection:
    """Test connection handling."""

    @patch("krl_data_connectors.education.ipeds_connector.IPEDSConnector._init_session")
    def test_connect_success(self, mock_init_session):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        connector = IPEDSConnector()
        connector.connect()

        assert connector.session is not None
        mock_init_session.assert_called_once()

    @patch("krl_data_connectors.education.ipeds_connector.IPEDSConnector._init_session")
    def test_connect_already_connected(self, mock_init_session):
        """Test connect when already connected."""
        connector = IPEDSConnector()
        connector.session = MagicMock()

        connector.connect()

        # Should not call _init_session again
        mock_init_session.assert_not_called()


class TestIPEDSConnectorGetInstitutions:
    """Test get_institutions method."""

    def test_get_institutions_returns_dataframe(self, ipeds_connector):
        """Test that get_institutions returns DataFrame."""
        result = ipeds_connector.get_institutions()
        assert isinstance(result, pd.DataFrame)

    def test_get_institutions_with_state_filter(self, ipeds_connector):
        """Test institutions query with state filter."""
        result = ipeds_connector.get_institutions(state="CA")
        assert isinstance(result, pd.DataFrame)

    def test_get_institutions_with_control_filter(self, ipeds_connector):
        """Test institutions query with control filter."""
        result = ipeds_connector.get_institutions(control=1)
        assert isinstance(result, pd.DataFrame)

    def test_get_institutions_with_multiple_filters(self, ipeds_connector):
        """Test institutions query with multiple filters."""
        result = ipeds_connector.get_institutions(state="CA", control=1, degree_granting=1)
        assert isinstance(result, pd.DataFrame)

    def test_get_institutions_cached(self, ipeds_connector):
        """Test that cached data is returned on second call."""
        # First call
        result1 = ipeds_connector.get_institutions(state="CA")

        # Second call - should use cache
        result2 = ipeds_connector.get_institutions(state="CA")

        assert result1.equals(result2)


class TestIPEDSConnectorGetEnrollmentData:
    """Test get_enrollment_data method."""

    def test_get_enrollment_data_returns_dataframe(self, ipeds_connector):
        """Test that get_enrollment_data returns DataFrame."""
        result = ipeds_connector.get_enrollment_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_enrollment_data_with_year(self, ipeds_connector):
        """Test enrollment query with year filter."""
        result = ipeds_connector.get_enrollment_data(year=2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_enrollment_data_with_unitid(self, ipeds_connector):
        """Test enrollment query with unit ID."""
        result = ipeds_connector.get_enrollment_data(unitid=110635)
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorGetGraduationRates:
    """Test get_graduation_rates method."""

    def test_get_graduation_rates_returns_dataframe(self, ipeds_connector):
        """Test that get_graduation_rates returns DataFrame."""
        result = ipeds_connector.get_graduation_rates()
        assert isinstance(result, pd.DataFrame)

    def test_get_graduation_rates_with_year(self, ipeds_connector):
        """Test graduation rates query with year."""
        result = ipeds_connector.get_graduation_rates(year=2020)
        assert isinstance(result, pd.DataFrame)

    def test_get_graduation_rates_with_state(self, ipeds_connector):
        """Test graduation rates query with state."""
        result = ipeds_connector.get_graduation_rates(state="CA")
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorGetFinancialAid:
    """Test get_financial_aid method."""

    def test_get_financial_aid_returns_dataframe(self, ipeds_connector):
        """Test that get_financial_aid returns DataFrame."""
        result = ipeds_connector.get_financial_aid()
        assert isinstance(result, pd.DataFrame)

    def test_get_financial_aid_with_filters(self, ipeds_connector):
        """Test financial aid query with filters."""
        result = ipeds_connector.get_financial_aid(year=2023, state="CA")
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorGetTuitionFees:
    """Test get_tuition_fees method."""

    def test_get_tuition_fees_returns_dataframe(self, ipeds_connector):
        """Test that get_tuition_fees returns DataFrame."""
        result = ipeds_connector.get_tuition_fees()
        assert isinstance(result, pd.DataFrame)

    def test_get_tuition_fees_with_year(self, ipeds_connector):
        """Test tuition query with year."""
        result = ipeds_connector.get_tuition_fees(year=2024)
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorGetInstitutionalFinances:
    """Test get_institutional_finances method."""

    def test_get_finances_returns_dataframe(self, ipeds_connector):
        """Test that get_institutional_finances returns DataFrame."""
        result = ipeds_connector.get_institutional_finances()
        assert isinstance(result, pd.DataFrame)

    def test_get_finances_with_filters(self, ipeds_connector):
        """Test finances query with filters."""
        result = ipeds_connector.get_institutional_finances(year=2023, state="CA")
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorGetCompletions:
    """Test get_completions method."""

    def test_get_completions_returns_dataframe(self, ipeds_connector):
        """Test that get_completions returns DataFrame."""
        result = ipeds_connector.get_completions()
        assert isinstance(result, pd.DataFrame)

    def test_get_completions_with_award_level(self, ipeds_connector):
        """Test completions query with award level."""
        result = ipeds_connector.get_completions(award_level=5)
        assert isinstance(result, pd.DataFrame)

    def test_get_completions_with_multiple_filters(self, ipeds_connector):
        """Test completions query with multiple filters."""
        result = ipeds_connector.get_completions(year=2023, award_level=5, state="CA")
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorGetInstitutionByName:
    """Test get_institution_by_name method."""

    def test_get_institution_by_name_returns_dataframe(self, ipeds_connector):
        """Test that get_institution_by_name returns DataFrame."""
        result = ipeds_connector.get_institution_by_name("University of California")
        assert isinstance(result, pd.DataFrame)

    def test_get_institution_by_name_cached(self, ipeds_connector):
        """Test that cached search results are returned."""
        # First call
        result1 = ipeds_connector.get_institution_by_name("Stanford")

        # Second call - should use cache
        result2 = ipeds_connector.get_institution_by_name("Stanford")

        assert result1.equals(result2)


class TestIPEDSConnectorGetInstitutionsByState:
    """Test get_institutions_by_state method."""

    def test_get_institutions_by_state_returns_dataframe(self, ipeds_connector):
        """Test that get_institutions_by_state returns DataFrame."""
        result = ipeds_connector.get_institutions_by_state("CA")
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorGetPublicInstitutions:
    """Test get_public_institutions method."""

    def test_get_public_institutions_returns_dataframe(self, ipeds_connector):
        """Test that get_public_institutions returns DataFrame."""
        result = ipeds_connector.get_public_institutions()
        assert isinstance(result, pd.DataFrame)

    def test_get_public_institutions_with_state(self, ipeds_connector):
        """Test public institutions query with state filter."""
        result = ipeds_connector.get_public_institutions(state="CA")
        assert isinstance(result, pd.DataFrame)


class TestIPEDSConnectorClose:
    """Test close method."""

    def test_close_closes_session(self):
        """Test that close properly closes session."""
        connector = IPEDSConnector()
        connector.session = MagicMock()

        connector.close()

        connector.session.close.assert_called_once()
        assert connector.session is None

    def test_close_when_no_session(self):
        """Test close when session is None."""
        connector = IPEDSConnector()
        connector.session = None

        # Should not raise error
        connector.close()


# Phase 4 Layer 8: Contract Tests


class TestIPEDSConnectorTypeContracts:
    """Contract tests for return types (Phase 4 Layer 8)."""

    def test_get_institutions_returns_dataframe(self, ipeds_connector):
        """Contract: get_institutions returns DataFrame."""
        result = ipeds_connector.get_institutions()
        assert isinstance(result, pd.DataFrame)

    def test_get_enrollment_data_returns_dataframe(self, ipeds_connector):
        """Contract: get_enrollment_data returns DataFrame."""
        result = ipeds_connector.get_enrollment_data()
        assert isinstance(result, pd.DataFrame)

    def test_get_graduation_rates_returns_dataframe(self, ipeds_connector):
        """Contract: get_graduation_rates returns DataFrame."""
        result = ipeds_connector.get_graduation_rates()
        assert isinstance(result, pd.DataFrame)

    def test_get_financial_aid_returns_dataframe(self, ipeds_connector):
        """Contract: get_financial_aid returns DataFrame."""
        result = ipeds_connector.get_financial_aid()
        assert isinstance(result, pd.DataFrame)

    def test_get_tuition_fees_returns_dataframe(self, ipeds_connector):
        """Contract: get_tuition_fees returns DataFrame."""
        result = ipeds_connector.get_tuition_fees()
        assert isinstance(result, pd.DataFrame)

    def test_get_institutional_finances_returns_dataframe(self, ipeds_connector):
        """Contract: get_institutional_finances returns DataFrame."""
        result = ipeds_connector.get_institutional_finances()
        assert isinstance(result, pd.DataFrame)

    def test_get_completions_returns_dataframe(self, ipeds_connector):
        """Contract: get_completions returns DataFrame."""
        result = ipeds_connector.get_completions()
        assert isinstance(result, pd.DataFrame)

    def test_get_institution_by_name_returns_dataframe(self, ipeds_connector):
        """Contract: get_institution_by_name returns DataFrame."""
        result = ipeds_connector.get_institution_by_name("Test")
        assert isinstance(result, pd.DataFrame)

    def test_get_institutions_by_state_returns_dataframe(self, ipeds_connector):
        """Contract: get_institutions_by_state returns DataFrame."""
        result = ipeds_connector.get_institutions_by_state("CA")
        assert isinstance(result, pd.DataFrame)

    def test_get_public_institutions_returns_dataframe(self, ipeds_connector):
        """Contract: get_public_institutions returns DataFrame."""
        result = ipeds_connector.get_public_institutions()
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
