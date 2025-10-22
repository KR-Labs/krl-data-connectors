# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for NIHConnector.

Tests the National Institutes of Health data connector functionality
including research projects, grants, publications, and clinical trials.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from krl_data_connectors.health.nih_connector import (
    ACTIVITY_CODES,
    AWARD_TYPES,
    NIH_INSTITUTES,
    NIHConnector,
)


class TestNIHConnectorInit:
    """Test NIHConnector initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = NIHConnector()
        assert connector.timeout == 30
        assert connector.api_url == "https://api.reporter.nih.gov/v2/projects/search"

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = NIHConnector(api_key="test_key")
        assert connector._nih_api_key == "test_key"

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = NIHConnector(timeout=60)
        assert connector.timeout == 60


class TestNIHConnectorConnection:
    """Test NIHConnector connection management."""

    def test_connect_success(self):
        """Test successful connection."""
        connector = NIHConnector(api_key="test_key")
        connector.connect()
        assert connector.session is not None
        connector.close()


class TestNIHConnectorGetProjects:
    """Test get_projects method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_projects_no_filters(self, nih_connector):
        """Test getting projects without filters."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123456",
                    "ProjectTitle": "Cancer Research",
                    "AwardAmount": 500000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_projects_with_keywords(self, nih_connector):
        """Test getting projects by keywords."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123457",
                    "ProjectTitle": "Breast Cancer Study",
                    "AwardAmount": 750000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects(keywords="breast cancer")

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_with_fiscal_year(self, nih_connector):
        """Test getting projects by fiscal year."""
        mock_response = {
            "results": [{"ProjectNum": "1R01CA123458", "FiscalYear": 2023, "AwardAmount": 600000}]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects(fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_with_agency(self, nih_connector):
        """Test getting projects by agency."""
        mock_response = {
            "results": [{"ProjectNum": "1R01CA123459", "Agency": "NCI", "AwardAmount": 800000}]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects(agency="NCI")

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_with_project_num(self, nih_connector):
        """Test getting specific project by number."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123460",
                    "ProjectTitle": "Specific Project",
                    "AwardAmount": 450000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects(project_num="1R01CA123460")

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_list_response(self, nih_connector):
        """Test getting projects with list response."""
        mock_response = [
            {"ProjectNum": "1R01CA123461", "ProjectTitle": "Project", "AwardAmount": 550000}
        ]

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects()

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_projects()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_projects_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_projects()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetPIProjects:
    """Test get_pi_projects method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_pi_projects_no_filters(self, nih_connector):
        """Test getting PI projects without filters."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123462",
                    "ContactPiName": "Smith, Jane",
                    "AwardAmount": 500000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_pi_projects()

            assert isinstance(result, pd.DataFrame)

    def test_get_pi_projects_with_name(self, nih_connector):
        """Test getting PI projects by name."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123463",
                    "ContactPiName": "Johnson, Robert",
                    "AwardAmount": 650000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_pi_projects(pi_name="Johnson")

            assert isinstance(result, pd.DataFrame)

    def test_get_pi_projects_with_id(self, nih_connector):
        """Test getting PI projects by ID."""
        mock_response = {
            "results": [
                {"ProjectNum": "1R01CA123464", "PiProfileId": "12345", "AwardAmount": 700000}
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_pi_projects(pi_id="12345")

            assert isinstance(result, pd.DataFrame)

    def test_get_pi_projects_with_fiscal_year(self, nih_connector):
        """Test getting PI projects by fiscal year."""
        mock_response = {
            "results": [{"ProjectNum": "1R01CA123465", "FiscalYear": 2023, "AwardAmount": 600000}]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_pi_projects(fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_pi_projects_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_pi_projects()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_pi_projects_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_pi_projects()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetOrganizationProjects:
    """Test get_organization_projects method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_organization_projects(self, nih_connector):
        """Test getting organization projects."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123466",
                    "Organization": "Harvard University",
                    "AwardAmount": 900000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_organization_projects(organization="Harvard")

            assert isinstance(result, pd.DataFrame)

    def test_get_organization_projects_with_state(self, nih_connector):
        """Test getting organization projects by state."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123467",
                    "Organization": "Stanford",
                    "OrgState": "CA",
                    "AwardAmount": 850000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_organization_projects(organization="Stanford", state="CA")

            assert isinstance(result, pd.DataFrame)

    def test_get_organization_projects_with_fiscal_year(self, nih_connector):
        """Test getting organization projects by fiscal year."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123468",
                    "Organization": "MIT",
                    "FiscalYear": 2023,
                    "AwardAmount": 950000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_organization_projects(organization="MIT", fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_organization_projects_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_organization_projects(organization="Test")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_organization_projects_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_organization_projects(organization="Test")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetProjectsByActivity:
    """Test get_projects_by_activity method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_projects_by_activity(self, nih_connector):
        """Test getting projects by activity code."""
        mock_response = {
            "results": [
                {"ProjectNum": "1R01CA123469", "ActivityCode": "R01", "AwardAmount": 750000}
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects_by_activity(activity_code="R01")

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_by_activity_with_fiscal_year(self, nih_connector):
        """Test getting projects by activity and fiscal year."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R21CA123470",
                    "ActivityCode": "R21",
                    "FiscalYear": 2023,
                    "AwardAmount": 400000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects_by_activity(activity_code="R21", fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_by_activity_with_agency(self, nih_connector):
        """Test getting projects by activity and agency."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1K01CA123471",
                    "ActivityCode": "K01",
                    "Agency": "NCI",
                    "AwardAmount": 600000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_projects_by_activity(activity_code="K01", agency="NCI")

            assert isinstance(result, pd.DataFrame)

    def test_get_projects_by_activity_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_projects_by_activity(activity_code="R01")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_projects_by_activity_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_projects_by_activity(activity_code="R01")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetClinicalTrials:
    """Test get_clinical_trials method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_clinical_trials_no_filters(self, nih_connector):
        """Test getting clinical trials without filters."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1U01CA123472",
                    "ClinicalTrialId": "NCT12345678",
                    "AwardAmount": 2000000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_clinical_trials()

            assert isinstance(result, pd.DataFrame)

    def test_get_clinical_trials_with_keywords(self, nih_connector):
        """Test getting clinical trials by keywords."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1U01CA123473",
                    "ProjectTitle": "Phase III Cancer Trial",
                    "AwardAmount": 2500000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_clinical_trials(keywords="phase III")

            assert isinstance(result, pd.DataFrame)

    def test_get_clinical_trials_with_fiscal_year(self, nih_connector):
        """Test getting clinical trials by fiscal year."""
        mock_response = {
            "results": [{"ProjectNum": "1U01CA123474", "FiscalYear": 2023, "AwardAmount": 1800000}]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_clinical_trials(fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_clinical_trials_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_clinical_trials()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_clinical_trials_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_clinical_trials()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetFundingByState:
    """Test get_funding_by_state method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_funding_by_state(self, nih_connector):
        """Test getting funding by state."""
        mock_response = {
            "results": [{"ProjectNum": "1R01CA123475", "OrgState": "CA", "AwardAmount": 800000}]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_funding_by_state(state="CA")

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_state_with_fiscal_year(self, nih_connector):
        """Test getting funding by state and fiscal year."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123476",
                    "OrgState": "MA",
                    "FiscalYear": 2023,
                    "AwardAmount": 900000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_funding_by_state(state="MA", fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_state_with_agency(self, nih_connector):
        """Test getting funding by state and agency."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123477",
                    "OrgState": "NY",
                    "Agency": "NCI",
                    "AwardAmount": 1000000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_funding_by_state(state="NY", agency="NCI")

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_state_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_funding_by_state(state="TX")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_funding_by_state_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_funding_by_state(state="TX")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetPublications:
    """Test get_publications method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_publications_no_filters(self, nih_connector):
        """Test getting publications without filters."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123478",
                    "Publications": ["PMID:12345678"],
                    "AwardAmount": 600000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_publications()

            assert isinstance(result, pd.DataFrame)

    def test_get_publications_with_project_num(self, nih_connector):
        """Test getting publications by project number."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123479",
                    "Publications": ["PMID:98765432"],
                    "AwardAmount": 650000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_publications(project_num="1R01CA123479")

            assert isinstance(result, pd.DataFrame)

    def test_get_publications_with_pmid(self, nih_connector):
        """Test getting publications by PMID."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123480",
                    "Publications": ["PMID:11111111"],
                    "AwardAmount": 700000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_publications(pmid="11111111")

            assert isinstance(result, pd.DataFrame)

    def test_get_publications_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_publications()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_publications_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_publications()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetProjectDetails:
    """Test get_project_details method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_project_details(self, nih_connector):
        """Test getting project details."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123481",
                    "ProjectTitle": "Detailed Project",
                    "AbstractText": "This is the abstract...",
                    "AwardAmount": 800000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_project_details(project_num="1R01CA123481")

            assert isinstance(result, pd.DataFrame)

    def test_get_project_details_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_project_details(project_num="9999999")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_project_details_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_project_details(project_num="9999999")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetNewAwards:
    """Test get_new_awards method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_new_awards(self, nih_connector):
        """Test getting new awards."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123482",
                    "AwardType": "1",
                    "FiscalYear": 2023,
                    "AwardAmount": 750000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_new_awards(fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_new_awards_with_agency(self, nih_connector):
        """Test getting new awards by agency."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123483",
                    "AwardType": "1",
                    "Agency": "NCI",
                    "FiscalYear": 2023,
                    "AwardAmount": 800000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_new_awards(fiscal_year=2023, agency="NCI")

            assert isinstance(result, pd.DataFrame)

    def test_get_new_awards_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_new_awards(fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_new_awards_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_new_awards(fiscal_year=2023)

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorGetFundingTrends:
    """Test get_funding_trends method."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_funding_trends(self, nih_connector):
        """Test getting funding trends."""
        mock_response = {
            "results": [
                {"ProjectNum": "1R01CA123484", "FiscalYear": 2020, "AwardAmount": 600000},
                {"ProjectNum": "1R01CA123485", "FiscalYear": 2021, "AwardAmount": 650000},
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_funding_trends(start_year=2020, end_year=2021)

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_trends_with_agency(self, nih_connector):
        """Test getting funding trends by agency."""
        mock_response = {
            "results": [
                {
                    "ProjectNum": "1R01CA123486",
                    "FiscalYear": 2020,
                    "Agency": "NCI",
                    "AwardAmount": 700000,
                }
            ]
        }

        with patch.object(nih_connector, "fetch", return_value=mock_response):
            result = nih_connector.get_funding_trends(start_year=2020, end_year=2023, agency="NCI")

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_trends_error(self, nih_connector):
        """Test handling of fetch error."""
        with patch.object(nih_connector, "fetch", side_effect=Exception("API error")):
            result = nih_connector.get_funding_trends(start_year=2020, end_year=2023)

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_funding_trends_empty_response(self, nih_connector):
        """Test handling of empty response."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_funding_trends(start_year=2020, end_year=2023)

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNIHConnectorClose:
    """Test close method."""

    def test_close(self):
        """Test closing connection."""
        connector = NIHConnector()
        connector.connect()
        assert connector.session is not None
        connector.close()
        assert connector.session is None


class TestNIHConnectorTypeContracts:
    """Test type contracts and return types (Phase 4 Layer 8)."""

    @pytest.fixture
    def nih_connector(self):
        """Create NIHConnector instance for testing."""
        connector = NIHConnector()
        yield connector
        connector.close()

    def test_get_projects_returns_dataframe(self, nih_connector):
        """Test get_projects returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_projects()
            assert isinstance(result, pd.DataFrame)

    def test_get_pi_projects_returns_dataframe(self, nih_connector):
        """Test get_pi_projects returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_pi_projects()
            assert isinstance(result, pd.DataFrame)

    def test_get_organization_projects_returns_dataframe(self, nih_connector):
        """Test get_organization_projects returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_organization_projects(organization="Test")
            assert isinstance(result, pd.DataFrame)

    def test_get_projects_by_activity_returns_dataframe(self, nih_connector):
        """Test get_projects_by_activity returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_projects_by_activity(activity_code="R01")
            assert isinstance(result, pd.DataFrame)

    def test_get_clinical_trials_returns_dataframe(self, nih_connector):
        """Test get_clinical_trials returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_clinical_trials()
            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_state_returns_dataframe(self, nih_connector):
        """Test get_funding_by_state returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_funding_by_state(state="CA")
            assert isinstance(result, pd.DataFrame)

    def test_get_publications_returns_dataframe(self, nih_connector):
        """Test get_publications returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_publications()
            assert isinstance(result, pd.DataFrame)

    def test_get_project_details_returns_dataframe(self, nih_connector):
        """Test get_project_details returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_project_details(project_num="1234567")
            assert isinstance(result, pd.DataFrame)

    def test_get_new_awards_returns_dataframe(self, nih_connector):
        """Test get_new_awards returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_new_awards(fiscal_year=2023)
            assert isinstance(result, pd.DataFrame)

    def test_get_funding_trends_returns_dataframe(self, nih_connector):
        """Test get_funding_trends returns DataFrame."""
        with patch.object(nih_connector, "fetch", return_value={}):
            result = nih_connector.get_funding_trends(start_year=2020, end_year=2023)
            assert isinstance(result, pd.DataFrame)

    def test_constants_are_dicts(self):
        """Test that constants are dictionaries."""
        assert isinstance(ACTIVITY_CODES, dict)
        assert isinstance(NIH_INSTITUTES, dict)
        assert isinstance(AWARD_TYPES, dict)
