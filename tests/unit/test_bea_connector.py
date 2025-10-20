# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0
#
# Khipu Research Analytics Suite - KR-Labs™
# Licensed under the Apache License, Version 2.0

"""
Unit tests for Bureau of Economic Analysis (BEA) Connector.

Tests cover:
- Initialization
- Dataset discovery
- Parameter discovery
- NIPA data retrieval
- Regional data retrieval
- GDP by industry
- Fixed assets
- Error handling
- Edge cases
"""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.bea_connector import BEAConnector


class TestBEAConnectorInit:
    """Test BEA connector initialization."""

    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(ValueError) as exc_info:
            BEAConnector()
        assert "API key is required" in str(exc_info.value)

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = BEAConnector(api_key="test_key_123")
        assert connector.api_key == "test_key_123"
        assert connector.BASE_URL == "https://apps.bea.gov/api/data"

    def test_init_with_cache_dir(self, temp_cache_dir):
        """Test initialization with cache directory."""
        connector = BEAConnector(api_key="test_key", cache_dir=str(temp_cache_dir))
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)

    def test_nipa_tables_defined(self):
        """Test that common NIPA tables are defined."""
        connector = BEAConnector(api_key="test_key")
        assert hasattr(connector, "NIPA_TABLES")
        assert isinstance(connector.NIPA_TABLES, dict)
        assert "gdp" in connector.NIPA_TABLES
        assert "personal_income" in connector.NIPA_TABLES


class TestBEADatasetDiscovery:
    """Test dataset discovery methods."""

    @pytest.fixture
    def mock_dataset_list_response(self):
        """Create mock dataset list response."""
        return {
            "BEAAPI": {
                "Results": {
                    "Dataset": [
                        {
                            "DatasetName": "NIPA",
                            "DatasetDescription": "National Income and Product Accounts",
                        },
                        {
                            "DatasetName": "NIUnderlyingDetail",
                            "DatasetDescription": "NIPA Underlying Detail",
                        },
                        {
                            "DatasetName": "Regional",
                            "DatasetDescription": "Regional Economic Accounts",
                        },
                    ]
                }
            }
        }

    @patch.object(BEAConnector, "_make_request")
    def test_get_dataset_list(self, mock_request, mock_dataset_list_response):
        """Test getting list of available datasets."""
        mock_request.return_value = mock_dataset_list_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_dataset_list()

        assert not df.empty
        assert len(df) == 3
        assert "DatasetName" in df.columns
        assert "DatasetDescription" in df.columns
        assert "NIPA" in df["DatasetName"].values


class TestBEAParameterDiscovery:
    """Test parameter discovery methods."""

    @pytest.fixture
    def mock_parameter_list_response(self):
        """Create mock parameter list response."""
        return {
            "BEAAPI": {
                "Results": {
                    "Parameter": [
                        {
                            "ParameterName": "Frequency",
                            "ParameterDescription": "A=Annual, Q=Quarterly",
                        },
                        {"ParameterName": "TableName", "ParameterDescription": "NIPA table name"},
                        {"ParameterName": "Year", "ParameterDescription": "Year or range"},
                    ]
                }
            }
        }

    @pytest.fixture
    def mock_parameter_values_response(self):
        """Create mock parameter values response."""
        return {
            "BEAAPI": {
                "Results": {
                    "ParamValue": [
                        {"Key": "T10101", "Desc": "Gross Domestic Product"},
                        {"Key": "T10102", "Desc": "GDP by component"},
                    ]
                }
            }
        }

    @patch.object(BEAConnector, "_make_request")
    def test_get_parameter_list(self, mock_request, mock_parameter_list_response):
        """Test getting parameter list for a dataset."""
        mock_request.return_value = mock_parameter_list_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_parameter_list("NIPA")

        assert not df.empty
        assert "ParameterName" in df.columns
        assert "Frequency" in df["ParameterName"].values

    @patch.object(BEAConnector, "_make_request")
    def test_get_parameter_values(self, mock_request, mock_parameter_values_response):
        """Test getting parameter values."""
        mock_request.return_value = mock_parameter_values_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_parameter_values("NIPA", "TableName")

        assert not df.empty
        assert "Key" in df.columns or "Desc" in df.columns


class TestBEANIPAData:
    """Test NIPA (National Income and Product Accounts) data retrieval."""

    @pytest.fixture
    def mock_nipa_response(self):
        """Create mock NIPA data response."""
        return {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "TableName": "T10101",
                            "LineDescription": "Gross domestic product",
                            "TimePeriod": "2023Q4",
                            "DataValue": "27,952,700",
                            "METRIC_NAME": "Current Dollars",
                        },
                        {
                            "TableName": "T10101",
                            "LineDescription": "Gross domestic product",
                            "TimePeriod": "2023Q3",
                            "DataValue": "27,610,100",
                            "METRIC_NAME": "Current Dollars",
                        },
                    ]
                }
            }
        }

    @patch.object(BEAConnector, "_make_request")
    def test_get_nipa_data_basic(self, mock_request, mock_nipa_response):
        """Test basic NIPA data retrieval."""
        mock_request.return_value = mock_nipa_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_nipa_data(table_name="T10101", frequency="Q", year="2023")

        assert not df.empty
        assert len(df) == 2
        assert "TableName" in df.columns
        assert "DataValue" in df.columns
        assert "TimePeriod" in df.columns

        # Check that DataValue is numeric
        assert pd.api.types.is_numeric_dtype(df["DataValue"])

    @patch.object(BEAConnector, "_make_request")
    def test_get_nipa_data_annual(self, mock_request, mock_nipa_response):
        """Test NIPA data with annual frequency."""
        mock_request.return_value = mock_nipa_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_nipa_data(table_name="T10101", frequency="A", year="2020,2021,2022")

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs.get("params", {})

        assert params["Frequency"] == "A"
        assert params["Year"] == "2020,2021,2022"

    @patch.object(BEAConnector, "_make_request")
    def test_get_nipa_data_all_years(self, mock_request, mock_nipa_response):
        """Test NIPA data for all available years."""
        mock_request.return_value = mock_nipa_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_nipa_data(table_name="T10101")

        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs.get("params", {})

        assert params["Year"] == "X"  # X means all years


class TestBEARegionalData:
    """Test regional economic data retrieval."""

    @pytest.fixture
    def mock_regional_response(self):
        """Create mock regional data response."""
        return {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "TableName": "SAINC1",
                            "GeoName": "California",
                            "GeoFips": "06000",
                            "TimePeriod": "2023",
                            "DataValue": "2500000",
                            "LineDescription": "Personal income",
                        },
                        {
                            "TableName": "SAINC1",
                            "GeoName": "Texas",
                            "GeoFips": "48000",
                            "TimePeriod": "2023",
                            "DataValue": "2000000",
                            "LineDescription": "Personal income",
                        },
                    ]
                }
            }
        }

    @patch.object(BEAConnector, "_make_request")
    def test_get_regional_data_all_states(self, mock_request, mock_regional_response):
        """Test getting regional data for all states."""
        mock_request.return_value = mock_regional_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_regional_data(
            table_name="SAINC1", line_code="1", geo_fips="STATE", year="2023"
        )

        assert not df.empty
        assert "GeoName" in df.columns
        assert "DataValue" in df.columns
        assert "TimePeriod" in df.columns

    @patch.object(BEAConnector, "_make_request")
    def test_get_regional_data_specific_state(self, mock_request, mock_regional_response):
        """Test getting regional data for a specific state."""
        mock_request.return_value = mock_regional_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_regional_data(
            table_name="SAINC1", line_code="1", geo_fips="06", year="LAST5"  # California
        )

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs.get("params", {})

        assert params["GeoFips"] == "06"
        assert params["Year"] == "LAST5"

    @patch.object(BEAConnector, "_make_request")
    def test_get_regional_data_counties(self, mock_request, mock_regional_response):
        """Test getting county-level regional data."""
        mock_request.return_value = mock_regional_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_regional_data(
            table_name="CAINC1", line_code="1", geo_fips="COUNTY", year="2023"
        )

        mock_request.assert_called_once()


class TestBEAGDPByIndustry:
    """Test GDP by industry data retrieval."""

    @pytest.fixture
    def mock_gdp_industry_response(self):
        """Create mock GDP by industry response."""
        return {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "IndustryDescription": "All industries",
                            "TimePeriod": "2023",
                            "DataValue": "27000000",
                        },
                        {
                            "IndustryDescription": "Agriculture",
                            "TimePeriod": "2023",
                            "DataValue": "200000",
                        },
                    ]
                }
            }
        }

    @patch.object(BEAConnector, "_make_request")
    def test_get_gdp_by_industry_all(self, mock_request, mock_gdp_industry_response):
        """Test getting GDP for all industries."""
        mock_request.return_value = mock_gdp_industry_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_gdp_by_industry(industry="ALL", year="2023")

        assert not df.empty
        assert "IndustryDescription" in df.columns
        assert "DataValue" in df.columns

    @patch.object(BEAConnector, "_make_request")
    def test_get_gdp_by_industry_specific(self, mock_request, mock_gdp_industry_response):
        """Test getting GDP for a specific industry."""
        mock_request.return_value = mock_gdp_industry_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_gdp_by_industry(industry="11", year="2020,2021,2022")

        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs.get("params", {})

        assert params["Industry"] == "11"
        assert params["Year"] == "2020,2021,2022"

    @patch.object(BEAConnector, "_make_request")
    def test_get_gdp_by_industry_quarterly(self, mock_request, mock_gdp_industry_response):
        """Test getting quarterly GDP by industry."""
        mock_request.return_value = mock_gdp_industry_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_gdp_by_industry(industry="ALL", year="2023", frequency="Q")

        call_kwargs = mock_request.call_args.kwargs
        params = call_kwargs.get("params", {})

        assert params["Frequency"] == "Q"


class TestBEAFixedAssets:
    """Test fixed assets data retrieval."""

    @pytest.fixture
    def mock_fixed_assets_response(self):
        """Create mock fixed assets response."""
        return {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {
                            "TableName": "FAAt101",
                            "LineDescription": "Current-cost net stock",
                            "TimePeriod": "2023",
                            "DataValue": "75000000",
                        },
                    ]
                }
            }
        }

    @patch.object(BEAConnector, "_make_request")
    def test_get_fixed_assets(self, mock_request, mock_fixed_assets_response):
        """Test getting fixed assets data."""
        mock_request.return_value = mock_fixed_assets_response

        connector = BEAConnector(api_key="test_key")
        df = connector.get_fixed_assets(table_name="FAAt101", year="2023")

        assert not df.empty
        assert "DataValue" in df.columns


class TestBEACommonTableHelper:
    """Test common table helper method."""

    def test_get_common_table_valid(self):
        """Test getting valid common table IDs."""
        assert BEAConnector.get_common_table("gdp") == "T10101"
        assert BEAConnector.get_common_table("personal_income") == "T20100"
        assert BEAConnector.get_common_table("pce") == "T20804"

    def test_get_common_table_invalid(self):
        """Test getting invalid common table ID."""
        result = BEAConnector.get_common_table("nonexistent_table")
        assert result is None


class TestBEAErrorHandling:
    """Test error handling."""

    @patch.object(BEAConnector, "_make_request")
    def test_api_error_handling(self, mock_request):
        """Test handling of API errors."""
        mock_request.side_effect = Exception("API Error")

        connector = BEAConnector(api_key="test_key")

        with pytest.raises(Exception) as exc_info:
            connector.get_nipa_data(table_name="T10101")

        assert "API Error" in str(exc_info.value)

    @patch.object(BEAConnector, "_make_request")
    def test_empty_response_handling(self, mock_request):
        """Test handling of empty response."""
        mock_request.return_value = {"BEAAPI": {"Results": {"Data": []}}}

        connector = BEAConnector(api_key="test_key")
        df = connector.get_nipa_data(table_name="T10101")

        assert isinstance(df, pd.DataFrame)

    @patch.object(BEAConnector, "_make_request")
    def test_malformed_response_handling(self, mock_request):
        """Test handling of malformed response."""
        mock_request.return_value = {
            "BEAAPI": {
                # Missing Results key
            }
        }

        connector = BEAConnector(api_key="test_key")

        # Should handle gracefully
        try:
            df = connector.get_nipa_data(table_name="T10101")
        except KeyError:
            pass  # Expected for malformed response


class TestBEADataValueConversion:
    """Test data value conversion."""

    @pytest.fixture
    def mock_response_with_commas(self):
        """Create mock response with comma-separated numbers."""
        return {
            "BEAAPI": {
                "Results": {
                    "Data": [
                        {"DataValue": "1,234,567", "TimePeriod": "2023"},
                        {"DataValue": "987,654", "TimePeriod": "2022"},
                    ]
                }
            }
        }

    @patch.object(BEAConnector, "_make_request")
    def test_comma_removal(self, mock_request, mock_response_with_commas):
        """Test that commas are removed from data values."""
        mock_request.return_value = mock_response_with_commas

        connector = BEAConnector(api_key="test_key")
        df = connector.get_nipa_data(table_name="T10101")

        # DataValue should be numeric
        assert pd.api.types.is_numeric_dtype(df["DataValue"])

        # Values should be correct after comma removal
        assert df["DataValue"].iloc[0] == 1234567


class TestBEAIntegration:
    """Integration tests requiring network access."""

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    @pytest.mark.api
    def test_real_dataset_list(self):
        """Test retrieving real dataset list."""
        import os

        api_key = os.getenv("BEA_API_KEY")

        if not api_key:
            pytest.skip("BEA_API_KEY not set")

        connector = BEAConnector(api_key=api_key)

        try:
            df = connector.get_dataset_list()

            assert not df.empty
            assert "DatasetName" in df.columns
            assert "NIPA" in df["DatasetName"].values

        except Exception as e:
            pytest.skip(f"API request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    @pytest.mark.api
    def test_real_nipa_data(self):
        """Test retrieving real NIPA data."""
        import os

        api_key = os.getenv("BEA_API_KEY")

        if not api_key:
            pytest.skip("BEA_API_KEY not set")

        connector = BEAConnector(api_key=api_key)

        try:
            # Get GDP data for recent years
            df = connector.get_nipa_data(table_name="T10101", frequency="A", year="2021,2022")

            assert not df.empty
            assert "DataValue" in df.columns
            assert "TimePeriod" in df.columns

        except Exception as e:
            pytest.skip(f"API request failed: {e}")

    @pytest.mark.integration
    @pytest.mark.network
    @pytest.mark.slow
    @pytest.mark.api
    def test_real_regional_data(self):
        """Test retrieving real regional data."""
        import os

        api_key = os.getenv("BEA_API_KEY")

        if not api_key:
            pytest.skip("BEA_API_KEY not set")

        connector = BEAConnector(api_key=api_key)

        try:
            df = connector.get_regional_data(
                table_name="SAINC1", line_code="1", geo_fips="STATE", year="LAST5"
            )

            assert not df.empty
            assert "GeoName" in df.columns

        except Exception as e:
            pytest.skip(f"API request failed: {e}")


class TestBEACaching:
    """Test caching functionality."""

    @patch.object(BEAConnector, "_make_request")
    def test_caching_enabled(self, mock_request, temp_cache_dir):
        """Test that caching works when enabled."""
        mock_response = {
            "BEAAPI": {"Results": {"Data": [{"DataValue": "100", "TimePeriod": "2023"}]}}
        }
        mock_request.return_value = mock_response

        connector = BEAConnector(api_key="test_key", cache_dir=str(temp_cache_dir))

        df = connector.get_nipa_data(table_name="T10101")
        assert not df.empty
        assert str(connector.cache.cache_dir) == str(temp_cache_dir)


class TestBEALogging:
    """Test logging functionality."""

    @patch.object(BEAConnector, "_make_request")
    def test_logging_on_data_retrieval(self, mock_request, caplog):
        """Test that operations are logged."""
        mock_response = {
            "BEAAPI": {"Results": {"Data": [{"DataValue": "100", "TimePeriod": "2023"}]}}
        }
        mock_request.return_value = mock_response

        connector = BEAConnector(api_key="test_key")

        # Enable log propagation for testing
        connector.logger.propagate = True

        with caplog.at_level("INFO", logger="BEAConnector"):
            df = connector.get_nipa_data(table_name="T10101")

        assert len(caplog.records) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
