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
Unit tests for U.S. Census Bureau Connector.

Tests cover:
- Type contracts (Layer 8)
- Return type validation
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.census_connector import CensusConnector


# ============================================================================
# Layer 8: Contract Tests
# ============================================================================


class TestCensusConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    @patch.object(CensusConnector, "_make_request")
    def test_connect_return_type(self, mock_request):
        """Test that connect returns None."""
        mock_request.return_value = [["NAME"], ["United States"]]

        census = CensusConnector(api_key="test_key")

        result = census.connect()

        assert result is None

    @patch("requests.Session.get")
    def test_get_data_return_type(self, mock_get):
        """Test that get_data returns DataFrame."""
        mock_response = Mock()
        mock_response.json.return_value = [
            ["NAME", "B01001_001E"],
            ["United States", "331449281"],
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        census = CensusConnector(api_key="test_key")
        census.connect()

        result = census.get_data(
            dataset="acs/acs5",
            year=2019,
            variables=["NAME", "B01001_001E"],
            geography="us:*",
        )

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.get")
    def test_fetch_return_type(self, mock_get):
        """Test that fetch returns DataFrame."""
        mock_response = Mock()
        mock_response.json.return_value = [
            ["NAME", "B01001_001E"],
            ["United States", "331449281"],
        ]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        census = CensusConnector(api_key="test_key")
        census.connect()

        result = census.fetch(
            dataset="acs/acs5", year=2019, variables=["NAME", "B01001_001E"]
        )

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.get")
    def test_list_variables_return_type(self, mock_get):
        """Test that list_variables returns DataFrame."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "variables": {
                "B01001_001E": {"label": "Total Population", "concept": "Sex by Age"}
            }
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        census = CensusConnector(api_key="test_key")
        census.connect()

        result = census.list_variables(dataset="acs/acs5", year=2019)

        assert isinstance(result, pd.DataFrame)

    def test_get_api_key_return_type(self):
        """Test that _get_api_key returns Optional[str]."""
        census = CensusConnector(api_key="test_key")

        result = census._get_api_key()

        assert result is None or isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
