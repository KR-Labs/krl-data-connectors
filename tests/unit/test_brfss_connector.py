# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract Tests for BRFSSConnector

Tests validate the interface contracts (Layer 8) for BRFSS health behavior data.
Focus: Return types, data structures, required columns, and basic data validation.

Author: KR-Labs
Date: December 31, 2025
"""

import pandas as pd
import pytest

from krl_data_connectors.health.brfss_connector import BRFSSConnector


@pytest.fixture
def connector():
    """Create BRFSSConnector instance for testing."""
    return BRFSSConnector()


def test_get_health_indicators_return_type(connector):
    """Test get_health_indicators returns correct DataFrame structure."""
    result = connector.get_health_indicators(
        indicator="diabetes", state="CA", year_start=2020, year_end=2024
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "year",
        "state",
        "state_name",
        "indicator",
        "prevalence",
        "sample_size",
        "confidence_low",
        "confidence_high",
        "stratification",
        "stratification_value",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert pd.api.types.is_numeric_dtype(result["year"])
    assert result["state"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["prevalence"])
    assert pd.api.types.is_numeric_dtype(result["sample_size"])

    # Validate data values
    assert result["year"].min() >= 2020
    assert result["year"].max() <= 2024
    assert (result["prevalence"] >= 0).all()
    assert (result["prevalence"] <= 100).all()
    assert result["sample_size"].min() > 0

    # Validate confidence intervals
    assert (result["confidence_low"] < result["prevalence"]).all()
    assert (result["confidence_high"] > result["prevalence"]).all()

    # Validate state filter
    assert (result["state"] == "CA").all()


def test_analyze_chronic_disease_return_type(connector):
    """Test analyze_chronic_disease returns correct structure."""
    result = connector.analyze_chronic_disease(
        disease_type="diabetes", geographic_level="state", year=2024, include_demographics=True
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "geography",
        "prevalence",
        "diagnosed_count",
        "age_adjusted_prevalence",
        "rank",
        "trend_5yr",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["geography"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["prevalence"])
    assert pd.api.types.is_numeric_dtype(result["diagnosed_count"])
    assert pd.api.types.is_numeric_dtype(result["rank"])

    # Validate data values
    assert (result["prevalence"] >= 0).all()
    assert (result["prevalence"] <= 100).all()
    assert result["diagnosed_count"].min() >= 0
    assert result["rank"].min() == 1
    assert result["rank"].is_monotonic_increasing

    # Validate age adjustment
    assert (result["age_adjusted_prevalence"] <= result["prevalence"] * 1.1).all()

    # Validate demographics when included
    assert "demographic_group" in result.columns
    assert "demographic_prevalence" in result.columns
    assert (result["demographic_prevalence"] >= 0).all()


def test_get_preventive_care_return_type(connector):
    """Test get_preventive_care returns correct structure."""
    result = connector.get_preventive_care(
        service_type="mammogram", state="NY", year_start=2020, year_end=2024
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "year",
        "state",
        "service_type",
        "utilization_rate",
        "guideline_adherent",
        "insurance_covered",
        "uninsured_rate",
        "disparity_gap",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert pd.api.types.is_numeric_dtype(result["year"])
    assert result["service_type"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["utilization_rate"])
    assert pd.api.types.is_numeric_dtype(result["insurance_covered"])

    # Validate data values
    assert (result["utilization_rate"] >= 0).all()
    assert (result["utilization_rate"] <= 100).all()
    assert (result["guideline_adherent"] <= result["utilization_rate"] * 1.1).all()

    # Validate insurance disparity
    assert (result["insurance_covered"] > result["uninsured_rate"]).all()
    assert (result["disparity_gap"] > 0).all()

    # Validate state filter
    assert (result["state"] == "NY").all()


def test_track_risk_behaviors_return_type(connector):
    """Test track_risk_behaviors returns correct time series structure."""
    result = connector.track_risk_behaviors(
        behavior="smoking", year_start=2015, year_end=2024, demographic_breakdown="age"
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "year",
        "behavior",
        "prevalence",
        "prevalence_change",
        "highest_risk_group",
        "disparity_ratio",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert pd.api.types.is_numeric_dtype(result["year"])
    assert result["behavior"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["prevalence"])
    assert pd.api.types.is_numeric_dtype(result["prevalence_change"])

    # Validate data values
    assert result["year"].min() >= 2015
    assert result["year"].max() <= 2024
    assert (result["prevalence"] >= 0).all()
    assert (result["prevalence"] <= 100).all()
    assert result["disparity_ratio"].min() >= 1.0

    # Validate demographic breakdown
    assert "demographic_group" in result.columns
    assert "demographic_prevalence" in result.columns

    # Validate time series
    years = result["year"].unique()
    assert len(years) == (2024 - 2015 + 1)


def test_analyze_health_disparities_return_type(connector):
    """Test analyze_health_disparities returns correct structure."""
    result = connector.analyze_health_disparities(
        indicator="diabetes", disparity_dimension="race", year=2024
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "indicator",
        "dimension",
        "group",
        "prevalence",
        "reference_group",
        "reference_prevalence",
        "disparity_ratio",
        "excess_cases",
        "rank",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["indicator"].dtype == object
    assert result["dimension"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["prevalence"])
    assert pd.api.types.is_numeric_dtype(result["disparity_ratio"])
    assert pd.api.types.is_numeric_dtype(result["excess_cases"])

    # Validate data values
    assert (result["prevalence"] >= 0).all()
    assert (result["prevalence"] <= 100).all()
    assert result["disparity_ratio"].min() >= 0
    assert result["rank"].min() == 1
    assert result["rank"].is_monotonic_increasing

    # Validate reference group consistency
    assert result["reference_group"].nunique() == 1
    assert (result["reference_prevalence"] == result["reference_prevalence"].iloc[0]).all()

    # Validate disparity calculations
    expected_ratios = result["prevalence"] / result["reference_prevalence"]
    assert ((result["disparity_ratio"] - expected_ratios).abs() < 0.1).all()


def test_get_mental_health_indicators_return_type(connector):
    """Test get_mental_health_indicators returns correct structure."""
    result = connector.get_mental_health_indicators(
        state="CA", year_start=2020, year_end=2024, include_demographics=True
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "year",
        "state",
        "depression_prevalence",
        "poor_mental_health_days",
        "frequent_mental_distress",
        "anxiety_prevalence",
        "mental_health_treatment",
        "unmet_need",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert pd.api.types.is_numeric_dtype(result["year"])
    assert result["state"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["depression_prevalence"])
    assert pd.api.types.is_numeric_dtype(result["poor_mental_health_days"])

    # Validate data values
    assert (result["depression_prevalence"] >= 0).all()
    assert (result["depression_prevalence"] <= 100).all()
    assert (result["poor_mental_health_days"] >= 0).all()
    assert (result["poor_mental_health_days"] <= 30).all()
    assert (result["frequent_mental_distress"] >= 0).all()
    assert (result["frequent_mental_distress"] <= 100).all()

    # Validate treatment access
    assert (result["mental_health_treatment"] <= result["depression_prevalence"]).all()
    assert (result["unmet_need"] >= 0).all()

    # Validate demographics when included
    assert "demographic_group" in result.columns
    assert "demographic_prevalence" in result.columns


def test_compare_states_return_type(connector):
    """Test compare_states returns correct comparison structure."""
    states = ["CA", "TX", "NY", "FL"]
    indicators = ["diabetes", "obesity", "smoking"]

    result = connector.compare_states(states=states, indicators=indicators, year=2024)

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "state",
        "state_name",
        "indicator",
        "prevalence",
        "national_average",
        "difference_from_national",
        "rank",
        "percentile",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["state"].dtype == object
    assert result["state_name"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["prevalence"])
    assert pd.api.types.is_numeric_dtype(result["national_average"])
    assert pd.api.types.is_numeric_dtype(result["rank"])

    # Validate data values
    assert (result["prevalence"] >= 0).all()
    assert (result["prevalence"] <= 100).all()
    assert (result["percentile"] >= 0).all()
    assert (result["percentile"] <= 100).all()

    # Validate all requested states and indicators are present
    assert set(result["state"].unique()) == set(states)
    assert set(result["indicator"].unique()) == set(indicators)

    # Validate difference calculation
    calculated_diff = result["prevalence"] - result["national_average"]
    assert ((result["difference_from_national"] - calculated_diff).abs() < 0.1).all()

    # Validate expected number of rows
    assert len(result) == len(states) * len(indicators)


def test_fetch_method_routing(connector):
    """Test fetch method correctly routes to all query types."""

    # Test indicators routing
    result = connector.fetch(query_type="indicators", indicator="obesity", state="TX")
    assert isinstance(result, pd.DataFrame)
    assert "prevalence" in result.columns

    # Test chronic_disease routing
    result = connector.fetch(query_type="chronic_disease", disease_type="diabetes")
    assert isinstance(result, pd.DataFrame)
    assert "diagnosed_count" in result.columns

    # Test preventive_care routing
    result = connector.fetch(query_type="preventive_care", service_type="flu_vaccine")
    assert isinstance(result, pd.DataFrame)
    assert "utilization_rate" in result.columns

    # Test risk_behaviors routing
    result = connector.fetch(
        query_type="risk_behaviors", behavior="smoking", year_start=2020, year_end=2024
    )
    assert isinstance(result, pd.DataFrame)
    assert "prevalence_change" in result.columns

    # Test disparities routing
    result = connector.fetch(
        query_type="disparities", indicator="heart_disease", disparity_dimension="income"
    )
    assert isinstance(result, pd.DataFrame)
    assert "disparity_ratio" in result.columns

    # Test mental_health routing
    result = connector.fetch(query_type="mental_health", state="WA")
    assert isinstance(result, pd.DataFrame)
    assert "depression_prevalence" in result.columns

    # Test compare_states routing
    result = connector.fetch(
        query_type="compare_states", states=["CA", "NY"], indicators=["diabetes"]
    )
    assert isinstance(result, pd.DataFrame)
    assert "national_average" in result.columns

    # Test invalid query_type raises ValueError
    with pytest.raises(ValueError, match="Unknown query_type"):
        connector.fetch(query_type="invalid_type")

    # Test missing query_type raises ValueError
    with pytest.raises(ValueError, match="query_type parameter is required"):
        connector.fetch(indicator="diabetes")
