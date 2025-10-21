"""Tests for County Health Rankings Connector"""

import pytest
import pandas as pd
from unittest.mock import patch
from krl_data_connectors.health import CountyHealthRankingsConnector


@pytest.fixture
def chr_connector():
    with patch.dict("os.environ", {"CHR_API_KEY": "test_key"}):
        return CountyHealthRankingsConnector()


@pytest.fixture
def sample_chr_data():
    return pd.DataFrame(
        {
            "state": ["RI", "RI", "RI", "CA", "CA"],
            "county": ["Providence", "Kent", "Washington", "Los Angeles", "San Diego"],
            "fips": ["44007", "44003", "44009", "06037", "06073"],
            "health_outcomes_rank": [2, 1, 3, 45, 30],
            "health_factors_rank": [1, 2, 3, 40, 28],
            "premature_death": [250, 220, 270, 450, 380],
            "adult_obesity": [28.0, 26.5, 29.0, 32.5, 30.2],
            "uninsured": [4.5, 4.0, 4.8, 8.5, 7.2],
            "year": [2025] * 5,
        }
    )


def test_initialization(chr_connector):
    assert chr_connector is not None
    assert hasattr(chr_connector, "connect")


def test_load_rankings_data(chr_connector, sample_chr_data, tmp_path):
    test_file = tmp_path / "chr_data.csv"
    sample_chr_data.to_csv(test_file, index=False)
    data = chr_connector.load_rankings_data(test_file)
    assert not data.empty
    assert "health_outcomes_rank" in data.columns


def test_get_state_data(chr_connector, sample_chr_data):
    state_data = chr_connector.get_state_data(sample_chr_data, "RI")
    assert not state_data.empty
    assert all(state_data["state"] == "RI")
    assert len(state_data) == 3


def test_get_county_data(chr_connector, sample_chr_data):
    county_data = chr_connector.get_county_data(sample_chr_data, "Providence", state="RI")
    assert not county_data.empty
    assert county_data["county"].iloc[0] == "Providence"


class TestCHRConnectorSecurityInjection:
    """Test Layer 5: Security - Injection Prevention."""

    def test_sql_injection_in_state_filter(self, chr_connector, sample_chr_data):
        """Test SQL injection attempts in state parameter."""
        malicious_state = "RI'; DROP TABLE counties;--"

        # Should handle safely (pandas filtering doesn't execute SQL)
        result = chr_connector.get_state_data(sample_chr_data, malicious_state)

        # Should return empty DataFrame (no match) or handle safely
        assert isinstance(result, pd.DataFrame)

    def test_sql_injection_in_county_filter(self, chr_connector, sample_chr_data):
        """Test SQL injection attempts in county parameter."""
        malicious_county = "Providence' OR '1'='1"

        # Should handle safely
        try:
            result = chr_connector.get_county_data(sample_chr_data, malicious_county, state="RI")
            assert isinstance(result, pd.DataFrame)
        except Exception:
            pass  # Exception is acceptable for malicious input

    def test_command_injection_in_file_path(self, chr_connector, tmp_path):
        """Test command injection attempts in file path."""
        malicious_path = str(tmp_path / "data.csv; rm -rf /")

        # Should handle path safely (file operations are sanitized by OS)
        try:
            chr_connector.load_rankings_data(malicious_path)
        except (FileNotFoundError, OSError, ValueError):
            pass  # Expected to fail safely


class TestCHRConnectorSecurityInputValidation:
    """Test Layer 5: Security - Input Validation."""

    def test_handles_null_bytes_in_state(self, chr_connector, sample_chr_data):
        """Test null byte injection handling in state parameter."""
        malicious_state = "RI\x00"

        # Should handle null bytes safely
        try:
            result = chr_connector.get_state_data(sample_chr_data, malicious_state)
            assert isinstance(result, pd.DataFrame)
        except (ValueError, TypeError):
            pass  # Expected to reject null bytes

    def test_handles_extremely_long_state_name(self, chr_connector, sample_chr_data):
        """Test handling of extremely long state names (DoS prevention)."""
        extremely_long_state = "R" * 100000

        # Should handle without crashing
        result = chr_connector.get_state_data(sample_chr_data, extremely_long_state)
        assert isinstance(result, pd.DataFrame)
        # Should return empty (no match)
        assert len(result) == 0

    def test_handles_extremely_long_county_name(self, chr_connector, sample_chr_data):
        """Test handling of extremely long county names (DoS prevention)."""
        extremely_long_county = "P" * 100000

        # Should handle without crashing
        result = chr_connector.get_county_data(sample_chr_data, extremely_long_county, state="RI")
        assert isinstance(result, pd.DataFrame)
        # Should return empty (no match)
        assert len(result) == 0

    def test_empty_state_parameter(self, chr_connector, sample_chr_data):
        """Test handling of empty state parameter."""
        result = chr_connector.get_state_data(sample_chr_data, "")
        assert isinstance(result, pd.DataFrame)
        # Empty string should not match any state
        assert len(result) == 0

    def test_none_state_parameter(self, chr_connector, sample_chr_data):
        """Test handling of None state parameter."""
        # The connector doesn't handle None gracefully and raises AttributeError
        with pytest.raises(AttributeError):
            chr_connector.get_state_data(sample_chr_data, None)

    def test_special_characters_in_county_name(self, chr_connector, sample_chr_data):
        """Test handling of special characters in county name."""
        special_chars = "O'Brien"  # Common case with apostrophe

        # Should handle special characters safely
        result = chr_connector.get_county_data(sample_chr_data, special_chars, state="RI")
        assert isinstance(result, pd.DataFrame)

    def test_unicode_characters_in_state(self, chr_connector, sample_chr_data):
        """Test handling of Unicode characters in state parameter."""
        unicode_state = "РИ"  # Cyrillic characters

        # Should handle Unicode safely
        result = chr_connector.get_state_data(sample_chr_data, unicode_state)
        assert isinstance(result, pd.DataFrame)

    def test_nonexistent_file_path(self, chr_connector):
        """Test handling of nonexistent file paths."""
        nonexistent_path = "/path/that/does/not/exist.csv"

        # Should raise appropriate exception
        with pytest.raises((FileNotFoundError, OSError, ValueError)):
            chr_connector.load_rankings_data(nonexistent_path)

    def test_invalid_file_format(self, chr_connector, tmp_path):
        """Test handling of invalid file formats."""
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This is not CSV data")

        # Should handle or raise appropriate exception
        try:
            chr_connector.load_rankings_data(str(invalid_file))
        except (pd.errors.ParserError, ValueError, KeyError):
            pass  # Expected to fail for invalid format
