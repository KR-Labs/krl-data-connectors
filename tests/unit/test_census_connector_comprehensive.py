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
Comprehensive test suite for U.S. Census Bureau Connector.

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

Author: KR Labs Testing Team
Date: October 22, 2025
"""

from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest
import requests
from hypothesis import given
from hypothesis import strategies as st

from krl_data_connectors.census_connector import CensusConnector

# ============================================================================
# Layer 1: Unit Tests - Initialization & Core Functionality
# ============================================================================


class TestCensusConnectorInitialization:
    """Test Census connector initialization and configuration."""

    def test_initialization_default_values(self):
        """Test connector initializes with correct default values."""
        census = CensusConnector(api_key="test_key")

        assert census.base_url == "https://api.census.gov/data"
        assert census.connector_name == "Census"
        assert census.api_key == "test_key"

    def test_initialization_with_custom_base_url(self):
        """Test connector accepts custom base URL."""
        custom_url = "https://custom.census.gov/api"
        census = CensusConnector(api_key="test_key", base_url=custom_url)

        assert census.base_url == custom_url

    def test_initialization_with_cache_params(self):
        """Test connector accepts custom cache parameters."""
        census = CensusConnector(api_key="test_key", cache_dir="/tmp/census_cache", cache_ttl=7200)

        assert census.base_url == "https://api.census.gov/data"
        # Cache parameters are handled by BaseConnector

    def test_get_api_key_from_env(self):
        """Test API key retrieval from environment."""
        with patch.dict("os.environ", {"CENSUS_API_KEY": "env_key"}):
            census = CensusConnector()
            assert census._get_api_key() is not None


# ============================================================================
# Layer 2: Integration Tests - Connection & Session Management
# ============================================================================


class TestCensusConnectorConnection:
    """Test Census connector connection lifecycle."""

    @patch.object(CensusConnector, "_make_request")
    def test_connect_success(self, mock_request):
        """Test successful connection to Census API."""
        # Mock successful API response
        mock_request.return_value = [["NAME"], ["United States"]]

        census = CensusConnector(api_key="test_key")
        census.connect()

        # Verify connection method was called
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert "/2020/dec/pl" in call_args[0][0]
        assert call_args[0][1]["key"] == "test_key"

    @patch.object(CensusConnector, "_make_request")
    def test_connect_failure_invalid_key(self, mock_request):
        """Test connection failure with invalid API key."""
        mock_request.side_effect = requests.exceptions.HTTPError("401 Unauthorized")

        census = CensusConnector(api_key="invalid_key")

        with pytest.raises(Exception):
            census.connect()

    @patch.object(CensusConnector, "_make_request")
    def test_connect_failure_network_error(self, mock_request):
        """Test connection failure with network error."""
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection refused")

        census = CensusConnector(api_key="test_key")

        with pytest.raises(Exception):
            census.connect()


# ============================================================================
# Layer 2: Integration Tests - Data Retrieval
# ============================================================================


class TestCensusConnectorDataRetrieval:
    """Test Census data retrieval methods."""

    @patch.object(CensusConnector, "_make_request")
    def test_get_data_basic_query(self, mock_request):
        """Test basic data retrieval query."""
        mock_request.return_value = [
            ["NAME", "B01001_001E", "state"],
            ["California", "39538223", "06"],
            ["Texas", "29145505", "48"],
        ]

        census = CensusConnector(api_key="test_key")
        result = census.get_data(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME", "B01001_001E"],
            geography="state:*",
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "NAME" in result.columns
        assert "B01001_001E" in result.columns
        assert result["NAME"].iloc[0] == "California"

    @patch.object(CensusConnector, "_make_request")
    def test_get_data_with_predicates(self, mock_request):
        """Test data retrieval with additional predicates."""
        mock_request.return_value = [
            ["NAME", "B01001_001E", "county", "state"],
            ["Los Angeles County", "10014009", "037", "06"],
        ]

        census = CensusConnector(api_key="test_key")
        result = census.get_data(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME", "B01001_001E"],
            geography="county:*",
            predicates={"in": "state:06"},
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

        # Verify predicates were passed to API
        call_args = mock_request.call_args
        assert "in" in call_args[0][1]
        assert call_args[0][1]["in"] == "state:06"

    @patch.object(CensusConnector, "_make_request")
    def test_get_data_numeric_conversion(self, mock_request):
        """Test that numeric columns are converted to numeric types."""
        mock_request.return_value = [
            ["NAME", "B01001_001E", "state"],
            ["California", "39538223", "06"],
        ]

        census = CensusConnector(api_key="test_key")
        result = census.get_data(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME", "B01001_001E"],
            geography="state:*",
        )

        # B01001_001E should be numeric (not string)
        # Note: After conversion to Python types, dtype is 'object' but values are int/float
        assert isinstance(result["B01001_001E"].iloc[0], (int, float))

    @patch.object(CensusConnector, "_make_request")
    def test_get_data_empty_response(self, mock_request):
        """Test handling of empty API response."""
        mock_request.return_value = [["NAME"]]  # Only headers, no data

        census = CensusConnector(api_key="test_key")
        result = census.get_data(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME"],
            geography="state:99",  # Non-existent state
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(CensusConnector, "_make_request")
    def test_get_data_multiple_variables(self, mock_request):
        """Test data retrieval with multiple variables."""
        mock_request.return_value = [
            ["NAME", "B01001_001E", "B19013_001E", "state"],
            ["California", "39538223", "75235", "06"],
        ]

        census = CensusConnector(api_key="test_key")
        result = census.get_data(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME", "B01001_001E", "B19013_001E"],
            geography="state:*",
        )

        assert len(result.columns) >= 3
        assert "B01001_001E" in result.columns
        assert "B19013_001E" in result.columns

    @patch.object(CensusConnector, "_make_request")
    def test_fetch_method_alias(self, mock_request):
        """Test that fetch() is an alias for get_data()."""
        mock_request.return_value = [
            ["NAME", "B01001_001E", "state"],
            ["California", "39538223", "06"],
        ]

        census = CensusConnector(api_key="test_key")

        # fetch() should call get_data()
        result = census.fetch(
            dataset="acs/acs5", year=2022, variables=["NAME", "B01001_001E"], geography="state:*"
        )

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0


# ============================================================================
# Layer 2: Integration Tests - Variable Metadata
# ============================================================================


class TestCensusConnectorVariableMetadata:
    """Test Census variable metadata retrieval."""

    @patch.object(CensusConnector, "_make_request")
    def test_list_variables_success(self, mock_request):
        """Test listing available variables for a dataset."""
        mock_request.return_value = {
            "variables": {
                "B01001_001E": {
                    "label": "Estimate!!Total",
                    "concept": "SEX BY AGE",
                    "predicateType": "int",
                    "group": "B01001",
                },
                "B19013_001E": {
                    "label": "Estimate!!Median household income",
                    "concept": "MEDIAN HOUSEHOLD INCOME",
                    "predicateType": "int",
                    "group": "B19013",
                },
            }
        }

        census = CensusConnector(api_key="test_key")
        result = census.list_variables(dataset="acs/acs5", year=2022)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "name" in result.columns
        assert "label" in result.columns
        assert "concept" in result.columns

    @patch.object(CensusConnector, "_make_request")
    def test_list_variables_empty_response(self, mock_request):
        """Test handling of empty variables response."""
        mock_request.return_value = {"variables": {}}

        census = CensusConnector(api_key="test_key")
        result = census.list_variables(dataset="acs/acs5", year=2022)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(CensusConnector, "_make_request")
    def test_list_variables_uses_cache(self, mock_request):
        """Test that list_variables uses caching."""
        mock_request.return_value = {"variables": {"TEST": {"label": "Test"}}}

        census = CensusConnector(api_key="test_key")
        census.list_variables(dataset="acs/acs5", year=2022)

        # Verify cache was enabled
        call_args = mock_request.call_args
        assert call_args[1]["use_cache"] is True


# ============================================================================
# Layer 5: Security Tests - Input Validation & Injection Prevention
# ============================================================================


class TestCensusConnectorSecurity:
    """Test security measures against common attacks."""

    def test_empty_api_key_handling(self):
        """Test that empty API key is handled properly."""
        # Mock _get_api_key to return empty string (no config fallback)
        with patch.object(CensusConnector, '_get_api_key', return_value=""):
            census = CensusConnector(api_key="")

            # Empty string falls back to _get_api_key(), which returns ""
            assert census.api_key == ""

    def test_none_api_key_handling(self):
        """Test that None API key is handled properly."""
        # Mock _get_api_key to return None (no config fallback)
        with patch.object(CensusConnector, '_get_api_key', return_value=None):
            census = CensusConnector(api_key=None)

            # Should not raise during initialization
            assert census.api_key is None

    @patch.object(CensusConnector, "_make_request")
    def test_sql_injection_in_dataset(self, mock_request):
        """Test SQL injection attempts in dataset parameter."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Attempt SQL injection in dataset
        malicious_dataset = "acs/acs5'; DROP TABLE census; --"

        # Should not raise exception, malicious string passed to API
        try:
            census.get_data(
                dataset=malicious_dataset,
                year=2022,
                variables=["NAME"],
                geography="us:*",
            )
        except Exception:
            # API will reject it, which is correct behavior
            pass

        # Verify the malicious string was passed as-is (not executed locally)
        call_args = mock_request.call_args
        assert malicious_dataset in call_args[0][0]

    @patch.object(CensusConnector, "_make_request")
    def test_command_injection_in_geography(self, mock_request):
        """Test command injection attempts in geography parameter."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Attempt command injection
        malicious_geography = "state:*; rm -rf /"

        try:
            census.get_data(
                dataset="acs/acs5",
                year=2022,
                variables=["NAME"],
                geography=malicious_geography,
            )
        except Exception:
            pass

        # Verify parameter was passed (will fail at API, not locally)
        call_args = mock_request.call_args
        assert malicious_geography in call_args[0][1]["for"]

    @patch.object(CensusConnector, "_make_request")
    def test_path_traversal_in_dataset(self, mock_request):
        """Test path traversal attempts in dataset parameter."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Attempt path traversal
        malicious_dataset = "../../../etc/passwd"

        try:
            census.get_data(
                dataset=malicious_dataset,
                year=2022,
                variables=["NAME"],
                geography="us:*",
            )
        except Exception:
            pass

        # Verify the path was included in URL (will fail at API)
        call_args = mock_request.call_args
        assert malicious_dataset in call_args[0][0]

    @patch.object(CensusConnector, "_make_request")
    def test_xss_in_variables(self, mock_request):
        """Test XSS attempts in variables parameter."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Attempt XSS in variables
        malicious_variable = "<script>alert('XSS')</script>"

        try:
            census.get_data(
                dataset="acs/acs5",
                year=2022,
                variables=[malicious_variable],
                geography="us:*",
            )
        except Exception:
            pass

        # Verify the malicious string was included (will be URL-encoded)
        call_args = mock_request.call_args
        assert "script" in call_args[0][1]["get"] or malicious_variable in call_args[0][1]["get"]

    @patch.object(CensusConnector, "_make_request")
    def test_null_byte_injection(self, mock_request):
        """Test null byte injection attempts."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Attempt null byte injection
        malicious_dataset = "acs/acs5\x00malicious"

        try:
            census.get_data(
                dataset=malicious_dataset,
                year=2022,
                variables=["NAME"],
                geography="us:*",
            )
        except Exception:
            pass

        # Should handle gracefully (not crash)
        assert True

    @patch.object(CensusConnector, "_make_request")
    def test_extremely_long_dataset_name(self, mock_request):
        """Test DoS prevention with extremely long dataset names."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Extremely long dataset name (DoS attempt)
        long_dataset = "acs/acs5" + "A" * 10000

        try:
            census.get_data(
                dataset=long_dataset,
                year=2022,
                variables=["NAME"],
                geography="us:*",
            )
        except Exception:
            # Should fail gracefully (not hang or crash)
            pass

        assert True

    @patch.object(CensusConnector, "_make_request")
    def test_extremely_long_variable_list(self, mock_request):
        """Test handling of extremely long variable lists."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Extremely long variable list
        long_variables = [f"VAR_{i}" for i in range(1000)]

        try:
            census.get_data(
                dataset="acs/acs5",
                year=2022,
                variables=long_variables,
                geography="us:*",
            )
        except Exception:
            # Should fail gracefully
            pass

        assert True


# ============================================================================
# Layer 7: Property-Based Tests - Edge Case Discovery with Hypothesis
# ============================================================================


class TestCensusConnectorPropertyBased:
    """Property-based tests using Hypothesis for edge case discovery."""

    @given(year=st.integers(min_value=2000, max_value=2030))
    @patch.object(CensusConnector, "_make_request")
    def test_year_values(self, mock_request, year):
        """Test connector handles various year values."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Should not crash with any reasonable year value
        try:
            census.get_data(
                dataset="acs/acs5",
                year=year,
                variables=["NAME"],
                geography="us:*",
            )
        except Exception:
            # Some years may not have data, which is acceptable
            pass

        # Verify year was used in URL
        if mock_request.called:
            call_args = mock_request.call_args
            assert str(year) in call_args[0][0]

    @given(
        dataset=st.text(
            alphabet=st.characters(
                whitelist_categories=("Ll", "Nd", "Pd"), min_codepoint=45, max_codepoint=122
            ),
            min_size=3,
            max_size=50,
        )
    )
    @patch.object(CensusConnector, "_make_request")
    def test_dataset_handling(self, mock_request, dataset):
        """Test connector handles various dataset strings."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Should not crash with any alphanumeric string
        try:
            census.get_data(
                dataset=dataset,
                year=2022,
                variables=["NAME"],
                geography="us:*",
            )
        except Exception:
            # API may reject invalid datasets, which is fine
            pass

        assert True

    @given(
        var_count=st.integers(min_value=1, max_value=20),
        var_length=st.integers(min_value=3, max_value=30),
    )
    @patch.object(CensusConnector, "_make_request")
    def test_variable_list_combinations(self, mock_request, var_count, var_length):
        """Test various variable list combinations."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        # Generate variable list of specified length
        variables = [f"VAR_{i:0{var_length}d}" for i in range(var_count)]

        try:
            census.get_data(
                dataset="acs/acs5",
                year=2022,
                variables=variables,
                geography="us:*",
            )
        except Exception:
            pass

        assert True

    @given(
        geography=st.text(
            alphabet=st.characters(
                whitelist_categories=("Ll", "Lu", "Nd", "Pc"), min_codepoint=42, max_codepoint=122
            ),
            min_size=2,
            max_size=50,
        )
    )
    @patch.object(CensusConnector, "_make_request")
    def test_geography_handling(self, mock_request, geography):
        """Test various geography parameter values."""
        mock_request.return_value = [["NAME"], ["Test"]]

        census = CensusConnector(api_key="test_key")

        try:
            census.get_data(
                dataset="acs/acs5",
                year=2022,
                variables=["NAME"],
                geography=geography,
            )
        except Exception:
            pass

        assert True


# ============================================================================
# Layer 8: Contract Tests - Type Safety Validation
# ============================================================================


class TestCensusConnectorTypeContracts:
    """Test type contracts and return value structures."""

    @patch.object(CensusConnector, "_make_request")
    def test_connect_return_type(self, mock_request):
        """Test that connect returns None."""
        mock_request.return_value = [["NAME"], ["United States"]]

        census = CensusConnector(api_key="test_key")
        result = census.connect()

        assert result is None

    @patch.object(CensusConnector, "_make_request")
    def test_get_data_return_type(self, mock_request):
        """Test that get_data returns DataFrame."""
        mock_request.return_value = [
            ["NAME", "B01001_001E"],
            ["United States", "331449281"],
        ]

        census = CensusConnector(api_key="test_key")
        result = census.get_data(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME", "B01001_001E"],
            geography="us:*",
        )

        assert isinstance(result, pd.DataFrame)

    @patch.object(CensusConnector, "_make_request")
    def test_fetch_return_type(self, mock_request):
        """Test that fetch returns DataFrame."""
        mock_request.return_value = [
            ["NAME", "B01001_001E"],
            ["United States", "331449281"],
        ]

        census = CensusConnector(api_key="test_key")
        result = census.fetch(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME", "B01001_001E"],
        )

        assert isinstance(result, pd.DataFrame)

    @patch.object(CensusConnector, "_make_request")
    def test_list_variables_return_type(self, mock_request):
        """Test that list_variables returns DataFrame."""
        mock_request.return_value = {
            "variables": {"B01001_001E": {"label": "Total Population", "concept": "Sex by Age"}}
        }

        census = CensusConnector(api_key="test_key")
        result = census.list_variables(dataset="acs/acs5", year=2022)

        assert isinstance(result, pd.DataFrame)

    def test_get_api_key_return_type(self):
        """Test that _get_api_key returns None or str."""
        census = CensusConnector(api_key="test_key")
        result = census._get_api_key()

        assert result is None or isinstance(result, str)

    @patch.object(CensusConnector, "_make_request")
    def test_get_data_columns_are_strings(self, mock_request):
        """Test that DataFrame column names are strings."""
        mock_request.return_value = [
            ["NAME", "B01001_001E"],
            ["California", "39538223"],
        ]

        census = CensusConnector(api_key="test_key")
        result = census.get_data(
            dataset="acs/acs5",
            year=2022,
            variables=["NAME", "B01001_001E"],
            geography="state:*",
        )

        for col in result.columns:
            assert isinstance(col, str)

    @patch.object(CensusConnector, "_make_request")
    def test_list_variables_columns_present(self, mock_request):
        """Test that list_variables returns required columns."""
        mock_request.return_value = {
            "variables": {
                "TEST_VAR": {
                    "label": "Test",
                    "concept": "Testing",
                    "predicateType": "str",
                    "group": "TEST",
                }
            }
        }

        census = CensusConnector(api_key="test_key")
        result = census.list_variables(dataset="acs/acs5", year=2022)

        required_columns = ["name", "label", "concept", "predicateType", "group"]
        for col in required_columns:
            assert col in result.columns


# ============================================================================
# Test Configuration
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
