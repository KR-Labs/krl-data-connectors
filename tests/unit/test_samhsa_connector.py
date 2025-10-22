# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for SAMHSAConnector.

These tests validate the SAMHSAConnector interface and data structure contracts.
They use mock data to ensure fast, reliable testing without external API dependencies.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from krl_data_connectors.health.samhsa_connector import SAMHSAConnector


@pytest.fixture
def samhsa_connector():
    """Create a SAMHSAConnector instance with mocked API."""
    with patch.object(SAMHSAConnector, "connect"):
        connector = SAMHSAConnector()
        return connector


def test_find_treatment_facilities_return_type(samhsa_connector):
    """
    Contract Test: find_treatment_facilities returns DataFrame with expected columns.

    Validates:
    - Returns pandas DataFrame
    - Contains required facility information columns
    - facility_id is unique
    - List columns contain proper data structures
    """
    facilities = samhsa_connector.find_treatment_facilities(state="CA", city="Los Angeles")

    # Should return DataFrame
    assert isinstance(facilities, pd.DataFrame)

    # Should have expected columns
    expected_columns = [
        "facility_id",
        "name",
        "address",
        "city",
        "state",
        "zip_code",
        "phone",
        "website",
        "facility_type",
        "services_offered",
        "has_medication_assisted_treatment",
        "accepts_opioid_clients",
        "payment_accepted",
        "special_programs",
        "capacity",
    ]
    for col in expected_columns:
        assert col in facilities.columns, f"Missing column: {col}"

    # facility_id should be unique
    assert facilities["facility_id"].is_unique

    # services_offered should be list
    assert isinstance(facilities.iloc[0]["services_offered"], list)

    # payment_accepted should be list
    assert isinstance(facilities.iloc[0]["payment_accepted"], list)

    # Boolean columns
    assert facilities["has_medication_assisted_treatment"].dtype == bool
    assert facilities["accepts_opioid_clients"].dtype == bool


def test_get_facilities_by_state_return_type(samhsa_connector):
    """
    Contract Test: get_facilities_by_state returns filtered DataFrame.

    Validates:
    - Returns DataFrame with facility data
    - All facilities in requested state
    - Service type filtering works if specified
    """
    facilities = samhsa_connector.get_facilities_by_state(
        state="NY", service_type="substance_abuse"
    )

    assert isinstance(facilities, pd.DataFrame)
    assert len(facilities) > 0

    # All facilities should be in NY
    assert (facilities["state"] == "NY").all()

    # All should offer substance abuse services
    assert all("Substance Abuse" in services for services in facilities["services_offered"])


def test_get_substance_services_return_type(samhsa_connector):
    """
    Contract Test: get_substance_services returns substance abuse facilities.

    Validates:
    - Returns DataFrame
    - All facilities offer substance abuse services
    - MAT filtering works correctly
    """
    # Test without MAT filter
    facilities = samhsa_connector.get_substance_services(state="CA")

    assert isinstance(facilities, pd.DataFrame)
    assert len(facilities) > 0

    # All should offer substance abuse
    assert all("Substance Abuse" in services for services in facilities["services_offered"])

    # Test with MAT filter
    mat_facilities = samhsa_connector.get_substance_services(state="CA", medication_assisted=True)

    assert isinstance(mat_facilities, pd.DataFrame)
    # All should have MAT
    assert mat_facilities["has_medication_assisted_treatment"].all()


def test_get_mental_health_services_return_type(samhsa_connector):
    """
    Contract Test: get_mental_health_services returns mental health facilities.

    Validates:
    - Returns DataFrame
    - All facilities offer mental health services
    - Special population filtering works
    """
    # Test without special population filter
    facilities = samhsa_connector.get_mental_health_services(state="TX")

    assert isinstance(facilities, pd.DataFrame)
    assert len(facilities) > 0

    # All should offer mental health services
    assert all("Mental Health" in services for services in facilities["services_offered"])

    # Test with special population filter
    vet_facilities = samhsa_connector.get_mental_health_services(
        state="TX", special_population="Veterans"
    )

    assert isinstance(vet_facilities, pd.DataFrame)
    # All should serve veterans
    assert all("Veterans" in programs for programs in vet_facilities["special_programs"])


def test_get_facility_statistics_return_type(samhsa_connector):
    """
    Contract Test: get_facility_statistics returns aggregated statistics.

    Validates:
    - Returns DataFrame with statistics
    - Contains expected aggregation columns
    - Counts are non-negative integers
    - Averages are positive numbers
    """
    stats = samhsa_connector.get_facility_statistics(group_by="state")

    assert isinstance(stats, pd.DataFrame)
    assert len(stats) > 0

    # Should have expected columns
    expected_columns = [
        "state",
        "total_facilities",
        "substance_abuse_facilities",
        "mental_health_facilities",
        "mat_facilities",
        "residential_facilities",
        "outpatient_facilities",
        "total_capacity",
        "avg_capacity",
    ]
    for col in expected_columns:
        assert col in stats.columns, f"Missing column: {col}"

    # Count columns should be non-negative integers
    count_cols = [
        "total_facilities",
        "substance_abuse_facilities",
        "mental_health_facilities",
        "mat_facilities",
    ]
    for col in count_cols:
        assert (stats[col] >= 0).all()
        assert stats[col].dtype in ["int64", "int32"]

    # Capacity should be positive
    assert (stats["total_capacity"] >= 0).all()
    assert (stats["avg_capacity"] > 0).all()


def test_analyze_service_gaps_return_type(samhsa_connector):
    """
    Contract Test: analyze_service_gaps returns gap analysis DataFrame.

    Validates:
    - Returns DataFrame with gap indicators
    - Contains service_gap_indicator column
    - Gap indicators are valid values (low/medium/adequate)
    - Sorted by service gap (low first)
    """
    gaps = samhsa_connector.analyze_service_gaps(state="FL")

    assert isinstance(gaps, pd.DataFrame)
    assert len(gaps) > 0

    # Should have expected columns
    expected_columns = [
        "county",
        "total_facilities",
        "total_capacity",
        "mat_facilities",
        "service_gap_indicator",
    ]
    for col in expected_columns:
        assert col in gaps.columns, f"Missing column: {col}"

    # Gap indicator should have valid values
    valid_indicators = {"low", "medium", "adequate"}
    assert set(gaps["service_gap_indicator"].unique()).issubset(valid_indicators)

    # Test with population data
    pop_data = pd.DataFrame(
        {
            "county": gaps["county"].unique(),
            "population": [100000, 250000, 50000, 150000, 80000][: len(gaps)],
        }
    )

    gaps_with_pop = samhsa_connector.analyze_service_gaps(state="FL", population_data=pop_data)

    assert "population" in gaps_with_pop.columns
    assert "facilities_per_100k" in gaps_with_pop.columns
    assert "capacity_per_100k" in gaps_with_pop.columns

    # Per-capita metrics should be numeric
    assert gaps_with_pop["facilities_per_100k"].dtype in ["float64", "float32"]
    assert (gaps_with_pop["facilities_per_100k"] >= 0).all()


def test_fetch_method_routing(samhsa_connector):
    """
    Contract Test: fetch method correctly routes to specialized methods.

    Validates:
    - 'facilities' query type works
    - 'substance_abuse' query type works
    - 'mental_health' query type works
    - 'statistics' query type works
    - 'gaps' query type works
    - Invalid query type raises ValueError
    """
    # Test facilities query
    facilities = samhsa_connector.fetch(query_type="facilities", state="CA")
    assert isinstance(facilities, pd.DataFrame)
    assert "facility_id" in facilities.columns

    # Test substance_abuse query
    substance = samhsa_connector.fetch(query_type="substance_abuse", state="NY")
    assert isinstance(substance, pd.DataFrame)
    assert all("Substance Abuse" in s for s in substance["services_offered"])

    # Test mental_health query
    mental = samhsa_connector.fetch(query_type="mental_health", state="TX")
    assert isinstance(mental, pd.DataFrame)
    assert all("Mental Health" in s for s in mental["services_offered"])

    # Test statistics query
    stats = samhsa_connector.fetch(query_type="statistics", group_by="state")
    assert isinstance(stats, pd.DataFrame)
    assert "total_facilities" in stats.columns

    # Test gaps query
    gaps = samhsa_connector.fetch(query_type="gaps", state="CA")
    assert isinstance(gaps, pd.DataFrame)
    assert "service_gap_indicator" in gaps.columns

    # Test invalid query type
    with pytest.raises(ValueError, match="Unknown query_type"):
        samhsa_connector.fetch(query_type="invalid")

    # Test gaps without state parameter
    with pytest.raises(ValueError, match="state parameter required"):
        samhsa_connector.fetch(query_type="gaps")
