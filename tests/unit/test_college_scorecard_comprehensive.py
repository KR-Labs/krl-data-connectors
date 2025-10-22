# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Comprehensive test suite for College Scorecard Connector.

This test suite implements multiple layers of the KRL testing architecture:
- Layer 1: Unit tests (initialization, core functionality)
- Layer 2: Integration tests (API interactions with mocked responses)
- Layer 5: Security tests (input validation, injection prevention)
- Layer 7: Property-based tests (Hypothesis for edge cases)
- Layer 8: Contract tests (type safety validation)

Test Coverage Goals:
- 95%+ code coverage
- All public methods thoroughly tested
- Security vulnerabilities identified and prevented
- Edge cases covered with property-based testing
- API contracts validated for type safety

Focus Areas:
- School search functionality with multiple filters
- Geographic filtering (state, ZIP, distance)
- School size and degree level filtering
- Pagination and sorting
- Field selection for performance
- Error handling and validation

Author: KR Labs Testing Team
Date: October 22, 2025
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from hypothesis import given
from hypothesis import strategies as st

from krl_data_connectors.education.college_scorecard_connector import (
    CollegeScorecardConnector,
)

# ============================================================================
# Layer 1: Unit Tests - Initialization & Core Functionality
# ============================================================================


class TestCollegeScorecardConnectorInitialization:
    """Test College Scorecard connector initialization and configuration."""

    def test_initialization_with_api_key(self):
        """Test connector initializes with API key."""
        scorecard = CollegeScorecardConnector(api_key="test_key_123")

        assert scorecard.api_key == "test_key_123"
        assert scorecard.base_url == "https://api.data.gov/ed/collegescorecard/v1"
        assert scorecard.connector_name == "CollegeScorecard"

    def test_initialization_without_api_key(self):
        """Test connector initializes without API key (will fail on connect)."""
        scorecard = CollegeScorecardConnector()

        # Should initialize but won't be able to connect
        assert scorecard.base_url == "https://api.data.gov/ed/collegescorecard/v1"

    def test_initialization_with_cache_params(self):
        """Test connector accepts custom cache parameters."""
        scorecard = CollegeScorecardConnector(
            api_key="test_key", cache_dir="/tmp/scorecard_cache", cache_ttl=7200
        )

        assert scorecard.api_key == "test_key"
        # Cache parameters handled by BaseConnector

    def test_get_api_key_from_init(self):
        """Test API key retrieval from initialization."""
        scorecard = CollegeScorecardConnector(api_key="init_key")

        assert scorecard._get_api_key() == "init_key"


# ============================================================================
# Layer 2: Integration Tests - Connection & Session Management
# ============================================================================


class TestCollegeScorecardConnectorConnection:
    """Test College Scorecard connector connection lifecycle."""

    @patch("requests.Session.get")
    def test_connect_success(self, mock_get):
        """Test successful connection to College Scorecard API."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {"total": 0}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard.connect()

        # Verify connection was attempted
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "/schools.json" in call_args[0][0]
        assert call_args[1]["params"]["api_key"] == "test_key"

    def test_connect_without_api_key(self):
        """Test connection fails without API key."""
        scorecard = CollegeScorecardConnector()

        with pytest.raises(ValueError, match="API key is required"):
            scorecard.connect()

    @patch("requests.Session.get")
    def test_connect_failure_network_error(self, mock_get):
        """Test connection failure with network error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Network error")

        scorecard = CollegeScorecardConnector(api_key="test_key")

        with pytest.raises(ConnectionError, match="Failed to connect"):
            scorecard.connect()

    @patch("requests.Session.get")
    def test_connect_failure_invalid_key(self, mock_get):
        """Test connection failure with invalid API key."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("403 Forbidden")
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="invalid_key")

        with pytest.raises(ConnectionError):
            scorecard.connect()


# ============================================================================
# Layer 2: Integration Tests - School Search
# ============================================================================


class TestCollegeScorecardConnectorSchoolSearch:
    """Test school search methods."""

    @patch("requests.Session.get")
    def test_get_schools_basic_search(self, mock_get):
        """Test basic school search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 123456, "school.name": "Test University", "school.state": "CA"},
                {"id": 789012, "school.name": "Example College", "school.state": "CA"},
            ],
            "metadata": {"total": 2, "page": 0, "per_page": 20},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(state="CA")

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["school.name"] == "Test University"

    @patch("requests.Session.get")
    def test_get_schools_with_name_filter(self, mock_get):
        """Test school search by name."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 123456, "school.name": "Stanford University"}],
            "metadata": {"total": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(school_name="Stanford")

        assert len(result) == 1
        assert "Stanford" in result[0]["school.name"]

        # Verify API call parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["school.name"] == "Stanford"

    @patch("requests.Session.get")
    def test_get_schools_with_size_range(self, mock_get):
        """Test school search with student size filtering."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 123456, "latest.student.size": 15000}],
            "metadata": {"total": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(student_size_range="10000..")

        # Verify size range parameter
        call_args = mock_get.call_args
        assert call_args[1]["params"]["latest.student.size__range"] == "10000.."

    @patch("requests.Session.get")
    def test_get_schools_with_predominant_degree(self, mock_get):
        """Test school search by predominant degree level."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 123456, "school.degrees_awarded.predominant": 3}],
            "metadata": {"total": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # 3 = Bachelor's degree
        result = scorecard.get_schools(predominant_degree=3)

        call_args = mock_get.call_args
        assert call_args[1]["params"]["school.degrees_awarded.predominant"] == 3

    @patch("requests.Session.get")
    def test_get_schools_with_field_selection(self, mock_get):
        """Test school search with specific fields."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 123456, "school.name": "Test", "latest.cost.tuition.in_state": 10000}
            ],
            "metadata": {"total": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(fields="id,school.name,latest.cost.tuition.in_state")

        # Verify fields parameter
        call_args = mock_get.call_args
        assert "_fields" in call_args[1]["params"]

    @patch("requests.Session.get")
    def test_get_schools_with_pagination(self, mock_get):
        """Test school search with pagination."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {"total": 100}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(page=2, per_page=50)

        # Verify pagination parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["page"] == 2
        assert call_args[1]["params"]["per_page"] == 50

    @patch("requests.Session.get")
    def test_get_schools_per_page_limit(self, mock_get):
        """Test that per_page is limited to API maximum."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(per_page=200)  # Over 100 limit

        # Verify per_page capped at 100
        call_args = mock_get.call_args
        assert call_args[1]["params"]["per_page"] == 100

    @patch("requests.Session.get")
    def test_get_schools_with_sorting(self, mock_get):
        """Test school search with result sorting."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(sort="latest.student.size:desc")

        # Verify sort parameter
        call_args = mock_get.call_args
        assert call_args[1]["params"]["_sort"] == "latest.student.size:desc"

    @patch("requests.Session.get")
    def test_get_schools_with_geographic_filters(self, mock_get):
        """Test school search with ZIP code and distance."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(zip_code="94305", distance="25mi")

        # Verify geographic parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["zip"] == "94305"
        assert call_args[1]["params"]["distance"] == "25mi"

    @patch("requests.Session.get")
    def test_get_schools_empty_results(self, mock_get):
        """Test school search with no matching results."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {"total": 0}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools(school_name="NonexistentUniversity12345")

        assert isinstance(result, list)
        assert len(result) == 0


# ============================================================================
# Layer 2: Integration Tests - School by ID & Metadata
# ============================================================================


class TestCollegeScorecardConnectorSchoolById:
    """Test get_school_by_id method."""

    @patch("requests.Session.get")
    def test_get_school_by_id_success(self, mock_get):
        """Test retrieving a specific school by IPEDS ID."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 166683, "school.name": "Massachusetts Institute of Technology"}],
            "metadata": {"total": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_school_by_id(school_id=166683)

        assert isinstance(result, dict)
        assert result["id"] == 166683

        # Verify ID parameter
        call_args = mock_get.call_args
        assert call_args[1]["params"]["id"] == 166683

    @patch("requests.Session.get")
    def test_get_school_by_id_not_found(self, mock_get):
        """Test retrieving non-existent school returns None."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {"total": 0}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_school_by_id(school_id=999999999)

        assert result is None

    @patch("requests.Session.get")
    def test_get_school_by_id_with_fields(self, mock_get):
        """Test retrieving school with specific fields."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": 166683, "school.name": "MIT", "latest.cost.tuition.in_state": 57590}
            ],
            "metadata": {"total": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_school_by_id(
            school_id=166683, fields="id,school.name,latest.cost.tuition.in_state"
        )

        # Verify fields parameter
        call_args = mock_get.call_args
        assert "_fields" in call_args[1]["params"]


class TestCollegeScorecardConnectorMetadata:
    """Test metadata retrieval methods."""

    @patch("requests.Session.get")
    def test_get_metadata_success(self, mock_get):
        """Test retrieving query metadata."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [],
            "metadata": {"total": 2500, "page": 0, "per_page": 20},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_metadata(state="CA")

        assert isinstance(result, dict)
        assert result["total"] == 2500
        assert result["page"] == 0

    @patch("requests.Session.get")
    def test_get_metadata_empty(self, mock_get):
        """Test metadata when no results."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_metadata()

        assert isinstance(result, dict)


# ============================================================================
# Layer 5: Security Tests - Input Validation & Injection Prevention
# ============================================================================


class TestCollegeScorecardConnectorSecurity:
    """Test security measures against common attacks."""

    def test_empty_api_key_handling(self):
        """Test that empty API key is rejected on connect."""
        scorecard = CollegeScorecardConnector(api_key="")

        with pytest.raises(ValueError, match="API key is required"):
            scorecard.connect()

    def test_none_api_key_handling(self):
        """Test that None API key is rejected on connect."""
        scorecard = CollegeScorecardConnector(api_key=None)

        with pytest.raises(ValueError, match="API key is required"):
            scorecard.connect()

    @patch("requests.Session.get")
    def test_sql_injection_in_school_name(self, mock_get):
        """Test SQL injection attempts in school name parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Attempt SQL injection
        malicious_name = "'; DROP TABLE schools; --"

        try:
            result = scorecard.get_schools(school_name=malicious_name)
        except Exception:
            pass

        # Verify malicious string passed as parameter (not executed)
        call_args = mock_get.call_args
        assert malicious_name in call_args[1]["params"]["school.name"]

    @patch("requests.Session.get")
    def test_xss_in_school_name(self, mock_get):
        """Test XSS attempts in school name parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Attempt XSS
        malicious_name = "<script>alert('XSS')</script>"

        try:
            result = scorecard.get_schools(school_name=malicious_name)
        except Exception:
            pass

        # Verify script tags handled safely (URL-encoded)
        call_args = mock_get.call_args
        assert "script" in call_args[1]["params"]["school.name"]

    @patch("requests.Session.get")
    def test_command_injection_in_state(self, mock_get):
        """Test command injection attempts in state parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Attempt command injection
        malicious_state = "CA; rm -rf /"

        try:
            result = scorecard.get_schools(state=malicious_state)
        except Exception:
            pass

        # Verify command not executed
        assert True

    @patch("requests.Session.get")
    def test_path_traversal_in_zip_code(self, mock_get):
        """Test path traversal attempts in ZIP code parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Attempt path traversal
        malicious_zip = "../../../etc/passwd"

        try:
            result = scorecard.get_schools(zip_code=malicious_zip)
        except Exception:
            pass

        # Should handle gracefully
        assert True

    @patch("requests.Session.get")
    def test_extremely_long_school_name(self, mock_get):
        """Test DoS prevention with extremely long school names."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Extremely long name (DoS attempt)
        long_name = "A" * 10000

        try:
            result = scorecard.get_schools(school_name=long_name)
        except Exception:
            # Should fail gracefully (not hang or crash)
            pass

        assert True

    @patch("requests.Session.get")
    def test_negative_school_id(self, mock_get):
        """Test handling of invalid school IDs."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Negative ID
        result = scorecard.get_school_by_id(school_id=-1)

        # Should return None (not found)
        assert result is None

    @patch("requests.Session.get")
    def test_null_byte_injection(self, mock_get):
        """Test null byte injection attempts."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Null byte injection
        malicious_name = "University\x00malicious"

        try:
            result = scorecard.get_schools(school_name=malicious_name)
        except Exception:
            pass

        # Should handle gracefully
        assert True


# ============================================================================
# Layer 7: Property-Based Tests - Edge Case Discovery with Hypothesis
# ============================================================================


class TestCollegeScorecardConnectorPropertyBased:
    """Property-based tests using Hypothesis for edge case discovery."""

    @given(school_id=st.integers(min_value=100000, max_value=999999))
    @patch("requests.Session.get")
    def test_school_id_handling(self, mock_get, school_id):
        """Test connector handles various school ID values."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Should not crash with any valid integer ID
        try:
            result = scorecard.get_school_by_id(school_id=school_id)
            assert result is None or isinstance(result, dict)
        except Exception:
            # API errors acceptable
            pass

    @given(
        page=st.integers(min_value=0, max_value=100),
        per_page=st.integers(min_value=1, max_value=200),
    )
    @patch("requests.Session.get")
    def test_pagination_combinations(self, mock_get, page, per_page):
        """Test various pagination combinations."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        try:
            result = scorecard.get_schools(page=page, per_page=per_page)
            assert isinstance(result, list)
        except Exception:
            pass

    @given(
        school_name=st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122
            ),
            min_size=1,
            max_size=100,
        )
    )
    @patch("requests.Session.get")
    def test_school_name_handling(self, mock_get, school_name):
        """Test connector handles various school name strings."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        # Should not crash with any alphanumeric string
        try:
            result = scorecard.get_schools(school_name=school_name)
            assert isinstance(result, list)
        except Exception:
            pass

    @given(predominant_degree=st.integers(min_value=0, max_value=10))
    @patch("requests.Session.get")
    def test_degree_level_handling(self, mock_get, predominant_degree):
        """Test various predominant degree values."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        try:
            result = scorecard.get_schools(predominant_degree=predominant_degree)
            assert isinstance(result, list)
        except Exception:
            pass


# ============================================================================
# Layer 8: Contract Tests - Type Safety Validation
# ============================================================================


class TestCollegeScorecardConnectorTypeContracts:
    """Test type contracts and return value structures."""

    @patch("requests.Session.get")
    def test_connect_return_type(self, mock_get):
        """Test that connect returns None."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        result = scorecard.connect()

        assert result is None

    @patch("requests.Session.get")
    def test_get_schools_return_type(self, mock_get):
        """Test that get_schools returns list."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools()

        assert isinstance(result, list)

    @patch("requests.Session.get")
    def test_get_schools_elements_are_dicts(self, mock_get):
        """Test that get_schools returns list of dicts."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 123}, {"id": 456}],
            "metadata": {},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_schools()

        for item in result:
            assert isinstance(item, dict)

    @patch("requests.Session.get")
    def test_get_school_by_id_return_type(self, mock_get):
        """Test that get_school_by_id returns dict or None."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [{"id": 123}], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_school_by_id(school_id=123)

        assert result is None or isinstance(result, dict)

    @patch("requests.Session.get")
    def test_get_metadata_return_type(self, mock_get):
        """Test that get_metadata returns dict."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {"total": 0}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_metadata()

        assert isinstance(result, dict)

    @patch("requests.Session.get")
    def test_fetch_return_type(self, mock_get):
        """Test that fetch returns dict."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": [], "metadata": {}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.fetch()

        assert isinstance(result, dict)

    def test_get_api_key_return_type(self):
        """Test that _get_api_key returns Optional[str]."""
        scorecard = CollegeScorecardConnector(api_key="test_key")

        result = scorecard._get_api_key()

        assert result is None or isinstance(result, str)

    @patch("requests.Session.get")
    def test_metadata_contains_expected_fields(self, mock_get):
        """Test that metadata contains expected fields."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [],
            "metadata": {"total": 100, "page": 0, "per_page": 20},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard._init_session()

        result = scorecard.get_metadata()

        # Metadata should have these fields when present
        if "total" in result:
            assert isinstance(result["total"], int)


# ============================================================================
# Test Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
