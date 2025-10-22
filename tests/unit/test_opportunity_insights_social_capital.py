# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for OpportunityInsightsConnector Social Capital Enhancement (Week 4).

Tests validate the 7 new social capital analysis methods added in Week 4:
1. get_high_ec_areas() - High economic connectedness areas
2. get_low_ec_areas() - Low economic connectedness areas
3. compare_ec_by_state() - State-level EC comparison
4. get_ec_clustering_correlation() - EC vs clustering correlation
5. get_social_capital_summary() - Area-specific summary
6. rank_areas_by_ec() - EC ranking
7. compare_mobility_and_social_capital() - Mobility + SC integration

Layer 8 (Contract): Type validation and structural correctness.
"""

import pandas as pd
import pytest
from krl_data_connectors.mobility import OpportunityInsightsConnector


# ============================================================
# TEST DATA
# ============================================================


@pytest.fixture
def social_capital_sample():
    """Sample social capital data for testing."""
    return pd.DataFrame(
        {
            "county": ["06037", "06059", "36061", "36047", "48201"],
            "ec_county": [0.892, 0.856, 0.945, 0.912, 0.784],
            "clustering_county": [0.234, 0.256, 0.198, 0.221, 0.287],
            "support_ratio_county": [0.456, 0.478, 0.501, 0.489, 0.423],
        }
    )


@pytest.fixture
def mobility_sample():
    """Sample mobility data for testing."""
    return pd.DataFrame(
        {
            "state": ["06", "06", "36", "36", "48"],
            "county": ["06037", "06059", "36061", "36047", "48201"],
            "kfr_pooled_p25": [0.412, 0.398, 0.456, 0.432, 0.387],
            "kfr_pooled_p50": [0.523, 0.498, 0.567, 0.542, 0.476],
        }
    )


@pytest.fixture
def mock_connector(monkeypatch, social_capital_sample, mobility_sample):
    """Mock OpportunityInsightsConnector with test data."""
    oi = OpportunityInsightsConnector(cache_dir="/tmp/test_cache")

    # Mock fetch_social_capital to return sample data
    def mock_fetch_sc(geography="county", metrics=None, force_download=False):
        return social_capital_sample.copy()

    # Mock fetch_opportunity_atlas to return sample data
    def mock_fetch_atlas(
        geography="county", metrics=None, state=None, county=None, force_download=False
    ):
        return mobility_sample.copy()

    monkeypatch.setattr(oi, "fetch_social_capital", mock_fetch_sc)
    monkeypatch.setattr(oi, "fetch_opportunity_atlas", mock_fetch_atlas)

    return oi


# ============================================================
# CONTRACT TESTS (Layer 8)
# ============================================================


def test_get_high_ec_areas_return_type(mock_connector):
    """Test get_high_ec_areas returns DataFrame with correct structure."""
    result = mock_connector.get_high_ec_areas(geography="county", threshold_percentile=80.0)

    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"

    # Validate columns exist
    assert "county" in result.columns, "Should have county column"
    assert "ec_county" in result.columns, "Should have ec_county column"

    # Validate data types
    assert result["county"].dtype == object, "County should be string"
    assert pd.api.types.is_numeric_dtype(result["ec_county"]), "EC should be numeric"

    # Validate filtering logic
    assert len(result) <= 5, "Should filter to high-EC areas only"
    assert len(result) > 0, "Should have at least one high-EC area"

    # Validate sorting (descending by EC)
    ec_values = result["ec_county"].values
    assert all(
        ec_values[i] >= ec_values[i + 1] for i in range(len(ec_values) - 1)
    ), "Should be sorted descending by EC"


def test_get_low_ec_areas_return_type(mock_connector):
    """Test get_low_ec_areas returns DataFrame with correct structure."""
    result = mock_connector.get_low_ec_areas(geography="county", threshold_percentile=20.0)

    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"

    # Validate columns exist
    assert "county" in result.columns, "Should have county column"
    assert "ec_county" in result.columns, "Should have ec_county column"

    # Validate data types
    assert result["county"].dtype == object, "County should be string"
    assert pd.api.types.is_numeric_dtype(result["ec_county"]), "EC should be numeric"

    # Validate filtering logic
    assert len(result) <= 5, "Should filter to low-EC areas only"
    assert len(result) > 0, "Should have at least one low-EC area"

    # Validate sorting (ascending by EC)
    ec_values = result["ec_county"].values
    assert all(
        ec_values[i] <= ec_values[i + 1] for i in range(len(ec_values) - 1)
    ), "Should be sorted ascending by EC"


def test_compare_ec_by_state_return_type(mock_connector):
    """Test compare_ec_by_state returns DataFrame with aggregated statistics."""
    result = mock_connector.compare_ec_by_state(states=["06", "36", "48"])

    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"

    # Validate required columns
    required_cols = ["state", "ec_mean", "ec_median", "ec_min", "ec_max", "ec_std", "county_count"]
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"

    # Validate data types
    assert result["state"].dtype == object, "State should be string"
    assert pd.api.types.is_numeric_dtype(result["ec_mean"]), "ec_mean should be numeric"
    assert pd.api.types.is_numeric_dtype(result["ec_median"]), "ec_median should be numeric"
    assert pd.api.types.is_numeric_dtype(result["county_count"]), "county_count should be numeric"

    # Validate aggregation logic
    assert len(result) == 3, "Should have 3 states"
    assert result["county_count"].sum() == 5, "Should aggregate all 5 counties"

    # Validate sorting (descending by mean EC)
    ec_means = result["ec_mean"].values
    assert all(
        ec_means[i] >= ec_means[i + 1] for i in range(len(ec_means) - 1)
    ), "Should be sorted descending by ec_mean"


def test_get_ec_clustering_correlation_return_type(mock_connector):
    """Test get_ec_clustering_correlation returns dict with correlation stats."""
    result = mock_connector.get_ec_clustering_correlation(geography="county")

    # Validate return type
    assert isinstance(result, dict), "Should return dict"

    # Validate required keys
    required_keys = ["pearson_r", "sample_size", "geography"]
    for key in required_keys:
        assert key in result, f"Should have {key} key"

    # Validate data types
    assert isinstance(result["pearson_r"], float), "pearson_r should be float"
    assert isinstance(result["sample_size"], int), "sample_size should be int"
    assert isinstance(result["geography"], str), "geography should be string"

    # Validate correlation bounds
    assert -1.0 <= result["pearson_r"] <= 1.0, "Pearson r should be in [-1, 1]"

    # Validate sample size
    assert result["sample_size"] == 5, "Should use all 5 counties"


def test_get_social_capital_summary_return_type(mock_connector):
    """Test get_social_capital_summary returns dict with area metrics."""
    result = mock_connector.get_social_capital_summary(
        geography="county", geo_id="06037"  # Los Angeles County
    )

    # Validate return type
    assert isinstance(result, dict), "Should return dict"

    # Validate required metrics
    assert "county" in result, "Should have county identifier"
    assert "ec_county" in result, "Should have ec_county metric"
    assert "clustering_county" in result, "Should have clustering_county metric"

    # Validate data types
    assert isinstance(result["county"], str), "County should be string"
    assert isinstance(result["ec_county"], float), "ec_county should be float"
    assert isinstance(result["clustering_county"], float), "clustering_county should be float"

    # Validate correct county
    assert result["county"] == "06037", "Should return LA County data"

    # Validate reasonable metric values
    assert 0.0 <= result["ec_county"] <= 1.0, "EC should be in [0, 1]"
    assert result["ec_county"] == 0.892, "LA County EC should match sample data"


def test_rank_areas_by_ec_return_type(mock_connector):
    """Test rank_areas_by_ec returns ranked DataFrame with rank column."""
    result = mock_connector.rank_areas_by_ec(geography="county", top_n=3, ascending=False)

    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"

    # Validate columns
    assert "county" in result.columns, "Should have county column"
    assert "ec_county" in result.columns, "Should have ec_county column"
    assert "ec_rank" in result.columns, "Should have ec_rank column"

    # Validate data types
    assert result["county"].dtype == object, "County should be string"
    assert pd.api.types.is_numeric_dtype(result["ec_county"]), "EC should be numeric"
    assert pd.api.types.is_integer_dtype(result["ec_rank"]), "Rank should be integer"

    # Validate top_n limiting
    assert len(result) == 3, "Should return top 3 areas"

    # Validate ranking logic
    assert result.iloc[0]["ec_rank"] == 1, "First row should be rank 1"
    assert result.iloc[1]["ec_rank"] == 2, "Second row should be rank 2"
    assert result.iloc[2]["ec_rank"] == 3, "Third row should be rank 3"

    # Validate sorting (highest EC first)
    ec_values = result["ec_county"].values
    assert all(
        ec_values[i] >= ec_values[i + 1] for i in range(len(ec_values) - 1)
    ), "Should be sorted descending by EC"

    # Validate top county is correct
    assert result.iloc[0]["county"] == "36061", "Highest EC county should be 36061 (0.945)"


def test_compare_mobility_and_social_capital_return_type(mock_connector):
    """Test compare_mobility_and_social_capital returns merged DataFrame."""
    result = mock_connector.compare_mobility_and_social_capital(
        geography="county", states=["06", "36"]
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"

    # Validate merged columns exist
    # Mobility columns
    assert "kfr_pooled_p25" in result.columns, "Should have mobility metric kfr_pooled_p25"
    assert "kfr_pooled_p50" in result.columns, "Should have mobility metric kfr_pooled_p50"

    # Social capital columns
    assert "ec_county" in result.columns, "Should have social capital metric ec_county"
    assert (
        "clustering_county" in result.columns
    ), "Should have social capital metric clustering_county"

    # Geographic columns
    assert "county" in result.columns, "Should have county identifier"
    assert "state" in result.columns, "Should have state identifier"

    # Validate data types
    assert result["county"].dtype == object, "County should be string"
    assert pd.api.types.is_numeric_dtype(result["kfr_pooled_p25"]), "Mobility should be numeric"
    assert pd.api.types.is_numeric_dtype(result["ec_county"]), "EC should be numeric"

    # Validate state filtering
    unique_states = result["state"].unique()
    assert set(unique_states) <= {"06", "36"}, "Should only have CA and NY counties"
    assert len(result) == 4, "Should have 4 counties (2 from CA, 2 from NY)"

    # Validate merge quality (no missing values in key columns)
    assert result["kfr_pooled_p25"].notna().all(), "Mobility data should be complete"
    assert result["ec_county"].notna().all(), "Social capital data should be complete"
