# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Unit tests for College Scorecard Connector.

Tests cover:
- Type contracts (Layer 8)
- Return type validation
"""

from unittest.mock import Mock, patch

import pytest

from krl_data_connectors.education.college_scorecard_connector import (
    CollegeScorecardConnector,
)


# ============================================================================
# Layer 8: Contract Tests
# ============================================================================


class TestCollegeScorecardConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    def test_connect_return_type(self):
        """Test that connect returns None."""
        scorecard = CollegeScorecardConnector(api_key="test_key")

        result = scorecard.connect()

        assert result is None

    @patch("requests.Session.get")
    def test_get_schools_return_type(self, mock_get):
        """Test that get_schools returns dict."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 123456, "school.name": "Test University"}],
            "metadata": {"total": 1},
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard.connect()

        result = scorecard.get_schools()

        assert isinstance(result, dict)
        assert "results" in result

    @patch("requests.Session.get")
    def test_get_school_by_id_return_type(self, mock_get):
        """Test that get_school_by_id returns dict."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"id": 123456, "school.name": "Test University"}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard.connect()

        result = scorecard.get_school_by_id(school_id=123456)

        assert isinstance(result, dict)

    @patch("requests.Session.get")
    def test_get_metadata_return_type(self, mock_get):
        """Test that get_metadata returns dict."""
        mock_response = Mock()
        mock_response.json.return_value = {"fields": {"school.name": {"type": "string"}}}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        scorecard = CollegeScorecardConnector(api_key="test_key")
        scorecard.connect()

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
        scorecard.connect()

        result = scorecard.fetch()

        assert isinstance(result, dict)

    def test_get_api_key_return_type(self):
        """Test that _get_api_key returns Optional[str]."""
        scorecard = CollegeScorecardConnector(api_key="test_key")

        result = scorecard._get_api_key()

        assert result is None or isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
