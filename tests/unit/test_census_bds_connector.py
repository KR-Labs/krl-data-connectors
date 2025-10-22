# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for CensusBDSConnector

Tests verify contract compliance for Census Business Dynamics Statistics data access.
"""

import pandas as pd
import pytest

from krl_data_connectors.economic.census_bds_connector import CensusBDSConnector


@pytest.fixture
def connector():
    """Create CensusBDSConnector instance for testing."""
    return CensusBDSConnector(api_key="DEMO_KEY")


def test_get_startup_rates_return_type(connector):
    """Test that get_startup_rates returns DataFrame with correct structure."""
    result = connector.get_startup_rates(year=2020, geography="state")

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Required columns
    required_columns = [
        "geography_name",
        "geography_code",
        "year",
        "establishments_total",
        "establishments_births",
        "startup_rate",
        "employment_births",
        "avg_size_births",
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Verify data types
    assert pd.api.types.is_numeric_dtype(result["establishments_total"])
    assert pd.api.types.is_numeric_dtype(result["establishments_births"])
    assert pd.api.types.is_numeric_dtype(result["startup_rate"])

    # Verify startup_rate is percentage
    assert (result["startup_rate"] >= 0).all()
    assert (result["startup_rate"] <= 100).all()


def test_analyze_job_creation_return_type(connector):
    """Test that analyze_job_creation returns DataFrame with job dynamics."""
    result = connector.analyze_job_creation(
        state="06", year_start=2015, year_end=2020, include_destruction=True
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Required columns
    required_columns = [
        "year",
        "geography_name",
        "geography_code",
        "job_creation",
        "job_creation_rate",
        "job_destruction",
        "job_destruction_rate",
        "net_job_creation",
        "net_job_creation_rate",
        "total_employment",
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Verify numeric columns
    numeric_columns = [
        "job_creation",
        "job_creation_rate",
        "job_destruction",
        "job_destruction_rate",
        "net_job_creation",
        "total_employment",
    ]
    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), f"{col} should be numeric"

    # Verify time series (multiple years)
    assert result["year"].nunique() > 1

    # Verify net calculation logic
    assert (result["net_job_creation"] == result["job_creation"] - result["job_destruction"]).all()


def test_get_firm_age_distribution_return_type(connector):
    """Test that get_firm_age_distribution returns DataFrame with age groups."""
    result = connector.get_firm_age_distribution(year=2020, geography="state")

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Required columns
    required_columns = [
        "geography_name",
        "geography_code",
        "year",
        "age_0",
        "age_1_to_5",
        "age_6_to_10",
        "age_11_plus",
        "total_firms",
        "pct_young",
        "avg_age",
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Verify numeric columns
    age_columns = ["age_0", "age_1_to_5", "age_6_to_10", "age_11_plus"]
    for col in age_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), f"{col} should be numeric"

    # Verify totals sum correctly
    calculated_total = (
        result["age_0"] + result["age_1_to_5"] + result["age_6_to_10"] + result["age_11_plus"]
    )
    assert (calculated_total == result["total_firms"]).all()

    # Verify percentage bounds
    assert (result["pct_young"] >= 0).all()
    assert (result["pct_young"] <= 100).all()


def test_get_firm_size_distribution_return_type(connector):
    """Test that get_firm_size_distribution returns DataFrame with size groups."""
    result = connector.get_firm_size_distribution(year=2020, geography="state")

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Required columns
    required_columns = [
        "geography_name",
        "geography_code",
        "year",
        "size_1_to_4",
        "size_5_to_9",
        "size_10_to_19",
        "size_20_to_99",
        "size_100_to_499",
        "size_500_plus",
        "total_firms",
        "pct_small",
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Verify numeric columns
    size_columns = [
        "size_1_to_4",
        "size_5_to_9",
        "size_10_to_19",
        "size_20_to_99",
        "size_100_to_499",
        "size_500_plus",
    ]
    for col in size_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), f"{col} should be numeric"

    # Verify totals sum correctly
    calculated_total = sum(result[col] for col in size_columns)
    assert (calculated_total == result["total_firms"]).all()

    # Verify percentage bounds
    assert (result["pct_small"] >= 0).all()
    assert (result["pct_small"] <= 100).all()


def test_calculate_survival_rates_return_type(connector):
    """Test that calculate_survival_rates returns DataFrame with survival metrics."""
    result = connector.calculate_survival_rates(
        cohort_year=2015, years_tracked=5, geography="national"
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Required columns
    required_columns = [
        "geography_name",
        "geography_code",
        "cohort_year",
        "year_1_survival",
        "year_2_survival",
        "year_3_survival",
        "year_5_survival",
        "initial_cohort_size",
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Verify survival rates are percentages
    survival_columns = ["year_1_survival", "year_2_survival", "year_3_survival", "year_5_survival"]
    for col in survival_columns:
        if col in result.columns:
            # Filter out None values
            non_null = result[col].dropna()
            if len(non_null) > 0:
                assert (non_null >= 0).all(), f"{col} should be >= 0"
                assert (non_null <= 100).all(), f"{col} should be <= 100"

    # Verify survival rates decline over time
    assert (result["year_1_survival"] >= result["year_2_survival"]).all()
    assert (result["year_2_survival"] >= result["year_3_survival"]).all()


def test_compare_economic_dynamism_return_type(connector):
    """Test that compare_economic_dynamism returns DataFrame with comparison metrics."""
    result = connector.compare_economic_dynamism(
        year=2020, geographies=["06", "48", "36"], geography_type="state"
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Required columns
    required_columns = [
        "geography_name",
        "geography_code",
        "startup_rate",
        "job_creation_rate",
        "firm_exit_rate",
        "net_job_creation_rate",
        "pct_young_firms",
        "dynamism_score",
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Verify all requested geographies are present
    assert len(result) == 3
    assert set(result["geography_code"]) == {"06", "48", "36"}

    # Verify numeric columns
    numeric_columns = [
        "startup_rate",
        "job_creation_rate",
        "firm_exit_rate",
        "net_job_creation_rate",
        "pct_young_firms",
        "dynamism_score",
    ]
    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), f"{col} should be numeric"

    # Verify percentage bounds
    percentage_columns = [
        "startup_rate",
        "job_creation_rate",
        "firm_exit_rate",
        "net_job_creation_rate",
        "pct_young_firms",
    ]
    for col in percentage_columns:
        assert (result[col] >= 0).all()

    # Verify dynamism score bounds
    assert (result["dynamism_score"] >= 0).all()
    assert (result["dynamism_score"] <= 100).all()


def test_get_sector_dynamics_return_type(connector):
    """Test that get_sector_dynamics returns DataFrame with sector-specific data."""
    result = connector.get_sector_dynamics(year=2020, sector="51", geography="national")

    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Required columns
    required_columns = [
        "geography_name",
        "sector_code",
        "sector_name",
        "establishments_total",
        "establishments_births",
        "job_creation",
        "startup_rate",
        "avg_size",
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"

    # Verify sector code matches request
    assert (result["sector_code"] == "51").all()

    # Verify numeric columns
    numeric_columns = [
        "establishments_total",
        "establishments_births",
        "job_creation",
        "startup_rate",
        "avg_size",
    ]
    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), f"{col} should be numeric"


def test_fetch_method_routing(connector):
    """Test that fetch() correctly routes to appropriate methods."""
    # Test startup_rates
    startups = connector.fetch(query_type="startup_rates", year=2020, geography="national")
    assert isinstance(startups, pd.DataFrame)
    assert "startup_rate" in startups.columns

    # Test job_creation
    jobs = connector.fetch(query_type="job_creation", year_start=2015, year_end=2020)
    assert isinstance(jobs, pd.DataFrame)
    assert "job_creation" in jobs.columns

    # Test firm_age
    age = connector.fetch(query_type="firm_age", year=2020, geography="national")
    assert isinstance(age, pd.DataFrame)
    assert "age_0" in age.columns

    # Test firm_size
    size = connector.fetch(query_type="firm_size", year=2020, geography="national")
    assert isinstance(size, pd.DataFrame)
    assert "size_1_to_4" in size.columns

    # Test survival
    survival = connector.fetch(query_type="survival", cohort_year=2015, years_tracked=5)
    assert isinstance(survival, pd.DataFrame)
    assert "year_1_survival" in survival.columns

    # Test dynamism
    dynamism = connector.fetch(query_type="dynamism", year=2020, geographies=["06", "48"])
    assert isinstance(dynamism, pd.DataFrame)
    assert "dynamism_score" in dynamism.columns

    # Test sector
    sector = connector.fetch(query_type="sector", year=2020, sector="51")
    assert isinstance(sector, pd.DataFrame)
    assert "sector_code" in sector.columns

    # Test invalid query_type
    with pytest.raises(ValueError):
        connector.fetch(query_type="invalid_type")
