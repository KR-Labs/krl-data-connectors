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
Unit tests for USDA Food Atlas Connector.

Tests cover:
- Type contracts (Layer 8)
- Return type validation
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.agricultural.usda_food_atlas_connector import (
    USDAFoodAtlasConnector,
)


# ============================================================================
# Layer 8: Contract Tests
# ============================================================================


class TestUSDAFoodAtlasConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    @patch("requests.Session.get")
    def test_connect_return_type(self, mock_get):
        """Test that connect returns None."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"FIPS": "06001", "County": "Alameda", "State": "California"}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        atlas = USDAFoodAtlasConnector()

        result = atlas.connect()

        assert result is None

    @patch.object(USDAFoodAtlasConnector, "_make_request")
    def test_get_county_data_return_type(self, mock_request):
        """Test that get_county_data returns DataFrame."""
        mock_request.return_value = {
            "data": [{"FIPS": "01001", "County": "Autauga", "State": "Alabama"}]
        }

        atlas = USDAFoodAtlasConnector()

        result = atlas.get_county_data(county_fips="01001")

        assert isinstance(result, pd.DataFrame)

    @patch.object(USDAFoodAtlasConnector, "_make_request")
    def test_get_indicators_return_type(self, mock_request):
        """Test that get_indicators returns DataFrame."""
        mock_request.return_value = {
            "data": [{"FIPS": "01001", "PCT_LACCESS_POP15": 5.2}]
        }

        atlas = USDAFoodAtlasConnector()

        result = atlas.get_indicators(indicators=["PCT_LACCESS_POP15"])

        assert isinstance(result, pd.DataFrame)

    def test_get_category_indicators_return_type(self):
        """Test that get_category_indicators returns list."""
        atlas = USDAFoodAtlasConnector()

        result = atlas.get_category_indicators("access")

        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], str)

    def test_list_categories_return_type(self):
        """Test that list_categories returns dict."""
        atlas = USDAFoodAtlasConnector()

        result = atlas.list_categories()

        assert isinstance(result, dict)

    @patch.object(USDAFoodAtlasConnector, "_make_request")
    def test_fetch_return_type(self, mock_request):
        """Test that fetch returns DataFrame."""
        mock_request.return_value = {
            "data": [{"FIPS": "01001", "County": "Autauga", "State": "Alabama"}]
        }

        atlas = USDAFoodAtlasConnector()

        result = atlas.fetch()

        assert isinstance(result, pd.DataFrame)

    def test_get_api_key_return_type(self):
        """Test that _get_api_key returns None."""
        atlas = USDAFoodAtlasConnector()

        result = atlas._get_api_key()

        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
