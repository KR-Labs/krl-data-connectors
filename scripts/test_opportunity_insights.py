#!/usr/bin/env python3
# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0


"""
Manual test script for OpportunityInsightsConnector

Tests:
1. Connection and initialization
2. Data download and caching
3. State/county filtering
4. Metric selection
5. Geographic aggregation
6. Cache behavior

Run from krl-data-connectors root:
    python scripts/test_opportunity_insights.py
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from krl_data_connectors.mobility import OpportunityInsightsConnector


def test_initialization():
    """Test connector initialization."""
    print("\n" + "="*60)
    print("TEST 1: Initialization")
    print("="*60)
    
    try:
        oi = OpportunityInsightsConnector()
        print(f"✅ Connector initialized: {oi}")
        print(f"   Cache directory: {oi.cache.cache_dir}")
        print(f"   API key required: {oi.api_key is not None}")
        return oi
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        raise


def test_connection(oi):
    """Test connection establishment."""
    print("\n" + "="*60)
    print("TEST 2: Connection")
    print("="*60)
    
    try:
        oi.connect()
        print(f"✅ Connected successfully")
        print(f"   Session initialized: {oi.session is not None}")
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


def test_small_dataset(oi):
    """Test with small dataset (Rhode Island - smallest state)."""
    print("\n" + "="*60)
    print("TEST 3: Small Dataset Download (Rhode Island)")
    print("="*60)
    
    try:
        start_time = time.time()
        
        # Rhode Island (FIPS 44) - only ~250 census tracts
        # Note: The "simple" STATA file only contains p25 metrics
        ri_data = oi.fetch_opportunity_atlas(
            geography="tract",
            state="44",  # Rhode Island
            metrics=["kfr_pooled_p25", "jail_pooled_p25"]
        )
        
        elapsed = time.time() - start_time
        
        print(f"✅ Downloaded Rhode Island data")
        print(f"   Rows: {len(ri_data)}")
        print(f"   Columns: {ri_data.columns.tolist()}")
        print(f"   Time: {elapsed:.2f} seconds")
        print(f"\nSample data:")
        print(ri_data.head())
        
        return ri_data
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_caching(oi):
    """Test that caching works correctly."""
    print("\n" + "="*60)
    print("TEST 4: Cache Behavior")
    print("="*60)
    
    try:
        # First fetch (from cache or download)
        print("First fetch...")
        start1 = time.time()
        data1 = oi.fetch_opportunity_atlas(
            geography="tract",
            state="44",
            metrics=["kfr_pooled_p25"]
        )
        time1 = time.time() - start1
        
        # Second fetch (should be from cache)
        print("\nSecond fetch (should be cached)...")
        start2 = time.time()
        data2 = oi.fetch_opportunity_atlas(
            geography="tract",
            state="44",
            metrics=["kfr_pooled_p25"]
        )
        time2 = time.time() - start2
        
        speedup = time1 / time2 if time2 > 0 else float('inf')
        
        print(f"\n✅ Cache test complete")
        print(f"   First fetch: {time1:.2f}s")
        print(f"   Second fetch: {time2:.2f}s")
        print(f"   Speedup: {speedup:.1f}x")
        
        if time2 < time1 * 0.1:  # Should be much faster
            print(f"   ✅ Cache is working effectively!")
        else:
            print(f"   ⚠️  Cache may not be working optimally")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False


def test_state_filtering(oi):
    """Test state-level filtering."""
    print("\n" + "="*60)
    print("TEST 5: State Filtering")
    print("="*60)
    
    try:
        # Test multiple states
        states = {
            "44": "Rhode Island",
            "50": "Vermont",
            "10": "Delaware"
        }
        
        for fips, name in states.items():
            data = oi.fetch_opportunity_atlas(
                geography="tract",
                state=fips,
                metrics=["kfr_pooled_p25"]
            )
            
            print(f"✅ {name} (FIPS {fips}): {len(data)} tracts")
            
            # Verify all rows have correct state FIPS
            if 'state' in data.columns:
                unique_states = data['state'].unique()
                if len(unique_states) == 1 and unique_states[0] == fips.zfill(2):
                    print(f"   ✅ State filter working correctly")
                else:
                    print(f"   ❌ State filter error: Found states {unique_states}")
        
        return True
        
    except Exception as e:
        print(f"❌ State filtering test failed: {e}")
        return False


def test_county_filtering(oi):
    """Test county-level filtering."""
    print("\n" + "="*60)
    print("TEST 6: County Filtering")
    print("="*60)
    
    try:
        # Test specific county (Providence County, RI = 44007)
        county_data = oi.fetch_opportunity_atlas(
            geography="tract",
            county="44007",
            metrics=["kfr_pooled_p25", "jail_pooled_p25"]
        )
        
        print(f"✅ Providence County, RI: {len(county_data)} tracts")
        print(f"   Columns: {county_data.columns.tolist()}")
        
        # Verify all rows have correct county FIPS
        if 'county' in county_data.columns:
            unique_counties = county_data['county'].unique()
            if len(unique_counties) == 1 and unique_counties[0] == "44007":
                print(f"   ✅ County filter working correctly")
            else:
                print(f"   ❌ County filter error: Found counties {unique_counties}")
        
        print(f"\nSample data:")
        print(county_data.head())
        
        return county_data
        
    except Exception as e:
        print(f"❌ County filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_metric_selection(oi):
    """Test metric selection."""
    print("\n" + "="*60)
    print("TEST 7: Metric Selection")
    print("="*60)
    
    try:
        # Get available metrics
        metrics = oi.get_available_metrics("atlas")
        print(f"Available metrics: {len(metrics)}")
        print(f"   {metrics[:5]}...")
        
        # Test selecting specific metrics
        selected_metrics = ["kfr_pooled_p25", "jail_pooled_p25"]
        data = oi.fetch_opportunity_atlas(
            geography="tract",
            state="44",
            metrics=selected_metrics
        )
        
        print(f"\n✅ Selected {len(selected_metrics)} metrics")
        print(f"   Requested: {selected_metrics}")
        print(f"   Columns in data: {data.columns.tolist()}")
        
        # Verify columns
        for metric in selected_metrics:
            if metric in data.columns:
                print(f"   ✅ {metric} present")
            else:
                print(f"   ❌ {metric} missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Metric selection test failed: {e}")
        return False


def test_aggregation(oi):
    """Test geographic aggregation."""
    print("\n" + "="*60)
    print("TEST 8: Geographic Aggregation")
    print("="*60)
    
    try:
        # Get tract-level data for Rhode Island
        tract_data = oi.fetch_opportunity_atlas(
            geography="tract",
            state="44",
            metrics=["kfr_pooled_p25", "jail_pooled_p25"]
        )
        
        print(f"Tract-level data: {len(tract_data)} rows")
        
        # Aggregate to county
        county_data = oi.aggregate_to_county(tract_data)
        print(f"✅ County aggregation: {len(county_data)} rows")
        
        # Aggregate to state
        state_data = oi.aggregate_to_state(tract_data)
        print(f"✅ State aggregation: {len(state_data)} rows")
        
        # Verify aggregation reduced row count
        if len(county_data) < len(tract_data) and len(state_data) < len(county_data):
            print(f"   ✅ Aggregation working correctly")
            print(f"   Tract → County: {len(tract_data)} → {len(county_data)}")
            print(f"   County → State: {len(county_data)} → {len(state_data)}")
        else:
            print(f"   ⚠️  Aggregation may have issues")
        
        print(f"\nCounty-level sample:")
        print(county_data.head())
        
        return True
        
    except Exception as e:
        print(f"❌ Aggregation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_geography_levels(oi):
    """Test different geography levels."""
    print("\n" + "="*60)
    print("TEST 9: Geography Levels")
    print("="*60)
    
    try:
        geographies = ["tract", "county", "state"]
        
        for geo in geographies:
            data = oi.fetch_opportunity_atlas(
                geography=geo,
                state="44",
                metrics=["kfr_pooled_p25"]
            )
            print(f"✅ Geography '{geo}': {len(data)} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ Geography levels test failed: {e}")
        return False


def run_all_tests():
    """Run all manual tests."""
    print("\n" + "🔬"*30)
    print("OPPORTUNITY INSIGHTS CONNECTOR - MANUAL TEST SUITE")
    print("🔬"*30)
    
    try:
        # Initialize
        oi = test_initialization()
        
        # Connect
        if not test_connection(oi):
            print("\n❌ Connection failed, aborting tests")
            return False
        
        # Run tests
        test_small_dataset(oi)
        test_caching(oi)
        test_state_filtering(oi)
        test_county_filtering(oi)
        test_metric_selection(oi)
        test_aggregation(oi)
        test_geography_levels(oi)
        
        print("\n" + "="*60)
        print("✅ ALL MANUAL TESTS COMPLETED")
        print("="*60)
        print(f"\nCache location: {oi.cache.cache_dir}")
        print(f"Check the cache directory to verify file storage.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
