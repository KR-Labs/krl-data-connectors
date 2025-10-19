"""
Unit tests for CDC WONDER connector.

Copyright (c) 2024-2025 KR-Labs Foundation
Licensed under the Apache License, Version 2.0
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
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
            parameters = call_args[0][1]

            # Verify request was made
            assert mock_request.called
            assert not df.empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
