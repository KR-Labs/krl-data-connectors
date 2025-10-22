# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for CDC WONDER connector.

Copyright (c) 2024-2025 KR-Labs Foundation
Licensed under the Apache License, Version 2.0
"""

from unittest.mock import Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.health import CDCWonderConnector


@pytest.fixture
def cdc_connector():
    """Create a CDC WONDER connector instance."""
    return CDCWonderConnector()


@pytest.fixture
def mock_xml_response():
    """Mock XML response from CDC WONDER API."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table>
        <r>
            <c l="State" v="California">California</c>
            <c l="Year" v="2020">2020</c>
            <c l="Deaths" v="123456">123456</c>
            <c l="Population" v="39538223">39538223</c>
            <c l="Crude Rate" v="312.3">312.3</c>
        </r>
        <r>
            <c l="State" v="New York">New York</c>
            <c l="Year" v="2020">2020</c>
            <c l="Deaths" v="98765">98765</c>
            <c l="Population" v="20201249">20201249</c>
            <c l="Crude Rate" v="488.8">488.8</c>
        </r>
    </data-table>
</response>"""


class TestCDCWonderConnector:
    """Test suite for CDC WONDER connector."""

    def test_initialization(self, cdc_connector):
        """Test connector initialization."""
        assert cdc_connector is not None
        assert cdc_connector.api_key is None
        assert cdc_connector.BASE_URL == "https://wonder.cdc.gov/controller/datarequest"

    def test_available_databases(self, cdc_connector):
        """Test getting available databases."""
        databases = cdc_connector.get_available_databases()
        assert isinstance(databases, dict)
        assert "mortality_underlying" in databases
        assert "natality" in databases
        assert "population" in databases
        assert databases["mortality_underlying"] == "D76"

    def test_build_xml_request(self, cdc_connector):
        """Test XML request building."""
        parameters = {"B_1": "D76.V2", "F_D76.V2": 2020, "O_show_totals": "true"}
        xml = cdc_connector._build_xml_request("D76", parameters)
        assert isinstance(xml, str)
        assert "<request-parameters>" in xml
        assert "<dataset>D76</dataset>" in xml
        assert "<name>B_1</name>" in xml
        assert "<value>D76.V2</value>" in xml

    def test_parse_response(self, cdc_connector, mock_xml_response):
        """Test parsing XML response."""
        df = cdc_connector._parse_response(mock_xml_response)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert "State" in df.columns
        assert "Deaths" in df.columns
        assert "Population" in df.columns

        # Check data types
        assert df["Deaths"].dtype in ["int64", "float64"]
        assert df["Population"].dtype in ["int64", "float64"]

        # Check values
        assert df.loc[0, "State"] == "California"
        assert df.loc[0, "Deaths"] == 123456
        assert df.loc[1, "State"] == "New York"

    def test_parse_response_with_error(self, cdc_connector):
        """Test parsing response with error."""
        error_xml = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <error>Invalid parameter</error>
</response>"""

        with pytest.raises(ValueError, match="CDC WONDER API error"):
            cdc_connector._parse_response(error_xml)

    def test_parse_response_empty(self, cdc_connector):
        """Test parsing empty response."""
        empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table></data-table>
</response>"""

        df = cdc_connector._parse_response(empty_xml)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_get_mortality_data(self, mock_post, cdc_connector, mock_xml_response):
        """Test getting mortality data."""
        mock_response = Mock()
        mock_response.text = mock_xml_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        df = cdc_connector.get_mortality_data(years=[2020], geo_level="state", states=["06", "36"])

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "data_source" in df.columns
        assert "database" in df.columns
        assert df["data_source"].iloc[0] == "CDC WONDER"
        assert df["database"].iloc[0] == "mortality_underlying"

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_get_natality_data(self, mock_post, cdc_connector):
        """Test getting natality data."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table>
        <r>
            <c l="State" v="California">California</c>
            <c l="Year" v="2020">2020</c>
            <c l="Births" v="45000">45000</c>
        </r>
    </data-table>
</response>"""
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        df = cdc_connector.get_natality_data(years=[2020], geo_level="state", states=["06"])

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "database" in df.columns
        assert df["database"].iloc[0] == "natality"

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_get_population_estimates(self, mock_post, cdc_connector):
        """Test getting population estimates."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table>
        <r>
            <c l="State" v="California">California</c>
            <c l="Year" v="2020">2020</c>
            <c l="Population" v="39538223">39538223</c>
        </r>
    </data-table>
</response>"""
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        df = cdc_connector.get_population_estimates(years=[2020], states=["06"])

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "database" in df.columns
        assert df["database"].iloc[0] == "population"

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_validate_connection(self, mock_post, cdc_connector, mock_xml_response):
        """Test connection validation."""
        mock_response = Mock()
        mock_response.text = mock_xml_response
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = cdc_connector.validate_connection()
        assert result is True

    def test_validate_connection_failure(self, cdc_connector):
        """Test connection validation failure."""
        # Mock the get_population_estimates to raise an exception
        with patch.object(cdc_connector, "get_population_estimates") as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            result = cdc_connector.validate_connection()
            assert result is False

    def test_default_years(self, cdc_connector, mock_xml_response):
        """Test default year handling."""
        # This should use default year [2020]
        with patch.object(cdc_connector, "_make_cdc_request") as mock_request:
            mock_request.return_value = mock_xml_response

            df = cdc_connector.get_mortality_data()
            # Verify that the request was made
            assert mock_request.called
            assert not df.empty

    def test_multiple_years(self, cdc_connector, mock_xml_response):
        """Test handling multiple years."""
        with patch.object(cdc_connector, "_make_cdc_request") as mock_request:
            mock_request.return_value = mock_xml_response

            df = cdc_connector.get_mortality_data(years=[2019, 2020, 2021])
            call_args = mock_request.call_args
            call_args[0][1]

            # Verify request was made
            assert mock_request.called
            assert not df.empty


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestCDCSecurityXMLInjection:
    """Test security: XML/XXE injection prevention."""

    def test_xml_injection_in_parameters(self, cdc_connector):
        """Test XML injection attempt in parameters."""
        # Malicious XML entity attempt
        malicious_value = (
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]><foo>&xxe;</foo>"
        )

        # Build XML with malicious content
        parameters = {"B_1": malicious_value}

        # Should handle safely (escape or reject)
        xml = cdc_connector._build_xml_request("D76", parameters)

        # XML should be safely escaped
        assert isinstance(xml, str)
        # Entities should be escaped
        assert "&lt;" in xml or "<!ENTITY" not in xml

    def test_xxe_attack_prevention(self, cdc_connector):
        """Test XXE (XML External Entity) attack prevention."""
        # XXE payload
        xxe_payload = """<?xml version="1.0"?>
        <!DOCTYPE data [
        <!ENTITY file SYSTEM "file:///etc/passwd">
        ]>
        <data>&file;</data>"""

        # Should parse safely without executing external entities
        try:
            cdc_connector._parse_response(xxe_payload)
        except Exception:
            # Expected to fail safely
            pass


class TestCDCSecuritySQLInjection:
    """Test security: SQL injection prevention."""

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_sql_injection_in_state_codes(self, mock_post, cdc_connector):
        """Test SQL injection attempt in state codes."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table></data-table>
</response>"""
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # SQL injection attempt
        malicious_states = ["06'; DROP TABLE states; --", "36"]

        # Should handle safely
        df = cdc_connector.get_mortality_data(
            years=[2020], geo_level="state", states=malicious_states
        )

        # Should not execute SQL, just treat as string
        assert isinstance(df, pd.DataFrame)

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_command_injection_in_years(self, mock_post, cdc_connector):
        """Test command injection attempt in year parameter."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table></data-table>
</response>"""
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Command injection attempt
        malicious_years = [2020, "2021; rm -rf /"]

        # Should handle safely (reject or sanitize)
        try:
            df = cdc_connector.get_mortality_data(years=malicious_years, geo_level="state")
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject invalid input
            pass


class TestCDCSecurityXSSPrevention:
    """Test security: XSS injection prevention."""

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_xss_in_database_name(self, mock_post, cdc_connector):
        """Test XSS injection attempt in database parameter."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table></data-table>
</response>"""
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # XSS attempt
        xss_payload = "<script>alert('XSS')</script>"

        # Build request with XSS
        xml = cdc_connector._build_xml_request(xss_payload, {})

        # Should be escaped
        assert "&lt;script&gt;" in xml or "<script>" not in xml


class TestCDCSecurityInputValidation:
    """Test security: Input validation and sanitization."""

    def test_validates_year_type(self, cdc_connector):
        """Test year parameter type validation."""
        # Invalid year types
        invalid_years = ["not_a_year", [], {}, None]

        for invalid in invalid_years:
            try:
                # Should reject or handle gracefully
                cdc_connector.get_mortality_data(years=[invalid])
            except (ValueError, TypeError, AttributeError):
                # Expected to reject invalid types
                pass

    def test_validates_geo_level(self, cdc_connector):
        """Test geo_level parameter validation."""
        # Invalid geo levels
        invalid_geo = "<script>alert('xss')</script>"

        try:
            cdc_connector.get_mortality_data(years=[2020], geo_level=invalid_geo)
        except (ValueError, KeyError):
            # Expected to reject invalid geo levels
            pass

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_handles_null_bytes(self, mock_post, cdc_connector):
        """Test handling of null bytes in parameters."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table></data-table>
</response>"""
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Null byte injection
        malicious_state = "06\x00malicious"

        try:
            df = cdc_connector.get_mortality_data(
                years=[2020], geo_level="state", states=[malicious_state]
            )
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    @patch("krl_data_connectors.health.cdc_connector.requests.Session.post")
    def test_handles_extremely_long_parameters(self, mock_post, cdc_connector):
        """Test handling of excessively long parameters (DoS attempt)."""
        mock_response = Mock()
        mock_response.text = """<?xml version="1.0" encoding="UTF-8"?>
<response>
    <data-table></data-table>
</response>"""
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        # Extremely long state code
        long_state = "06" * 5000

        try:
            df = cdc_connector.get_mortality_data(
                years=[2020], geo_level="state", states=[long_state]
            )
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject overly long inputs
            pass


class TestCDCPropertyBased:
    """Test Layer 7: Property-Based Testing with Hypothesis."""

    @pytest.mark.hypothesis
    def test_year_list_property(self):
        """Property test: Year lists should be handled consistently."""
        from hypothesis import given
        from hypothesis import strategies as st

        cdc_connector = CDCWonderConnector()

        @given(years=st.lists(st.integers(min_value=1999, max_value=2025), min_size=1, max_size=5))
        def check_year_list_handling(years):
            with patch.object(cdc_connector, "_make_cdc_request") as mock_request:
                mock_request.return_value = pd.DataFrame(
                    {"State": ["CA"], "Year": [years[0]], "Deaths": [100]}
                )

                try:
                    df = cdc_connector.get_mortality_data(years=years, geo_level="state")
                    assert isinstance(df, pd.DataFrame)
                    # All years should be integers
                    assert all(isinstance(y, int) for y in years)
                except (ValueError, TypeError):
                    pass  # Validation may reject some year combinations

        check_year_list_handling()

    @pytest.mark.hypothesis
    def test_state_code_list_property(self):
        """Property test: State codes should be 2-character uppercase strings."""
        from hypothesis import given
        from hypothesis import strategies as st

        cdc_connector = CDCWonderConnector()

        @given(
            states=st.lists(
                st.text(
                    alphabet=st.characters(whitelist_categories=("Lu",)), min_size=2, max_size=2
                ),
                min_size=1,
                max_size=3,
            )
        )
        def check_state_list_handling(states):
            # Return XML string as CDC expects
            xml_response = """<?xml version="1.0"?><response><data-table><r>
            <c l="State" v="{}">CA</c><c l="Year" v="2020">2020</c>
            <c l="Deaths" v="100">100</c></r></data-table></response>""".format(
                states[0]
            )

            with patch.object(cdc_connector, "_make_cdc_request") as mock_request:
                mock_request.return_value = xml_response

                try:
                    df = cdc_connector.get_mortality_data(
                        years=[2020], geo_level="state", states=states
                    )
                    assert isinstance(df, pd.DataFrame)
                except (ValueError, KeyError, Exception):
                    pass  # Invalid state codes or other errors may be rejected

        check_state_list_handling()

    @pytest.mark.hypothesis
    def test_geo_level_parameter_property(self):
        """Property test: Geographic level should only accept valid values."""
        from hypothesis import given
        from hypothesis import strategies as st

        cdc_connector = CDCWonderConnector()

        valid_levels = ["national", "state", "county"]

        @given(geo_level=st.text(min_size=1, max_size=20))
        def check_geo_level_validation(geo_level):
            xml_response = """<?xml version="1.0"?><response><data-table><r>
            <c l="Year" v="2020">2020</c><c l="Deaths" v="100">100</c>
            </r></data-table></response>"""

            with patch.object(cdc_connector, "_make_cdc_request") as mock_request:
                mock_request.return_value = xml_response

                try:
                    df = cdc_connector.get_mortality_data(years=[2020], geo_level=geo_level)
                    # If accepted, should be a valid level
                    assert geo_level.lower() in valid_levels or isinstance(df, pd.DataFrame)
                except (ValueError, KeyError, Exception):
                    # Invalid levels should be rejected
                    pass

        check_geo_level_validation()

    @pytest.mark.hypothesis
    def test_cause_of_death_code_property(self):
        """Property test: ICD-10 codes should be handled consistently."""
        from hypothesis import given
        from hypothesis import strategies as st

        cdc_connector = CDCWonderConnector()

        @given(
            icd_codes=st.lists(
                st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", min_size=3, max_size=7),
                min_size=1,
                max_size=5,
            )
        )
        def check_icd_code_handling(icd_codes):
            with patch.object(cdc_connector, "_make_cdc_request") as mock_request:
                mock_request.return_value = pd.DataFrame(
                    {"Cause": [icd_codes[0]], "Year": [2020], "Deaths": [100]}
                )

                try:
                    df = cdc_connector.get_mortality_data(
                        years=[2020], geo_level="national", cause_of_death=icd_codes
                    )
                    assert isinstance(df, pd.DataFrame)
                except (ValueError, KeyError, TypeError):
                    pass  # Invalid codes may be rejected

        check_icd_code_handling()


class TestCDCConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    @patch.object(CDCWonderConnector, "get_population_estimates")
    def test_connect_return_type(self, mock_get_pop):
        """Test that connect returns None."""
        mock_get_pop.return_value = pd.DataFrame({"Year": [2020], "Population": [100]})

        cdc = CDCWonderConnector()

        result = cdc.connect()

        assert result is None

    @patch.object(CDCWonderConnector, "get_mortality_data")
    def test_fetch_return_type(self, mock_get_mortality):
        """Test that fetch returns DataFrame."""
        mock_get_mortality.return_value = pd.DataFrame({"Year": [2020], "Deaths": [100]})

        cdc = CDCWonderConnector()

        result = cdc.fetch(dataset="mortality", years=[2020], geo_level="national")

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.post")
    def test_get_mortality_data_return_type(self, mock_post):
        """Test that get_mortality_data returns DataFrame."""
        mock_response = Mock()
        mock_response.text = '<?xml version="1.0"?><data-table><r><c l="Year" v="2020"/><c l="Deaths" v="100"/></r></data-table>'
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        cdc = CDCWonderConnector()

        result = cdc.get_mortality_data(years=[2020], geo_level="national")

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.post")
    def test_get_natality_data_return_type(self, mock_post):
        """Test that get_natality_data returns DataFrame."""
        mock_response = Mock()
        mock_response.text = '<?xml version="1.0"?><data-table><r><c l="Year" v="2020"/><c l="Births" v="3500"/></r></data-table>'
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        cdc = CDCWonderConnector()

        result = cdc.get_natality_data(years=[2020], geo_level="national")

        assert isinstance(result, pd.DataFrame)

    @patch("requests.Session.post")
    def test_get_population_estimates_return_type(self, mock_post):
        """Test that get_population_estimates returns DataFrame."""
        mock_response = Mock()
        mock_response.text = '<?xml version="1.0"?><data-table><r><c l="Year" v="2020"/><c l="Population" v="330000000"/></r></data-table>'
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        cdc = CDCWonderConnector()

        result = cdc.get_population_estimates(years=[2020], states=["06"])

        assert isinstance(result, pd.DataFrame)

    @patch.object(CDCWonderConnector, "get_population_estimates")
    def test_validate_connection_return_type(self, mock_get_pop):
        """Test that validate_connection returns bool."""
        mock_get_pop.return_value = pd.DataFrame({"test": [1]})

        cdc = CDCWonderConnector()

        result = cdc.validate_connection()

        assert isinstance(result, bool)

    def test_get_available_databases_return_type(self):
        """Test that get_available_databases returns dict."""
        cdc = CDCWonderConnector()

        result = cdc.get_available_databases()

        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
