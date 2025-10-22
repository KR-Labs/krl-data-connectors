# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for IRS990Connector.

These tests validate the IRS990Connector interface and data structure contracts.
They use mock data to ensure fast, reliable testing without external API dependencies.
"""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from krl_data_connectors.social.irs990_connector import IRS990Connector


@pytest.fixture
def irs990_connector():
    """Create an IRS990Connector instance with mocked API."""
    with patch.object(IRS990Connector, "connect"):
        connector = IRS990Connector()
        return connector


def test_search_nonprofits_return_type(irs990_connector):
    """
    Contract Test: search_nonprofits returns DataFrame with expected columns.

    Validates:
    - Returns pandas DataFrame
    - Contains required organization information columns
    - EIN is unique identifier
    - Financial columns are numeric
    """
    nonprofits = irs990_connector.search_nonprofits(query="museum", state="NY")

    # Should return DataFrame
    assert isinstance(nonprofits, pd.DataFrame)
    assert len(nonprofits) > 0

    # Should have expected columns
    expected_columns = [
        "ein",
        "name",
        "city",
        "state",
        "zip_code",
        "ntee_code",
        "subsection_code",
        "tax_period",
        "total_revenue",
        "total_assets",
        "total_expenses",
        "program_expenses",
        "administrative_expenses",
        "fundraising_expenses",
    ]
    for col in expected_columns:
        assert col in nonprofits.columns, f"Missing column: {col}"

    # EIN should be unique
    assert nonprofits["ein"].is_unique

    # Financial columns should be numeric
    financial_cols = ["total_revenue", "total_assets", "total_expenses"]
    for col in financial_cols:
        assert pd.api.types.is_numeric_dtype(nonprofits[col])
        assert (nonprofits[col] >= 0).all()


def test_get_by_ntee_code_return_type(irs990_connector):
    """
    Contract Test: get_by_ntee_code returns filtered DataFrame.

    Validates:
    - Returns DataFrame with organizations
    - All organizations match requested NTEE codes
    - NTEE code filtering works correctly
    """
    # Test with major category code
    arts_orgs = irs990_connector.get_by_ntee_code(ntee_codes=["A"], state="CA")

    assert isinstance(arts_orgs, pd.DataFrame)
    assert len(arts_orgs) > 0

    # All should be NTEE category A (Arts)
    assert all(arts_orgs["ntee_code"].str.startswith("A"))

    # Test with specific NTEE codes
    specific_orgs = irs990_connector.get_by_ntee_code(ntee_codes=["A50", "A60"])

    assert isinstance(specific_orgs, pd.DataFrame)
    # All should start with A5 or A6
    assert all(
        ntee.startswith("A5") or ntee.startswith("A6") for ntee in specific_orgs["ntee_code"]
    )


def test_get_financial_metrics_return_type(irs990_connector):
    """
    Contract Test: get_financial_metrics calculates financial ratios.

    Validates:
    - Returns DataFrame with financial metrics
    - Contains calculated ratio columns
    - Ratios are within expected ranges
    - Financial health score is 0-100
    """
    # Get sample organizations
    orgs = irs990_connector.search_nonprofits(state="NY")

    # Calculate financial metrics
    metrics = irs990_connector.get_financial_metrics(organizations=orgs)

    assert isinstance(metrics, pd.DataFrame)
    assert len(metrics) > 0

    # Should have calculated metric columns
    expected_metrics = [
        "program_expense_ratio",
        "fundraising_efficiency",
        "administrative_ratio",
        "operating_reserve_months",
        "surplus_deficit",
        "surplus_margin",
        "financial_health_score",
    ]
    for col in expected_metrics:
        assert col in metrics.columns, f"Missing metric: {col}"

    # Ratios should be numeric
    for col in expected_metrics:
        assert pd.api.types.is_numeric_dtype(metrics[col])

    # Financial health score should be 0-100
    assert (metrics["financial_health_score"] >= 0).all()
    assert (metrics["financial_health_score"] <= 100).all()

    # Program expense ratio should be percentage
    assert (metrics["program_expense_ratio"] >= 0).all()
    assert (metrics["program_expense_ratio"] <= 100).all()


def test_analyze_cultural_organizations_return_type(irs990_connector):
    """
    Contract Test: analyze_cultural_organizations returns analysis DataFrame.

    Validates:
    - Returns DataFrame with cultural organizations
    - Includes financial health metrics
    - Subsector classification exists
    - Sorted by financial health score
    """
    analysis = irs990_connector.analyze_cultural_organizations(state="CA")

    assert isinstance(analysis, pd.DataFrame)
    assert len(analysis) > 0

    # Should have subsector classification
    assert "subsector" in analysis.columns
    assert "financial_health_score" in analysis.columns

    # Should be sorted by financial health score (descending)
    scores = analysis["financial_health_score"].values
    assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))

    # Test with specific subsector
    museums = irs990_connector.analyze_cultural_organizations(state="NY", subsector="museums")

    assert isinstance(museums, pd.DataFrame)
    # Should have subsector column
    assert "subsector" in museums.columns


def test_get_arts_nonprofits_return_type(irs990_connector):
    """
    Contract Test: get_arts_nonprofits returns arts organizations.

    Validates:
    - Returns DataFrame with arts organizations
    - All have NTEE code starting with 'A'
    - Revenue filtering works if specified
    """
    arts = irs990_connector.get_arts_nonprofits(state="TX")

    assert isinstance(arts, pd.DataFrame)
    assert len(arts) > 0

    # All should be arts organizations (NTEE A)
    assert all(arts["ntee_code"].str.startswith("A"))

    # Test with revenue filter
    min_revenue = 10_000_000
    large_arts = irs990_connector.get_arts_nonprofits(state="NY", min_revenue=min_revenue)

    assert isinstance(large_arts, pd.DataFrame)
    # All should meet minimum revenue
    assert (large_arts["total_revenue"] >= min_revenue).all()


def test_get_nonprofit_statistics_return_type(irs990_connector):
    """
    Contract Test: get_nonprofit_statistics returns aggregate statistics.

    Validates:
    - Returns DataFrame with statistics
    - Contains aggregation columns
    - Counts and sums are non-negative
    - Sorted by organization count
    """
    stats = irs990_connector.get_nonprofit_statistics(ntee_codes=["A"], group_by="state")

    assert isinstance(stats, pd.DataFrame)
    assert len(stats) > 0

    # Should have expected statistic columns
    expected_stats = [
        "state",
        "organization_count",
        "total_revenue_sum",
        "total_assets_sum",
        "total_expenses_sum",
        "avg_revenue",
        "median_revenue",
        "avg_financial_health_score",
    ]
    for col in expected_stats:
        assert col in stats.columns, f"Missing statistic: {col}"

    # Counts and sums should be non-negative
    assert (stats["organization_count"] > 0).all()
    assert (stats["total_revenue_sum"] >= 0).all()
    assert (stats["total_assets_sum"] >= 0).all()

    # Should be sorted by organization count (descending)
    counts = stats["organization_count"].values
    assert all(counts[i] >= counts[i + 1] for i in range(len(counts) - 1))

    # Test different grouping
    ntee_stats = irs990_connector.get_nonprofit_statistics(group_by="ntee")

    assert isinstance(ntee_stats, pd.DataFrame)
    assert "ntee_code" in ntee_stats.columns


def test_fetch_method_routing(irs990_connector):
    """
    Contract Test: fetch method correctly routes to specialized methods.

    Validates:
    - 'search' query type works
    - 'ntee' query type works
    - 'financial' query type works
    - 'cultural' query type works
    - 'arts' query type works
    - 'statistics' query type works
    - Invalid query type raises ValueError
    """
    # Test search query
    search_result = irs990_connector.fetch(query_type="search", query="museum", state="NY")
    assert isinstance(search_result, pd.DataFrame)
    assert "ein" in search_result.columns

    # Test NTEE query
    ntee_result = irs990_connector.fetch(query_type="ntee", ntee_codes=["A"], state="CA")
    assert isinstance(ntee_result, pd.DataFrame)
    assert all(ntee_result["ntee_code"].str.startswith("A"))

    # Test financial query
    orgs = irs990_connector.search_nonprofits(state="NY")
    financial_result = irs990_connector.fetch(query_type="financial", organizations=orgs)
    assert isinstance(financial_result, pd.DataFrame)
    assert "financial_health_score" in financial_result.columns

    # Test cultural query
    cultural_result = irs990_connector.fetch(query_type="cultural", state="CA")
    assert isinstance(cultural_result, pd.DataFrame)
    assert "subsector" in cultural_result.columns

    # Test arts query
    arts_result = irs990_connector.fetch(query_type="arts", state="TX")
    assert isinstance(arts_result, pd.DataFrame)
    assert all(arts_result["ntee_code"].str.startswith("A"))

    # Test statistics query
    stats_result = irs990_connector.fetch(
        query_type="statistics", ntee_codes=["A"], group_by="state"
    )
    assert isinstance(stats_result, pd.DataFrame)
    assert "organization_count" in stats_result.columns

    # Test invalid query type
    with pytest.raises(ValueError, match="Unknown query_type"):
        irs990_connector.fetch(query_type="invalid")

    # Test NTEE query without ntee_codes parameter
    with pytest.raises(ValueError, match="ntee_codes parameter required"):
        irs990_connector.fetch(query_type="ntee")
