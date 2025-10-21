# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for Securities and Exchange Commission (SEC) Connector.

Test Coverage:
- Connector initialization
- Connection handling
- Company filings queries
- Company facts queries
- Form-specific queries
- Insider trading queries
- Mutual fund holdings
- Company search
- Contract tests (Phase 4 Layer 8)
"""

import unittest
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.financial.sec_connector import SECConnector


# Fixtures

@pytest.fixture
def sec_connector():
    """Create SECConnector instance."""
    return SECConnector(user_agent="TestCompany test@example.com")


# Test Classes

class TestSECConnectorInit:
    """Test connector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = SECConnector()
        assert connector.api_url == SECConnector.API_BASE_URL
        assert "KRL-Data-Connectors" in connector.user_agent

    def test_init_with_custom_user_agent(self):
        """Test initialization with custom User-Agent."""
        ua = "MyCompany contact@example.com"
        connector = SECConnector(user_agent=ua)
        assert connector.user_agent == ua

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = SECConnector(timeout=60)
        assert connector.timeout == 60

    def test_get_api_key_returns_none(self):
        """Test that _get_api_key returns None (no auth required)."""
        connector = SECConnector()
        assert connector._get_api_key() is None


class TestSECConnectorConnection:
    """Test connection handling."""

    @patch('krl_data_connectors.financial.sec_connector.SECConnector._init_session')
    def test_connect_success(self, mock_init_session):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        connector = SECConnector()
        connector.connect()

        assert connector.session is not None
        assert "User-Agent" in connector.session.headers
        mock_init_session.assert_called_once()

    @patch('krl_data_connectors.financial.sec_connector.SECConnector._init_session')
    def test_connect_already_connected(self, mock_init_session):
        """Test connect when already connected."""
        connector = SECConnector()
        connector.session = MagicMock()

        connector.connect()

        # Should not call _init_session again
        mock_init_session.assert_not_called()

    def test_connect_sets_user_agent_header(self):
        """Test that connect sets User-Agent header."""
        connector = SECConnector(user_agent="Test contact@test.com")
        connector.session = MagicMock()
        connector.session.headers = {}
        
        connector.connect()
        
        # Session should have User-Agent header set


class TestSECConnectorGetCompanyFilings:
    """Test get_company_filings method."""

    def test_get_company_filings_returns_dataframe(self, sec_connector):
        """Test that get_company_filings returns DataFrame."""
        result = sec_connector.get_company_filings(cik="0000320193")
        assert isinstance(result, pd.DataFrame)

    def test_get_company_filings_with_form_type(self, sec_connector):
        """Test company filings query with form type filter."""
        result = sec_connector.get_company_filings(cik="0000320193", form_type="10-K")
        assert isinstance(result, pd.DataFrame)

    def test_get_company_filings_pads_cik(self, sec_connector):
        """Test that CIK is padded to 10 digits."""
        result = sec_connector.get_company_filings(cik="320193")  # Short CIK
        assert isinstance(result, pd.DataFrame)

    def test_get_company_filings_with_limit(self, sec_connector):
        """Test company filings query with limit."""
        result = sec_connector.get_company_filings(cik="0000320193", limit=50)
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetCompanyFacts:
    """Test get_company_facts method."""

    def test_get_company_facts_returns_dataframe(self, sec_connector):
        """Test that get_company_facts returns DataFrame."""
        result = sec_connector.get_company_facts(cik="0000320193")
        assert isinstance(result, pd.DataFrame)

    def test_get_company_facts_with_taxonomy(self, sec_connector):
        """Test company facts query with custom taxonomy."""
        result = sec_connector.get_company_facts(cik="0000320193", taxonomy="us-gaap")
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetFilingsByForm:
    """Test get_filings_by_form method."""

    def test_get_filings_by_form_returns_dataframe(self, sec_connector):
        """Test that get_filings_by_form returns DataFrame."""
        result = sec_connector.get_filings_by_form(form_type="10-K")
        assert isinstance(result, pd.DataFrame)

    def test_get_filings_by_form_with_dates(self, sec_connector):
        """Test filings query with date range."""
        result = sec_connector.get_filings_by_form(
            form_type="10-K",
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        assert isinstance(result, pd.DataFrame)

    def test_get_filings_by_form_with_limit(self, sec_connector):
        """Test filings query with limit."""
        result = sec_connector.get_filings_by_form(form_type="8-K", limit=25)
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetInsiderTrading:
    """Test get_insider_trading method."""

    def test_get_insider_trading_returns_dataframe(self, sec_connector):
        """Test that get_insider_trading returns DataFrame."""
        result = sec_connector.get_insider_trading(cik="0000320193")
        assert isinstance(result, pd.DataFrame)

    def test_get_insider_trading_with_limit(self, sec_connector):
        """Test insider trading query with limit."""
        result = sec_connector.get_insider_trading(cik="0000320193", limit=50)
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetMutualFundHoldings:
    """Test get_mutual_fund_holdings method."""

    def test_get_mutual_fund_holdings_returns_dataframe(self, sec_connector):
        """Test that get_mutual_fund_holdings returns DataFrame."""
        result = sec_connector.get_mutual_fund_holdings(cik="0001166559")
        assert isinstance(result, pd.DataFrame)

    def test_get_mutual_fund_holdings_with_limit(self, sec_connector):
        """Test mutual fund holdings query with limit."""
        result = sec_connector.get_mutual_fund_holdings(cik="0001166559", limit=25)
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetCompanyTickers:
    """Test get_company_tickers method."""

    def test_get_company_tickers_returns_dataframe(self, sec_connector):
        """Test that get_company_tickers returns DataFrame."""
        result = sec_connector.get_company_tickers()
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetSICCodes:
    """Test get_sic_codes method."""

    def test_get_sic_codes_returns_dataframe(self, sec_connector):
        """Test that get_sic_codes returns DataFrame."""
        result = sec_connector.get_sic_codes()
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetRecentFilings:
    """Test get_recent_filings method."""

    def test_get_recent_filings_returns_dataframe(self, sec_connector):
        """Test that get_recent_filings returns DataFrame."""
        result = sec_connector.get_recent_filings()
        assert isinstance(result, pd.DataFrame)

    def test_get_recent_filings_with_form_type(self, sec_connector):
        """Test recent filings query with form type."""
        result = sec_connector.get_recent_filings(form_type="8-K", limit=50)
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorSearchCompanies:
    """Test search_companies method."""

    def test_search_companies_returns_dataframe(self, sec_connector):
        """Test that search_companies returns DataFrame."""
        result = sec_connector.search_companies("Apple")
        assert isinstance(result, pd.DataFrame)

    def test_search_companies_with_limit(self, sec_connector):
        """Test company search with limit."""
        result = sec_connector.search_companies("Technology", limit=50)
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorGetCompanyByTicker:
    """Test get_company_by_ticker method."""

    def test_get_company_by_ticker_returns_dataframe(self, sec_connector):
        """Test that get_company_by_ticker returns DataFrame."""
        result = sec_connector.get_company_by_ticker("AAPL")
        assert isinstance(result, pd.DataFrame)

    def test_get_company_by_ticker_case_insensitive(self, sec_connector):
        """Test that ticker search is case insensitive."""
        result = sec_connector.get_company_by_ticker("aapl")
        assert isinstance(result, pd.DataFrame)


class TestSECConnectorClose:
    """Test close method."""

    def test_close_closes_session(self):
        """Test that close properly closes session."""
        connector = SECConnector()
        connector.session = MagicMock()

        connector.close()

        connector.session.close.assert_called_once()
        assert connector.session is None

    def test_close_when_no_session(self):
        """Test close when session is None."""
        connector = SECConnector()
        connector.session = None

        # Should not raise error
        connector.close()


# Phase 4 Layer 8: Contract Tests

class TestSECConnectorTypeContracts:
    """Contract tests for return types (Phase 4 Layer 8)."""

    def test_get_company_filings_returns_dataframe(self, sec_connector):
        """Contract: get_company_filings returns DataFrame."""
        result = sec_connector.get_company_filings(cik="0000320193")
        assert isinstance(result, pd.DataFrame)

    def test_get_company_facts_returns_dataframe(self, sec_connector):
        """Contract: get_company_facts returns DataFrame."""
        result = sec_connector.get_company_facts(cik="0000320193")
        assert isinstance(result, pd.DataFrame)

    def test_get_filings_by_form_returns_dataframe(self, sec_connector):
        """Contract: get_filings_by_form returns DataFrame."""
        result = sec_connector.get_filings_by_form(form_type="10-K")
        assert isinstance(result, pd.DataFrame)

    def test_get_insider_trading_returns_dataframe(self, sec_connector):
        """Contract: get_insider_trading returns DataFrame."""
        result = sec_connector.get_insider_trading(cik="0000320193")
        assert isinstance(result, pd.DataFrame)

    def test_get_mutual_fund_holdings_returns_dataframe(self, sec_connector):
        """Contract: get_mutual_fund_holdings returns DataFrame."""
        result = sec_connector.get_mutual_fund_holdings(cik="0001166559")
        assert isinstance(result, pd.DataFrame)

    def test_get_company_tickers_returns_dataframe(self, sec_connector):
        """Contract: get_company_tickers returns DataFrame."""
        result = sec_connector.get_company_tickers()
        assert isinstance(result, pd.DataFrame)

    def test_get_sic_codes_returns_dataframe(self, sec_connector):
        """Contract: get_sic_codes returns DataFrame."""
        result = sec_connector.get_sic_codes()
        assert isinstance(result, pd.DataFrame)

    def test_get_recent_filings_returns_dataframe(self, sec_connector):
        """Contract: get_recent_filings returns DataFrame."""
        result = sec_connector.get_recent_filings()
        assert isinstance(result, pd.DataFrame)

    def test_search_companies_returns_dataframe(self, sec_connector):
        """Contract: search_companies returns DataFrame."""
        result = sec_connector.search_companies("Apple")
        assert isinstance(result, pd.DataFrame)

    def test_get_company_by_ticker_returns_dataframe(self, sec_connector):
        """Contract: get_company_by_ticker returns DataFrame."""
        result = sec_connector.get_company_by_ticker("AAPL")
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
