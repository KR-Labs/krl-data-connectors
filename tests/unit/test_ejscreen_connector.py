"""
Tests for EPA EJScreen connector.

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from krl_data_connectors.environment import EJScreenConnector


@pytest.fixture
def sample_ejscreen_data():
    """Create sample EJScreen data for testing."""
    return pd.DataFrame(
        {
            "ID": [
                "010010201001",
                "010010201002",
                "010010202001",
                "440070401001",
                "440070401002",
                "440070402001",
                "060370101001",
                "060370101002",
                "060370102001",
            ],
            "ST_ABBREV": ["AL", "AL", "AL", "RI", "RI", "RI", "CA", "CA", "CA"],
            "CNTY_FIPS": [
                "01001",
                "01001",
                "01001",
                "44007",
                "44007",
                "44007",
                "06037",
                "06037",
                "06037",
            ],
            "P_PM25": [45.2, 67.8, 89.3, 72.4, 85.1, 91.2, 55.3, 78.9, 82.4],
            "P_OZONE": [38.9, 72.1, 85.6, 68.2, 79.4, 88.7, 51.2, 74.8, 80.3],
            "P_DSLPM": [42.1, 69.5, 87.2, 70.3, 82.8, 89.9, 53.7, 76.2, 84.1],
            "P_MINORTY": [35.4, 65.2, 82.7, 68.9, 81.3, 87.6, 48.5, 72.4, 79.8],
            "P_LWINCPCT": [41.8, 68.3, 85.9, 71.2, 83.5, 90.4, 54.9, 77.1, 83.8],
            "P_D2_PM25": [50.3, 75.8, 92.1, 78.4, 88.9, 94.3, 61.7, 82.5, 87.9],
            "P_D5_PM25": [48.9, 73.2, 90.4, 76.8, 87.1, 93.2, 59.8, 80.9, 86.3],
            "ACSTOTPOP": [3245, 4892, 2156, 5234, 3987, 2891, 6523, 5178, 4329],
        }
    )


@pytest.fixture
def ejscreen_connector():
    """Create EJScreen connector instance."""
    return EJScreenConnector()


@pytest.fixture
def temp_csv_file(sample_ejscreen_data):
    """Create temporary CSV file with sample data."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        sample_ejscreen_data.to_csv(f.name, index=False)
        yield Path(f.name)
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


class TestEJScreenConnectorInit:
    """Test EJScreen connector initialization."""

    def test_init_default(self):
        """Test connector initialization with defaults."""
        connector = EJScreenConnector()
        assert connector.api_key is None
        assert connector.timeout == 30

    def test_init_with_params(self):
        """Test connector initialization with parameters."""
        connector = EJScreenConnector(cache_dir="/tmp/test", timeout=60)
        # cache_dir is stored in cache.cache_dir, not directly on connector
        assert str(connector.cache.cache_dir) == "/tmp/test"
        assert connector.timeout == 60

    def test_indicator_mappings(self, ejscreen_connector):
        """Test that indicator mappings are defined."""
        assert len(ejscreen_connector.ENVIRONMENTAL_INDICATORS) > 0
        assert len(ejscreen_connector.DEMOGRAPHIC_INDICATORS) > 0
        assert len(ejscreen_connector.EJ_INDEX_INDICATORS) > 0
        assert "P_PM25" in ejscreen_connector.ENVIRONMENTAL_INDICATORS
        assert "P_MINORTY" in ejscreen_connector.DEMOGRAPHIC_INDICATORS
        assert "P_D2_PM25" in ejscreen_connector.EJ_INDEX_INDICATORS


class TestLoadData:
    """Test data loading functionality."""

    def test_load_data_success(self, ejscreen_connector, temp_csv_file):
        """Test successful data loading from CSV."""
        data = ejscreen_connector.load_data(temp_csv_file)
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 9
        assert "ST_ABBREV" in data.columns
        assert "P_PM25" in data.columns

    def test_load_data_file_not_found(self, ejscreen_connector):
        """Test loading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            ejscreen_connector.load_data("nonexistent_file.csv")

    def test_load_data_invalid_file(self, ejscreen_connector):
        """Test loading from invalid CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("invalid,csv,data\n")
            f.write("with,wrong,format\n")
            temp_path = Path(f.name)

        try:
            # Should load but might have different structure
            data = ejscreen_connector.load_data(temp_path)
            assert isinstance(data, pd.DataFrame)
        finally:
            temp_path.unlink(missing_ok=True)


class TestGetStateData:
    """Test state filtering functionality."""

    def test_get_state_data_single_state(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering by single state."""
        ri_data = ejscreen_connector.get_state_data(sample_ejscreen_data, "RI")
        assert len(ri_data) == 3
        assert all(ri_data["ST_ABBREV"] == "RI")

    def test_get_state_data_case_insensitive(self, ejscreen_connector, sample_ejscreen_data):
        """Test that state filtering is case-insensitive."""
        ri_data_lower = ejscreen_connector.get_state_data(sample_ejscreen_data, "ri")
        ri_data_upper = ejscreen_connector.get_state_data(sample_ejscreen_data, "RI")
        assert len(ri_data_lower) == len(ri_data_upper)

    def test_get_state_data_invalid_column(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering with invalid state column."""
        with pytest.raises(ValueError, match="State column"):
            ejscreen_connector.get_state_data(sample_ejscreen_data, "RI", state_column="INVALID")

    def test_get_state_data_no_matches(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering for state with no data."""
        tx_data = ejscreen_connector.get_state_data(sample_ejscreen_data, "TX")
        assert len(tx_data) == 0


class TestGetCountyData:
    """Test county filtering functionality."""

    def test_get_county_data_success(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering by county FIPS."""
        prov_data = ejscreen_connector.get_county_data(sample_ejscreen_data, "44007")
        assert len(prov_data) == 3
        assert all(prov_data["CNTY_FIPS"].astype(str).str.zfill(5) == "44007")

    def test_get_county_data_padding(self, ejscreen_connector, sample_ejscreen_data):
        """Test that county FIPS codes are properly padded."""
        # Test with unpadded FIPS
        al_data = ejscreen_connector.get_county_data(sample_ejscreen_data, "01001")
        assert len(al_data) == 3

    def test_get_county_data_invalid_column(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering with invalid county column."""
        with pytest.raises(ValueError, match="County FIPS column"):
            ejscreen_connector.get_county_data(sample_ejscreen_data, "44007", fips_column="INVALID")

    def test_get_county_data_no_matches(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering for county with no data."""
        no_data = ejscreen_connector.get_county_data(sample_ejscreen_data, "99999")
        assert len(no_data) == 0


class TestFilterByThreshold:
    """Test threshold filtering functionality."""

    def test_filter_by_threshold_above(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering for values above threshold."""
        high_pm25 = ejscreen_connector.filter_by_threshold(
            sample_ejscreen_data, "P_PM25", threshold=80, above=True
        )
        assert len(high_pm25) == 4  # Values >= 80
        assert all(high_pm25["P_PM25"] >= 80)

    def test_filter_by_threshold_below(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering for values below threshold."""
        low_pm25 = ejscreen_connector.filter_by_threshold(
            sample_ejscreen_data, "P_PM25", threshold=60, above=False
        )
        assert len(low_pm25) == 2  # Values <= 60
        assert all(low_pm25["P_PM25"] <= 60)

    def test_filter_by_threshold_invalid_indicator(self, ejscreen_connector, sample_ejscreen_data):
        """Test filtering with invalid indicator."""
        with pytest.raises(ValueError, match="Indicator .* not found"):
            ejscreen_connector.filter_by_threshold(sample_ejscreen_data, "INVALID_COL", 80)

    def test_filter_by_threshold_edge_cases(self, ejscreen_connector, sample_ejscreen_data):
        """Test threshold filtering edge cases."""
        # Threshold at 0 (above)
        all_data = ejscreen_connector.filter_by_threshold(
            sample_ejscreen_data, "P_PM25", threshold=0, above=True
        )
        assert len(all_data) == 9

        # Threshold at 100 (below)
        all_data = ejscreen_connector.filter_by_threshold(
            sample_ejscreen_data, "P_PM25", threshold=100, above=False
        )
        assert len(all_data) == 9


class TestGetHighBurdenTracts:
    """Test high burden tract identification."""

    def test_get_high_burden_tracts_default(self, ejscreen_connector, sample_ejscreen_data):
        """Test identifying high burden tracts with defaults."""
        high_burden = ejscreen_connector.get_high_burden_tracts(sample_ejscreen_data)
        # Should have tracts with both PM25 >= 80 AND MINORTY >= 80
        assert len(high_burden) == 3  # Updated based on actual data
        assert all(high_burden["P_PM25"] >= 80)
        assert all(high_burden["P_MINORTY"] >= 80)

    def test_get_high_burden_tracts_custom_thresholds(
        self, ejscreen_connector, sample_ejscreen_data
    ):
        """Test high burden tracts with custom thresholds."""
        high_burden = ejscreen_connector.get_high_burden_tracts(
            sample_ejscreen_data,
            environmental_threshold=70,
            demographic_threshold=70,
        )
        assert len(high_burden) >= 4  # More lenient thresholds
        assert all(high_burden["P_PM25"] >= 70)
        assert all(high_burden["P_MINORTY"] >= 70)

    def test_get_high_burden_tracts_different_indicators(
        self, ejscreen_connector, sample_ejscreen_data
    ):
        """Test high burden tracts with different indicators."""
        high_burden = ejscreen_connector.get_high_burden_tracts(
            sample_ejscreen_data,
            environmental_indicator="P_OZONE",
            demographic_indicator="P_LWINCPCT",
            environmental_threshold=80,
            demographic_threshold=80,
        )
        assert all(high_burden["P_OZONE"] >= 80)
        assert all(high_burden["P_LWINCPCT"] >= 80)


class TestGetAvailableIndicators:
    """Test indicator availability checking."""

    def test_get_available_indicators(self, ejscreen_connector, sample_ejscreen_data):
        """Test getting available indicators from data."""
        indicators = ejscreen_connector.get_available_indicators(sample_ejscreen_data)

        assert "environmental" in indicators
        assert "demographic" in indicators
        assert "ej_index" in indicators

        # Check that indicators present in data are listed
        assert "P_PM25" in indicators["environmental"]
        assert "P_MINORTY" in indicators["demographic"]
        assert "P_D2_PM25" in indicators["ej_index"]

    def test_get_available_indicators_partial_data(self, ejscreen_connector):
        """Test getting indicators from data with missing columns."""
        partial_data = pd.DataFrame({"P_PM25": [50, 60, 70], "ST_ABBREV": ["RI", "RI", "RI"]})

        indicators = ejscreen_connector.get_available_indicators(partial_data)

        # Only PM25 should be available
        assert "P_PM25" in indicators["environmental"]
        assert len(indicators["demographic"]) == 0


class TestSummarizeByState:
    """Test state-level summarization."""

    def test_summarize_by_state_single_indicator(self, ejscreen_connector, sample_ejscreen_data):
        """Test summarizing single indicator by state."""
        summary = ejscreen_connector.summarize_by_state(sample_ejscreen_data, indicators=["P_PM25"])

        assert len(summary) == 3  # AL, RI, CA
        assert "ST_ABBREV" in summary.columns
        assert ("P_PM25", "mean") in summary.columns
        assert ("P_PM25", "median") in summary.columns

    def test_summarize_by_state_multiple_indicators(self, ejscreen_connector, sample_ejscreen_data):
        """Test summarizing multiple indicators by state."""
        summary = ejscreen_connector.summarize_by_state(
            sample_ejscreen_data, indicators=["P_PM25", "P_MINORTY", "P_D2_PM25"]
        )

        assert len(summary) == 3
        # Check all stats are present for all indicators
        for indicator in ["P_PM25", "P_MINORTY", "P_D2_PM25"]:
            assert (indicator, "mean") in summary.columns
            assert (indicator, "min") in summary.columns
            assert (indicator, "max") in summary.columns

    def test_summarize_by_state_invalid_column(self, ejscreen_connector, sample_ejscreen_data):
        """Test summarizing with invalid state column."""
        with pytest.raises(ValueError, match="State column"):
            ejscreen_connector.summarize_by_state(
                sample_ejscreen_data, indicators=["P_PM25"], state_column="INVALID"
            )

    def test_summarize_by_state_missing_indicator(self, ejscreen_connector, sample_ejscreen_data):
        """Test summarizing with missing indicator."""
        with pytest.raises(ValueError, match="Indicators not found"):
            ejscreen_connector.summarize_by_state(
                sample_ejscreen_data, indicators=["P_PM25", "INVALID_INDICATOR"]
            )


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_load_filter_chain(self, ejscreen_connector, temp_csv_file):
        """Test chaining load and filter operations."""
        # Load data
        data = ejscreen_connector.load_data(temp_csv_file)

        # Filter to Rhode Island
        ri_data = ejscreen_connector.get_state_data(data, "RI")

        # Get high PM2.5 tracts
        high_pm25 = ejscreen_connector.filter_by_threshold(ri_data, "P_PM25", 80)

        assert len(high_pm25) == 2  # 2 RI tracts with PM25 >= 80

    def test_environmental_justice_analysis(self, ejscreen_connector, temp_csv_file):
        """Test full environmental justice analysis workflow."""
        # Load data
        data = ejscreen_connector.load_data(temp_csv_file)

        # Get available indicators
        indicators = ejscreen_connector.get_available_indicators(data)
        assert len(indicators["environmental"]) > 0

        # Identify high burden tracts
        ej_tracts = ejscreen_connector.get_high_burden_tracts(data)
        assert len(ej_tracts) > 0

        # Summarize by state
        summary = ejscreen_connector.summarize_by_state(data, indicators=["P_PM25", "P_MINORTY"])
        assert len(summary) == 3  # 3 states in test data


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestEJScreenSecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    def test_sql_injection_in_state(self, ejscreen_connector, temp_csv_file):
        """Test SQL injection attempt in state parameter."""
        data = ejscreen_connector.load_data(temp_csv_file)

        # SQL injection attempt
        malicious_state = "RI'; DROP TABLE data; --"

        # Should handle safely
        try:
            df = ejscreen_connector.get_state_data(data, malicious_state)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, KeyError):
            # Acceptable to reject invalid state codes
            pass

    def test_command_injection_in_indicator(self, ejscreen_connector, temp_csv_file):
        """Test command injection prevention."""
        data = ejscreen_connector.load_data(temp_csv_file)

        # Command injection attempt
        malicious_indicator = "P_PM25; rm -rf /"

        # Should handle safely
        try:
            df = ejscreen_connector.filter_by_threshold(data, malicious_indicator, 80)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, KeyError):
            # Acceptable to reject invalid indicators
            pass

    def test_path_traversal_in_load(self, ejscreen_connector):
        """Test path traversal prevention."""
        # Path traversal attempt
        malicious_path = "../../etc/passwd"

        # Should prevent path traversal
        with pytest.raises((FileNotFoundError, ValueError, OSError)):
            ejscreen_connector.load_data(malicious_path)


class TestEJScreenSecurityInputValidation:
    """Test security: Input validation and sanitization."""

    def test_threshold_type_validation(self, ejscreen_connector, temp_csv_file):
        """Test threshold parameter type validation."""
        data = ejscreen_connector.load_data(temp_csv_file)

        # Invalid threshold type
        with pytest.raises((ValueError, TypeError)):
            ejscreen_connector.filter_by_threshold(data, "P_PM25", "not_a_number")

    def test_threshold_range_validation(self, ejscreen_connector, temp_csv_file):
        """Test threshold range validation."""
        data = ejscreen_connector.load_data(temp_csv_file)

        # Negative threshold
        with pytest.raises((ValueError, TypeError)):
            ejscreen_connector.filter_by_threshold(data, "P_PM25", -1)

        # Threshold > 100 (percentiles should be 0-100)
        with pytest.raises((ValueError, TypeError)):
            ejscreen_connector.filter_by_threshold(data, "P_PM25", 101)

    def test_handles_null_bytes_in_state(self, ejscreen_connector, temp_csv_file):
        """Test handling of null bytes in state parameter."""
        data = ejscreen_connector.load_data(temp_csv_file)

        # Null byte injection
        malicious_state = "RI\x00malicious"

        # Should handle safely or reject
        try:
            df = ejscreen_connector.get_state_data(data, malicious_state)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    def test_handles_extremely_long_indicator_names(self, ejscreen_connector, temp_csv_file):
        """Test handling of excessively long indicator names (DoS prevention)."""
        data = ejscreen_connector.load_data(temp_csv_file)

        # Extremely long indicator name
        long_indicator = "P_PM25" * 10000

        # Should handle safely or reject
        try:
            df = ejscreen_connector.filter_by_threshold(data, long_indicator, 80)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, KeyError, Exception):
            # Acceptable to reject overly long inputs
            pass

    def test_empty_state_validation(self, ejscreen_connector, temp_csv_file):
        """Test empty state parameter validation."""
        data = ejscreen_connector.load_data(temp_csv_file)

        # Empty state
        with pytest.raises((ValueError, KeyError)):
            ejscreen_connector.get_state_data(data, "")

    def test_none_dataframe_handling(self, ejscreen_connector):
        """Test handling of None DataFrame."""
        # None DataFrame
        with pytest.raises((ValueError, AttributeError, TypeError)):
            ejscreen_connector.get_state_data(None, "RI")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
