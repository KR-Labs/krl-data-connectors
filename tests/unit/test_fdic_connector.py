# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for FDICConnector.

This test suite validates the FDICConnector's ability to query
Federal Deposit Insurance Corporation data, including failed banks,
institution information, financial data, and regulatory information.

Test Coverage:
    - Initialization and configuration
    - Connection management
    - Failed banks queries
    - Institution queries
    - Financial data queries
    - Summary of deposits queries
    - Branch location queries
    - Structure change queries
    - Institution lookup by CERT
    - Institution search by name
    - Financial ratios queries
    - Bank holding company queries
    - Session cleanup
    - Type contracts (Phase 4 Layer 8)

Dependencies:
    - pytest: Test framework
    - unittest.mock: Mocking framework
    - pandas: For DataFrame validation

Author: KR-Labs
License: Apache-2.0
"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from krl_data_connectors.financial.fdic_connector import FDICConnector


@pytest.fixture
def fdic_connector():
    """Fixture providing an FDICConnector instance."""
    return FDICConnector(timeout=30)


class TestFDICConnectorInit:
    """Test FDICConnector initialization."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        connector = FDICConnector()
        assert connector.timeout == 30
        assert connector.api_url == FDICConnector.API_BASE_URL

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        connector = FDICConnector(timeout=60)
        assert connector.timeout == 60

    def test_init_base_url_set(self):
        """Test that base URL is properly set."""
        connector = FDICConnector()
        assert connector.BASE_URL == "https://banks.data.fdic.gov"
        assert connector.API_BASE_URL.startswith("https://banks.data.fdic.gov/api")

    def test_get_api_key_returns_none(self, fdic_connector):
        """Test that _get_api_key returns None (no key required)."""
        api_key = fdic_connector._get_api_key()
        assert api_key is None


class TestFDICConnectorConnection:
    """Test FDICConnector connection management."""

    @patch("krl_data_connectors.financial.fdic_connector.FDICConnector._init_session")
    def test_connect_success(self, mock_init_session, fdic_connector):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        fdic_connector.connect()

        assert fdic_connector.session == mock_session
        mock_init_session.assert_called_once()

    @patch("krl_data_connectors.financial.fdic_connector.FDICConnector._init_session")
    def test_connect_already_connected(self, mock_init_session, fdic_connector):
        """Test connect when already connected."""
        fdic_connector.session = MagicMock()

        fdic_connector.connect()

        mock_init_session.assert_not_called()

    @patch("krl_data_connectors.financial.fdic_connector.FDICConnector._init_session")
    def test_connect_failure(self, mock_init_session, fdic_connector):
        """Test connection failure."""
        mock_init_session.side_effect = Exception("Connection error")

        with pytest.raises(ConnectionError, match="Could not connect to FDIC API"):
            fdic_connector.connect()


class TestFDICConnectorGetFailedBanks:
    """Test get_failed_banks method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_failed_banks_no_filters(self, mock_fetch, fdic_connector):
        """Test getting failed banks without filters."""
        mock_data = pd.DataFrame({"bank_name": ["Test Bank"], "fail_date": ["2023-01-01"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_failed_banks()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_failed_banks_with_dates(self, mock_fetch, fdic_connector):
        """Test getting failed banks with date filters."""
        mock_data = pd.DataFrame({"bank_name": ["Test Bank"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_failed_banks(start_date="2020-01-01", end_date="2023-12-31")

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_failed_banks_with_state(self, mock_fetch, fdic_connector):
        """Test getting failed banks for specific state."""
        mock_data = pd.DataFrame({"bank_name": ["Test Bank"], "state": ["NY"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_failed_banks(state="NY")

        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_failed_banks_empty_result(self, mock_fetch, fdic_connector):
        """Test getting failed banks with empty result."""
        mock_fetch.return_value = pd.DataFrame()

        result = fdic_connector.get_failed_banks()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestFDICConnectorGetInstitutions:
    """Test get_institutions method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_institutions_no_filters(self, mock_fetch, fdic_connector):
        """Test getting institutions without filters."""
        mock_data = pd.DataFrame({"name": ["Test Bank"], "cert": ["12345"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_institutions()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_institutions_with_state(self, mock_fetch, fdic_connector):
        """Test getting institutions for specific state."""
        mock_data = pd.DataFrame({"name": ["Test Bank"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_institutions(state="NY")

        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_institutions_with_city(self, mock_fetch, fdic_connector):
        """Test getting institutions for specific city."""
        mock_data = pd.DataFrame({"name": ["Test Bank"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_institutions(city="New York")

        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_institutions_with_type(self, mock_fetch, fdic_connector):
        """Test getting institutions of specific type."""
        mock_data = pd.DataFrame({"name": ["Test Bank"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_institutions(institution_type="N")

        mock_fetch.assert_called_once()


class TestFDICConnectorGetFinancials:
    """Test get_financials method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_financials_no_filters(self, mock_fetch, fdic_connector):
        """Test getting financial data without filters."""
        mock_data = pd.DataFrame({"cert": ["3511"], "assets": [1000000000]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_financials()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_financials_with_cert(self, mock_fetch, fdic_connector):
        """Test getting financial data for specific institution."""
        mock_data = pd.DataFrame({"cert": ["3511"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_financials(cert="3511")

        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_financials_with_report_date(self, mock_fetch, fdic_connector):
        """Test getting financial data for specific report date."""
        mock_data = pd.DataFrame({"cert": ["3511"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_financials(report_date="2023-12-31")

        mock_fetch.assert_called_once()


class TestFDICConnectorGetSummaryOfDeposits:
    """Test get_summary_of_deposits method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_summary_of_deposits_no_filters(self, mock_fetch, fdic_connector):
        """Test getting summary of deposits without filters."""
        mock_data = pd.DataFrame({"year": [2023], "deposits": [1000000000]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_summary_of_deposits()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_summary_of_deposits_with_year(self, mock_fetch, fdic_connector):
        """Test getting deposits for specific year."""
        mock_data = pd.DataFrame({"year": [2023]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_summary_of_deposits(year=2023)

        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_summary_of_deposits_with_state(self, mock_fetch, fdic_connector):
        """Test getting deposits for specific state."""
        mock_data = pd.DataFrame({"state": ["NY"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_summary_of_deposits(state="NY")

        mock_fetch.assert_called_once()


class TestFDICConnectorGetInstitutionBranches:
    """Test get_institution_branches method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_branches_no_filters(self, mock_fetch, fdic_connector):
        """Test getting branches without filters."""
        mock_data = pd.DataFrame({"cert": ["3511"], "address": ["123 Main St"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_institution_branches()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_branches_with_cert(self, mock_fetch, fdic_connector):
        """Test getting branches for specific institution."""
        mock_data = pd.DataFrame({"cert": ["3511"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_institution_branches(cert="3511")

        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_branches_with_state(self, mock_fetch, fdic_connector):
        """Test getting branches in specific state."""
        mock_data = pd.DataFrame({"state": ["NY"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_institution_branches(state="NY")

        mock_fetch.assert_called_once()


class TestFDICConnectorGetStructureChanges:
    """Test get_structure_changes method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_structure_changes_no_filters(self, mock_fetch, fdic_connector):
        """Test getting structure changes without filters."""
        mock_data = pd.DataFrame({"change_type": ["MERGER"], "date": ["2023-01-01"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_structure_changes()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_structure_changes_with_dates(self, mock_fetch, fdic_connector):
        """Test getting structure changes with date range."""
        mock_data = pd.DataFrame({"change_type": ["MERGER"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_structure_changes(start_date="2023-01-01", end_date="2023-12-31")

        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_structure_changes_with_type(self, mock_fetch, fdic_connector):
        """Test getting structure changes of specific type."""
        mock_data = pd.DataFrame({"change_type": ["MERGER"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_structure_changes(change_type="MERGER")

        mock_fetch.assert_called_once()


class TestFDICConnectorGetInstitutionByCert:
    """Test get_institution_by_cert method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_by_cert(self, mock_fetch, fdic_connector):
        """Test getting institution by CERT number."""
        mock_data = pd.DataFrame({"cert": ["3511"], "name": ["Test Bank"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_institution_by_cert("3511")

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()


class TestFDICConnectorGetInstitutionByName:
    """Test get_institution_by_name method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_by_name(self, mock_fetch, fdic_connector):
        """Test searching institutions by name."""
        mock_data = pd.DataFrame({"name": ["Chase Bank"], "cert": ["628"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_institution_by_name("Chase")

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_by_name_with_limit(self, mock_fetch, fdic_connector):
        """Test searching institutions with custom limit."""
        mock_data = pd.DataFrame({"name": ["Chase Bank"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_institution_by_name("Chase", limit=50)

        mock_fetch.assert_called_once()


class TestFDICConnectorGetFinancialRatios:
    """Test get_financial_ratios method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_financial_ratios_cert_only(self, mock_fetch, fdic_connector):
        """Test getting financial ratios with CERT only."""
        mock_data = pd.DataFrame({"cert": ["3511"], "ratio": [0.12]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_financial_ratios(cert="3511")

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_financial_ratios_with_dates(self, mock_fetch, fdic_connector):
        """Test getting financial ratios with date range."""
        mock_data = pd.DataFrame({"cert": ["3511"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_financial_ratios(
            cert="3511", start_date="2023-01-01", end_date="2023-12-31"
        )

        mock_fetch.assert_called_once()


class TestFDICConnectorGetBankHoldingCompanies:
    """Test get_bank_holding_companies method."""

    @patch.object(FDICConnector, "fetch")
    def test_get_bank_holding_companies_no_filters(self, mock_fetch, fdic_connector):
        """Test getting bank holding companies without filters."""
        mock_data = pd.DataFrame({"name": ["Test BHC"], "cert": ["12345"]})
        mock_fetch.return_value = mock_data

        result = fdic_connector.get_bank_holding_companies()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDICConnector, "fetch")
    def test_get_bank_holding_companies_with_state(self, mock_fetch, fdic_connector):
        """Test getting bank holding companies for specific state."""
        mock_data = pd.DataFrame({"name": ["Test BHC"]})
        mock_fetch.return_value = mock_data

        fdic_connector.get_bank_holding_companies(state="NY")

        mock_fetch.assert_called_once()


class TestFDICConnectorClose:
    """Test close method."""

    def test_close_closes_session(self, fdic_connector):
        """Test that close() closes the session."""
        mock_session = MagicMock()
        fdic_connector.session = mock_session

        fdic_connector.close()

        mock_session.close.assert_called_once()
        assert fdic_connector.session is None

    def test_close_no_session(self, fdic_connector):
        """Test close when no session exists."""
        fdic_connector.session = None

        fdic_connector.close()

        assert fdic_connector.session is None


class TestFDICConnectorTypeContracts:
    """Test type contracts for Phase 4 Layer 8 validation."""

    @patch.object(FDICConnector, "fetch")
    def test_get_failed_banks_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_failed_banks returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_failed_banks()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_institutions_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_institutions returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_institutions()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_financials_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_financials returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_financials()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_summary_of_deposits_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_summary_of_deposits returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_summary_of_deposits()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_branches_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_institution_branches returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_institution_branches()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_structure_changes_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_structure_changes returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_structure_changes()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_by_cert_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_institution_by_cert returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_institution_by_cert("3511")
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_institution_by_name_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_institution_by_name returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_institution_by_name("Chase")
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_financial_ratios_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_financial_ratios returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_financial_ratios(cert="3511")
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDICConnector, "fetch")
    def test_get_bank_holding_companies_returns_dataframe(self, mock_fetch, fdic_connector):
        """Test that get_bank_holding_companies returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fdic_connector.get_bank_holding_companies()
        assert isinstance(result, pd.DataFrame)
