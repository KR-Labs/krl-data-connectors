# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for FDAConnector.

This test suite validates the FDAConnector's ability to query
Food and Drug Administration data, including drug recalls, adverse events,
device classifications, and regulatory information.

Test Coverage:
    - Initialization and configuration
    - Connection management
    - Drug recalls queries
    - Drug adverse events queries
    - Device recalls queries
    - Device classifications queries
    - Device adverse events queries
    - Food recalls queries
    - Drug approvals queries
    - Drug labels queries
    - Device registrations queries
    - Tobacco problem reports queries
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

from krl_data_connectors.health.fda_connector import FDAConnector


@pytest.fixture
def fda_connector():
    """Fixture providing an FDAConnector instance."""
    return FDAConnector(timeout=30)


class TestFDAConnectorInit:
    """Test FDAConnector initialization."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        connector = FDAConnector()
        assert connector.timeout == 30
        assert connector.api_url == FDAConnector.API_BASE_URL

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = FDAConnector(api_key="test_key")
        assert connector.api_key == "test_key"

    def test_init_custom_timeout(self):
        """Test initialization with custom timeout."""
        connector = FDAConnector(timeout=60)
        assert connector.timeout == 60

    def test_init_base_url_set(self):
        """Test that base URL is properly set."""
        connector = FDAConnector()
        assert connector.BASE_URL == "https://open.fda.gov"
        assert connector.API_BASE_URL.startswith("https://api.fda.gov")

    def test_get_api_key_returns_key(self):
        """Test that _get_api_key returns configured key."""
        connector = FDAConnector(api_key="test_key")
        api_key = connector._get_api_key()
        assert api_key == "test_key"


class TestFDAConnectorConnection:
    """Test FDAConnector connection management."""

    @patch("krl_data_connectors.health.fda_connector.FDAConnector._init_session")
    def test_connect_success(self, mock_init_session, fda_connector):
        """Test successful connection."""
        mock_session = MagicMock()
        mock_init_session.return_value = mock_session

        fda_connector.connect()

        assert fda_connector.session == mock_session
        mock_init_session.assert_called_once()

    @patch("krl_data_connectors.health.fda_connector.FDAConnector._init_session")
    def test_connect_already_connected(self, mock_init_session, fda_connector):
        """Test connect when already connected."""
        fda_connector.session = MagicMock()

        fda_connector.connect()

        mock_init_session.assert_not_called()

    @patch("krl_data_connectors.health.fda_connector.FDAConnector._init_session")
    def test_connect_failure(self, mock_init_session, fda_connector):
        """Test connection failure."""
        mock_init_session.side_effect = Exception("Connection error")

        with pytest.raises(ConnectionError, match="Could not connect to FDA API"):
            fda_connector.connect()


class TestFDAConnectorGetDrugRecalls:
    """Test get_drug_recalls method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_recalls_no_filters(self, mock_fetch, fda_connector):
        """Test getting drug recalls without filters."""
        mock_data = pd.DataFrame(
            {"product_description": ["Test Drug"], "recall_date": ["20230101"]}
        )
        mock_fetch.return_value = mock_data

        result = fda_connector.get_drug_recalls()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_recalls_with_dates(self, mock_fetch, fda_connector):
        """Test getting drug recalls with date filters."""
        mock_data = pd.DataFrame({"product_description": ["Test Drug"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_drug_recalls(start_date="20230101", end_date="20231231")

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_recalls_with_classification(self, mock_fetch, fda_connector):
        """Test getting drug recalls with classification filter."""
        mock_data = pd.DataFrame({"classification": ["Class I"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_recalls(classification="Class I")

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_recalls_empty_result(self, mock_fetch, fda_connector):
        """Test getting drug recalls with empty result."""
        mock_fetch.return_value = pd.DataFrame()

        result = fda_connector.get_drug_recalls()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestFDAConnectorGetDrugAdverseEvents:
    """Test get_drug_adverse_events method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_adverse_events_no_filters(self, mock_fetch, fda_connector):
        """Test getting adverse events without filters."""
        mock_data = pd.DataFrame({"serious": ["1"], "receivedate": ["20230101"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_drug_adverse_events()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_adverse_events_with_brand_name(self, mock_fetch, fda_connector):
        """Test getting adverse events for specific brand."""
        mock_data = pd.DataFrame({"brand_name": ["Aspirin"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_adverse_events(brand_name="Aspirin")

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_adverse_events_with_generic_name(self, mock_fetch, fda_connector):
        """Test getting adverse events for specific generic."""
        mock_data = pd.DataFrame({"generic_name": ["acetaminophen"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_adverse_events(generic_name="acetaminophen")

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_adverse_events_with_dates(self, mock_fetch, fda_connector):
        """Test getting adverse events with date range."""
        mock_data = pd.DataFrame({"receivedate": ["20230101"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_adverse_events(start_date="20230101", end_date="20231231")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetDeviceRecalls:
    """Test get_device_recalls method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_device_recalls_no_filters(self, mock_fetch, fda_connector):
        """Test getting device recalls without filters."""
        mock_data = pd.DataFrame({"product_description": ["Test Device"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_device_recalls()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_device_recalls_with_dates(self, mock_fetch, fda_connector):
        """Test getting device recalls with date filters."""
        mock_data = pd.DataFrame({"recall_date": ["20230101"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_device_recalls(start_date="20230101", end_date="20231231")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetDeviceClassifications:
    """Test get_device_classifications method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_device_classifications_no_filters(self, mock_fetch, fda_connector):
        """Test getting device classifications without filters."""
        mock_data = pd.DataFrame({"device_class": ["III"], "device_name": ["Pacemaker"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_device_classifications()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_device_classifications_with_class(self, mock_fetch, fda_connector):
        """Test getting classifications for specific class."""
        mock_data = pd.DataFrame({"device_class": ["III"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_device_classifications(device_class="III")

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_device_classifications_with_specialty(self, mock_fetch, fda_connector):
        """Test getting classifications for specific specialty."""
        mock_data = pd.DataFrame({"medical_specialty": ["Cardiovascular"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_device_classifications(medical_specialty="Cardiovascular")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetDeviceAdverseEvents:
    """Test get_device_adverse_events method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_device_adverse_events_no_filters(self, mock_fetch, fda_connector):
        """Test getting device adverse events without filters."""
        mock_data = pd.DataFrame({"device_name": ["Test Device"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_device_adverse_events()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_device_adverse_events_with_name(self, mock_fetch, fda_connector):
        """Test getting adverse events for specific device."""
        mock_data = pd.DataFrame({"device_name": ["Pacemaker"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_device_adverse_events(device_name="Pacemaker")

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_device_adverse_events_with_dates(self, mock_fetch, fda_connector):
        """Test getting device adverse events with date range."""
        mock_data = pd.DataFrame({"date_received": ["20230101"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_device_adverse_events(start_date="20230101", end_date="20231231")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetFoodRecalls:
    """Test get_food_recalls method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_food_recalls_no_filters(self, mock_fetch, fda_connector):
        """Test getting food recalls without filters."""
        mock_data = pd.DataFrame({"product_description": ["Test Food"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_food_recalls()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_food_recalls_with_dates(self, mock_fetch, fda_connector):
        """Test getting food recalls with date filters."""
        mock_data = pd.DataFrame({"recall_date": ["20230101"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_food_recalls(start_date="20230101", end_date="20231231")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetDrugApprovals:
    """Test get_drug_approvals method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_approvals_no_filters(self, mock_fetch, fda_connector):
        """Test getting drug approvals without filters."""
        mock_data = pd.DataFrame({"application_number": ["NDA123456"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_drug_approvals()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_approvals_with_year(self, mock_fetch, fda_connector):
        """Test getting drug approvals for specific year."""
        mock_data = pd.DataFrame({"approval_year": [2023]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_approvals(year=2023)

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_approvals_with_sponsor(self, mock_fetch, fda_connector):
        """Test getting drug approvals for specific sponsor."""
        mock_data = pd.DataFrame({"sponsor_name": ["Test Pharma"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_approvals(sponsor_name="Test Pharma")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetDrugLabels:
    """Test get_drug_labels method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_labels_no_filters(self, mock_fetch, fda_connector):
        """Test getting drug labels without filters."""
        mock_data = pd.DataFrame({"set_id": ["abc123"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_drug_labels()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_labels_with_brand_name(self, mock_fetch, fda_connector):
        """Test getting drug labels for specific brand."""
        mock_data = pd.DataFrame({"brand_name": ["Tylenol"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_labels(brand_name="Tylenol")

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_labels_with_generic_name(self, mock_fetch, fda_connector):
        """Test getting drug labels for specific generic."""
        mock_data = pd.DataFrame({"generic_name": ["acetaminophen"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_drug_labels(generic_name="acetaminophen")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetDeviceRegistrations:
    """Test get_device_registrations method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_device_registrations_no_filters(self, mock_fetch, fda_connector):
        """Test getting device registrations without filters."""
        mock_data = pd.DataFrame({"registration_number": ["1234567"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_device_registrations()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_device_registrations_with_number(self, mock_fetch, fda_connector):
        """Test getting registration for specific number."""
        mock_data = pd.DataFrame({"registration_number": ["1234567"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_device_registrations(registration_number="1234567")

        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_device_registrations_with_name(self, mock_fetch, fda_connector):
        """Test getting registrations for specific device name."""
        mock_data = pd.DataFrame({"proprietary_name": ["Test Device"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_device_registrations(proprietary_name="Test Device")

        mock_fetch.assert_called_once()


class TestFDAConnectorGetTobaccoProblemReports:
    """Test get_tobacco_problem_reports method."""

    @patch.object(FDAConnector, "fetch")
    def test_get_tobacco_problem_reports_no_filters(self, mock_fetch, fda_connector):
        """Test getting tobacco reports without filters."""
        mock_data = pd.DataFrame({"report_id": ["ABC123"]})
        mock_fetch.return_value = mock_data

        result = fda_connector.get_tobacco_problem_reports()

        assert isinstance(result, pd.DataFrame)
        mock_fetch.assert_called_once()

    @patch.object(FDAConnector, "fetch")
    def test_get_tobacco_problem_reports_with_dates(self, mock_fetch, fda_connector):
        """Test getting tobacco reports with date range."""
        mock_data = pd.DataFrame({"date_submitted": ["20230101"]})
        mock_fetch.return_value = mock_data

        fda_connector.get_tobacco_problem_reports(start_date="20230101", end_date="20231231")

        mock_fetch.assert_called_once()


class TestFDAConnectorClose:
    """Test close method."""

    def test_close_closes_session(self, fda_connector):
        """Test that close() closes the session."""
        fda_connector.session = MagicMock()

        fda_connector.close()

        fda_connector.session.close.assert_called_once()
        assert fda_connector.session is None

    def test_close_no_session(self, fda_connector):
        """Test close when no session exists."""
        fda_connector.session = None

        fda_connector.close()

        assert fda_connector.session is None


class TestFDAConnectorTypeContracts:
    """Test type contracts for Phase 4 Layer 8 validation."""

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_recalls_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_drug_recalls returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_drug_recalls()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_adverse_events_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_drug_adverse_events returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_drug_adverse_events()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_device_recalls_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_device_recalls returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_device_recalls()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_device_classifications_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_device_classifications returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_device_classifications()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_device_adverse_events_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_device_adverse_events returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_device_adverse_events()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_food_recalls_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_food_recalls returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_food_recalls()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_approvals_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_drug_approvals returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_drug_approvals()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_drug_labels_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_drug_labels returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_drug_labels()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_device_registrations_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_device_registrations returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_device_registrations()
        assert isinstance(result, pd.DataFrame)

    @patch.object(FDAConnector, "fetch")
    def test_get_tobacco_problem_reports_returns_dataframe(self, mock_fetch, fda_connector):
        """Test that get_tobacco_problem_reports returns DataFrame."""
        mock_fetch.return_value = pd.DataFrame()
        result = fda_connector.get_tobacco_problem_reports()
        assert isinstance(result, pd.DataFrame)
