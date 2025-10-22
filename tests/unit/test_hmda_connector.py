# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for HMDAConnector (Layer 8: Interface Contracts)

These tests validate the interface contracts of the HMDAConnector, ensuring that:
- Methods return correct data types (DataFrame)
- Required columns are present in returned DataFrames
- Calculated values (percentages, rates) are within valid ranges
- Aggregations produce expected output structure

These are contract tests, not comprehensive functional tests. They use mock/sample
data to validate interfaces without requiring external API access.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from krl_data_connectors.financial.hmda_connector import HMDAConnector


@pytest.fixture
def mock_connector():
    """Create a mock HMDAConnector with sample data."""
    connector = HMDAConnector()

    # Mock the abstract methods
    connector.connect = MagicMock(return_value=True)
    connector._get_api_key = MagicMock(return_value=None)

    # Mock loan data
    sample_loans = pd.DataFrame(
        {
            "activity_year": [2022] * 10,
            "state_code": ["CA"] * 5 + ["NY"] * 5,
            "county_code": ["06037"] * 5 + ["36061"] * 5,  # LA County, Manhattan
            "census_tract": [
                "0601.02",
                "0601.02",
                "0602.01",
                "0602.01",
                "0603.01",
                "3606.01",
                "3606.02",
                "3607.01",
                "3607.02",
                "3608.01",
            ],
            "lei": [
                "LENDER_A",
                "LENDER_A",
                "LENDER_B",
                "LENDER_B",
                "LENDER_C",
                "LENDER_A",
                "LENDER_B",
                "LENDER_C",
                "LENDER_C",
                "LENDER_A",
            ],
            "loan_type": [1] * 10,  # Conventional
            "loan_purpose": [1] * 10,  # Home purchase
            "loan_amount": [
                350000,
                400000,
                275000,
                425000,
                500000,
                650000,
                700000,
                600000,
                550000,
                675000,
            ],
            "action_taken": [1, 1, 1, 3, 1, 1, 3, 1, 1, 3],  # 1=originated, 3=denied
            "denial_reason_1": [None, None, None, 1, None, None, 2, None, None, 1],
            "applicant_race_1": [5, 5, 3, 3, 2, 5, 3, 5, 2, 3],  # 2=Asian, 3=Black, 5=White
            "applicant_ethnicity_1": [2, 2, 2, 1, 2, 2, 1, 2, 2, 1],  # 1=Hispanic, 2=Not Hispanic
            "applicant_sex": [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],  # 1=Male, 2=Female
            "applicant_income": [
                95000,
                105000,
                75000,
                68000,
                120000,
                135000,
                88000,
                142000,
                128000,
                95000,
            ],
            "derived_msa_md": ["31080"] * 5 + ["35620"] * 5,  # LA MSA, NY MSA
            "derived_loan_to_value_ratio": [
                0.80,
                0.75,
                0.85,
                0.90,
                0.70,
                0.78,
                0.88,
                0.72,
                0.80,
                0.85,
            ],
            "derived_dwelling_category": ["Single Family"] * 10,
            "debt_to_income_ratio": ["25%-<30%"] * 10,
        }
    )

    # Patch load_loan_data to return sample data
    def mock_load(*args, **kwargs):
        return sample_loans.copy()

    connector.load_loan_data = mock_load

    return connector


def test_load_loan_data_return_type(mock_connector):
    """Test that load_loan_data returns a DataFrame with required columns."""
    result = mock_connector.load_loan_data(year=2022, state_code="CA")

    assert isinstance(result, pd.DataFrame), "load_loan_data must return a DataFrame"
    assert len(result) > 0, "DataFrame should not be empty"

    # Check for required columns (subset of HMDA LAR schema)
    required_cols = [
        "activity_year",
        "state_code",
        "county_code",
        "census_tract",
        "loan_amount",
        "action_taken",
        "applicant_race_1",
        "applicant_ethnicity_1",
        "applicant_sex",
        "applicant_income",
    ]

    for col in required_cols:
        assert col in result.columns, f"Required column '{col}' missing"

    # Check data types
    assert pd.api.types.is_integer_dtype(result["activity_year"]), "activity_year should be integer"
    assert pd.api.types.is_object_dtype(result["state_code"]), "state_code should be string"
    assert pd.api.types.is_integer_dtype(result["action_taken"]), "action_taken should be integer"


def test_get_loans_by_state_return_type(mock_connector):
    """Test that get_loans_by_state returns filtered DataFrame."""
    result = mock_connector.get_loans_by_state(year=2022, state_code="CA", action_taken=1)

    assert isinstance(result, pd.DataFrame), "get_loans_by_state must return a DataFrame"
    assert len(result) > 0, "Should have at least some loans"

    # Check structure (mock data returns all states)
    assert "state_code" in result.columns, "Should include state_code column"
    assert "loan_amount" in result.columns, "Should include loan_amount column"
    assert "action_taken" in result.columns, "Should include action_taken column"


def test_get_denial_rates_return_type(mock_connector):
    """Test that get_denial_rates returns properly structured aggregation."""
    result = mock_connector.get_denial_rates(year=2022, state_code="CA", by_race=True)

    assert isinstance(result, pd.DataFrame), "get_denial_rates must return a DataFrame"
    assert len(result) > 0, "Should have at least one racial group"

    # Check for required columns
    required_cols = ["race", "total_applications", "denied", "originated", "denial_rate"]
    for col in required_cols:
        assert col in result.columns, f"Required column '{col}' missing"

    # Validate calculated values
    assert (result["denial_rate"] >= 0).all(), "Denial rate cannot be negative"
    assert (result["denial_rate"] <= 100).all(), "Denial rate cannot exceed 100%"

    # Check arithmetic consistency
    assert (
        result["total_applications"] == result["denied"] + result["originated"]
    ).all(), "Total applications should equal denied + originated"

    # Check data types
    assert pd.api.types.is_numeric_dtype(
        result["total_applications"]
    ), "total_applications should be numeric"
    assert pd.api.types.is_numeric_dtype(result["denial_rate"]), "denial_rate should be numeric"


def test_get_loans_by_demographic_return_type(mock_connector):
    """Test that get_loans_by_demographic filters correctly."""
    result = mock_connector.get_loans_by_demographic(
        year=2022, race=3, state_code="CA"  # Black or African American
    )

    assert isinstance(result, pd.DataFrame), "get_loans_by_demographic must return a DataFrame"

    # Check structure
    assert "applicant_race_1" in result.columns, "Should include applicant_race_1"
    assert "applicant_ethnicity_1" in result.columns, "Should include applicant_ethnicity_1"
    assert "applicant_sex" in result.columns, "Should include applicant_sex"

    # All returned loans should match race filter
    if len(result) > 0:
        assert (result["applicant_race_1"] == 3).all(), "All loans should match race filter"


def test_get_lending_patterns_return_type(mock_connector):
    """Test that get_lending_patterns returns geographic aggregation."""
    result = mock_connector.get_lending_patterns(year=2022, state_code="CA", group_by="county")

    assert isinstance(result, pd.DataFrame), "get_lending_patterns must return a DataFrame"
    assert len(result) > 0, "Should have at least one county"

    # Check for required columns
    required_cols = [
        "county_code",
        "total_applications",
        "total_originations",
        "median_loan_amount",
        "origination_rate",
    ]
    for col in required_cols:
        assert col in result.columns, f"Required column '{col}' missing"

    # Validate calculated values
    assert (result["origination_rate"] >= 0).all(), "Origination rate cannot be negative"
    assert (result["origination_rate"] <= 100).all(), "Origination rate cannot exceed 100%"
    assert (
        result["total_originations"] <= result["total_applications"]
    ).all(), "Originations cannot exceed applications"

    # Check data types
    assert pd.api.types.is_numeric_dtype(
        result["total_applications"]
    ), "total_applications should be numeric"
    assert pd.api.types.is_numeric_dtype(
        result["median_loan_amount"]
    ), "median_loan_amount should be numeric"


def test_analyze_redlining_indicators_return_type(mock_connector):
    """Test that analyze_redlining_indicators returns comparative analysis."""
    result = mock_connector.analyze_redlining_indicators(
        year=2022, state_code="CA", minority_threshold=0.5
    )

    assert isinstance(result, pd.DataFrame), "analyze_redlining_indicators must return a DataFrame"
    assert len(result) > 0, "Should have at least one tract category"

    # Check for required columns
    required_cols = [
        "tract_category",
        "total_applications",
        "origination_rate",
        "denial_rate",
        "median_loan_amount",
    ]
    for col in required_cols:
        assert col in result.columns, f"Required column '{col}' missing"

    # Validate rates
    assert (result["origination_rate"] >= 0).all(), "Origination rate cannot be negative"
    assert (result["origination_rate"] <= 100).all(), "Origination rate cannot exceed 100%"
    assert (result["denial_rate"] >= 0).all(), "Denial rate cannot be negative"
    assert (result["denial_rate"] <= 100).all(), "Denial rate cannot exceed 100%"

    # Check tract categories
    valid_categories = ["Minority-Majority", "Non-Minority"]
    assert (
        result["tract_category"].isin(valid_categories).all()
    ), f"tract_category must be one of {valid_categories}"


def test_get_lender_statistics_return_type(mock_connector):
    """Test that get_lender_statistics returns lender aggregation."""
    result = mock_connector.get_lender_statistics(year=2022, state_code="CA", top_n=5)

    assert isinstance(result, pd.DataFrame), "get_lender_statistics must return a DataFrame"
    assert len(result) > 0, "Should have at least one lender"
    assert len(result) <= 5, "Should respect top_n parameter"

    # Check for required columns
    required_cols = [
        "lei",
        "total_applications",
        "total_originations",
        "origination_rate",
        "median_loan_amount",
    ]
    for col in required_cols:
        assert col in result.columns, f"Required column '{col}' missing"

    # Validate calculated values
    assert (result["origination_rate"] >= 0).all(), "Origination rate cannot be negative"
    assert (result["origination_rate"] <= 100).all(), "Origination rate cannot exceed 100%"
    assert (
        result["total_originations"] <= result["total_applications"]
    ).all(), "Originations cannot exceed applications"

    # Should be sorted by total_applications descending
    apps = result["total_applications"].values
    assert all(
        apps[i] >= apps[i + 1] for i in range(len(apps) - 1)
    ), "Results should be sorted by total_applications descending"
