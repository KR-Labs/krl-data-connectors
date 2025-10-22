# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for FECConnector

Tests verify contract compliance for Federal Election Commission data access.
"""

import pandas as pd
import pytest

from krl_data_connectors.political.fec_connector import FECConnector


@pytest.fixture
def connector():
    """Create FECConnector instance for testing."""
    return FECConnector(api_key='DEMO_KEY')


def test_search_candidates_return_type(connector):
    """Test that search_candidates returns DataFrame with correct structure."""
    result = connector.search_candidates(
        office='S',
        state='PA',
        cycle=2024,
        limit=5
    )
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    
    # Required columns
    required_columns = [
        'candidate_id', 'name', 'office', 'office_full',
        'state', 'party', 'party_full',
        'incumbent_challenge', 'incumbent_challenge_full',
        'cycles', 'election_year'
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"
    
    # Verify data types
    assert result['candidate_id'].dtype == object
    assert result['name'].dtype == object
    assert result['office'].dtype == object
    assert result['party'].dtype == object


def test_get_committee_finances_return_type(connector):
    """Test that get_committee_finances returns DataFrame with financial data."""
    result = connector.get_committee_finances(
        committee_type='H',
        cycle=2024,
        limit=5
    )
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    
    # Required columns
    required_columns = [
        'committee_id', 'committee_name', 'committee_type',
        'cycle', 'receipts', 'disbursements',
        'cash_on_hand_end_period', 'debts_owed',
        'individual_contributions', 'pac_contributions'
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"
    
    # Verify numeric columns
    numeric_columns = [
        'receipts', 'disbursements', 'cash_on_hand_end_period',
        'individual_contributions', 'pac_contributions'
    ]
    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), \
            f"{col} should be numeric"


def test_get_contributions_return_type(connector):
    """Test that get_contributions returns DataFrame with contribution records."""
    result = connector.get_contributions(
        committee_id='C00000001',
        min_amount=1000,
        cycle=2024,
        limit=5
    )
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    
    # Required columns
    required_columns = [
        'committee_id', 'committee_name',
        'contributor_name', 'contributor_city', 'contributor_state',
        'contributor_employer', 'contributor_occupation',
        'contribution_receipt_date', 'contribution_amount',
        'cycle'
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"
    
    # Verify amount is numeric
    assert pd.api.types.is_numeric_dtype(result['contribution_amount'])
    
    # Verify date is datetime
    assert pd.api.types.is_datetime64_any_dtype(result['contribution_receipt_date'])
    
    # Verify min_amount filter
    assert (result['contribution_amount'] >= 1000).all()


def test_analyze_fundraising_patterns_return_type(connector):
    """Test that analyze_fundraising_patterns returns analytical DataFrame."""
    result = connector.analyze_fundraising_patterns(
        committee_id='C00000001',
        cycle=2024
    )
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    
    # Required columns
    required_columns = [
        'entity_id', 'entity_name', 'cycle',
        'total_raised', 'total_contributions', 'avg_contribution',
        'small_donor_count', 'small_donor_amount', 'small_donor_percentage',
        'large_donor_count', 'large_donor_amount', 'large_donor_percentage',
        'pac_amount', 'pac_percentage',
        'burn_rate', 'cash_on_hand'
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"
    
    # Verify numeric columns
    numeric_columns = [
        'total_raised', 'total_contributions', 'avg_contribution',
        'small_donor_percentage', 'large_donor_percentage',
        'pac_percentage', 'burn_rate'
    ]
    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), \
            f"{col} should be numeric"
    
    # Verify percentage ranges (0-100)
    percentage_columns = [
        'small_donor_percentage', 'large_donor_percentage',
        'pac_percentage'
    ]
    for col in percentage_columns:
        assert (result[col] >= 0).all(), f"{col} should be >= 0"
        assert (result[col] <= 100).all(), f"{col} should be <= 100"


def test_get_expenditures_return_type(connector):
    """Test that get_expenditures returns DataFrame with expenditure records."""
    result = connector.get_expenditures(
        committee_id='C00000001',
        min_amount=5000,
        cycle=2024,
        limit=5
    )
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    
    # Required columns
    required_columns = [
        'committee_id', 'committee_name',
        'recipient_name', 'recipient_city', 'recipient_state',
        'disbursement_date', 'disbursement_amount',
        'disbursement_description', 'cycle'
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"
    
    # Verify amount is numeric
    assert pd.api.types.is_numeric_dtype(result['disbursement_amount'])
    
    # Verify date is datetime
    assert pd.api.types.is_datetime64_any_dtype(result['disbursement_date'])
    
    # Verify min_amount filter
    assert (result['disbursement_amount'] >= 5000).all()


def test_get_campaign_statistics_return_type(connector):
    """Test that get_campaign_statistics returns aggregated statistics."""
    result = connector.get_campaign_statistics(
        office='H',
        cycle=2024,
        group_by='state'
    )
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0
    
    # Required columns
    required_columns = [
        'group', 'candidate_count',
        'total_raised', 'avg_raised', 'median_raised',
        'total_spent', 'avg_cash_on_hand'
    ]
    for col in required_columns:
        assert col in result.columns, f"Missing column: {col}"
    
    # Verify numeric columns
    numeric_columns = [
        'candidate_count', 'total_raised', 'avg_raised',
        'median_raised', 'total_spent', 'avg_cash_on_hand'
    ]
    for col in numeric_columns:
        assert pd.api.types.is_numeric_dtype(result[col]), \
            f"{col} should be numeric"
    
    # Verify aggregations make sense
    assert (result['candidate_count'] >= 1).all()
    assert (result['total_raised'] >= 0).all()
    assert (result['total_spent'] >= 0).all()


def test_fetch_method_routing(connector):
    """Test that fetch() correctly routes to appropriate methods."""
    # Test candidates
    candidates = connector.fetch(
        query_type='candidates',
        office='H',
        limit=5
    )
    assert isinstance(candidates, pd.DataFrame)
    assert 'candidate_id' in candidates.columns
    
    # Test committees
    committees = connector.fetch(
        query_type='committees',
        cycle=2024,
        limit=5
    )
    assert isinstance(committees, pd.DataFrame)
    assert 'committee_id' in committees.columns
    
    # Test contributions
    contributions = connector.fetch(
        query_type='contributions',
        limit=5
    )
    assert isinstance(contributions, pd.DataFrame)
    assert 'contribution_amount' in contributions.columns
    
    # Test expenditures
    expenditures = connector.fetch(
        query_type='expenditures',
        limit=5
    )
    assert isinstance(expenditures, pd.DataFrame)
    assert 'disbursement_amount' in expenditures.columns
    
    # Test fundraising
    fundraising = connector.fetch(
        query_type='fundraising',
        committee_id='C00000001',
        cycle=2024
    )
    assert isinstance(fundraising, pd.DataFrame)
    assert 'total_raised' in fundraising.columns
    
    # Test statistics
    statistics = connector.fetch(
        query_type='statistics',
        office='H',
        cycle=2024,
        group_by='state'
    )
    assert isinstance(statistics, pd.DataFrame)
    assert 'group' in statistics.columns
    
    # Test invalid query_type
    with pytest.raises(ValueError):
        connector.fetch(query_type='invalid_type')
