# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Tests for EIA (Energy Information Administration) Connector."""

from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from krl_data_connectors.energy.eia_connector import (
    ELECTRICITY_SECTORS,
    ENERGY_SOURCES,
    EIAConnector,
)


@pytest.fixture
def eia_connector():
    """Create EIA connector instance for testing."""
    connector = EIAConnector(api_key="test_api_key")
    connector.session = MagicMock()
    return connector


class TestEIAConnectorInit:
    """Test EIA connector initialization."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = EIAConnector(api_key="test_key")
        assert connector.api_key == "test_key"
        assert connector._eia_api_key == "test_key"
        assert connector.api_url == "https://api.eia.gov/v2"

    def test_init_without_api_key(self):
        """Test initialization without API key."""
        connector = EIAConnector()
        assert connector.api_key is None

    def test_get_api_key(self):
        """Test _get_api_key method."""
        connector = EIAConnector(api_key="test_key")
        assert connector._get_api_key() == "test_key"


class TestEIAConnectorConnection:
    """Test connection methods."""

    def test_connect_success(self, eia_connector):
        """Test successful connection."""
        eia_connector.session = None
        eia_connector.connect()
        assert eia_connector.session is not None


class TestEIAConnectorGetElectricityGeneration:
    """Test get_electricity_generation method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_generation_no_filters(self, mock_fetch, eia_connector):
        """Test getting generation data without filters."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 100000, "stateid": "CA"}]}
        }

        result = eia_connector.get_electricity_generation(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "generation" in result.columns

    @patch.object(EIAConnector, "fetch")
    def test_get_generation_by_state(self, mock_fetch, eia_connector):
        """Test getting generation data filtered by state."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 50000, "stateid": "TX"}]}
        }

        result = eia_connector.get_electricity_generation(state="TX", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_generation_by_energy_source(self, mock_fetch, eia_connector):
        """Test getting generation data filtered by energy source."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 25000, "fueltypeid": "SUN"}]}
        }

        result = eia_connector.get_electricity_generation(energy_source="solar", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_generation_with_date_range(self, mock_fetch, eia_connector):
        """Test getting generation data with date range."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 30000}]}
        }

        result = eia_connector.get_electricity_generation(
            start_date="2024-01-01", end_date="2024-12-31", limit=100
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_generation_error_handling(self, mock_fetch, eia_connector):
        """Test generation error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_electricity_generation(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_generation_empty_response(self, mock_fetch, eia_connector):
        """Test generation with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_electricity_generation(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetElectricityConsumption:
    """Test get_electricity_consumption method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_consumption_no_filters(self, mock_fetch, eia_connector):
        """Test getting consumption data without filters."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "sales": 80000, "stateid": "NY"}]}
        }

        result = eia_connector.get_electricity_consumption(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "sales" in result.columns

    @patch.object(EIAConnector, "fetch")
    def test_get_consumption_by_state(self, mock_fetch, eia_connector):
        """Test getting consumption data filtered by state."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "sales": 60000, "stateid": "CA"}]}
        }

        result = eia_connector.get_electricity_consumption(state="CA", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_consumption_by_sector(self, mock_fetch, eia_connector):
        """Test getting consumption data filtered by sector."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "sales": 40000, "sectorid": "RES"}]}
        }

        result = eia_connector.get_electricity_consumption(sector="residential", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_consumption_error_handling(self, mock_fetch, eia_connector):
        """Test consumption error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_electricity_consumption(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_consumption_empty_response(self, mock_fetch, eia_connector):
        """Test consumption with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_electricity_consumption(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetNaturalGasData:
    """Test get_natural_gas_data method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_gas_production(self, mock_fetch, eia_connector):
        """Test getting natural gas production data."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "value": 90000, "stateid": "TX"}]}
        }

        result = eia_connector.get_natural_gas_data(series_type="production", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_gas_consumption(self, mock_fetch, eia_connector):
        """Test getting natural gas consumption data."""
        mock_fetch.return_value = {"response": {"data": [{"period": "2024-01", "value": 70000}]}}

        result = eia_connector.get_natural_gas_data(series_type="consumption", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_gas_by_state(self, mock_fetch, eia_connector):
        """Test getting natural gas data filtered by state."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "value": 50000, "stateid": "PA"}]}
        }

        result = eia_connector.get_natural_gas_data(state="PA", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_gas_error_handling(self, mock_fetch, eia_connector):
        """Test natural gas error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_natural_gas_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_gas_empty_response(self, mock_fetch, eia_connector):
        """Test natural gas with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_natural_gas_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetPetroleumData:
    """Test get_petroleum_data method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_petroleum_no_filters(self, mock_fetch, eia_connector):
        """Test getting petroleum data without filters."""
        mock_fetch.return_value = {"response": {"data": [{"period": "2024-W01", "value": 400000}]}}

        result = eia_connector.get_petroleum_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_petroleum_by_product(self, mock_fetch, eia_connector):
        """Test getting petroleum data filtered by product."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-W01", "value": 300000, "product": "CRUDE_OIL"}]}
        }

        result = eia_connector.get_petroleum_data(product="crude_oil", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_petroleum_error_handling(self, mock_fetch, eia_connector):
        """Test petroleum error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_petroleum_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_petroleum_empty_response(self, mock_fetch, eia_connector):
        """Test petroleum with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_petroleum_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetCoalData:
    """Test get_coal_data method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_coal_no_filters(self, mock_fetch, eia_connector):
        """Test getting coal data without filters."""
        mock_fetch.return_value = {"response": {"data": [{"period": "2024-01", "value": 50000}]}}

        result = eia_connector.get_coal_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_coal_by_state(self, mock_fetch, eia_connector):
        """Test getting coal data filtered by state."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "value": 40000, "stateid": "WY"}]}
        }

        result = eia_connector.get_coal_data(state="WY", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_coal_error_handling(self, mock_fetch, eia_connector):
        """Test coal error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_coal_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_coal_empty_response(self, mock_fetch, eia_connector):
        """Test coal with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_coal_data(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetRenewableEnergy:
    """Test get_renewable_energy method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_renewable_no_filters(self, mock_fetch, eia_connector):
        """Test getting renewable energy data without filters."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 20000}]}
        }

        result = eia_connector.get_renewable_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_renewable_by_source(self, mock_fetch, eia_connector):
        """Test getting renewable energy filtered by source."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 15000, "fueltypeid": "WND"}]}
        }

        result = eia_connector.get_renewable_energy(energy_source="wind", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_renewable_by_state(self, mock_fetch, eia_connector):
        """Test getting renewable energy filtered by state."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 18000, "stateid": "CA"}]}
        }

        result = eia_connector.get_renewable_energy(state="CA", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_renewable_error_handling(self, mock_fetch, eia_connector):
        """Test renewable energy error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_renewable_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_renewable_empty_response(self, mock_fetch, eia_connector):
        """Test renewable energy with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_renewable_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetNuclearEnergy:
    """Test get_nuclear_energy method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_nuclear_no_filters(self, mock_fetch, eia_connector):
        """Test getting nuclear energy data without filters."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 70000}]}
        }

        result = eia_connector.get_nuclear_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_nuclear_by_state(self, mock_fetch, eia_connector):
        """Test getting nuclear energy filtered by state."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "generation": 65000, "stateid": "IL"}]}
        }

        result = eia_connector.get_nuclear_energy(state="IL", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_nuclear_error_handling(self, mock_fetch, eia_connector):
        """Test nuclear energy error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_nuclear_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_nuclear_empty_response(self, mock_fetch, eia_connector):
        """Test nuclear energy with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_nuclear_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetEnergyPrices:
    """Test get_energy_prices method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_prices_electricity(self, mock_fetch, eia_connector):
        """Test getting electricity price data."""
        mock_fetch.return_value = {"response": {"data": [{"period": "2024-01", "price": 0.13}]}}

        result = eia_connector.get_energy_prices(energy_type="electricity", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_prices_by_state(self, mock_fetch, eia_connector):
        """Test getting energy prices filtered by state."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "price": 0.15, "stateid": "CA"}]}
        }

        result = eia_connector.get_energy_prices(state="CA", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_prices_by_sector(self, mock_fetch, eia_connector):
        """Test getting energy prices filtered by sector."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024-01", "price": 0.12, "sectorid": "COM"}]}
        }

        result = eia_connector.get_energy_prices(sector="commercial", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_prices_error_handling(self, mock_fetch, eia_connector):
        """Test energy prices error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_energy_prices(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_prices_empty_response(self, mock_fetch, eia_connector):
        """Test energy prices with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_energy_prices(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetStateEnergyData:
    """Test get_state_energy_data method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_state_data(self, mock_fetch, eia_connector):
        """Test getting state energy data."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024", "stateid": "TX", "value": 1000000}]}
        }

        result = eia_connector.get_state_energy_data(state="TX", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "stateid" in result.columns

    @patch.object(EIAConnector, "fetch")
    def test_get_state_data_with_date_range(self, mock_fetch, eia_connector):
        """Test getting state energy data with date range."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024", "stateid": "CA", "value": 900000}]}
        }

        result = eia_connector.get_state_energy_data(
            state="CA", start_date="2024-01-01", end_date="2024-12-31", limit=100
        )
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_state_data_error_handling(self, mock_fetch, eia_connector):
        """Test state energy data error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_state_energy_data(state="TX", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_state_data_empty_response(self, mock_fetch, eia_connector):
        """Test state energy data with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_state_energy_data(state="CA", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorGetInternationalEnergy:
    """Test get_international_energy method."""

    @patch.object(EIAConnector, "fetch")
    def test_get_international_no_filters(self, mock_fetch, eia_connector):
        """Test getting international energy data without filters."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024", "countryRegionId": "USA", "value": 100000000}]}
        }

        result = eia_connector.get_international_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_international_by_country(self, mock_fetch, eia_connector):
        """Test getting international energy data filtered by country."""
        mock_fetch.return_value = {
            "response": {"data": [{"period": "2024", "countryRegionId": "CHN", "value": 150000000}]}
        }

        result = eia_connector.get_international_energy(country="CHN", limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    @patch.object(EIAConnector, "fetch")
    def test_get_international_error_handling(self, mock_fetch, eia_connector):
        """Test international energy error handling."""
        mock_fetch.side_effect = Exception("API Error")

        result = eia_connector.get_international_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    @patch.object(EIAConnector, "fetch")
    def test_get_international_empty_response(self, mock_fetch, eia_connector):
        """Test international energy with empty response."""
        mock_fetch.return_value = {}

        result = eia_connector.get_international_energy(limit=100)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


class TestEIAConnectorClose:
    """Test close method."""

    def test_close(self, eia_connector):
        """Test closing connection."""
        mock_session = MagicMock()
        eia_connector.session = mock_session
        eia_connector.close()
        mock_session.close.assert_called_once()
        assert eia_connector.session is None


class TestEIAConnectorTypeContracts:
    """Test type contracts - Phase 4 Layer 8."""

    @patch.object(EIAConnector, "fetch")
    def test_get_electricity_generation_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_electricity_generation returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_electricity_generation()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_electricity_consumption_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_electricity_consumption returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_electricity_consumption()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_natural_gas_data_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_natural_gas_data returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_natural_gas_data()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_petroleum_data_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_petroleum_data returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_petroleum_data()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_coal_data_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_coal_data returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_coal_data()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_renewable_energy_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_renewable_energy returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_renewable_energy()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_nuclear_energy_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_nuclear_energy returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_nuclear_energy()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_energy_prices_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_energy_prices returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_energy_prices()
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_state_energy_data_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_state_energy_data returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_state_energy_data(state="TX")
        assert isinstance(result, pd.DataFrame)

    @patch.object(EIAConnector, "fetch")
    def test_get_international_energy_returns_dataframe(self, mock_fetch, eia_connector):
        """Test that get_international_energy returns DataFrame."""
        mock_fetch.return_value = {"response": {"data": []}}
        result = eia_connector.get_international_energy()
        assert isinstance(result, pd.DataFrame)
