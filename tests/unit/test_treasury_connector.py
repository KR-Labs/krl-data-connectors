# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for TreasuryConnector.

This test suite validates the TreasuryConnector's ability to query
U.S. Department of Treasury fiscal data, including treasury rates,
federal debt, revenue, spending, and exchange rates.

Test Coverage:
    - Initialization and configuration
    - Connection management
    - Daily treasury rates queries
    - Monthly treasury rates queries
    - Federal debt queries
    - Federal revenue queries
    - Federal spending queries
    - Exchange rate queries
    - Treasury auction queries
    - Interest expense queries
    - Gift contributions queries
    - Budget outlook queries
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

from krl_data_connectors.financial.treasury_connector import TreasuryConnector


@pytest.fixture
def treasury_connector():
    """Fixture providing a TreasuryConnector instance."""
    return TreasuryConnector(timeout=30)


class TestTreasuryConnectorInit:
    """Test TreasuryConnector initialization."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        connector = TreasuryConnector()
        assert connector.timeout == 30
        assert connector.api_url == TreasuryConnector.API_BASE_URL

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        connector = TreasuryConnector(timeout=60)
        assert connector.timeout == 60

    def test_init_base_url_set(self):
        """Test that base URL is properly set."""
        connector = TreasuryConnector()
        assert connector.BASE_URL == "https://fiscaldata.treasury.gov"
        assert connector.API_BASE_URL.startswith("https://api.fiscaldata.treasury.gov")

    def test_get_api_key_returns_none(self, treasury_connector):
        """Test that _get_api_key returns None (no key required)."""
        api_key = treasury_connector._get_api_key()
        assert api_key is None


class TestTreasuryConnectorConnection:
    """Test TreasuryConnector connection management."""

    @patch('krl_data_connectors.financial.treasury_connector.TreasuryConnector._init_session')
    def test_connect_success(self, mock_init_session, treasury_connector):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        treasury_connector.connect()

        assert treasury_connector.session == mock_session
        mock_init_session.assert_called_once()

    @patch('krl_data_connectors.financial.treasury_connector.TreasuryConnector._init_session')
    def test_connect_already_connected(self, mock_init_session, treasury_connector):
        """Test connect when already connected."""
        treasury_connector.session = MagicMock()

        treasury_connector.connect()

        mock_init_session.assert_not_called()

    @patch('krl_data_connectors.financial.treasury_connector.TreasuryConnector._init_session')
    def test_connect_failure(self, mock_init_session, treasury_connector):
        """Test connection failure."""
        mock_init_session.side_effect = Exception("Connection error")

        with pytest.raises(ConnectionError, match="Could not connect to Treasury API"):
            treasury_connector.connect()


class TestTreasuryConnectorGetDailyTreasuryRates:
    """Test get_daily_treasury_rates method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_daily_treasury_rates_no_filters(self, mock_fetch, treasury_connector):
        """Test getting daily rates without filters."""
        mock_data = pd.DataFrame({'rate': [1.5, 2.0], 'date': ['2023-01-01', '2023-01-02']})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_daily_treasury_rates()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_daily_treasury_rates_with_dates(self, mock_fetch, treasury_connector):
        """Test getting daily rates with date filters."""
        mock_data = pd.DataFrame({'rate': [1.5], 'date': ['2023-01-01']})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_daily_treasury_rates(
            start_date="2023-01-01",
            end_date="2023-01-31"
        )

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_daily_treasury_rates_with_limit(self, mock_fetch, treasury_connector):
        """Test getting daily rates with custom limit."""
        mock_data = pd.DataFrame({'rate': [1.5]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_daily_treasury_rates(limit=500)

        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_daily_treasury_rates_empty_result(self, mock_fetch, treasury_connector):
        """Test getting daily rates with empty result."""
        mock_fetch.return_value = pd.DataFrame()

        result = treasury_connector.get_daily_treasury_rates()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestTreasuryConnectorGetMonthlyTreasuryRates:
    """Test get_monthly_treasury_rates method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_monthly_treasury_rates_no_filters(self, mock_fetch, treasury_connector):
        """Test getting monthly rates without filters."""
        mock_data = pd.DataFrame({'rate': [1.5, 2.0]})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_monthly_treasury_rates()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_monthly_treasury_rates_with_dates(self, mock_fetch, treasury_connector):
        """Test getting monthly rates with date filters."""
        mock_data = pd.DataFrame({'rate': [1.5]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_monthly_treasury_rates(
            start_date="2023-01",
            end_date="2023-12"
        )

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetFederalDebt:
    """Test get_federal_debt method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_debt_no_filters(self, mock_fetch, treasury_connector):
        """Test getting federal debt without filters."""
        mock_data = pd.DataFrame({'debt_amount': [30000000000000]})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_federal_debt()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_debt_with_fiscal_year(self, mock_fetch, treasury_connector):
        """Test getting federal debt for specific fiscal year."""
        mock_data = pd.DataFrame({'debt_amount': [30000000000000]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_federal_debt(fiscal_year=2023)

        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_debt_with_dates(self, mock_fetch, treasury_connector):
        """Test getting federal debt with date range."""
        mock_data = pd.DataFrame({'debt_amount': [30000000000000]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_federal_debt(
            start_date="2023-01-01",
            end_date="2023-12-31"
        )

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetFederalRevenue:
    """Test get_federal_revenue method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_revenue_no_filters(self, mock_fetch, treasury_connector):
        """Test getting federal revenue without filters."""
        mock_data = pd.DataFrame({'revenue': [4000000000000]})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_federal_revenue()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_revenue_with_fiscal_year(self, mock_fetch, treasury_connector):
        """Test getting revenue for specific fiscal year."""
        mock_data = pd.DataFrame({'revenue': [4000000000000]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_federal_revenue(fiscal_year=2023)

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetFederalSpending:
    """Test get_federal_spending method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_spending_no_filters(self, mock_fetch, treasury_connector):
        """Test getting federal spending without filters."""
        mock_data = pd.DataFrame({'spending': [5000000000000]})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_federal_spending()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_spending_with_fiscal_year(self, mock_fetch, treasury_connector):
        """Test getting spending for specific fiscal year."""
        mock_data = pd.DataFrame({'spending': [5000000000000]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_federal_spending(fiscal_year=2023)

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetExchangeRates:
    """Test get_exchange_rates method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_exchange_rates_no_filters(self, mock_fetch, treasury_connector):
        """Test getting exchange rates without filters."""
        mock_data = pd.DataFrame({'rate': [6.5], 'country': ['China']})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_exchange_rates()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_exchange_rates_with_country(self, mock_fetch, treasury_connector):
        """Test getting exchange rates for specific country."""
        mock_data = pd.DataFrame({'rate': [6.5]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_exchange_rates(country="China")

        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_exchange_rates_with_dates(self, mock_fetch, treasury_connector):
        """Test getting exchange rates with date range."""
        mock_data = pd.DataFrame({'rate': [6.5]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_exchange_rates(
            start_date="2023-01-01",
            end_date="2023-12-31"
        )

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetTreasuryAuctions:
    """Test get_treasury_auctions method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_treasury_auctions_no_filters(self, mock_fetch, treasury_connector):
        """Test getting treasury auctions without filters."""
        mock_data = pd.DataFrame({'security_type': ['Bill'], 'amount': [1000000000]})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_treasury_auctions()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_treasury_auctions_with_security_type(self, mock_fetch, treasury_connector):
        """Test getting auctions for specific security type."""
        mock_data = pd.DataFrame({'security_type': ['Bill']})
        mock_fetch.return_value = mock_data

        treasury_connector.get_treasury_auctions(security_type="Bill")

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetInterestExpense:
    """Test get_interest_expense method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_interest_expense_no_filters(self, mock_fetch, treasury_connector):
        """Test getting interest expense without filters."""
        mock_data = pd.DataFrame({'expense': [500000000000]})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_interest_expense()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_interest_expense_with_fiscal_year(self, mock_fetch, treasury_connector):
        """Test getting interest expense for specific fiscal year."""
        mock_data = pd.DataFrame({'expense': [500000000000]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_interest_expense(fiscal_year=2023)

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetGiftContributions:
    """Test get_gift_contributions method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_gift_contributions_no_filters(self, mock_fetch, treasury_connector):
        """Test getting gift contributions without filters."""
        mock_data = pd.DataFrame({'amount': [1000000]})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_gift_contributions()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_gift_contributions_with_dates(self, mock_fetch, treasury_connector):
        """Test getting gift contributions with date range."""
        mock_data = pd.DataFrame({'amount': [1000000]})
        mock_fetch.return_value = mock_data

        treasury_connector.get_gift_contributions(
            start_date="2023-01-01",
            end_date="2023-12-31"
        )

        mock_fetch.assert_called_once()


class TestTreasuryConnectorGetBudgetOutlook:
    """Test get_budget_outlook method."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_budget_outlook_no_filters(self, mock_fetch, treasury_connector):
        """Test getting budget outlook without filters."""
        mock_data = pd.DataFrame({'outlook': ['deficit']})
        mock_fetch.return_value = mock_data

        result = treasury_connector.get_budget_outlook()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_budget_outlook_with_fiscal_year(self, mock_fetch, treasury_connector):
        """Test getting budget outlook for specific fiscal year."""
        mock_data = pd.DataFrame({'outlook': ['deficit']})
        mock_fetch.return_value = mock_data

        treasury_connector.get_budget_outlook(fiscal_year=2024)

        mock_fetch.assert_called_once()


class TestTreasuryConnectorClose:
    """Test close method."""

    def test_close_closes_session(self, treasury_connector):
        """Test that close() closes the session."""
        treasury_connector.session = MagicMock()

        treasury_connector.close()

        treasury_connector.session.close.assert_called_once()
        assert treasury_connector.session is None

    def test_close_no_session(self, treasury_connector):
        """Test close when no session exists."""
        treasury_connector.session = None

        treasury_connector.close()

        assert treasury_connector.session is None


class TestTreasuryConnectorTypeContracts:
    """Test type contracts for Phase 4 Layer 8 validation."""

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_daily_treasury_rates_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_daily_treasury_rates returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_daily_treasury_rates()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_monthly_treasury_rates_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_monthly_treasury_rates returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_monthly_treasury_rates()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_debt_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_federal_debt returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_federal_debt()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_revenue_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_federal_revenue returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_federal_revenue()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_federal_spending_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_federal_spending returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_federal_spending()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_exchange_rates_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_exchange_rates returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_exchange_rates()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_treasury_auctions_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_treasury_auctions returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_treasury_auctions()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_interest_expense_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_interest_expense returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_interest_expense()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_gift_contributions_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_gift_contributions returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_gift_contributions()
        assert isinstance(result, pd.DataFrame)

    @patch.object(TreasuryConnector, 'fetch')
    def test_get_budget_outlook_returns_dataframe(self, mock_fetch, treasury_connector):
        """Test that get_budget_outlook returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = treasury_connector.get_budget_outlook()
        assert isinstance(result, pd.DataFrame)
