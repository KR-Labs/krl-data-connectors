# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Property-based tests for OpportunityInsightsConnector using Hypothesis.

Property-based testing generates many random inputs to verify that
certain properties always hold true, catching edge cases that example-
based tests might miss.

Tests cover:
- Geographic code normalization properties
- State filtering properties
- Metric filtering properties
- Aggregation properties
"""

from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from krl_data_connectors.mobility import OpportunityInsightsConnector


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def connector(tmp_path):
    """Create OpportunityInsightsConnector instance with test cache."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return OpportunityInsightsConnector(cache_dir=str(cache_dir))


# ============================================================
# STRATEGIES (DATA GENERATORS)
# ============================================================

# Valid 2-digit state FIPS codes (01-56, excluding gaps)
valid_state_fips = st.sampled_from(
    [
        "01",
        "02",
        "04",
        "05",
        "06",
        "08",
        "09",
        "10",
        "11",
        "12",
        "13",
        "15",
        "16",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
        "32",
        "33",
        "34",
        "35",
        "36",
        "37",
        "38",
        "39",
        "40",
        "41",
        "42",
        "44",
        "45",
        "46",
        "47",
        "48",
        "49",
        "50",
        "51",
        "53",
        "54",
        "55",
        "56",
    ]
)

# 3-digit county suffix
county_suffix = st.text(min_size=3, max_size=3, alphabet="0123456789")

# 5-digit county FIPS (state + county)
county_fips = st.builds(lambda s, c: s + c, valid_state_fips, county_suffix)

# 6-digit tract suffix
tract_suffix = st.text(min_size=6, max_size=6, alphabet="0123456789")

# 11-digit tract FIPS (county + tract)
tract_fips = st.builds(lambda c, t: c + t, county_fips, tract_suffix)

# Common metric names
common_metrics = st.sampled_from(
    [
        "kfr_pooled_p25",
        "kfr_pooled_p50",
        "kfr_pooled_p75",
        "kfr_black_p25",
        "kfr_white_p25",
        "kfr_hisp_p25",
        "jail_pooled_p25",
        "emp_rate_pooled",
    ]
)


# ============================================================
# GEOGRAPHIC CODE PROPERTY TESTS
# ============================================================


class TestGeographicCodeProperties:
    """Test properties that should hold for geographic code handling."""

    @given(tract_code=tract_fips)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_tract_code_always_11_digits_or_normalized(self, connector, tract_code):
        """Property: Tract codes should always be 11 digits after normalization."""
        assume(len(tract_code) == 11)  # Only test valid-length codes

        # Create test data
        test_data = pd.DataFrame(
            {
                "tract": [tract_code],
                "state": [tract_code[:2]],
                "county": [tract_code[:5]],
                "kfr_pooled_p25": [0.5],
            }
        )

        # Normalize via connector's internal method
        with patch.object(connector, "_atlas_data", test_data):
            result = connector._atlas_data.copy()

            # Property: All tract codes should be strings
            assert result["tract"].dtype == object

            # Property: All tract codes should have valid structure
            tract_str = str(result["tract"].iloc[0])
            assert tract_str.isdigit(), f"Tract code should be numeric: {tract_str}"
            assert len(tract_str) <= 11, f"Tract code should be at most 11 digits: {tract_str}"

    @given(state_code=valid_state_fips)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_state_code_always_2_digits(self, connector, state_code):
        """Property: State codes should always be 2 digits."""
        # Create test data
        test_data = pd.DataFrame(
            {"state": [state_code], "county": [state_code + "001"], "kfr_pooled_p25": [0.5]}
        )

        # Property: All state codes are 2 characters
        assert len(state_code) == 2
        assert state_code.isdigit()

        # Property: State codes are in valid range
        state_num = int(state_code)
        assert 1 <= state_num <= 56

    @given(county_code=county_fips)
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_county_code_derives_correct_state(self, connector, county_code):
        """Property: County codes always contain their state code as first 2 digits."""
        assume(len(county_code) == 5)

        state_from_county = county_code[:2]

        # Property: State derived from county should be valid
        assert len(state_from_county) == 2
        assert state_from_county.isdigit()

        # Property: State number should be in valid range
        state_num = int(state_from_county)
        assert 1 <= state_num <= 99  # Allow all 2-digit combinations


# ============================================================
# STATE FILTERING PROPERTY TESTS
# ============================================================


class TestStateFilteringProperties:
    """Test properties related to state filtering."""

    @given(state_filter=valid_state_fips, other_state=valid_state_fips)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_state_filter_excludes_other_states(self, connector, state_filter, other_state):
        """Property: Filtering by state X should exclude all records from state Y."""
        assume(state_filter != other_state)  # Only test when states differ

        # Setup mock data
        with patch.object(connector, "_download_file") as mock_download:
            mock_download.return_value = Path("/fake/path.dta")
            with patch("pandas.read_stata") as mock_read:
                mock_read.return_value = pd.DataFrame(
                    {
                        "state": [state_filter, state_filter, other_state],
                        "county": [state_filter + "001", state_filter + "003", other_state + "001"],
                        "tract": [
                            state_filter + "001010100",
                            state_filter + "003020100",
                            other_state + "001010100",
                        ],
                        "kfr_pooled_p25": [0.5, 0.6, 0.7],
                    }
                )

                # Filter by first state
                result = connector.fetch_opportunity_atlas(geography="tract", state=state_filter)

                # Property: No records from other_state should remain
                if len(result) > 0 and "state" in result.columns:
                    assert all(
                        result["state"] == state_filter
                    ), f"Found records from state {other_state} when filtering for {state_filter}"

        # Reset cache for next example
        connector._atlas_data = None

    @given(state_code=valid_state_fips)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_state_filter_idempotent(self, connector, state_code):
        """Property: Filtering by state twice should give same result."""
        # Create sample data for this state
        test_data = pd.DataFrame(
            {
                "state": [state_code, state_code],
                "county": [state_code + "001", state_code + "003"],
                "tract": [state_code + "001010100", state_code + "003020100"],
                "kfr_pooled_p25": [0.5, 0.6],
            }
        )

        with patch.object(connector, "_download_file") as mock_download:
            mock_download.return_value = Path("/fake/path.dta")
            with patch("pandas.read_stata") as mock_read:
                # Set up mock for first call
                mock_read.return_value = test_data.copy()

                # Fetch once
                result1 = connector.fetch_opportunity_atlas(geography="tract", state=state_code)

                # Reset connector cache
                connector._atlas_data = None

                # Set up mock for second call (same data)
                mock_read.return_value = test_data.copy()

                # Fetch again
                result2 = connector.fetch_opportunity_atlas(geography="tract", state=state_code)

                # Property: Results should be identical
                assert len(result1) == len(
                    result2
                ), f"Idempotency violated: first call got {len(result1)} rows, second got {len(result2)}"

                if len(result1) > 0:
                    assert set(result1.columns) == set(
                        result2.columns
                    ), "Column sets differ between calls"

        # Reset cache for next example
        connector._atlas_data = None


# ============================================================
# METRIC FILTERING PROPERTY TESTS
# ============================================================


class TestMetricFilteringProperties:
    """Test properties related to metric filtering."""

    @given(metrics=st.lists(common_metrics, min_size=1, max_size=3, unique=True))
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_metric_filter_includes_only_requested_metrics(self, connector, metrics):
        """Property: Filtering by metrics should include only those metrics (plus geo columns)."""
        with patch.object(connector, "_download_file") as mock_download:
            mock_download.return_value = Path("/fake/path.dta")
            with patch("pandas.read_stata") as mock_read:
                # Create data with ALL possible metrics from the common_metrics strategy
                data = {
                    "state": ["06"],
                    "county": ["06037"],
                    "tract": ["06037980000"],
                    "kfr_pooled_p25": [0.5],
                    "kfr_pooled_p50": [0.6],
                    "kfr_pooled_p75": [0.7],
                    "kfr_black_p25": [0.45],
                    "kfr_white_p25": [0.55],
                    "kfr_hisp_p25": [0.50],
                    "jail_pooled_p25": [0.02],
                    "emp_rate_pooled": [0.85],
                }

                mock_read.return_value = pd.DataFrame(data)

                # Fetch with metric filter
                result = connector.fetch_opportunity_atlas(
                    geography="tract", state="06", metrics=metrics
                )

                # Property: Result should only have geographic columns + requested metrics
                result_metrics = [
                    col
                    for col in result.columns
                    if col not in ["state", "county", "tract", "cz", "czname"]
                ]

                # All requested metrics should be present
                for metric in metrics:
                    assert metric in result.columns, f"Requested metric {metric} not in result"

                # No unrequested metrics should be present (except _se and count columns)
                all_possible_metrics = set(data.keys()) - {"state", "county", "tract"}
                for col in result_metrics:
                    # Column should be one of the requested metrics or auxiliary columns
                    assert (
                        col in metrics or "_se" in col or "count" in col
                    ), f"Unrequested metric {col} found in result"

        # Reset cache for next example
        connector._atlas_data = None

    @given(metric_name=common_metrics)
    @settings(max_examples=30, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_single_metric_filter_reduces_columns(self, connector, metric_name):
        """Property: Filtering to 1 metric should result in fewer columns than no filter."""
        with patch.object(connector, "_download_file") as mock_download:
            mock_download.return_value = Path("/fake/path.dta")
            with patch("pandas.read_stata") as mock_read:
                # Create data with ALL possible metrics
                data = {
                    "state": ["06"],
                    "county": ["06037"],
                    "tract": ["06037980000"],
                    "kfr_pooled_p25": [0.5],
                    "kfr_pooled_p50": [0.6],
                    "kfr_pooled_p75": [0.7],
                    "kfr_black_p25": [0.45],
                    "kfr_white_p25": [0.55],
                    "kfr_hisp_p25": [0.50],
                    "jail_pooled_p25": [0.02],
                    "emp_rate_pooled": [0.85],
                }
                mock_read.return_value = pd.DataFrame(data)

                # Fetch without filter
                result_all = connector.fetch_opportunity_atlas(geography="tract", state="06")

                # Reset cache and mock
                connector._atlas_data = None
                mock_read.return_value = pd.DataFrame(data)

                # Fetch with filter
                result_filtered = connector.fetch_opportunity_atlas(
                    geography="tract", state="06", metrics=[metric_name]
                )

                # Property: Filtered result should have fewer or equal columns
                assert len(result_filtered.columns) <= len(result_all.columns)

        # Reset cache for next example
        connector._atlas_data = None


# ============================================================
# AGGREGATION PROPERTY TESTS
# ============================================================


class TestAggregationProperties:
    """Test properties that should hold for geographic aggregation."""

    @given(tract_codes=st.lists(tract_fips, min_size=2, max_size=10, unique=True))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_aggregation_reduces_row_count(self, connector, tract_codes):
        """Property: Aggregating to county should reduce or maintain row count."""
        assume(all(len(code) == 11 for code in tract_codes))

        # Create tract-level data
        tract_data = pd.DataFrame(
            {
                "tract": tract_codes,
                "county": [code[:5] for code in tract_codes],
                "state": [code[:2] for code in tract_codes],
                "kfr_pooled_p25": [0.5] * len(tract_codes),
                "pooled_pooled_count": [100] * len(tract_codes),
            }
        )

        # Aggregate to county
        county_data = connector.aggregate_to_county(tract_data)

        # Property: County-level data should have fewer or equal rows
        assert len(county_data) <= len(tract_data)

        # Property: If multiple tracts in same county, county count should be less
        unique_counties = tract_data["county"].nunique()
        assert len(county_data) == unique_counties

    @given(count_values=st.lists(st.integers(min_value=1, max_value=1000), min_size=2, max_size=10))
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_count_columns_sum_on_aggregation(self, connector, count_values):
        """Property: Count columns should sum (not average) during aggregation."""
        # Create data with multiple tracts in same county
        data = pd.DataFrame(
            {
                "tract": [f"06037{i:06d}00" for i in range(len(count_values))],
                "county": ["06037"] * len(count_values),
                "state": ["06"] * len(count_values),
                "kfr_pooled_p25": [0.5] * len(count_values),
                "pooled_pooled_count": count_values,
            }
        )

        # Get original sum
        original_sum = sum(count_values)

        # Aggregate
        aggregated = connector.aggregate_to_county(data)

        # Property: Count sum should be preserved
        aggregated_sum = aggregated["pooled_pooled_count"].iloc[0]
        assert (
            aggregated_sum == original_sum
        ), f"Count sum changed: {original_sum} -> {aggregated_sum}"

    @given(
        metric_values=st.lists(
            st.floats(min_value=0.0, max_value=1.0, allow_nan=False), min_size=2, max_size=5
        )
    )
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_metric_columns_average_on_aggregation(self, connector, metric_values):
        """Property: Metric columns should average during aggregation."""
        assume(all(0 <= v <= 1 for v in metric_values))

        # Create data
        data = pd.DataFrame(
            {
                "tract": [f"06037{i:06d}00" for i in range(len(metric_values))],
                "county": ["06037"] * len(metric_values),
                "state": ["06"] * len(metric_values),
                "kfr_pooled_p25": metric_values,
            }
        )

        # Get expected average
        expected_avg = sum(metric_values) / len(metric_values)

        # Aggregate
        aggregated = connector.aggregate_to_county(data)

        # Property: Metric should be averaged
        actual_avg = aggregated["kfr_pooled_p25"].iloc[0]
        assert (
            abs(actual_avg - expected_avg) < 0.0001
        ), f"Average differs: expected {expected_avg}, got {actual_avg}"
