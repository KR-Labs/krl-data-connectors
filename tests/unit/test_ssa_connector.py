# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Tests for SSA Connector."""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from krl_data_connectors.social.ssa_connector import (
    SSAConnector,
    PROGRAM_TYPES,
    BENEFICIARY_TYPES,
    PAYMENT_CATEGORIES,
)


@pytest.fixture
def ssa_connector():
    """Create SSA connector instance for testing."""
    connector = SSAConnector()
    connector.session = MagicMock()
    return connector


class TestSSAConnectorInit:
    """Test SSA connector initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = SSAConnector()
        assert connector.api_url == "https://www.ssa.gov/open/data"
        assert connector._ssa_api_key is None

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = SSAConnector(api_key="test-key")
        assert connector._ssa_api_key == "test-key"

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = SSAConnector(timeout=60)
        assert connector.timeout == 60


class TestSSAConnectorConnection:
    """Test SSA connector connection methods."""

    def test_connect_success(self, ssa_connector):
        """Test successful connection."""
        ssa_connector.session = None
        with patch.object(ssa_connector, "_init_session", return_value=MagicMock()):
            ssa_connector.connect()
            assert ssa_connector.session is not None


class TestSSAConnectorGetBeneficiaryData:
    """Test get_beneficiary_data method."""

    def test_get_beneficiary_data_no_filters(self, ssa_connector):
        """Test getting beneficiary data without filters."""
        mock_response = [{"state": "CA", "program": "oasi", "beneficiaries": 5000000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_beneficiary_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "beneficiaries" in result.columns

    def test_get_beneficiary_data_with_program(self, ssa_connector):
        """Test getting beneficiary data by program."""
        mock_response = [{"state": "CA", "program": "di", "beneficiaries": 500000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_beneficiary_data(program="di")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_beneficiary_data_with_state(self, ssa_connector):
        """Test getting beneficiary data by state."""
        mock_response = [{"state": "TX", "program": "oasi", "beneficiaries": 4000000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_beneficiary_data(state="TX")

            assert isinstance(result, pd.DataFrame)

    def test_get_beneficiary_data_with_year(self, ssa_connector):
        """Test getting beneficiary data by year."""
        mock_response = [{"state": "CA", "program": "oasi", "beneficiaries": 4800000, "year": 2023}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_beneficiary_data(year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_beneficiary_data_with_month(self, ssa_connector):
        """Test getting beneficiary data by month."""
        mock_response = [
            {"state": "CA", "program": "oasi", "beneficiaries": 5000000, "year": 2024, "month": 3}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_beneficiary_data(year=2024, month=3)

            assert isinstance(result, pd.DataFrame)

    def test_get_beneficiary_data_with_beneficiary_type(self, ssa_connector):
        """Test getting beneficiary data by beneficiary type."""
        mock_response = [
            {"beneficiary_type": "retired_workers", "beneficiaries": 3000000, "year": 2024}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_beneficiary_data(beneficiary_type="retired_workers")

            assert isinstance(result, pd.DataFrame)

    def test_get_beneficiary_data_dict_response(self, ssa_connector):
        """Test handling dict response with data key."""
        mock_response = {
            "data": [{"state": "CA", "program": "oasi", "beneficiaries": 5000000, "year": 2024}]
        }

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_beneficiary_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_beneficiary_data_error(self, ssa_connector):
        """Test error handling in get_beneficiary_data."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_beneficiary_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_beneficiary_data_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_beneficiary_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetPaymentData:
    """Test get_payment_data method."""

    def test_get_payment_data_no_filters(self, ssa_connector):
        """Test getting payment data without filters."""
        mock_response = [
            {"state": "CA", "category": "retirement", "total_payments": 50000000000, "year": 2024}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_payment_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "total_payments" in result.columns

    def test_get_payment_data_with_category(self, ssa_connector):
        """Test getting payment data by category."""
        mock_response = [
            {"state": "CA", "category": "disability", "total_payments": 10000000000, "year": 2024}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_payment_data(category="disability")

            assert isinstance(result, pd.DataFrame)

    def test_get_payment_data_with_state(self, ssa_connector):
        """Test getting payment data by state."""
        mock_response = [
            {"state": "NY", "category": "retirement", "total_payments": 45000000000, "year": 2024}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_payment_data(state="NY")

            assert isinstance(result, pd.DataFrame)

    def test_get_payment_data_with_year_and_month(self, ssa_connector):
        """Test getting payment data with year and month."""
        mock_response = [
            {
                "state": "CA",
                "category": "retirement",
                "total_payments": 4000000000,
                "year": 2024,
                "month": 3,
            }
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_payment_data(year=2024, month=3)

            assert isinstance(result, pd.DataFrame)

    def test_get_payment_data_error(self, ssa_connector):
        """Test error handling in get_payment_data."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_payment_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_payment_data_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_payment_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetDisabilityData:
    """Test get_disability_data method."""

    def test_get_disability_data_no_filters(self, ssa_connector):
        """Test getting disability data without filters."""
        mock_response = [{"state": "CA", "disabled_workers": 500000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_disability_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_disability_data_with_state(self, ssa_connector):
        """Test getting disability data by state."""
        mock_response = [{"state": "TX", "disabled_workers": 400000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_disability_data(state="TX")

            assert isinstance(result, pd.DataFrame)

    def test_get_disability_data_with_age_group(self, ssa_connector):
        """Test getting disability data by age group."""
        mock_response = [{"age_group": "50-59", "disabled_workers": 250000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_disability_data(age_group="50-59")

            assert isinstance(result, pd.DataFrame)

    def test_get_disability_data_error(self, ssa_connector):
        """Test error handling in get_disability_data."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_disability_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_disability_data_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_disability_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetRetirementData:
    """Test get_retirement_data method."""

    def test_get_retirement_data_no_filters(self, ssa_connector):
        """Test getting retirement data without filters."""
        mock_response = [{"state": "FL", "retired_workers": 4000000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_retirement_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_retirement_data_with_state(self, ssa_connector):
        """Test getting retirement data by state."""
        mock_response = [{"state": "AZ", "retired_workers": 1200000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_retirement_data(state="AZ")

            assert isinstance(result, pd.DataFrame)

    def test_get_retirement_data_error(self, ssa_connector):
        """Test error handling in get_retirement_data."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_retirement_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_retirement_data_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_retirement_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetSurvivorsData:
    """Test get_survivors_data method."""

    def test_get_survivors_data_no_filters(self, ssa_connector):
        """Test getting survivors data without filters."""
        mock_response = [{"state": "CA", "survivors": 1000000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_survivors_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_survivors_data_with_relationship(self, ssa_connector):
        """Test getting survivors data by relationship."""
        mock_response = [{"relationship": "widow", "survivors": 500000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_survivors_data(relationship="widow")

            assert isinstance(result, pd.DataFrame)

    def test_get_survivors_data_error(self, ssa_connector):
        """Test error handling in get_survivors_data."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_survivors_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_survivors_data_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_survivors_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetSSIData:
    """Test get_ssi_data method."""

    def test_get_ssi_data_no_filters(self, ssa_connector):
        """Test getting SSI data without filters."""
        mock_response = [{"state": "CA", "recipients": 1200000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_ssi_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_ssi_data_with_recipient_type(self, ssa_connector):
        """Test getting SSI data by recipient type."""
        mock_response = [{"recipient_type": "disabled", "recipients": 800000, "year": 2024}]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_ssi_data(recipient_type="disabled")

            assert isinstance(result, pd.DataFrame)

    def test_get_ssi_data_error(self, ssa_connector):
        """Test error handling in get_ssi_data."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_ssi_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_ssi_data_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_ssi_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetStateSummary:
    """Test get_state_summary method."""

    def test_get_state_summary(self, ssa_connector):
        """Test getting state summary data."""
        mock_response = [
            {
                "state": "CA",
                "total_beneficiaries": 6000000,
                "total_payments": 60000000000,
                "year": 2024,
            }
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_state_summary(state="CA")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_state_summary_with_year(self, ssa_connector):
        """Test getting state summary with year filter."""
        mock_response = [
            {
                "state": "TX",
                "total_beneficiaries": 5000000,
                "total_payments": 50000000000,
                "year": 2023,
            }
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_state_summary(state="TX", year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_state_summary_error(self, ssa_connector):
        """Test error handling in get_state_summary."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_state_summary(state="CA")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_state_summary_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_state_summary(state="CA")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetNationalSummary:
    """Test get_national_summary method."""

    def test_get_national_summary_no_filters(self, ssa_connector):
        """Test getting national summary without filters."""
        mock_response = [
            {"total_beneficiaries": 70000000, "total_payments": 1200000000000, "year": 2024}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_national_summary()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_national_summary_with_program(self, ssa_connector):
        """Test getting national summary by program."""
        mock_response = [
            {
                "program": "oasi",
                "total_beneficiaries": 50000000,
                "total_payments": 900000000000,
                "year": 2024,
            }
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_national_summary(program="oasi")

            assert isinstance(result, pd.DataFrame)

    def test_get_national_summary_error(self, ssa_connector):
        """Test error handling in get_national_summary."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_national_summary()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_national_summary_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_national_summary()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetMonthlyStatistics:
    """Test get_monthly_statistics method."""

    def test_get_monthly_statistics(self, ssa_connector):
        """Test getting monthly statistics."""
        mock_response = [
            {"year": 2024, "month": 3, "beneficiaries": 70000000, "payments": 100000000000}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_monthly_statistics(year=2024, month=3)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_monthly_statistics_with_program(self, ssa_connector):
        """Test getting monthly statistics by program."""
        mock_response = [
            {
                "year": 2024,
                "month": 3,
                "program": "di",
                "beneficiaries": 10000000,
                "payments": 15000000000,
            }
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_monthly_statistics(year=2024, month=3, program="di")

            assert isinstance(result, pd.DataFrame)

    def test_get_monthly_statistics_error(self, ssa_connector):
        """Test error handling in get_monthly_statistics."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_monthly_statistics(year=2024, month=3)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_monthly_statistics_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_monthly_statistics(year=2024, month=3)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorGetDemographicData:
    """Test get_demographic_data method."""

    def test_get_demographic_data_no_filters(self, ssa_connector):
        """Test getting demographic data without filters."""
        mock_response = [
            {"age_group": "65-74", "gender": "F", "beneficiaries": 15000000, "year": 2024}
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_demographic_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_demographic_data_with_filters(self, ssa_connector):
        """Test getting demographic data with filters."""
        mock_response = [
            {
                "program": "oasi",
                "age_group": "62-64",
                "gender": "M",
                "beneficiaries": 5000000,
                "year": 2024,
            }
        ]

        with patch.object(ssa_connector, "fetch", return_value=mock_response):
            result = ssa_connector.get_demographic_data(
                program="oasi", age_group="62-64", gender="M"
            )

            assert isinstance(result, pd.DataFrame)

    def test_get_demographic_data_error(self, ssa_connector):
        """Test error handling in get_demographic_data."""
        with patch.object(ssa_connector, "fetch", side_effect=Exception("API error")):
            result = ssa_connector.get_demographic_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_demographic_data_empty_response(self, ssa_connector):
        """Test handling of empty response."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_demographic_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestSSAConnectorClose:
    """Test close method."""

    def test_close(self, ssa_connector):
        """Test closing connection."""
        mock_session = MagicMock()
        ssa_connector.session = mock_session
        ssa_connector.close()
        mock_session.close.assert_called_once()
        assert ssa_connector.session is None


class TestSSAConnectorTypeContracts:
    """Test type contracts and data validation (Phase 4 Layer 8)."""

    def test_get_beneficiary_data_returns_dataframe(self, ssa_connector):
        """Test that get_beneficiary_data returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_beneficiary_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_payment_data_returns_dataframe(self, ssa_connector):
        """Test that get_payment_data returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_payment_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_disability_data_returns_dataframe(self, ssa_connector):
        """Test that get_disability_data returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_disability_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_retirement_data_returns_dataframe(self, ssa_connector):
        """Test that get_retirement_data returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_retirement_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_survivors_data_returns_dataframe(self, ssa_connector):
        """Test that get_survivors_data returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_survivors_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_ssi_data_returns_dataframe(self, ssa_connector):
        """Test that get_ssi_data returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_ssi_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_state_summary_returns_dataframe(self, ssa_connector):
        """Test that get_state_summary returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_state_summary(state="CA")
            assert isinstance(result, pd.DataFrame)

    def test_get_national_summary_returns_dataframe(self, ssa_connector):
        """Test that get_national_summary returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_national_summary()
            assert isinstance(result, pd.DataFrame)

    def test_get_monthly_statistics_returns_dataframe(self, ssa_connector):
        """Test that get_monthly_statistics returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_monthly_statistics(year=2024, month=3)
            assert isinstance(result, pd.DataFrame)

    def test_get_demographic_data_returns_dataframe(self, ssa_connector):
        """Test that get_demographic_data returns DataFrame."""
        with patch.object(ssa_connector, "fetch", return_value={}):
            result = ssa_connector.get_demographic_data()
            assert isinstance(result, pd.DataFrame)

    def test_constants_defined(self):
        """Test that required constants are defined."""
        assert isinstance(PROGRAM_TYPES, dict)
        assert isinstance(BENEFICIARY_TYPES, dict)
        assert isinstance(PAYMENT_CATEGORIES, dict)
        assert "oasi" in PROGRAM_TYPES
        assert "retired_workers" in BENEFICIARY_TYPES
        assert "retirement" in PAYMENT_CATEGORIES
