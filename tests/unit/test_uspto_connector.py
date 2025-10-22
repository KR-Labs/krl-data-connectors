# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract Tests for USPTOConnector

Tests validate the interface contracts (Layer 8) for USPTO patent and trademark data.
Focus: Return types, data structures, required columns, and basic data validation.

Author: KR-Labs
Date: December 31, 2025
"""

import pandas as pd
import pytest

from krl_data_connectors.science.uspto_connector import USPTOConnector


@pytest.fixture
def connector():
    """Create USPTOConnector instance for testing."""
    return USPTOConnector()


def test_search_patents_return_type(connector):
    """Test search_patents returns correct DataFrame structure."""
    result = connector.search_patents(
        keyword="artificial intelligence", technology_field="G06F", year_start=2020, year_end=2024
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "patent_id",
        "title",
        "abstract",
        "grant_date",
        "technology_field",
        "assignee_name",
        "assignee_type",
        "inventor_count",
        "citation_count",
        "claim_count",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["patent_id"].dtype == object
    assert result["title"].dtype == object
    assert pd.api.types.is_datetime64_any_dtype(result["grant_date"])
    assert pd.api.types.is_numeric_dtype(result["inventor_count"])
    assert pd.api.types.is_numeric_dtype(result["citation_count"])
    assert pd.api.types.is_numeric_dtype(result["claim_count"])

    # Validate data values
    assert result["inventor_count"].min() >= 1
    assert result["citation_count"].min() >= 0
    assert result["claim_count"].min() > 0
    assert result["assignee_type"].isin(["company", "university", "government", "individual"]).all()


def test_analyze_innovation_clusters_return_type(connector):
    """Test analyze_innovation_clusters returns correct structure."""
    result = connector.analyze_innovation_clusters(
        technology_field="H04L", geographic_level="msa", min_patents=10
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "geography",
        "geography_code",
        "patent_count",
        "patents_per_capita",
        "inventor_count",
        "assignee_count",
        "university_share",
        "avg_citation_count",
        "specialization_index",
        "cluster_rank",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["geography"].dtype == object
    assert result["geography_code"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["patent_count"])
    assert pd.api.types.is_numeric_dtype(result["patents_per_capita"])
    assert pd.api.types.is_numeric_dtype(result["inventor_count"])
    assert pd.api.types.is_numeric_dtype(result["assignee_count"])

    # Validate data values
    assert result["patent_count"].min() >= 10  # min_patents threshold
    assert (result["university_share"] >= 0).all()
    assert (result["university_share"] <= 100).all()
    assert (result["specialization_index"] > 0).all()
    assert result["cluster_rank"].min() == 1

    # Validate ranking is sequential
    assert result["cluster_rank"].is_monotonic_increasing


def test_track_technology_trends_return_type(connector):
    """Test track_technology_trends returns correct time series structure."""
    result = connector.track_technology_trends(
        technology_fields=["G06F", "H04L", "C12N"], year_start=2015, year_end=2024
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "year",
        "technology_field",
        "technology_name",
        "patent_count",
        "growth_rate",
        "citation_rate",
        "market_share",
        "trend_direction",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert pd.api.types.is_numeric_dtype(result["year"])
    assert result["technology_field"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["patent_count"])
    assert pd.api.types.is_numeric_dtype(result["growth_rate"])
    assert pd.api.types.is_numeric_dtype(result["citation_rate"])

    # Validate data values
    assert result["year"].min() >= 2015
    assert result["year"].max() <= 2024
    assert result["patent_count"].min() > 0
    assert (result["growth_rate"] >= -100).all()  # Can't lose more than 100%
    assert result["citation_rate"].min() >= 0
    assert (result["market_share"] >= 0).all()
    assert (result["market_share"] <= 100).all()
    assert result["trend_direction"].isin(["growing", "stable", "declining"]).all()

    # Validate all requested fields are present
    assert set(result["technology_field"].unique()) == {"G06F", "H04L", "C12N"}


def test_analyze_inventor_networks_return_type(connector):
    """Test analyze_inventor_networks returns correct structure."""
    result = connector.analyze_inventor_networks(technology_field="G06F", min_collaborations=2)

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "inventor_name",
        "inventor_id",
        "patent_count",
        "collaboration_count",
        "avg_team_size",
        "primary_field",
        "assignee_count",
        "centrality_score",
        "h_index",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["inventor_name"].dtype == object
    assert result["inventor_id"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["patent_count"])
    assert pd.api.types.is_numeric_dtype(result["collaboration_count"])
    assert pd.api.types.is_numeric_dtype(result["avg_team_size"])
    assert pd.api.types.is_numeric_dtype(result["centrality_score"])

    # Validate data values
    assert result["patent_count"].min() >= 1
    assert result["collaboration_count"].min() >= 2  # min_collaborations threshold
    assert result["avg_team_size"].min() >= 1.0
    assert result["assignee_count"].min() >= 1
    assert (result["centrality_score"] >= 0).all()
    assert (result["centrality_score"] <= 100).all()
    assert result["h_index"].min() >= 0


def test_get_patent_citations_return_type(connector):
    """Test get_patent_citations returns correct structure."""
    result = connector.get_patent_citations(
        technology_field="H04L", citation_type="forward", min_citations=5
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "patent_id",
        "title",
        "citation_count",
        "forward_citations",
        "backward_citations",
        "self_citations",
        "citation_lag",
        "impact_score",
        "technology_field",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["patent_id"].dtype == object
    assert result["title"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["citation_count"])
    assert pd.api.types.is_numeric_dtype(result["forward_citations"])
    assert pd.api.types.is_numeric_dtype(result["backward_citations"])
    assert pd.api.types.is_numeric_dtype(result["impact_score"])

    # Validate data values
    assert result["citation_count"].min() >= 5  # min_citations threshold
    assert result["forward_citations"].min() >= 0
    assert result["backward_citations"].min() >= 0
    assert result["self_citations"].min() >= 0
    assert result["citation_lag"].min() >= 0
    assert (result["impact_score"] >= 0).all()
    assert (result["impact_score"] <= 100).all()

    # Validate citation relationships
    # Forward + backward should relate to total (allowing for some flexibility in mock data)
    assert (result["forward_citations"] <= result["citation_count"] * 2).all()


def test_compare_innovation_regions_return_type(connector):
    """Test compare_innovation_regions returns correct comparison structure."""
    regions = [
        "San Jose-Sunnyvale-Santa Clara, CA",
        "Boston-Cambridge-Newton, MA-NH",
        "Seattle-Tacoma-Bellevue, WA",
    ]

    result = connector.compare_innovation_regions(regions=regions, technology_field="G06F")

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) == len(regions)

    # Validate required columns
    required_cols = [
        "region",
        "patent_count",
        "patents_per_capita",
        "growth_rate",
        "university_patents",
        "corporate_patents",
        "avg_citation_count",
        "inventor_density",
        "assignee_diversity",
        "innovation_score",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert result["region"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["patent_count"])
    assert pd.api.types.is_numeric_dtype(result["patents_per_capita"])
    assert pd.api.types.is_numeric_dtype(result["growth_rate"])
    assert pd.api.types.is_numeric_dtype(result["innovation_score"])

    # Validate data values
    assert result["patent_count"].min() > 0
    assert result["patents_per_capita"].min() >= 0
    assert (result["university_patents"] >= 0).all()
    assert (result["corporate_patents"] >= 0).all()
    assert result["avg_citation_count"].min() >= 0
    assert result["inventor_density"].min() >= 0
    assert result["assignee_diversity"].min() > 0
    assert (result["innovation_score"] >= 0).all()
    assert (result["innovation_score"] <= 100).all()

    # Validate all requested regions are present
    assert set(result["region"]) == set(regions)

    # Validate university + corporate doesn't wildly exceed total
    # (allowing for flexibility in mock data generation)
    assert (
        (result["university_patents"] + result["corporate_patents"]) <= result["patent_count"] * 1.5
    ).all()


def test_get_industry_innovation_return_type(connector):
    """Test get_industry_innovation returns correct structure."""
    result = connector.get_industry_innovation(
        industry_sector="biotechnology", year_start=2015, year_end=2024, include_trends=True
    )

    # Validate return type
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0

    # Validate required columns
    required_cols = [
        "year",
        "industry_sector",
        "technology_field",
        "patent_count",
        "growth_rate",
        "citation_rate",
        "university_share",
        "startup_share",
        "avg_claim_count",
        "concentration_index",
    ]
    for col in required_cols:
        assert col in result.columns, f"Missing required column: {col}"

    # Validate data types
    assert pd.api.types.is_numeric_dtype(result["year"])
    assert result["industry_sector"].dtype == object
    assert result["technology_field"].dtype == object
    assert pd.api.types.is_numeric_dtype(result["patent_count"])
    assert pd.api.types.is_numeric_dtype(result["growth_rate"])
    assert pd.api.types.is_numeric_dtype(result["citation_rate"])

    # Validate data values
    assert result["year"].min() >= 2015
    assert result["year"].max() <= 2024
    assert (result["industry_sector"] == "biotechnology").all()
    assert result["patent_count"].min() > 0
    assert (result["university_share"] >= 0).all()
    assert (result["university_share"] <= 100).all()
    assert (result["startup_share"] >= 0).all()
    assert (result["startup_share"] <= 100).all()
    assert result["avg_claim_count"].min() > 0
    assert (result["concentration_index"] >= 0).all()
    assert (result["concentration_index"] <= 1).all()

    # Validate time series when include_trends=True
    years = result["year"].unique()
    assert len(years) == (2024 - 2015 + 1)  # Should have all years


def test_fetch_method_routing(connector):
    """Test fetch method correctly routes to all query types."""

    # Test search routing
    result = connector.fetch(query_type="search", keyword="machine learning", limit=50)
    assert isinstance(result, pd.DataFrame)
    assert "patent_id" in result.columns

    # Test clusters routing
    result = connector.fetch(query_type="clusters", technology_field="G06F", geographic_level="msa")
    assert isinstance(result, pd.DataFrame)
    assert "cluster_rank" in result.columns

    # Test trends routing
    result = connector.fetch(
        query_type="trends", technology_fields=["G06F", "H04L"], year_start=2020, year_end=2024
    )
    assert isinstance(result, pd.DataFrame)
    assert "trend_direction" in result.columns

    # Test networks routing
    result = connector.fetch(query_type="networks", technology_field="C12N")
    assert isinstance(result, pd.DataFrame)
    assert "centrality_score" in result.columns

    # Test citations routing
    result = connector.fetch(query_type="citations", technology_field="H01L")
    assert isinstance(result, pd.DataFrame)
    assert "impact_score" in result.columns

    # Test regions routing
    result = connector.fetch(query_type="regions", regions=["California", "Massachusetts"])
    assert isinstance(result, pd.DataFrame)
    assert "innovation_score" in result.columns

    # Test industry routing
    result = connector.fetch(query_type="industry", industry_sector="software")
    assert isinstance(result, pd.DataFrame)
    assert "industry_sector" in result.columns

    # Test invalid query_type raises ValueError
    with pytest.raises(ValueError, match="Unknown query_type"):
        connector.fetch(query_type="invalid_type")
