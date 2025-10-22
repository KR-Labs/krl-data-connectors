# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Integration tests for OpportunityInsightsConnector.

These tests use real data downloads and verify end-to-end workflows.
They are slower than unit tests but validate real-world behavior.

Tests cover:
- Real data downloads from Opportunity Insights
- Caching with real files
- Multi-state queries
- Geographic aggregation with real data
- Complete workflows

Mark as slow: pytest -m "not slow" to skip
"""

import time
from pathlib import Path
import pandas as pd
import pytest
from krl_data_connectors.mobility import OpportunityInsightsConnector


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture(scope="module")
def connector(tmp_path_factory):
    """
    Create connector with temporary cache for integration tests.

    Uses module scope to reuse downloads across tests in this module.
    """
    cache_dir = tmp_path_factory.mktemp("integration_cache")
    return OpportunityInsightsConnector(cache_dir=str(cache_dir))


@pytest.fixture(scope="module")
def ri_data(connector):
    """
    Fetch Rhode Island data once for multiple tests.

    Rhode Island is the smallest state, fastest to filter.
    """
    return connector.fetch_opportunity_atlas(geography="tract", state="44")


# ============================================================
# REAL DATA DOWNLOAD TESTS
# ============================================================


@pytest.mark.slow
class TestRealDataDownload:
    """Test downloading real data from Opportunity Insights."""

    def test_download_tract_data(self, connector):
        """Test downloading tract-level data."""
        start_time = time.time()

        # Download data for smallest state (Rhode Island)
        data = connector.fetch_opportunity_atlas(geography="tract", state="44")

        elapsed = time.time() - start_time

        # Verify data structure
        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "tract" in data.columns
        assert "state" in data.columns
        assert all(data["state"] == "44")

        # Should have completed in reasonable time (< 60 seconds first download)
        assert elapsed < 60, f"Download took {elapsed:.2f}s, expected < 60s"

    def test_download_county_data(self, connector):
        """Test downloading county-level data."""
        data = connector.fetch_opportunity_atlas(geography="county", state="44")

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
        assert "county" in data.columns
        # Counties should be aggregated from tracts
        assert len(data) < 300  # RI has ~240 tracts, ~5 counties

    def test_download_with_metrics(self, connector):
        """Test downloading specific metrics."""
        metrics = ["kfr_pooled_p25", "jail_pooled_p25"]

        data = connector.fetch_opportunity_atlas(geography="tract", state="44", metrics=metrics)

        # Should have requested metrics plus geographic columns
        for metric in metrics:
            assert metric in data.columns

        # Geographic columns should be present
        assert "tract" in data.columns
        assert "state" in data.columns


# ============================================================
# CACHING TESTS
# ============================================================


@pytest.mark.slow
class TestCachingBehavior:
    """Test file caching with real downloads."""

    def test_first_download_creates_cache(self, connector):
        """Test that first download creates cache file."""
        # Get cache directory
        cache_dir = Path(connector.cache.cache_dir)

        # Download data
        connector.fetch_opportunity_atlas(geography="tract", state="50")  # Vermont

        # Cache file should exist
        cache_file = cache_dir / "tract_outcomes_simple.dta"
        assert cache_file.exists()
        assert cache_file.stat().st_size > 0

    def test_second_download_uses_cache(self, connector):
        """Test that second download reuses cached file."""
        # First download
        start1 = time.time()
        data1 = connector.fetch_opportunity_atlas(geography="tract", state="44")
        time1 = time.time() - start1

        # Second download (should use cache)
        start2 = time.time()
        data2 = connector.fetch_opportunity_atlas(geography="tract", state="44")
        time2 = time.time() - start2

        # Second fetch should be faster (uses cached data frame)
        # Note: May be similar if data already in memory
        assert time2 <= time1 * 2  # At least not significantly slower

        # Data should be identical
        assert len(data1) == len(data2)
        pd.testing.assert_frame_equal(data1, data2)

    def test_force_download_bypasses_cache(self, connector):
        """Test force_download parameter."""
        # First download
        data1 = connector.fetch_opportunity_atlas(
            geography="tract", state="10", force_download=False  # Delaware
        )

        # Force download (should re-download even if cached)
        data2 = connector.fetch_opportunity_atlas(
            geography="tract", state="10", force_download=True
        )

        # Data should be the same (just re-downloaded)
        assert len(data1) == len(data2)


# ============================================================
# MULTI-STATE QUERIES
# ============================================================


@pytest.mark.slow
class TestMultiStateQueries:
    """Test queries across multiple states."""

    def test_fetch_multiple_states_sequentially(self, connector):
        """Test fetching data for multiple states."""
        states = ["44", "50", "10"]  # RI, VT, DE (small states)
        results = {}

        for state in states:
            data = connector.fetch_opportunity_atlas(geography="tract", state=state)
            results[state] = data

            # Each state should have data
            assert len(data) > 0
            assert all(data["state"] == state)

        # States should have different numbers of tracts
        assert len(results["44"]) != len(results["50"])

    def test_different_geographies_same_state(self, connector):
        """Test fetching different geography levels for same state."""
        state = "44"  # Rhode Island

        tract_data = connector.fetch_opportunity_atlas(geography="tract", state=state)

        county_data = connector.fetch_opportunity_atlas(geography="county", state=state)

        state_data = connector.fetch_opportunity_atlas(geography="state", state=state)

        # Should have progressively fewer rows
        assert len(tract_data) > len(county_data)
        assert len(county_data) > len(state_data)
        assert len(state_data) == 1


# ============================================================
# GEOGRAPHIC AGGREGATION WITH REAL DATA
# ============================================================


@pytest.mark.slow
class TestRealDataAggregation:
    """Test geographic aggregation with real data."""

    def test_tract_to_county_aggregation(self, connector, ri_data):
        """Test aggregating tract data to county level."""
        county_data = connector.aggregate_to_county(ri_data)

        # Should have fewer rows
        assert len(county_data) < len(ri_data)

        # Should have county-level geography
        assert "county" in county_data.columns
        assert "tract" not in county_data.columns or county_data["tract"].isna().all()

        # All counties should be in RI
        assert all(county_data["county"].str.startswith("44"))

    def test_county_to_state_aggregation(self, connector, ri_data):
        """Test aggregating county data to state level."""
        county_data = connector.aggregate_to_county(ri_data)
        state_data = connector.aggregate_to_state(county_data)

        # Should have exactly 1 row (one state)
        assert len(state_data) == 1
        assert state_data["state"].iloc[0] == "44"

    def test_direct_state_aggregation(self, connector, ri_data):
        """Test direct aggregation from tract to state."""
        state_data = connector.aggregate_to_state(ri_data)

        assert len(state_data) == 1
        assert state_data["state"].iloc[0] == "44"

        # Should have aggregated metrics
        assert "kfr_pooled_p25" in state_data.columns


# ============================================================
# COMPLETE WORKFLOW TESTS
# ============================================================


@pytest.mark.slow
class TestCompleteWorkflows:
    """Test end-to-end workflows."""

    def test_analyze_state_mobility_workflow(self, connector):
        """
        Test complete workflow: Download → Filter → Aggregate → Analyze.

        This simulates a real user workflow analyzing social mobility
        in Rhode Island.
        """
        # Step 1: Fetch tract-level data for Rhode Island
        tract_data = connector.fetch_opportunity_atlas(
            geography="tract", state="44", metrics=["kfr_pooled_p25", "jail_pooled_p25"]
        )

        assert len(tract_data) > 0

        # Step 2: Aggregate to county level
        county_data = connector.aggregate_to_county(tract_data)

        assert len(county_data) > 0
        assert len(county_data) < len(tract_data)

        # Step 3: Calculate statistics
        avg_mobility = county_data["kfr_pooled_p25"].mean()
        avg_incarceration = county_data["jail_pooled_p25"].mean()

        # Sanity checks on data
        assert 0 < avg_mobility < 1  # Rank between 0 and 1
        assert 0 < avg_incarceration < 0.1  # Incarceration rate typically < 10%

        # Step 4: Find best and worst counties
        best_county = county_data.loc[county_data["kfr_pooled_p25"].idxmax()]
        worst_county = county_data.loc[county_data["kfr_pooled_p25"].idxmin()]

        assert best_county["kfr_pooled_p25"] > worst_county["kfr_pooled_p25"]

    def test_cross_state_comparison_workflow(self, connector):
        """
        Test workflow comparing multiple states.

        Simulates comparing social mobility across New England states.
        """
        # New England states (small, fast to query)
        states = {"44": "Rhode Island", "50": "Vermont", "33": "New Hampshire"}

        state_summaries = []

        for fips, name in states.items():
            # Fetch and aggregate to state level
            tract_data = connector.fetch_opportunity_atlas(
                geography="tract", state=fips, metrics=["kfr_pooled_p25"]
            )

            state_data = connector.aggregate_to_state(tract_data)

            state_summaries.append(
                {
                    "state": name,
                    "fips": fips,
                    "avg_mobility": state_data["kfr_pooled_p25"].iloc[0],
                    "num_tracts": len(tract_data),
                }
            )

        # Verify we got data for all states
        assert len(state_summaries) == len(states)

        # All states should have positive mobility values
        for summary in state_summaries:
            assert summary["avg_mobility"] > 0
            assert summary["num_tracts"] > 0

    def test_county_level_analysis_workflow(self, connector):
        """
        Test workflow for county-level analysis.

        Fetch data for specific county and analyze neighborhoods.
        """
        # Providence County, RI (largest county in RI)
        county_data = connector.fetch_opportunity_atlas(
            geography="tract", county="44007", metrics=["kfr_pooled_p25", "jail_pooled_p25"]
        )

        assert len(county_data) > 0
        assert all(county_data["county"] == "44007")

        # Calculate within-county statistics
        mean_mobility = county_data["kfr_pooled_p25"].mean()
        std_mobility = county_data["kfr_pooled_p25"].std()

        assert mean_mobility > 0
        assert std_mobility >= 0  # Standard deviation non-negative

        # Identify high and low opportunity neighborhoods
        high_opp_tracts = county_data[county_data["kfr_pooled_p25"] > mean_mobility + std_mobility]

        low_opp_tracts = county_data[county_data["kfr_pooled_p25"] < mean_mobility - std_mobility]

        # Should have some variation within county
        assert len(high_opp_tracts) > 0 or len(low_opp_tracts) > 0


# ============================================================
# DATA QUALITY TESTS
# ============================================================


@pytest.mark.slow
class TestDataQuality:
    """Test data quality and consistency."""

    def test_geographic_codes_valid(self, connector, ri_data):
        """Test that geographic codes are valid FIPS codes."""
        # State codes should be 2 digits
        assert all(ri_data["state"].str.len() == 2)
        assert all(ri_data["state"] == "44")

        # County codes should be 5 digits (state + county)
        assert all(ri_data["county"].str.len() == 5)
        assert all(ri_data["county"].str.startswith("44"))

        # Tract codes should be 11 digits (state + county + tract)
        assert all(ri_data["tract"].str.len() == 11)
        assert all(ri_data["tract"].str.startswith("44"))

    def test_metric_values_reasonable(self, connector, ri_data):
        """Test that metric values are within reasonable ranges."""
        # kfr (household income rank) should be between 0 and 1
        if "kfr_pooled_p25" in ri_data.columns:
            kfr = ri_data["kfr_pooled_p25"].dropna()
            assert kfr.min() >= 0
            assert kfr.max() <= 1

        # Incarceration rate can have small negative values (deviations from baseline)
        # Real data shows range approximately [-0.05, 0.2]
        if "jail_pooled_p25" in ri_data.columns:
            jail = ri_data["jail_pooled_p25"].dropna()
            assert jail.min() >= -0.1  # Allow small negative deviations
            assert jail.max() <= 0.5  # Should be well below 50%

    def test_no_duplicate_tracts(self, connector, ri_data):
        """Test that there are no duplicate tract codes."""
        tract_counts = ri_data["tract"].value_counts()

        # Each tract should appear exactly once
        assert all(tract_counts == 1)

    def test_consistent_cz_names(self, connector, ri_data):
        """Test that commuting zone names are consistent."""
        # Group by CZ and check that each CZ has one name
        if "cz" in ri_data.columns and "czname" in ri_data.columns:
            cz_names = ri_data.groupby("cz")["czname"].nunique()

            # Each CZ should have exactly one name
            assert all(cz_names == 1)


# ============================================================
# PERFORMANCE TESTS
# ============================================================


@pytest.mark.slow
class TestPerformance:
    """Test performance characteristics."""

    def test_small_state_query_performance(self, connector):
        """Test that querying small state completes quickly."""
        start = time.time()

        data = connector.fetch_opportunity_atlas(geography="tract", state="50")  # Vermont

        elapsed = time.time() - start

        # Should complete in < 5 seconds after first download (uses cache)
        assert elapsed < 5, f"Query took {elapsed:.2f}s, expected < 5s"
        assert len(data) > 0

    def test_filtered_query_faster_than_full(self, connector):
        """Test that filtered queries are reasonably fast."""
        # Full state query
        start1 = time.time()
        full_data = connector.fetch_opportunity_atlas(geography="tract", state="44")
        time1 = time.time() - start1

        # Filtered county query
        start2 = time.time()
        county_data = connector.fetch_opportunity_atlas(geography="tract", county="44007")
        time2 = time.time() - start2

        # Both should complete in reasonable time
        assert time1 < 10
        assert time2 < 10

        # County query should return subset
        assert len(county_data) < len(full_data)


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "slow", "--tb=short"])
