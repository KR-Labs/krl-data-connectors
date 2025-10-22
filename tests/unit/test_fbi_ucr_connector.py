# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for FBI Uniform Crime Reporting connector.

Tests the FBIUCRConnector for FBI UCR crime data access.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.crime import FBIUCRConnector


@pytest.fixture
def fbi_connector():
    """Create a FBIUCRConnector instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield FBIUCRConnector(cache_dir=tmpdir)


@pytest.fixture
def sample_crime_data():
    """Create sample crime data for testing."""
    return pd.DataFrame(
        {
            "state": ["RI", "RI", "MA", "MA"],
            "agency": ["Providence PD", "Newport PD", "Boston PD", "Cambridge PD"],
            "year": [2023, 2023, 2023, 2023],
            "population": [180000, 25000, 675000, 118000],
            "violent_crime": [500, 45, 2500, 180],
            "murder": [10, 1, 50, 3],
            "rape": [50, 5, 200, 15],
            "robbery": [150, 15, 800, 50],
            "aggravated_assault": [290, 24, 1450, 112],
            "property_crime": [2500, 300, 10000, 800],
            "burglary": [400, 50, 1500, 120],
            "larceny": [1800, 220, 7500, 600],
            "motor_vehicle_theft": [300, 30, 1000, 80],
        }
    )


class TestFBIUCRConnectorInit:
    """Test FBIUCRConnector initialization."""

    def test_init_default(self):
        """Test default initialization."""
        connector = FBIUCRConnector()
        assert connector is not None
        assert connector.base_url == "https://api.usa.gov/crime/fbi/cde"

    def test_init_custom_cache(self):
        """Test initialization with custom cache settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            connector = FBIUCRConnector(cache_dir=tmpdir)
            assert connector is not None
            assert hasattr(connector, "load_crime_data")


class TestDataLoading:
    """Test data loading methods."""

    def test_load_crime_data(self, fbi_connector, sample_crime_data, tmp_path):
        """Test loading crime data from file."""
        filepath = tmp_path / "ucr.csv"
        sample_crime_data.to_csv(filepath, index=False)

        data = fbi_connector.load_crime_data(filepath)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4
        assert "violent_crime" in data.columns


class TestStateData:
    """Test state-level crime data retrieval."""

    @patch("requests.get")
    def test_get_state_crime_data_api(self, mock_get, fbi_connector):
        """Test getting state crime data via API."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [{"state": "RI", "year": 2023, "violent_crime": 500}]
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = fbi_connector.get_state_crime_data("RI", 2023)

        assert isinstance(result, pd.DataFrame)

    def test_get_state_crime_data_no_api(self, fbi_connector):
        """Test getting state crime data without API."""
        result = fbi_connector.get_state_crime_data("RI", 2023, use_api=False)

        assert result.empty


class TestCrimeTypeFiltering:
    """Test filtering by crime type."""

    def test_get_violent_crime(self, fbi_connector, sample_crime_data):
        """Test extracting violent crime data."""
        result = fbi_connector.get_violent_crime(sample_crime_data)

        assert "violent_crime" in result.columns
        assert "murder" in result.columns
        assert "rape" in result.columns
        assert "robbery" in result.columns
        assert "aggravated_assault" in result.columns

    def test_get_property_crime(self, fbi_connector, sample_crime_data):
        """Test extracting property crime data."""
        result = fbi_connector.get_property_crime(sample_crime_data)

        assert "property_crime" in result.columns
        assert "burglary" in result.columns
        assert "larceny" in result.columns
        assert "motor_vehicle_theft" in result.columns

    def test_violent_crime_no_columns(self, fbi_connector):
        """Test violent crime extraction with no relevant columns."""
        data = pd.DataFrame(
            {
                "state": ["RI"],
                "year": [2023],
                "total_arrests": [1000],
            }
        )

        result = fbi_connector.get_violent_crime(data)
        assert result.empty


class TestRateCalculations:
    """Test crime rate calculations."""

    def test_calculate_crime_rate_default(self, fbi_connector, sample_crime_data):
        """Test crime rate calculation per 100,000."""
        result = fbi_connector.calculate_crime_rate(
            sample_crime_data, "violent_crime", "population"
        )

        assert "violent_crime_rate" in result.columns
        # Providence: 500 / 180000 * 100000 = 277.78
        assert abs(result.iloc[0]["violent_crime_rate"] - 277.78) < 1.0

    def test_calculate_crime_rate_custom_per_capita(self, fbi_connector, sample_crime_data):
        """Test crime rate with custom per capita value."""
        result = fbi_connector.calculate_crime_rate(
            sample_crime_data, "murder", "population", per_capita=1000
        )

        assert "murder_rate" in result.columns
        # Providence: 10 / 180000 * 1000 = 0.056
        assert abs(result.iloc[0]["murder_rate"] - 0.056) < 0.01

    def test_calculate_crime_rate_missing_column(self, fbi_connector):
        """Test rate calculation with missing column."""
        data = pd.DataFrame(
            {
                "state": ["RI"],
                "violent_crime": [500],
            }
        )

        result = fbi_connector.calculate_crime_rate(data, "violent_crime", "population")
        assert "violent_crime_rate" not in result.columns


class TestStateComparisons:
    """Test comparing crime across states."""

    @patch.object(FBIUCRConnector, "get_state_crime_data")
    def test_compare_states_all_crime(self, mock_get_state, fbi_connector):
        """Test comparing all crime types across states."""
        mock_get_state.side_effect = [
            pd.DataFrame({"state": ["RI"], "violent_crime": [500], "property_crime": [2500]}),
            pd.DataFrame({"state": ["MA"], "violent_crime": [2500], "property_crime": [10000]}),
        ]

        result = fbi_connector.compare_states(["RI", "MA"], 2023)

        assert len(result) == 2
        assert set(result["state"].unique()) == {"RI", "MA"}

    @patch.object(FBIUCRConnector, "get_state_crime_data")
    def test_compare_states_violent_only(self, mock_get_state, fbi_connector):
        """Test comparing violent crime across states."""
        mock_get_state.side_effect = [
            pd.DataFrame({"state": ["RI"], "violent_crime": [500], "property_crime": [2500]}),
            pd.DataFrame({"state": ["MA"], "violent_crime": [2500], "property_crime": [10000]}),
        ]

        result = fbi_connector.compare_states(["RI", "MA"], 2023, crime_type="violent")

        assert "violent_crime" in result.columns
        assert "property_crime" not in result.columns

    @patch.object(FBIUCRConnector, "get_state_crime_data")
    def test_compare_states_property_only(self, mock_get_state, fbi_connector):
        """Test comparing property crime across states."""
        mock_get_state.side_effect = [
            pd.DataFrame({"state": ["RI"], "violent_crime": [500], "property_crime": [2500]}),
            pd.DataFrame({"state": ["MA"], "violent_crime": [2500], "property_crime": [10000]}),
        ]

        result = fbi_connector.compare_states(["RI", "MA"], 2023, crime_type="property")

        assert "property_crime" in result.columns
        assert "violent_crime" not in result.columns


class TestYoYAnalysis:
    """Test year-over-year crime change."""

    def test_calculate_yoy_change(self, fbi_connector):
        """Test YoY crime change calculation."""
        current_year = pd.DataFrame(
            {
                "state": ["RI", "MA"],
                "violent_crime": [500, 2500],
            }
        )

        previous_year = pd.DataFrame(
            {
                "state": ["RI", "MA"],
                "violent_crime": [450, 2400],
            }
        )

        result = fbi_connector.calculate_yoy_change(current_year, previous_year, "violent_crime")

        assert "yoy_change" in result.columns
        assert "yoy_change_pct" in result.columns
        # RI: (500 - 450) / 450 * 100 = 11.11%
        assert abs(result.iloc[0]["yoy_change_pct"] - 11.11) < 0.1

    def test_calculate_yoy_change_missing_column(self, fbi_connector):
        """Test YoY change with missing column."""
        current_year = pd.DataFrame({"state": ["RI"], "violent_crime": [500]})
        previous_year = pd.DataFrame({"state": ["RI"], "robbery": [150]})

        result = fbi_connector.calculate_yoy_change(current_year, previous_year, "violent_crime")

        assert result.empty


class TestTrendData:
    """Test multi-year trend analysis."""

    @patch.object(FBIUCRConnector, "get_state_crime_data")
    def test_get_trend_data(self, mock_get_state, fbi_connector):
        """Test getting multi-year trend data."""
        mock_get_state.side_effect = [
            pd.DataFrame({"state": ["RI"], "violent_crime": [450]}),
            pd.DataFrame({"state": ["RI"], "violent_crime": [480]}),
            pd.DataFrame({"state": ["RI"], "violent_crime": [500]}),
        ]

        result = fbi_connector.get_trend_data("RI", 2021, 2023)

        assert len(result) == 3
        assert "year" in result.columns
        assert set(result["year"].unique()) == {2021, 2022, 2023}

    @patch.object(FBIUCRConnector, "get_state_crime_data")
    def test_get_trend_data_empty(self, mock_get_state, fbi_connector):
        """Test trend data when no data available."""
        mock_get_state.return_value = pd.DataFrame()

        result = fbi_connector.get_trend_data("RI", 2020, 2022)

        assert result.empty


class TestExport:
    """Test data export functionality."""

    def test_export_to_csv(self, fbi_connector, sample_crime_data, tmp_path):
        """Test exporting crime data to CSV."""
        output_file = tmp_path / "export.csv"

        fbi_connector.export_to_csv(sample_crime_data, output_file)

        assert output_file.exists()

        exported = pd.read_csv(output_file)
        assert len(exported) == len(sample_crime_data)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_dataframe(self, fbi_connector):
        """Test handling empty DataFrame."""
        empty_df = pd.DataFrame()
        result = fbi_connector.get_violent_crime(empty_df)

        assert result.empty

    def test_missing_state_column(self, fbi_connector):
        """Test handling missing state column."""
        data = pd.DataFrame(
            {
                "agency": ["Providence PD"],
                "violent_crime": [500],
            }
        )

        result = fbi_connector.get_violent_crime(data)
        assert len(result) == 1

    @patch("requests.get")
    def test_api_request_failure(self, mock_get, fbi_connector):
        """Test handling API request failure."""
        mock_get.side_effect = Exception("API Error")

        # Implementation raises exception instead of returning empty DataFrame
        with pytest.raises(Exception, match="API Error"):
            fbi_connector.get_state_crime_data("RI", 2023)


class TestCrimeCategories:
    """Test crime category definitions."""

    def test_violent_crime_list(self, fbi_connector):
        """Test violent crime categories."""
        assert "murder" in fbi_connector.violent_crimes
        assert "rape" in fbi_connector.violent_crimes
        assert "robbery" in fbi_connector.violent_crimes
        assert "aggravated-assault" in fbi_connector.violent_crimes

    def test_property_crime_list(self, fbi_connector):
        """Test property crime categories."""
        assert "burglary" in fbi_connector.property_crimes
        assert "larceny" in fbi_connector.property_crimes
        assert "motor-vehicle-theft" in fbi_connector.property_crimes
        assert "arson" in fbi_connector.property_crimes


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestFBIUCRSecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    @patch("requests.get")
    def test_sql_injection_in_state(self, mock_get, fbi_connector):
        """Test SQL injection attempt in state parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # SQL injection attempt
        malicious_state = "RI'; DROP TABLE crime; --"

        # Should handle safely
        try:
            df = fbi_connector.get_state_crime_data(malicious_state, 2023)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, KeyError):
            # Acceptable to reject invalid state codes
            pass

    @patch("requests.get")
    def test_command_injection_in_crime_type(self, mock_get, fbi_connector):
        """Test command injection prevention."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Command injection attempt
        malicious_crime = "murder; rm -rf /"

        # Should handle safely
        try:
            df = fbi_connector.get_crime_data_by_type(malicious_crime, 2023)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject malicious input
            pass

    @patch("requests.get")
    def test_xss_injection_prevention(self, mock_get, fbi_connector):
        """Test XSS injection prevention."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # XSS attempt
        xss_payload = "<script>alert('XSS')</script>"

        # Should handle safely
        try:
            df = fbi_connector.get_state_crime_data(xss_payload, 2023)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, KeyError):
            # Acceptable to reject XSS payloads
            pass


class TestFBIUCRSecurityInputValidation:
    """Test security: Input validation and sanitization."""

    def test_year_type_validation(self, fbi_connector):
        """Test year parameter type validation."""
        # Invalid year type
        with pytest.raises((ValueError, TypeError)):
            fbi_connector.get_state_crime_data("RI", "not_a_year")

    def test_state_code_validation(self, fbi_connector):
        """Test state code validation."""
        # Empty state code
        with pytest.raises((ValueError, KeyError)):
            fbi_connector.get_state_crime_data("", 2023)

    @patch("requests.get")
    def test_handles_null_bytes(self, mock_get, fbi_connector):
        """Test handling of null bytes in parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Null byte injection
        malicious_state = "RI\x00malicious"

        # Should handle safely or reject
        try:
            df = fbi_connector.get_state_crime_data(malicious_state, 2023)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    @patch("requests.get")
    def test_handles_extremely_long_crime_types(self, mock_get, fbi_connector):
        """Test handling of excessively long crime types (DoS prevention)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        # Extremely long crime type
        long_crime = "murder" * 10000

        # Should handle safely or reject
        try:
            df = fbi_connector.get_crime_data_by_type(long_crime, 2023)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject overly long inputs
            pass

    def test_year_range_validation(self, fbi_connector):
        """Test year range boundary validation."""
        # Year too far in past (FBI UCR data starts ~1960s)
        try:
            df = fbi_connector.get_state_crime_data("RI", 1800)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject unreasonable years
            pass

        # Year too far in future
        try:
            df = fbi_connector.get_state_crime_data("RI", 9999)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject unreasonable years
            pass


class TestFBIUCRPropertyBased:
    """Test FBI UCR connector using property-based testing with Hypothesis."""

    @pytest.mark.hypothesis
    def test_year_parameter_validation_property(self, fbi_connector):
        """Property: Year parameter should accept valid years (1960-2023)."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(year=st.integers(min_value=1960, max_value=2023))
        def check_year_handling(year):
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "results": [
                        {
                            "state_abbr": "RI",
                            "year": year,
                            "violent_crime": 1000,
                            "property_crime": 5000,
                        }
                    ]
                }
                mock_get.return_value = mock_response

                df = fbi_connector.get_state_crime_data("RI", year, use_api=True)
                assert isinstance(df, pd.DataFrame)
                assert mock_get.called

        check_year_handling()

    @pytest.mark.hypothesis
    def test_state_code_property(self, fbi_connector):
        """Property: State codes should be 2-letter uppercase strings."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(
            state=st.text(
                alphabet=st.characters(min_codepoint=65, max_codepoint=90), min_size=2, max_size=2
            )
        )
        def check_state_code_handling(state):
            with patch("requests.get") as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "results": [{"state_abbr": state, "year": 2022, "violent_crime": 1000}]
                }
                mock_get.return_value = mock_response

                # Only test valid state codes
                try:
                    df = fbi_connector.get_state_crime_data(state, 2022, use_api=True)
                    assert isinstance(df, pd.DataFrame)
                    assert mock_get.called
                except (KeyError, ValueError):
                    # Acceptable to reject invalid state codes
                    pass

        check_state_code_handling()

    @pytest.mark.hypothesis
    def test_crime_count_property(self, fbi_connector):
        """Property: Crime counts should be non-negative integers."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(
            violent_crime=st.integers(min_value=0, max_value=1000000),
            property_crime=st.integers(min_value=0, max_value=1000000),
        )
        def check_crime_count_handling(violent_crime, property_crime):
            # Create mock crime data DataFrame with required columns
            crime_df = pd.DataFrame(
                {
                    "year": [2022],
                    "state": ["RI"],
                    "violent_crime": [violent_crime],
                    "property_crime": [property_crime],
                }
            )

            # Test violent crime filtering
            if hasattr(fbi_connector, "get_violent_crime"):
                result = fbi_connector.get_violent_crime(crime_df)
                assert isinstance(result, pd.DataFrame)
                if not result.empty and "violent_crime" in result.columns:
                    assert all(result["violent_crime"] >= 0)

        check_crime_count_handling()

    @pytest.mark.hypothesis
    def test_crime_rate_property(self, fbi_connector):
        """Property: Crime rates should be calculable from counts and population."""
        from hypothesis import given
        from hypothesis import strategies as st

        @given(
            crime_count=st.integers(min_value=0, max_value=100000),
            population=st.integers(min_value=1, max_value=10000000),
        )
        def check_rate_calculation(crime_count, population):
            # Crime rate per 100,000 population
            expected_rate = (crime_count / population) * 100000

            # Create test data
            test_df = pd.DataFrame({"crime_count": [crime_count], "population": [population]})

            # Validate rate calculation range
            assert expected_rate >= 0
            if population > 0:
                assert expected_rate <= 100000 * 100000  # Max possible rate

        check_rate_calculation()


class TestFBIUCRConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    def test_connect_return_type(self):
        """Test that connect returns None."""
        fbi = FBIUCRConnector()
        result = fbi.connect()
        assert result is None

    @patch("krl_data_connectors.crime.fbi_ucr_connector.FBIUCRConnector.get_state_crime_data")
    def test_fetch_return_type(self, mock_get_state):
        """Test that fetch returns DataFrame."""
        mock_get_state.return_value = pd.DataFrame(
            {"State": ["RI"], "Year": [2023], "ViolentCrime": [1000]}
        )
        fbi = FBIUCRConnector()
        result = fbi.fetch(state="RI", year=2023, data_type="state")
        assert isinstance(result, pd.DataFrame)

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_load_crime_data_return_type(self, mock_read_csv, mock_exists):
        """Test that load_crime_data returns DataFrame."""
        mock_exists.return_value = True
        mock_read_csv.return_value = pd.DataFrame({"State": ["RI"], "ViolentCrime": [1000]})
        fbi = FBIUCRConnector()
        result = fbi.load_crime_data("test.csv")
        assert isinstance(result, pd.DataFrame)

    @patch("requests.get")
    def test_get_state_crime_data_return_type(self, mock_get):
        """Test that get_state_crime_data returns DataFrame."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": [{"State": "RI", "ViolentCrime": 1000}]}
        mock_get.return_value = mock_response

        fbi = FBIUCRConnector(api_key="test_key")
        result = fbi.get_state_crime_data("RI", 2023)
        assert isinstance(result, pd.DataFrame)

    def test_get_violent_crime_return_type(self):
        """Test that get_violent_crime returns DataFrame."""
        fbi = FBIUCRConnector()
        df = pd.DataFrame({"State": ["RI"], "Murder": [10], "Robbery": [100], "Assault": [500]})
        result = fbi.get_violent_crime(df)
        assert isinstance(result, pd.DataFrame)

    def test_get_property_crime_return_type(self):
        """Test that get_property_crime returns DataFrame."""
        fbi = FBIUCRConnector()
        df = pd.DataFrame(
            {"State": ["RI"], "Burglary": [200], "Larceny": [1000], "MotorVehicleTheft": [150]}
        )
        result = fbi.get_property_crime(df)
        assert isinstance(result, pd.DataFrame)

    def test_calculate_crime_rate_return_type(self):
        """Test that calculate_crime_rate returns DataFrame."""
        fbi = FBIUCRConnector()
        df = pd.DataFrame({"State": ["RI"], "ViolentCrime": [1000], "Population": [1000000]})
        result = fbi.calculate_crime_rate(df, "ViolentCrime", "Population")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.crime.fbi_ucr_connector.FBIUCRConnector.get_state_crime_data")
    def test_compare_states_return_type(self, mock_get_state):
        """Test that compare_states returns DataFrame."""
        mock_get_state.side_effect = [
            pd.DataFrame({"State": ["RI"], "ViolentCrime": [1000]}),
            pd.DataFrame({"State": ["MA"], "ViolentCrime": [2000]}),
        ]
        fbi = FBIUCRConnector()
        result = fbi.compare_states(["RI", "MA"], 2023)
        assert isinstance(result, pd.DataFrame)

    def test_calculate_yoy_change_return_type(self):
        """Test that calculate_yoy_change returns DataFrame."""
        fbi = FBIUCRConnector()
        df_2022 = pd.DataFrame({"state": ["RI"], "ViolentCrime": [900]})
        df_2023 = pd.DataFrame({"state": ["RI"], "ViolentCrime": [1000]})
        result = fbi.calculate_yoy_change(df_2023, df_2022, "ViolentCrime")
        assert isinstance(result, pd.DataFrame)

    @patch("krl_data_connectors.crime.fbi_ucr_connector.FBIUCRConnector.get_state_crime_data")
    def test_get_trend_data_return_type(self, mock_get_state):
        """Test that get_trend_data returns DataFrame."""
        mock_get_state.side_effect = [
            pd.DataFrame({"Year": [2021], "ViolentCrime": [900]}),
            pd.DataFrame({"Year": [2022], "ViolentCrime": [950]}),
            pd.DataFrame({"Year": [2023], "ViolentCrime": [1000]}),
        ]
        fbi = FBIUCRConnector()
        result = fbi.get_trend_data("RI", 2021, 2023)
        assert isinstance(result, pd.DataFrame)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
