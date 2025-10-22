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
Unit tests for USDA NASS Connector.

Tests cover:
- Type contracts (Layer 8)
- Return type validation
"""

from unittest.mock import Mock, patch

import pytest

from krl_data_connectors.agricultural.usda_nass_connector import USDANASSConnector

# ============================================================================
# Layer 8: Contract Tests
# ============================================================================


class TestUSDANASSConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    @patch("requests.Session.get")
    def test_connect_return_type(self, mock_get):
        """Test that connect returns None."""
        mock_response = Mock()
        mock_response.json.return_value = {"year": ["2020", "2021", "2022"]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")

        result = nass.connect()

        assert result is None

    @patch("requests.Session.get")
    def test_get_data_return_type(self, mock_get):
        """Test that get_data returns list of dicts."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"year": 2020, "state_name": "CALIFORNIA", "Value": "1000"}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass.connect()

        result = nass.get_data(source_desc="SURVEY", year=2020)

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], dict)

    @patch("requests.Session.get")
    def test_get_param_values_return_type(self, mock_get):
        """Test that get_param_values returns list of strings."""
        mock_response = Mock()
        mock_response.json.return_value = {"state_name": ["CALIFORNIA", "TEXAS", "FLORIDA"]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass.connect()

        result = nass.get_param_values("state_name")

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], str)

    @patch("requests.Session.get")
    def test_get_counts_return_type(self, mock_get):
        """Test that get_counts returns int."""
        mock_response = Mock()
        mock_response.json.return_value = {"count": 1250}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass.connect()

        result = nass.get_counts(source_desc="SURVEY", year=2020)

        assert isinstance(result, int)

    @patch("requests.Session.get")
    def test_fetch_return_type(self, mock_get):
        """Test that fetch returns list of dicts."""
        mock_response = Mock()
        mock_response.json.return_value = {"data": [{"year": 2020}]}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        nass = USDANASSConnector(api_key="test_key")
        nass.connect()

        result = nass.fetch(source_desc="SURVEY")

        assert isinstance(result, list)

    def test_get_api_key_return_type(self):
        """Test that _get_api_key returns Optional[str]."""
        nass = USDANASSConnector(api_key="test_key")

        result = nass._get_api_key()

        assert result is None or isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
