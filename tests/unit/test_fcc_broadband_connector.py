# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for FCCBroadbandConnector.

Layer 8: Contract Testing - Type validation and basic interface contracts.

These tests ensure the connector meets the interface contract defined by BaseConnector
and returns data in expected formats. They DO NOT validate data accuracy or business logic.
"""

from pathlib import Path
from typing import Dict

import pandas as pd
import pytest

from krl_data_connectors.technology.fcc_broadband_connector import FCCBroadbandConnector


class TestFCCBroadbandConnectorContracts:
    """Contract tests verifying FCCBroadbandConnector interface compliance."""

    @pytest.fixture
    def connector(self):
        """Create connector instance for testing."""
        return FCCBroadbandConnector()

    def test_connect_return_type(self, connector):
        """
        Verify connect() returns None and doesn't raise unexpected errors.

        Contract: connect() should complete successfully and return None.
        Layer 8: Contract testing - interface validation.
        """
        result = connector.connect()
        assert result is None, "connect() should return None"

    def test_load_coverage_data_return_type(self, connector, tmp_path):
        """
        Verify load_coverage_data() returns DataFrame with correct structure.

        Contract: load_coverage_data() should return pandas DataFrame with
        expected columns when given valid CSV file.

        Layer 8: Contract testing - return type validation.
        """
        # Create minimal test CSV
        test_csv = tmp_path / "test_coverage.csv"
        test_csv.write_text(
            "state_abbr,county_geoid,block_geoid,provider_id,technology,max_down,max_up,low_latency\n"
            "CA,06001,060011001001000,1,50,1000,1000,1\n"
            "CA,06001,060011001001001,2,40,500,50,1\n"
        )

        connector.connect()
        result = connector.load_coverage_data(test_csv)

        # Verify return type
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"

        # Verify expected columns exist
        expected_columns = [
            "state_abbr",
            "county_geoid",
            "block_geoid",
            "provider_id",
            "technology",
            "max_down",
            "max_up",
            "low_latency",
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"

        # Verify data loaded
        assert len(result) == 2, "Should load 2 test records"

    def test_get_coverage_by_state_return_type(self, connector, tmp_path):
        """
        Verify get_coverage_by_state() returns DataFrame.

        Contract: get_coverage_by_state() should return DataFrame with
        filtered coverage data for specified state.

        Layer 8: Contract testing - method interface validation.
        """
        # Setup test data
        test_csv = tmp_path / "test_coverage.csv"
        test_csv.write_text(
            "state_abbr,county_geoid,block_geoid,provider_id,technology,max_down,max_up,low_latency\n"
            "CA,06001,060011001001000,1,50,1000,1000,1\n"
            "NY,36001,360011001001000,2,40,500,50,1\n"
        )

        connector.connect()
        connector.load_coverage_data(test_csv)

        # Test method
        result = connector.get_coverage_by_state("CA")

        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        assert len(result) == 1, "Should filter to CA records only"
        assert all(result["state_abbr"] == "CA"), "All records should be for CA"

    def test_get_underserved_areas_return_type(self, connector, tmp_path):
        """
        Verify get_underserved_areas() returns DataFrame with underserved blocks.

        Contract: get_underserved_areas() should return DataFrame identifying
        census blocks not meeting minimum broadband speed thresholds.

        Layer 8: Contract testing - filtering logic validation.
        """
        # Setup test data with mix of served/underserved
        test_csv = tmp_path / "test_coverage.csv"
        test_csv.write_text(
            "state_abbr,county_geoid,block_geoid,provider_id,technology,max_down,max_up,low_latency\n"
            "CA,06001,060011001001000,1,50,1000,1000,1\n"  # Well-served (fiber gigabit)
            "CA,06001,060011001001001,2,10,10,1,0\n"  # Underserved (DSL 10/1)
            "CA,06001,060011001001002,3,40,100,20,1\n"  # Adequate (cable 100/20)
        )

        connector.connect()
        connector.load_coverage_data(test_csv)

        # Test method (default 25/3 Mbps threshold)
        result = connector.get_underserved_areas()

        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        assert "block_geoid" in result.columns, "Should include block_geoid"

        # Verify underserved block is identified
        underserved_blocks = result["block_geoid"].tolist()
        assert "060011001001001" in underserved_blocks, "Should identify DSL block as underserved"

    def test_get_provider_competition_return_type(self, connector, tmp_path):
        """
        Verify get_provider_competition() returns DataFrame with competition metrics.

        Contract: get_provider_competition() should return DataFrame with
        provider counts and competition classification per census block.

        Layer 8: Contract testing - aggregation output validation.
        """
        # Setup test data with varying provider counts
        test_csv = tmp_path / "test_coverage.csv"
        test_csv.write_text(
            "state_abbr,county_geoid,block_geoid,provider_id,technology,max_down,max_up,low_latency\n"
            "CA,06001,060011001001000,1,50,1000,1000,1\n"  # Block with 1 provider (monopoly)
            "CA,06001,060011001001001,2,40,500,50,1\n"  # Block with 2 providers (duopoly)
            "CA,06001,060011001001001,3,50,1000,1000,1\n"  # (same block, provider 3)
            "CA,06001,060011001001002,4,40,100,20,1\n"  # Block with 3+ providers (competitive)
            "CA,06001,060011001001002,5,50,1000,1000,1\n"  # (same block, provider 5)
            "CA,06001,060011001001002,6,10,25,3,0\n"  # (same block, provider 6)
        )

        connector.connect()
        connector.load_coverage_data(test_csv)

        # Test method
        result = connector.get_provider_competition()

        assert isinstance(result, pd.DataFrame), "Should return DataFrame"

        # Verify expected columns
        expected_columns = ["block_geoid", "provider_count", "monopoly", "duopoly", "competitive"]
        for col in expected_columns:
            assert col in result.columns, f"Missing expected column: {col}"

        # Verify competition classification
        assert len(result) == 3, "Should have 3 unique blocks"

        # Check monopoly block
        monopoly_block = result[result["block_geoid"] == "060011001001000"].iloc[0]
        assert monopoly_block["provider_count"] == 1, "Monopoly block should have 1 provider"
        assert monopoly_block["monopoly"] is True, "Should flag monopoly"

        # Check duopoly block
        duopoly_block = result[result["block_geoid"] == "060011001001001"].iloc[0]
        assert duopoly_block["provider_count"] == 2, "Duopoly block should have 2 providers"
        assert duopoly_block["duopoly"] is True, "Should flag duopoly"

        # Check competitive block
        competitive_block = result[result["block_geoid"] == "060011001001002"].iloc[0]
        assert competitive_block["provider_count"] == 3, "Competitive block should have 3 providers"
        assert competitive_block["competitive"] is True, "Should flag competitive"

    def test_get_speed_tier_distribution_return_type(self, connector, tmp_path):
        """
        Verify get_speed_tier_distribution() returns Dict with speed categories.

        Contract: get_speed_tier_distribution() should return dictionary with
        counts for each speed tier category.

        Layer 8: Contract testing - return type and structure validation.
        """
        # Setup test data with various speed tiers
        test_csv = tmp_path / "test_coverage.csv"
        test_csv.write_text(
            "state_abbr,county_geoid,block_geoid,provider_id,technology,max_down,max_up,low_latency\n"
            "CA,06001,060011001001000,1,10,10,1,0\n"  # Under 25 Mbps
            "CA,06001,060011001001001,2,40,50,10,1\n"  # 25-100 Mbps
            "CA,06001,060011001001002,3,40,500,50,1\n"  # 100-1000 Mbps
            "CA,06001,060011001001003,4,50,1000,1000,1\n"  # Gigabit+
        )

        connector.connect()
        connector.load_coverage_data(test_csv)

        # Test method
        result = connector.get_speed_tier_distribution()

        assert isinstance(result, dict), "Should return dictionary"

        # Verify expected keys
        expected_keys = ["under_25mbps", "25_100mbps", "100_1000mbps", "gigabit_plus"]
        for key in expected_keys:
            assert key in result, f"Missing expected key: {key}"
            assert isinstance(result[key], int), f"Value for {key} should be int"

        # Verify counts (basic sanity check)
        assert result["under_25mbps"] >= 0, "Count should be non-negative"
        assert result["gigabit_plus"] >= 0, "Count should be non-negative"
