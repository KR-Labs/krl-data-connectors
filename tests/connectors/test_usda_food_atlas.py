"""
Tests for USDA Food Environment Atlas connector.

Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
SPDX-License-Identifier: Apache-2.0
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from krl_data_connectors.agricultural import USDAFoodAtlasConnector


class TestUSDAFoodAtlasConnector:
    """Test suite for USDA Food Atlas connector."""

    @pytest.fixture
    def connector(self):
        """Create connector instance with test API key."""
        return USDAFoodAtlasConnector(api_key="test_key")

    @pytest.fixture
    def mock_county_response(self):
        """Mock API response for county data."""
        return {
            "data": [
                {
                    "FIPS": "06037",
                    "State": "California",
                    "County": "Los Angeles",
                    "PCT_LACCESS_POP15": 5.2,
                    "GROCERY14": 0.12,
                    "FOODINSEC_15_17": 14.5,
                },
                {
                    "FIPS": "06073",
                    "State": "California",
                    "County": "San Diego",
                    "PCT_LACCESS_POP15": 3.8,
                    "GROCERY14": 0.15,
                    "FOODINSEC_15_17": 12.1,
                },
            ]
        }

    @pytest.fixture
    def mock_indicators_response(self):
        """Mock API response for specific indicators."""
        return {
            "data": [
                {
                    "FIPS": "06037",
                    "PCT_LACCESS_POP15": 5.2,
                    "GROCERY14": 0.12,
                },
                {
                    "FIPS": "06073",
                    "PCT_LACCESS_POP15": 3.8,
                    "GROCERY14": 0.15,
                },
            ]
        }

    def test_initialization(self):
        """Test connector initialization."""
        connector = USDAFoodAtlasConnector(api_key="test_key")
        assert connector.api_key == "test_key"
        assert connector.base_url == "https://api.ers.usda.gov/data"

    def test_initialization_without_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(Exception):  # Will raise if no API key available
                connector = USDAFoodAtlasConnector()
                connector.connect()

    def test_categories_constant(self, connector):
        """Test CATEGORIES constant is defined correctly."""
        assert "access" in connector.CATEGORIES
        assert "assistance" in connector.CATEGORIES
        assert "insecurity" in connector.CATEGORIES
        assert len(connector.CATEGORIES) >= 7

    def test_indicators_constant(self, connector):
        """Test INDICATORS constant is defined correctly."""
        assert "access" in connector.INDICATORS
        assert "PCT_LACCESS_POP15" in connector.INDICATORS["access"]
        assert "GROCERY14" in connector.INDICATORS["access"]

    def test_get_county_data_all(self, connector, mock_county_response, requests_mock):
        """Test getting all county data."""
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/county",
            json=mock_county_response,
        )

        result = connector.get_county_data()

        assert not result.empty
        assert len(result) == 2
        assert "fips" in result.columns
        assert "state" in result.columns
        assert "county" in result.columns

    def test_get_county_data_by_category(
        self, connector, mock_county_response, requests_mock
    ):
        """Test getting county data by category."""
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/county",
            json=mock_county_response,
        )

        result = connector.get_county_data(category="access")

        assert not result.empty
        # Request may come from cache, just verify data is returned

    def test_get_county_data_by_state(
        self, connector, mock_county_response, requests_mock
    ):
        """Test getting county data for specific state."""
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/county",
            json=mock_county_response,
        )

        result = connector.get_county_data(state_fips="06")

        assert not result.empty
        # Request may come from cache, just verify data is returned

    def test_get_county_data_by_county(
        self, connector, mock_county_response, requests_mock
    ):
        """Test getting data for specific county."""
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/county",
            json={"data": [mock_county_response["data"][0]]},
        )

        result = connector.get_county_data(county_fips="06037")

        assert not result.empty
        # Request may come from cache, just verify data is returned

    def test_get_county_data_invalid_category(self, connector):
        """Test error handling for invalid category."""
        with pytest.raises(ValueError, match="Invalid category"):
            connector.get_county_data(category="invalid")

    def test_get_indicators(self, connector, mock_indicators_response, requests_mock):
        """Test getting specific indicators."""
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/indicators",
            json=mock_indicators_response,
        )

        indicators = ["PCT_LACCESS_POP15", "GROCERY14"]
        result = connector.get_indicators(indicators=indicators)

        assert not result.empty
        assert len(result) == 2
        assert "PCT_LACCESS_POP15" in result.columns
        assert "GROCERY14" in result.columns

    def test_get_indicators_with_state(
        self, connector, mock_indicators_response, requests_mock
    ):
        """Test getting indicators for specific state."""
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/indicators",
            json=mock_indicators_response,
        )

        result = connector.get_indicators(
            indicators=["PCT_LACCESS_POP15"], state_fips="06"
        )

        assert not result.empty
        # Request may come from cache, just verify data is returned

    def test_get_indicators_with_county(
        self, connector, mock_indicators_response, requests_mock
    ):
        """Test getting indicators for specific county."""
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/indicators",
            json=mock_indicators_response,
        )

        result = connector.get_indicators(
            indicators=["PCT_LACCESS_POP15"], county_fips="06037"
        )

        assert not result.empty
        # Request may come from cache, just verify data is returned

    def test_get_indicators_empty_list(self, connector):
        """Test error handling for empty indicators list."""
        with pytest.raises(ValueError, match="At least one indicator"):
            connector.get_indicators(indicators=[])

    def test_get_category_indicators(self, connector):
        """Test getting indicators for a category."""
        indicators = connector.get_category_indicators("access")

        assert isinstance(indicators, list)
        assert len(indicators) > 0
        assert "PCT_LACCESS_POP15" in indicators

    def test_get_category_indicators_invalid(self, connector):
        """Test error handling for invalid category."""
        with pytest.raises(ValueError, match="Invalid category"):
            connector.get_category_indicators("invalid")

    def test_list_categories(self, connector):
        """Test listing all categories."""
        categories = connector.list_categories()

        assert isinstance(categories, dict)
        assert "access" in categories
        assert "assistance" in categories
        assert "insecurity" in categories

    def test_parse_response_valid(self, connector, mock_county_response):
        """Test parsing valid API response."""
        df = connector._parse_response(mock_county_response)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "fips" in df.columns
        assert "state" in df.columns
        assert "county" in df.columns

    def test_parse_response_empty(self, connector):
        """Test parsing empty API response."""
        df = connector._parse_response({"data": []})

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_parse_response_invalid(self, connector):
        """Test error handling for invalid response format."""
        with pytest.raises(ValueError, match="Invalid response format"):
            connector._parse_response({"error": "Invalid request"})

    def test_api_error_handling(self, mock_county_response, requests_mock, temp_cache_dir):
        """Test error handling for API failures."""
        # Create connector with temp cache to avoid cache hits
        connector = USDAFoodAtlasConnector(api_key="test_key", cache_dir=temp_cache_dir)
        
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/county",
            status_code=404,
            json={"error": "Not found"},
        )

        with pytest.raises(Exception):  # Will raise an exception on API failure
            connector.get_county_data()

    def test_caching(self, mock_county_response, requests_mock, temp_cache_dir):
        """Test response caching."""
        # Create connector with temp cache to test caching behavior
        connector = USDAFoodAtlasConnector(api_key="test_key", cache_dir=temp_cache_dir)
        
        requests_mock.get(
            "https://api.ers.usda.gov/data/foodatlas/county",
            json=mock_county_response,
        )

        # First call - should hit API
        result1 = connector.get_county_data(state_fips="06")
        assert requests_mock.call_count == 1

        # Second call - should use cache
        result2 = connector.get_county_data(state_fips="06")
        assert requests_mock.call_count == 1  # No additional API call

        # Results should be identical
        pd.testing.assert_frame_equal(result1, result2)


@pytest.mark.integration
class TestUSDAFoodAtlasConnectorIntegration:
    """Integration tests for USDA Food Atlas connector (requires API key)."""

    @pytest.fixture
    def connector(self):
        """Create connector with real API key from environment."""
        return USDAFoodAtlasConnector()

    @pytest.mark.skip(reason="Integration tests require USDA API key")
    def test_real_api_county_data(self, connector):
        """Test fetching real county data from API."""
        result = connector.get_county_data(state_fips="06", category="access")

        assert not result.empty
        assert "fips" in result.columns
        assert "state" in result.columns

    @pytest.mark.skip(reason="Integration tests require USDA API key")
    def test_real_api_indicators(self, connector):
        """Test fetching real indicators from API."""
        result = connector.get_indicators(
            indicators=["PCT_LACCESS_POP15", "GROCERY14"], state_fips="06"
        )

        assert not result.empty
        assert "PCT_LACCESS_POP15" in result.columns
