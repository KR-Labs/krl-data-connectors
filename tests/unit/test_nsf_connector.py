# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for NSFConnector.

Tests the National Science Foundation data connector functionality
including research awards, funding, institutions, and investigators.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import datetime

from krl_data_connectors.science.nsf_connector import (
    NSFConnector,
    AWARD_TYPES,
    DIRECTORATES,
    FUNDING_INSTRUMENTS,
)


class TestNSFConnectorInit:
    """Test NSFConnector initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = NSFConnector()
        assert connector.timeout == 30
        assert connector.api_url == "https://api.nsf.gov/services/v1/awards.json"

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = NSFConnector(api_key="test_key")
        assert connector._nsf_api_key == "test_key"

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = NSFConnector(timeout=60)
        assert connector.timeout == 60


class TestNSFConnectorConnection:
    """Test NSFConnector connection management."""

    def test_connect_success(self):
        """Test successful connection."""
        connector = NSFConnector(api_key="test_key")
        connector.connect()
        assert connector.session is not None
        connector.close()


class TestNSFConnectorGetAwards:
    """Test get_awards method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_awards_no_filters(self, nsf_connector):
        """Test getting awards without filters."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345678", "title": "Research Award", "fundsObligatedAmt": "500000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_awards_with_keyword(self, nsf_connector):
        """Test getting awards by keyword."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345679",
                        "title": "Machine Learning Research",
                        "fundsObligatedAmt": "750000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards(keyword="machine learning")

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_with_directorate(self, nsf_connector):
        """Test getting awards by directorate."""
        mock_response = {
            "response": {
                "award": [{"id": "2345680", "directorate": "CSE", "fundsObligatedAmt": "600000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards(directorate="CSE")

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_with_year(self, nsf_connector):
        """Test getting awards by year."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345681", "startDate": "2023-01-15", "fundsObligatedAmt": "800000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards(year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_with_award_id(self, nsf_connector):
        """Test getting specific award by ID."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345682", "title": "Specific Award", "fundsObligatedAmt": "450000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards(award_id="2345682")

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_list_response(self, nsf_connector):
        """Test getting awards with list response."""
        mock_response = [{"id": "2345683", "title": "Award", "fundsObligatedAmt": "550000"}]

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards()

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_awards_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetInstitutionAwards:
    """Test get_institution_awards method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_institution_awards_no_filters(self, nsf_connector):
        """Test getting institution awards without filters."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345684",
                        "institution": "Stanford University",
                        "fundsObligatedAmt": "1000000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_institution_awards()

            assert isinstance(result, pd.DataFrame)

    def test_get_institution_awards_with_name(self, nsf_connector):
        """Test getting institution awards by name."""
        mock_response = {
            "response": {
                "award": [{"id": "2345685", "institution": "MIT", "fundsObligatedAmt": "950000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_institution_awards(institution_name="MIT")

            assert isinstance(result, pd.DataFrame)

    def test_get_institution_awards_with_state(self, nsf_connector):
        """Test getting institution awards by state."""
        mock_response = {
            "response": {"award": [{"id": "2345686", "state": "CA", "fundsObligatedAmt": "850000"}]}
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_institution_awards(state="CA")

            assert isinstance(result, pd.DataFrame)

    def test_get_institution_awards_with_zip(self, nsf_connector):
        """Test getting institution awards by ZIP code."""
        mock_response = {
            "response": {
                "award": [{"id": "2345687", "zipCode": "02139", "fundsObligatedAmt": "900000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_institution_awards(zip_code="02139")

            assert isinstance(result, pd.DataFrame)

    def test_get_institution_awards_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_institution_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_institution_awards_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_institution_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetInvestigatorAwards:
    """Test get_investigator_awards method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_investigator_awards_no_filters(self, nsf_connector):
        """Test getting investigator awards without filters."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345688",
                        "piFirstName": "Jane",
                        "piLastName": "Smith",
                        "fundsObligatedAmt": "600000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_investigator_awards()

            assert isinstance(result, pd.DataFrame)

    def test_get_investigator_awards_with_name(self, nsf_connector):
        """Test getting investigator awards by name."""
        mock_response = {
            "response": {
                "award": [{"id": "2345689", "piLastName": "Johnson", "fundsObligatedAmt": "700000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_investigator_awards(last_name="Johnson")

            assert isinstance(result, pd.DataFrame)

    def test_get_investigator_awards_with_pi_name(self, nsf_connector):
        """Test getting investigator awards by PI name."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345690",
                        "piFirstName": "John",
                        "piLastName": "Doe",
                        "fundsObligatedAmt": "650000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_investigator_awards(pi_name="John Doe")

            assert isinstance(result, pd.DataFrame)

    def test_get_investigator_awards_with_year(self, nsf_connector):
        """Test getting investigator awards by year."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345691", "startDate": "2023-06-01", "fundsObligatedAmt": "750000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_investigator_awards(year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_investigator_awards_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_investigator_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_investigator_awards_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_investigator_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetFundingByDirectorate:
    """Test get_funding_by_directorate method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_funding_by_directorate(self, nsf_connector):
        """Test getting funding by directorate."""
        mock_response = {
            "response": {
                "award": [{"id": "2345692", "directorate": "CSE", "fundsObligatedAmt": "500000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_funding_by_directorate(directorate="CSE")

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_directorate_with_year(self, nsf_connector):
        """Test getting funding by directorate and year."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345693",
                        "directorate": "BIO",
                        "startDate": "2023-01-01",
                        "fundsObligatedAmt": "600000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_funding_by_directorate(directorate="BIO", year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_directorate_with_instrument(self, nsf_connector):
        """Test getting funding by directorate and funding instrument."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345694",
                        "directorate": "ENG",
                        "awardInstrument": "Standard Grant",
                        "fundsObligatedAmt": "550000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_funding_by_directorate(
                directorate="ENG", funding_instrument="Standard Grant"
            )

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_directorate_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_funding_by_directorate(directorate="MPS")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_funding_by_directorate_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_funding_by_directorate(directorate="GEO")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetAwardsByProgram:
    """Test get_awards_by_program method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_awards_by_program_no_filters(self, nsf_connector):
        """Test getting awards by program without filters."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345695", "programElement": "1234", "fundsObligatedAmt": "450000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards_by_program()

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_program_with_name(self, nsf_connector):
        """Test getting awards by program name."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345696", "programElement": "CAREER", "fundsObligatedAmt": "500000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards_by_program(program_name="CAREER")

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_program_with_element(self, nsf_connector):
        """Test getting awards by program element."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345697", "programElement": "7495", "fundsObligatedAmt": "480000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards_by_program(program_element="7495")

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_program_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_awards_by_program()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_awards_by_program_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_awards_by_program()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetAwardAbstract:
    """Test get_award_abstract method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_award_abstract(self, nsf_connector):
        """Test getting award abstract."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345698",
                        "title": "Award Title",
                        "abstractText": "This is the abstract...",
                        "fundsObligatedAmt": "750000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_award_abstract(award_id="2345698")

            assert isinstance(result, pd.DataFrame)

    def test_get_award_abstract_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_award_abstract(award_id="9999999")

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_award_abstract_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_award_abstract(award_id="9999999")

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetFundingStatistics:
    """Test get_funding_statistics method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_funding_statistics_no_filters(self, nsf_connector):
        """Test getting funding statistics without filters."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345699", "fundsObligatedAmt": "600000", "estimatedTotalAmt": "800000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_funding_statistics()

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_statistics_with_state(self, nsf_connector):
        """Test getting funding statistics by state."""
        mock_response = {
            "response": {"award": [{"id": "2345700", "state": "TX", "fundsObligatedAmt": "700000"}]}
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_funding_statistics(state="TX")

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_statistics_with_directorate(self, nsf_connector):
        """Test getting funding statistics by directorate."""
        mock_response = {
            "response": {
                "award": [{"id": "2345701", "directorate": "MPS", "fundsObligatedAmt": "650000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_funding_statistics(directorate="MPS")

            assert isinstance(result, pd.DataFrame)

    def test_get_funding_statistics_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_funding_statistics()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_funding_statistics_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_funding_statistics()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetCollaborativeAwards:
    """Test get_collaborative_awards method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_collaborative_awards_no_filters(self, nsf_connector):
        """Test getting collaborative awards without filters."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345702",
                        "title": "Collaborative Research: ...",
                        "fundsObligatedAmt": "550000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_collaborative_awards()

            assert isinstance(result, pd.DataFrame)

    def test_get_collaborative_awards_with_institution(self, nsf_connector):
        """Test getting collaborative awards by institution."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345703", "institution": "UC Berkeley", "fundsObligatedAmt": "600000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_collaborative_awards(lead_institution="UC Berkeley")

            assert isinstance(result, pd.DataFrame)

    def test_get_collaborative_awards_with_year(self, nsf_connector):
        """Test getting collaborative awards by year."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345704", "startDate": "2023-09-01", "fundsObligatedAmt": "575000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_collaborative_awards(year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_collaborative_awards_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_collaborative_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_collaborative_awards_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_collaborative_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetActiveAwards:
    """Test get_active_awards method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_active_awards_no_filters(self, nsf_connector):
        """Test getting active awards without filters."""
        mock_response = {
            "response": {
                "award": [{"id": "2345705", "status": "active", "fundsObligatedAmt": "500000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_active_awards()

            assert isinstance(result, pd.DataFrame)

    def test_get_active_awards_with_directorate(self, nsf_connector):
        """Test getting active awards by directorate."""
        mock_response = {
            "response": {
                "award": [{"id": "2345706", "directorate": "SBE", "fundsObligatedAmt": "450000"}]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_active_awards(directorate="SBE")

            assert isinstance(result, pd.DataFrame)

    def test_get_active_awards_with_state(self, nsf_connector):
        """Test getting active awards by state."""
        mock_response = {
            "response": {"award": [{"id": "2345707", "state": "NY", "fundsObligatedAmt": "520000"}]}
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_active_awards(state="NY")

            assert isinstance(result, pd.DataFrame)

    def test_get_active_awards_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_active_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_active_awards_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_active_awards()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorGetAwardsByAmount:
    """Test get_awards_by_amount method."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_awards_by_amount_no_filters(self, nsf_connector):
        """Test getting awards by amount without filters."""
        mock_response = {
            "response": {
                "award": [
                    {
                        "id": "2345708",
                        "fundsObligatedAmt": "1000000",
                        "estimatedTotalAmt": "1200000",
                    }
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards_by_amount()

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_amount_with_min(self, nsf_connector):
        """Test getting awards by minimum amount."""
        mock_response = {"response": {"award": [{"id": "2345709", "fundsObligatedAmt": "2000000"}]}}

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards_by_amount(min_amount=1000000)

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_amount_with_max(self, nsf_connector):
        """Test getting awards by maximum amount."""
        mock_response = {"response": {"award": [{"id": "2345710", "fundsObligatedAmt": "500000"}]}}

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards_by_amount(max_amount=1000000)

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_amount_with_year(self, nsf_connector):
        """Test getting awards by amount and year."""
        mock_response = {
            "response": {
                "award": [
                    {"id": "2345711", "startDate": "2023-04-01", "fundsObligatedAmt": "750000"}
                ]
            }
        }

        with patch.object(nsf_connector, "fetch", return_value=mock_response):
            result = nsf_connector.get_awards_by_amount(year=2023)

            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_amount_error(self, nsf_connector):
        """Test handling of fetch error."""
        with patch.object(nsf_connector, "fetch", side_effect=Exception("API error")):
            result = nsf_connector.get_awards_by_amount()

            assert isinstance(result, pd.DataFrame)
            assert result.empty

    def test_get_awards_by_amount_empty_response(self, nsf_connector):
        """Test handling of empty response."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_awards_by_amount()

            assert isinstance(result, pd.DataFrame)
            assert result.empty


class TestNSFConnectorClose:
    """Test close method."""

    def test_close(self):
        """Test closing connection."""
        connector = NSFConnector()
        connector.connect()
        assert connector.session is not None
        connector.close()
        assert connector.session is None


class TestNSFConnectorTypeContracts:
    """Test type contracts and return types (Phase 4 Layer 8)."""

    @pytest.fixture
    def nsf_connector(self):
        """Create NSFConnector instance for testing."""
        connector = NSFConnector()
        yield connector
        connector.close()

    def test_get_awards_returns_dataframe(self, nsf_connector):
        """Test get_awards returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_awards()
            assert isinstance(result, pd.DataFrame)

    def test_get_institution_awards_returns_dataframe(self, nsf_connector):
        """Test get_institution_awards returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_institution_awards()
            assert isinstance(result, pd.DataFrame)

    def test_get_investigator_awards_returns_dataframe(self, nsf_connector):
        """Test get_investigator_awards returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_investigator_awards()
            assert isinstance(result, pd.DataFrame)

    def test_get_funding_by_directorate_returns_dataframe(self, nsf_connector):
        """Test get_funding_by_directorate returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_funding_by_directorate(directorate="CSE")
            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_program_returns_dataframe(self, nsf_connector):
        """Test get_awards_by_program returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_awards_by_program()
            assert isinstance(result, pd.DataFrame)

    def test_get_award_abstract_returns_dataframe(self, nsf_connector):
        """Test get_award_abstract returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_award_abstract(award_id="1234567")
            assert isinstance(result, pd.DataFrame)

    def test_get_funding_statistics_returns_dataframe(self, nsf_connector):
        """Test get_funding_statistics returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_funding_statistics()
            assert isinstance(result, pd.DataFrame)

    def test_get_collaborative_awards_returns_dataframe(self, nsf_connector):
        """Test get_collaborative_awards returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_collaborative_awards()
            assert isinstance(result, pd.DataFrame)

    def test_get_active_awards_returns_dataframe(self, nsf_connector):
        """Test get_active_awards returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_active_awards()
            assert isinstance(result, pd.DataFrame)

    def test_get_awards_by_amount_returns_dataframe(self, nsf_connector):
        """Test get_awards_by_amount returns DataFrame."""
        with patch.object(nsf_connector, "fetch", return_value={}):
            result = nsf_connector.get_awards_by_amount()
            assert isinstance(result, pd.DataFrame)

    def test_constants_are_dicts(self):
        """Test that constants are dictionaries."""
        assert isinstance(AWARD_TYPES, dict)
        assert isinstance(DIRECTORATES, dict)
        assert isinstance(FUNDING_INSTRUMENTS, dict)
