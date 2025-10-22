# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for NHTSConnector (Week 5).

Tests validate the 7 new methods for NHTS transportation data:
1. load_household_data() - Household demographics and vehicles
2. load_trip_data() - Daily travel patterns
3. get_trips_by_state() - State-level trip filtering
4. get_commute_statistics() - Commute mode, distance, time
5. get_mode_share() - Transportation mode distribution
6. get_vehicle_ownership_by_state() - Vehicle ownership patterns
7. get_trip_purpose_distribution() - Trip purpose analysis

Layer 8 (Contract): Type validation and structural correctness.
"""

import pandas as pd
import pytest
from krl_data_connectors.transportation import NHTSConnector


# ============================================================
# TEST DATA
# ============================================================

@pytest.fixture
def household_sample():
    """Sample household data for testing."""
    return pd.DataFrame({
        'HOUSEID': [1001, 1002, 1003, 1004, 1005],
        'HHSTATE': [6, 6, 36, 36, 48],  # CA, CA, NY, NY, TX
        'HHSIZE': [2, 4, 1, 3, 2],
        'HHVEHCNT': [2, 3, 0, 2, 1],
        'HHFAMINC': [6, 8, 4, 7, 5],
        'NUMADLT': [2, 2, 1, 2, 2],
        'WRKCOUNT': [2, 2, 1, 2, 1],
    })


@pytest.fixture
def trip_sample():
    """Sample trip data for testing."""
    return pd.DataFrame({
        'HOUSEID': [1001, 1001, 1002, 1003, 1004, 1004, 1005],
        'PERSONID': [1, 1, 1, 1, 1, 2, 1],
        'TDTRPNUM': [1, 2, 1, 1, 1, 1, 1],
        'TRPTRANS': [1, 1, 1, 18, 1, 1, 1],  # 1=Car, 18=Walk
        'WHYTRP1S': [3, 10, 3, 6, 3, 3, 7],  # 3=Work, 6=Shopping, 7=Social, 10=Home
        'TRPMILES': [15.2, 14.8, 8.5, 0.5, 22.1, 18.3, 5.2],
        'TRVLCMIN': [25, 23, 18, 10, 35, 30, 12],
    })


@pytest.fixture
def mock_connector(monkeypatch, household_sample, trip_sample):
    """Mock NHTSConnector with test data."""
    nhts = NHTSConnector(cache_dir="/tmp/test_cache")
    
    # Mock data loading methods
    def mock_load_household(force_download=False):
        return household_sample.copy()
    
    def mock_load_trip(force_download=False):
        return trip_sample.copy()
    
    monkeypatch.setattr(nhts, "load_household_data", mock_load_household)
    monkeypatch.setattr(nhts, "load_trip_data", mock_load_trip)
    
    return nhts


# ============================================================
# CONTRACT TESTS (Layer 8)
# ============================================================

def test_load_household_data_return_type(mock_connector):
    """Test load_household_data returns DataFrame with correct structure."""
    result = mock_connector.load_household_data()
    
    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"
    
    # Validate required columns exist
    required_cols = ['HOUSEID', 'HHSTATE', 'HHSIZE', 'HHVEHCNT']
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"
    
    # Validate data types
    assert pd.api.types.is_numeric_dtype(result['HOUSEID']), "HOUSEID should be numeric"
    assert pd.api.types.is_numeric_dtype(result['HHSTATE']), "HHSTATE should be numeric"
    assert pd.api.types.is_numeric_dtype(result['HHVEHCNT']), "HHVEHCNT should be numeric"
    
    # Validate data presence
    assert len(result) == 5, "Should have 5 households"
    assert len(result.columns) >= 4, "Should have at least 4 columns"


def test_load_trip_data_return_type(mock_connector):
    """Test load_trip_data returns DataFrame with correct structure."""
    result = mock_connector.load_trip_data()
    
    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"
    
    # Validate required columns exist
    required_cols = ['HOUSEID', 'PERSONID', 'TRPTRANS', 'WHYTRP1S', 'TRPMILES', 'TRVLCMIN']
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"
    
    # Validate data types
    assert pd.api.types.is_numeric_dtype(result['HOUSEID']), "HOUSEID should be numeric"
    assert pd.api.types.is_numeric_dtype(result['TRPTRANS']), "TRPTRANS should be numeric"
    assert pd.api.types.is_numeric_dtype(result['TRPMILES']), "TRPMILES should be numeric"
    assert pd.api.types.is_numeric_dtype(result['TRVLCMIN']), "TRVLCMIN should be numeric"
    
    # Validate data presence
    assert len(result) == 7, "Should have 7 trips"
    assert len(result.columns) >= 6, "Should have at least 6 columns"


def test_get_trips_by_state_return_type(mock_connector):
    """Test get_trips_by_state filters and returns correct structure."""
    result = mock_connector.get_trips_by_state(state_fips="06")  # California
    
    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"
    
    # Validate required columns exist
    required_cols = ['HOUSEID', 'TRPTRANS', 'TRPMILES']
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"
    
    # Validate filtering logic
    assert len(result) > 0, "Should have trips for California"
    assert len(result) <= 7, "Should not have more than total trips"
    
    # Validate filtered to correct state
    # CA households are 1001, 1002, so should have their trips (1001: 2 trips, 1002: 1 trip = 3 total)
    assert len(result) == 3, "Should have 3 California trips"
    
    # Validate data types preserved
    assert pd.api.types.is_numeric_dtype(result['TRPMILES']), "TRPMILES should be numeric"


def test_get_commute_statistics_return_type(mock_connector):
    """Test get_commute_statistics returns aggregated statistics."""
    result = mock_connector.get_commute_statistics(geography="national")
    
    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"
    
    # Validate required columns
    required_cols = ['mode', 'trips', 'avg_miles', 'avg_minutes', 'mode_share']
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"
    
    # Validate data types
    assert pd.api.types.is_numeric_dtype(result['trips']), "trips should be numeric"
    assert pd.api.types.is_numeric_dtype(result['avg_miles']), "avg_miles should be numeric"
    assert pd.api.types.is_numeric_dtype(result['avg_minutes']), "avg_minutes should be numeric"
    assert pd.api.types.is_numeric_dtype(result['mode_share']), "mode_share should be numeric"
    
    # Validate aggregation logic
    assert len(result) > 0, "Should have at least one mode"
    assert result['trips'].sum() > 0, "Should have commute trips"
    
    # Validate mode share sums to 100%
    assert 99.9 <= result['mode_share'].sum() <= 100.1, "Mode shares should sum to ~100%"
    
    # Validate sorting (descending by mode_share)
    mode_shares = result['mode_share'].values
    assert all(mode_shares[i] >= mode_shares[i+1] for i in range(len(mode_shares)-1)), \
        "Should be sorted descending by mode_share"


def test_get_mode_share_return_type(mock_connector):
    """Test get_mode_share returns mode distribution."""
    result = mock_connector.get_mode_share()
    
    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"
    
    # Validate required columns
    required_cols = ['mode', 'trips', 'share_pct']
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"
    
    # Validate data types
    assert pd.api.types.is_numeric_dtype(result['trips']), "trips should be numeric"
    assert pd.api.types.is_numeric_dtype(result['share_pct']), "share_pct should be numeric"
    
    # Validate percentage calculation
    assert 99.9 <= result['share_pct'].sum() <= 100.1, "Shares should sum to ~100%"
    assert result['trips'].sum() == 7, "Should have all 7 trips"
    
    # Validate sorting (descending by share_pct)
    shares = result['share_pct'].values
    assert all(shares[i] >= shares[i+1] for i in range(len(shares)-1)), \
        "Should be sorted descending by share_pct"
    
    # Validate mode distribution (Car=1 appears 6 times, Walk=18 appears 1 time)
    assert len(result) == 2, "Should have 2 modes (car and walk)"
    assert result.iloc[0]['mode'] == 1, "Car should be most common mode"
    assert result.iloc[0]['trips'] == 6, "Should have 6 car trips"


def test_get_vehicle_ownership_by_state_return_type(mock_connector):
    """Test get_vehicle_ownership_by_state returns state-level statistics."""
    result = mock_connector.get_vehicle_ownership_by_state()
    
    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"
    
    # Validate required columns
    required_cols = ['state', 'avg_vehicles', 'zero_veh_pct', 'multi_veh_pct', 'households']
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"
    
    # Validate data types
    assert result['state'].dtype == object, "state should be string"
    assert pd.api.types.is_numeric_dtype(result['avg_vehicles']), "avg_vehicles should be numeric"
    assert pd.api.types.is_numeric_dtype(result['zero_veh_pct']), "zero_veh_pct should be numeric"
    assert pd.api.types.is_numeric_dtype(result['multi_veh_pct']), "multi_veh_pct should be numeric"
    assert pd.api.types.is_integer_dtype(result['households']), "households should be integer"
    
    # Validate aggregation
    assert len(result) == 3, "Should have 3 states (CA, NY, TX)"
    assert result['households'].sum() == 5, "Should have all 5 households"
    
    # Validate state FIPS formatting (2-digit string)
    assert all(len(s) == 2 for s in result['state']), "State FIPS should be 2 digits"
    assert '06' in result['state'].values, "Should have California (06)"
    
    # Validate percentages are reasonable
    assert all(0 <= pct <= 100 for pct in result['zero_veh_pct']), "Percentages should be 0-100"
    assert all(0 <= pct <= 100 for pct in result['multi_veh_pct']), "Percentages should be 0-100"
    
    # Validate sorting (descending by avg_vehicles)
    avg_vehs = result['avg_vehicles'].values
    assert all(avg_vehs[i] >= avg_vehs[i+1] for i in range(len(avg_vehs)-1)), \
        "Should be sorted descending by avg_vehicles"


def test_get_trip_purpose_distribution_return_type(mock_connector):
    """Test get_trip_purpose_distribution returns purpose breakdown."""
    result = mock_connector.get_trip_purpose_distribution()
    
    # Validate return type
    assert isinstance(result, pd.DataFrame), "Should return DataFrame"
    
    # Validate required columns
    required_cols = ['purpose', 'trips', 'share_pct']
    for col in required_cols:
        assert col in result.columns, f"Should have {col} column"
    
    # Validate data types
    assert pd.api.types.is_numeric_dtype(result['trips']), "trips should be numeric"
    assert pd.api.types.is_numeric_dtype(result['share_pct']), "share_pct should be numeric"
    
    # Validate percentage calculation
    assert 99.9 <= result['share_pct'].sum() <= 100.1, "Shares should sum to ~100%"
    assert result['trips'].sum() == 7, "Should have all 7 trips"
    
    # Validate trip purposes present
    # Test data has purposes: 3 (work-4 trips), 6 (shopping-1), 7 (social-1), 10 (home-1)
    assert len(result) == 4, "Should have 4 distinct purposes"
    assert 3 in result['purpose'].values, "Should have work trips (purpose 3)"
    
    # Validate most common purpose is work (4 out of 7 trips)
    assert result.iloc[0]['purpose'] == 3, "Work should be most common purpose"
    assert result.iloc[0]['trips'] == 4, "Should have 4 work trips"
    assert result.iloc[0]['share_pct'] > 50, "Work should be >50% of trips"
    
    # Validate sorting (descending by share_pct)
    shares = result['share_pct'].values
    assert all(shares[i] >= shares[i+1] for i in range(len(shares)-1)), \
        "Should be sorted descending by share_pct"
