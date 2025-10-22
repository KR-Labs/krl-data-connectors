# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for VAConnector.

Tests the Department of Veterans Affairs data connector functionality
including facilities, benefits, disability ratings, claims, and healthcare data.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from krl_data_connectors.veterans.va_connector import (
    BENEFIT_TYPES,
    FACILITY_TYPES,
    HEALTHCARE_SERVICES,
    VAConnector,
)


class TestVAConnectorInit:
    """Test VAConnector initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = VAConnector()
        assert connector.timeout == 30
        assert connector.api_url == "https://www.va.gov/api"

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = VAConnector(api_key="test_key")
        assert connector._va_api_key == "test_key"

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = VAConnector(timeout=60)
        assert connector.timeout == 60


class TestVAConnectorConnection:
    """Test VAConnector connection management."""

    def test_connect_success(self):
        """Test successful connection."""
        connector = VAConnector(api_key="test_key")
        connector.connect()
        assert connector.session is not None
        connector.close()


class TestVAConnectorGetFacilities:
    """Test get_facilities method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_facilities_no_filters(self, va_connector):
        """Test getting facilities without filters."""
        mock_response = [
            {"facility_id": "vha_123", "name": "VA Medical Center", "state": "CA", "type": "health"}
        ]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_facilities()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_facilities_with_state(self, va_connector):
        """Test getting facilities by state."""
        mock_response = [
            {
                "facility_id": "vha_456",
                "name": "Dallas VA Medical Center",
                "state": "TX",
                "type": "health",
            }
        ]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_facilities(state="TX")

            assert isinstance(result, pd.DataFrame)
            assert not result.empty

    def test_get_facilities_with_type(self, va_connector):
        """Test getting facilities by type."""
        mock_response = [
            {
                "facility_id": "vba_789",
                "name": "Regional Benefits Office",
                "state": "NY",
                "type": "benefits",
            }
        ]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_facilities(facility_type="benefits")

            assert isinstance(result, pd.DataFrame)

    def test_get_facilities_with_zip(self, va_connector):
        """Test getting facilities by ZIP code."""
        mock_response = [{"facility_id": "vha_999", "name": "Vet Center", "zip": "90210"}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_facilities(zip_code="90210")

            assert isinstance(result, pd.DataFrame)

    def test_get_facilities_dict_response(self, va_connector):
        """Test getting facilities with dict response."""
        mock_response = {
            "data": [{"facility_id": "vha_111", "name": "Cemetery", "type": "cemetery"}]
        }

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_facilities()

            assert isinstance(result, pd.DataFrame)

    def test_get_facilities_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_facilities()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_facilities_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_facilities()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetBenefitsData:
    """Test get_benefits_data method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_benefits_data_no_filters(self, va_connector):
        """Test getting benefits data without filters."""
        mock_response = [
            {"benefit_type": "compensation", "recipients": 5000000, "amount": 75000000000}
        ]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_benefits_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_benefits_data_with_type(self, va_connector):
        """Test getting benefits data by type."""
        mock_response = [{"benefit_type": "education", "recipients": 900000, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_benefits_data(benefit_type="education")

            assert isinstance(result, pd.DataFrame)

    def test_get_benefits_data_with_state(self, va_connector):
        """Test getting benefits data by state."""
        mock_response = [{"state": "CA", "recipients": 2000000, "benefit_type": "compensation"}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_benefits_data(state="CA")

            assert isinstance(result, pd.DataFrame)

    def test_get_benefits_data_with_year(self, va_connector):
        """Test getting benefits data by year."""
        mock_response = [{"year": 2023, "recipients": 5500000, "benefit_type": "compensation"}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_benefits_data(year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_benefits_data_dict_response(self, va_connector):
        """Test benefits data with dict response."""
        mock_response = {"data": [{"benefit_type": "pension", "recipients": 300000}]}

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_benefits_data()

            assert isinstance(result, pd.DataFrame)

    def test_get_benefits_data_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_benefits_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_benefits_data_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_benefits_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetDisabilityRatings:
    """Test get_disability_ratings method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_disability_ratings_no_filters(self, va_connector):
        """Test getting disability ratings without filters."""
        mock_response = [{"rating": 100, "veterans": 500000, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_disability_ratings()

            assert isinstance(result, pd.DataFrame)

    def test_get_disability_ratings_with_rating(self, va_connector):
        """Test getting disability ratings by rating percentage."""
        mock_response = [{"rating": 70, "veterans": 750000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_disability_ratings(rating_percentage=70)

            assert isinstance(result, pd.DataFrame)

    def test_get_disability_ratings_with_state(self, va_connector):
        """Test getting disability ratings by state."""
        mock_response = [{"state": "FL", "rating": 100, "veterans": 85000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_disability_ratings(state="FL")

            assert isinstance(result, pd.DataFrame)

    def test_get_disability_ratings_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_disability_ratings()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_disability_ratings_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_disability_ratings()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetClaimsData:
    """Test get_claims_data method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_claims_data_no_filters(self, va_connector):
        """Test getting claims data without filters."""
        mock_response = [{"claim_type": "compensation", "status": "pending", "count": 150000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_claims_data()

            assert isinstance(result, pd.DataFrame)

    def test_get_claims_data_with_type(self, va_connector):
        """Test getting claims data by type."""
        mock_response = [{"claim_type": "pension", "count": 25000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_claims_data(claim_type="pension")

            assert isinstance(result, pd.DataFrame)

    def test_get_claims_data_with_status(self, va_connector):
        """Test getting claims data by status."""
        mock_response = [{"status": "approved", "count": 500000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_claims_data(status="approved")

            assert isinstance(result, pd.DataFrame)

    def test_get_claims_data_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_claims_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_claims_data_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_claims_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetHealthcareData:
    """Test get_healthcare_data method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_healthcare_data_no_filters(self, va_connector):
        """Test getting healthcare data without filters."""
        mock_response = [{"service_type": "primary_care", "visits": 50000000, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_healthcare_data()

            assert isinstance(result, pd.DataFrame)

    def test_get_healthcare_data_with_service(self, va_connector):
        """Test getting healthcare data by service type."""
        mock_response = [{"service_type": "mental_health", "visits": 15000000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_healthcare_data(service_type="mental_health")

            assert isinstance(result, pd.DataFrame)

    def test_get_healthcare_data_with_state(self, va_connector):
        """Test getting healthcare data by state."""
        mock_response = [{"state": "TX", "visits": 8000000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_healthcare_data(state="TX")

            assert isinstance(result, pd.DataFrame)

    def test_get_healthcare_data_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_healthcare_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_healthcare_data_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_healthcare_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetEnrollmentData:
    """Test get_enrollment_data method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_enrollment_data_no_filters(self, va_connector):
        """Test getting enrollment data without filters."""
        mock_response = [{"priority_group": 1, "enrolled": 1500000, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_enrollment_data()

            assert isinstance(result, pd.DataFrame)

    def test_get_enrollment_data_with_priority(self, va_connector):
        """Test getting enrollment data by priority group."""
        mock_response = [{"priority_group": 5, "enrolled": 2000000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_enrollment_data(priority_group=5)

            assert isinstance(result, pd.DataFrame)

    def test_get_enrollment_data_with_state(self, va_connector):
        """Test getting enrollment data by state."""
        mock_response = [{"state": "CA", "enrolled": 1800000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_enrollment_data(state="CA")

            assert isinstance(result, pd.DataFrame)

    def test_get_enrollment_data_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_enrollment_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_enrollment_data_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_enrollment_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetVeteranPopulation:
    """Test get_veteran_population method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_veteran_population_no_filters(self, va_connector):
        """Test getting veteran population without filters."""
        mock_response = [{"total_veterans": 18500000, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_veteran_population()

            assert isinstance(result, pd.DataFrame)

    def test_get_veteran_population_with_state(self, va_connector):
        """Test getting veteran population by state."""
        mock_response = [{"state": "CA", "veterans": 1700000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_veteran_population(state="CA")

            assert isinstance(result, pd.DataFrame)

    def test_get_veteran_population_with_county(self, va_connector):
        """Test getting veteran population by county."""
        mock_response = [{"county": "Los Angeles", "veterans": 300000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_veteran_population(county="Los Angeles")

            assert isinstance(result, pd.DataFrame)

    def test_get_veteran_population_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_veteran_population()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_veteran_population_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_veteran_population()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetSuicidePreventionData:
    """Test get_suicide_prevention_data method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_suicide_prevention_data_no_filters(self, va_connector):
        """Test getting suicide prevention data without filters."""
        mock_response = [{"program": "Crisis Line", "contacts": 750000, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_suicide_prevention_data()

            assert isinstance(result, pd.DataFrame)

    def test_get_suicide_prevention_data_with_state(self, va_connector):
        """Test getting suicide prevention data by state."""
        mock_response = [{"state": "NY", "contacts": 50000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_suicide_prevention_data(state="NY")

            assert isinstance(result, pd.DataFrame)

    def test_get_suicide_prevention_data_with_year(self, va_connector):
        """Test getting suicide prevention data by year."""
        mock_response = [{"year": 2023, "contacts": 800000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_suicide_prevention_data(year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_suicide_prevention_data_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_suicide_prevention_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_suicide_prevention_data_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_suicide_prevention_data()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetPerformanceMetrics:
    """Test get_performance_metrics method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_performance_metrics_no_filters(self, va_connector):
        """Test getting performance metrics without filters."""
        mock_response = [{"metric_type": "wait_times", "value": 15.5, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_performance_metrics()

            assert isinstance(result, pd.DataFrame)

    def test_get_performance_metrics_with_type(self, va_connector):
        """Test getting performance metrics by type."""
        mock_response = [{"metric_type": "satisfaction", "score": 4.2}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_performance_metrics(metric_type="satisfaction")

            assert isinstance(result, pd.DataFrame)

    def test_get_performance_metrics_with_facility(self, va_connector):
        """Test getting performance metrics by facility."""
        mock_response = [{"facility_id": "vha_123", "metric_type": "outcomes", "value": 0.95}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_performance_metrics(facility_id="vha_123")

            assert isinstance(result, pd.DataFrame)

    def test_get_performance_metrics_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_performance_metrics()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_performance_metrics_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_performance_metrics()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorGetExpenditures:
    """Test get_expenditures method."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_expenditures_no_filters(self, va_connector):
        """Test getting expenditures without filters."""
        mock_response = [{"category": "benefits", "amount": 118000000000, "year": 2023}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_expenditures()

            assert isinstance(result, pd.DataFrame)

    def test_get_expenditures_with_category(self, va_connector):
        """Test getting expenditures by category."""
        mock_response = [{"category": "healthcare", "amount": 90000000000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_expenditures(category="healthcare")

            assert isinstance(result, pd.DataFrame)

    def test_get_expenditures_with_state(self, va_connector):
        """Test getting expenditures by state."""
        mock_response = [{"state": "CA", "amount": 15000000000}]

        with patch.object(va_connector, "fetch", return_value=mock_response):
            result = va_connector.get_expenditures(state="CA")

            assert isinstance(result, pd.DataFrame)

    def test_get_expenditures_error(self, va_connector):
        """Test handling of fetch error."""
        with patch.object(va_connector, "fetch", side_effect=Exception("API error")):
            result = va_connector.get_expenditures()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_expenditures_empty_response(self, va_connector):
        """Test handling of empty response."""
        with patch.object(va_connector, "fetch", return_value={}):
            result = va_connector.get_expenditures()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestVAConnectorClose:
    """Test close method."""

    def test_close(self):
        """Test closing connection."""
        connector = VAConnector()
        connector.connect()
        assert connector.session is not None
        connector.close()
        assert connector.session is None


class TestVAConnectorTypeContracts:
    """Test type contracts and return types (Phase 4 Layer 8)."""

    @pytest.fixture
    def va_connector(self):
        """Create VAConnector instance for testing."""
        connector = VAConnector()
        yield connector
        connector.close()

    def test_get_facilities_returns_dataframe(self, va_connector):
        """Test get_facilities returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_facilities()
            assert isinstance(result, pd.DataFrame)

    def test_get_benefits_data_returns_dataframe(self, va_connector):
        """Test get_benefits_data returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_benefits_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_disability_ratings_returns_dataframe(self, va_connector):
        """Test get_disability_ratings returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_disability_ratings()
            assert isinstance(result, pd.DataFrame)

    def test_get_claims_data_returns_dataframe(self, va_connector):
        """Test get_claims_data returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_claims_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_healthcare_data_returns_dataframe(self, va_connector):
        """Test get_healthcare_data returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_healthcare_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_enrollment_data_returns_dataframe(self, va_connector):
        """Test get_enrollment_data returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_enrollment_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_veteran_population_returns_dataframe(self, va_connector):
        """Test get_veteran_population returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_veteran_population()
            assert isinstance(result, pd.DataFrame)

    def test_get_suicide_prevention_data_returns_dataframe(self, va_connector):
        """Test get_suicide_prevention_data returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_suicide_prevention_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_performance_metrics_returns_dataframe(self, va_connector):
        """Test get_performance_metrics returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_performance_metrics()
            assert isinstance(result, pd.DataFrame)

    def test_get_expenditures_returns_dataframe(self, va_connector):
        """Test get_expenditures returns DataFrame."""
        with patch.object(va_connector, "fetch", return_value=[]):
            result = va_connector.get_expenditures()
            assert isinstance(result, pd.DataFrame)

    def test_constants_are_dicts(self):
        """Test that constants are dictionaries."""
        assert isinstance(FACILITY_TYPES, dict)
        assert isinstance(BENEFIT_TYPES, dict)
        assert isinstance(HEALTHCARE_SERVICES, dict)
