# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Tests for USGS Connector."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from krl_data_connectors.science.usgs_connector import (
    MAGNITUDE_TYPES,
    SITE_TYPES,
    WATER_PARAMETERS,
    USGSConnector,
)


@pytest.fixture
def usgs_connector():
    """Create USGS connector instance for testing."""
    connector = USGSConnector()
    connector.session = MagicMock()
    return connector


class TestUSGSConnectorInit:
    """Test USGS connector initialization."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = USGSConnector()
        assert connector.water_url == "https://waterservices.usgs.gov/nwis"
        assert connector.earthquake_url == "https://earthquake.usgs.gov/fdsnws/event/1"
        assert connector._usgs_api_key is None

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = USGSConnector(api_key="test-key")
        assert connector._usgs_api_key == "test-key"

    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = USGSConnector(timeout=60)
        assert connector.timeout == 60


class TestUSGSConnectorConnection:
    """Test USGS connector connection methods."""

    def test_connect_success(self, usgs_connector):
        """Test successful connection."""
        usgs_connector.session = None
        with patch.object(usgs_connector, "_init_session", return_value=MagicMock()):
            usgs_connector.connect()
            assert usgs_connector.session is not None


class TestUSGSConnectorGetStreamflowData:
    """Test get_streamflow_data method."""

    def test_get_streamflow_data_no_filters(self, usgs_connector):
        """Test getting streamflow data without filters."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "values": [
                            {
                                "value": [
                                    {
                                        "dateTime": "2024-01-01T00:00:00",
                                        "value": "1500",
                                        "qualifiers": ["A"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_streamflow_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "site_no" in result.columns
            assert result.iloc[0]["site_no"] == "01646500"

    def test_get_streamflow_data_with_site(self, usgs_connector):
        """Test getting streamflow data for specific site."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "values": [
                            {
                                "value": [
                                    {
                                        "dateTime": "2024-01-01T00:00:00",
                                        "value": "1500",
                                        "qualifiers": ["A"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_streamflow_data(site_no="01646500")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_streamflow_data_with_state(self, usgs_connector):
        """Test getting streamflow data by state."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "values": [
                            {
                                "value": [
                                    {
                                        "dateTime": "2024-01-01T00:00:00",
                                        "value": "1500",
                                        "qualifiers": ["A"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_streamflow_data(state_cd="MD")

            assert isinstance(result, pd.DataFrame)

    def test_get_streamflow_data_with_date_range(self, usgs_connector):
        """Test getting streamflow data with date range."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "values": [
                            {
                                "value": [
                                    {
                                        "dateTime": "2024-01-15T00:00:00",
                                        "value": "1500",
                                        "qualifiers": ["A"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_streamflow_data(
                start_date="2024-01-01", end_date="2024-01-31"
            )

            assert isinstance(result, pd.DataFrame)

    def test_get_streamflow_data_error(self, usgs_connector):
        """Test error handling in get_streamflow_data."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_streamflow_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_streamflow_data_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_streamflow_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetWaterQualityData:
    """Test get_water_quality_data method."""

    def test_get_water_quality_data_no_filters(self, usgs_connector):
        """Test getting water quality data without filters."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "variable": {"variableName": "Temperature", "unit": {"unitCode": "deg C"}},
                        "values": [
                            {"value": [{"dateTime": "2024-01-01T00:00:00", "value": "15.5"}]}
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_water_quality_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "parameter" in result.columns

    def test_get_water_quality_data_with_parameter(self, usgs_connector):
        """Test getting water quality data for specific parameter."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "variable": {"variableName": "pH", "unit": {"unitCode": "standard units"}},
                        "values": [
                            {"value": [{"dateTime": "2024-01-01T00:00:00", "value": "7.2"}]}
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_water_quality_data(parameter="ph")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_water_quality_data_with_site_and_state(self, usgs_connector):
        """Test getting water quality data with site and state."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "variable": {"variableName": "Temperature", "unit": {"unitCode": "deg C"}},
                        "values": [
                            {"value": [{"dateTime": "2024-01-01T00:00:00", "value": "15.5"}]}
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_water_quality_data(site_no="01646500", state_cd="MD")

            assert isinstance(result, pd.DataFrame)

    def test_get_water_quality_data_error(self, usgs_connector):
        """Test error handling in get_water_quality_data."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_water_quality_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_water_quality_data_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_water_quality_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetGroundwaterLevels:
    """Test get_groundwater_levels method."""

    def test_get_groundwater_levels_no_filters(self, usgs_connector):
        """Test getting groundwater data without filters."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "123456789"}],
                            "siteName": "Test Well",
                        },
                        "values": [
                            {
                                "value": [
                                    {
                                        "dateTime": "2024-01-01T00:00:00",
                                        "value": "50.5",
                                        "qualifiers": ["A"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_groundwater_levels()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "depth_to_water" in result.columns

    def test_get_groundwater_levels_with_site(self, usgs_connector):
        """Test getting groundwater data for specific site."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "123456789"}],
                            "siteName": "Test Well",
                        },
                        "values": [
                            {
                                "value": [
                                    {
                                        "dateTime": "2024-01-01T00:00:00",
                                        "value": "50.5",
                                        "qualifiers": ["A"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_groundwater_levels(site_no="123456789")

            assert isinstance(result, pd.DataFrame)

    def test_get_groundwater_levels_with_date_range(self, usgs_connector):
        """Test getting groundwater data with date range."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "123456789"}],
                            "siteName": "Test Well",
                        },
                        "values": [
                            {
                                "value": [
                                    {
                                        "dateTime": "2024-01-15T00:00:00",
                                        "value": "50.5",
                                        "qualifiers": ["A"],
                                    }
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_groundwater_levels(
                start_date="2024-01-01", end_date="2024-01-31"
            )

            assert isinstance(result, pd.DataFrame)

    def test_get_groundwater_levels_error(self, usgs_connector):
        """Test error handling in get_groundwater_levels."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_groundwater_levels()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_groundwater_levels_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_groundwater_levels()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetSiteInformation:
    """Test get_site_information method."""

    def test_get_site_information_no_filters(self, usgs_connector):
        """Test getting site information without filters."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                            "siteType": [{"value": "ST"}],
                            "geoLocation": {
                                "geogLocation": {"latitude": 38.9072, "longitude": -77.0369}
                            },
                            "siteProperty": [{"value": "District of Columbia"}],
                        }
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_site_information()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "site_name" in result.columns

    def test_get_site_information_with_site_type(self, usgs_connector):
        """Test getting site information by site type."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "123456789"}],
                            "siteName": "Test Well",
                            "siteType": [{"value": "GW"}],
                            "geoLocation": {
                                "geogLocation": {"latitude": 38.9072, "longitude": -77.0369}
                            },
                            "siteProperty": [{"value": "Test County"}],
                        }
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_site_information(site_type="well")

            assert isinstance(result, pd.DataFrame)

    def test_get_site_information_with_state(self, usgs_connector):
        """Test getting site information by state."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                            "siteType": [{"value": "ST"}],
                            "geoLocation": {
                                "geogLocation": {"latitude": 38.9072, "longitude": -77.0369}
                            },
                            "siteProperty": [{"value": "District of Columbia"}],
                        }
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_site_information(state_cd="DC")

            assert isinstance(result, pd.DataFrame)

    def test_get_site_information_error(self, usgs_connector):
        """Test error handling in get_site_information."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_site_information()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_site_information_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_site_information()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetEarthquakes:
    """Test get_earthquakes method."""

    def test_get_earthquakes_no_filters(self, usgs_connector):
        """Test getting earthquake data without filters."""
        mock_response = {
            "features": [
                {
                    "id": "eq123",
                    "properties": {
                        "mag": 5.5,
                        "place": "California",
                        "time": 1704067200000,
                        "updated": 1704067300000,
                        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/eq123",
                        "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/eq123.geojson",
                        "felt": 100,
                        "tsunami": 0,
                        "alert": "green",
                        "status": "reviewed",
                        "type": "earthquake",
                    },
                    "geometry": {"coordinates": [-120.5, 36.2, 10.0]},
                }
            ]
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_earthquakes()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "magnitude" in result.columns
            assert result.iloc[0]["magnitude"] == 5.5

    def test_get_earthquakes_with_magnitude(self, usgs_connector):
        """Test getting earthquakes with magnitude filter."""
        mock_response = {
            "features": [
                {
                    "id": "eq123",
                    "properties": {
                        "mag": 6.0,
                        "place": "California",
                        "time": 1704067200000,
                        "updated": 1704067300000,
                        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/eq123",
                        "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/eq123.geojson",
                        "felt": 200,
                        "tsunami": 0,
                        "alert": "yellow",
                        "status": "reviewed",
                        "type": "earthquake",
                    },
                    "geometry": {"coordinates": [-120.5, 36.2, 10.0]},
                }
            ]
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_earthquakes(min_magnitude=5.0)

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1

    def test_get_earthquakes_with_location(self, usgs_connector):
        """Test getting earthquakes with location filter."""
        mock_response = {
            "features": [
                {
                    "id": "eq123",
                    "properties": {
                        "mag": 5.5,
                        "place": "Near Location",
                        "time": 1704067200000,
                        "updated": 1704067300000,
                        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/eq123",
                        "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/eq123.geojson",
                        "felt": 100,
                        "tsunami": 0,
                        "alert": "green",
                        "status": "reviewed",
                        "type": "earthquake",
                    },
                    "geometry": {"coordinates": [-120.5, 36.2, 10.0]},
                }
            ]
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_earthquakes(
                latitude=36.0, longitude=-120.0, max_radius_km=100
            )

            assert isinstance(result, pd.DataFrame)

    def test_get_earthquakes_with_time_range(self, usgs_connector):
        """Test getting earthquakes with time range."""
        mock_response = {
            "features": [
                {
                    "id": "eq123",
                    "properties": {
                        "mag": 5.5,
                        "place": "California",
                        "time": 1704067200000,
                        "updated": 1704067300000,
                        "url": "https://earthquake.usgs.gov/earthquakes/eventpage/eq123",
                        "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/eq123.geojson",
                        "felt": 100,
                        "tsunami": 0,
                        "alert": "green",
                        "status": "reviewed",
                        "type": "earthquake",
                    },
                    "geometry": {"coordinates": [-120.5, 36.2, 10.0]},
                }
            ]
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_earthquakes(start_time="2024-01-01", end_time="2024-01-31")

            assert isinstance(result, pd.DataFrame)

    def test_get_earthquakes_error(self, usgs_connector):
        """Test error handling in get_earthquakes."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_earthquakes()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_earthquakes_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_earthquakes()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetDailyStreamflow:
    """Test get_daily_streamflow method."""

    def test_get_daily_streamflow_no_filters(self, usgs_connector):
        """Test getting daily streamflow data."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "values": [
                            {
                                "value": [
                                    {"dateTime": "2024-01-01", "value": "1500", "qualifiers": ["A"]}
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_daily_streamflow()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert "mean_discharge" in result.columns

    def test_get_daily_streamflow_with_site(self, usgs_connector):
        """Test getting daily streamflow for specific site."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                            "siteName": "Potomac River",
                        },
                        "values": [
                            {
                                "value": [
                                    {"dateTime": "2024-01-01", "value": "1500", "qualifiers": ["A"]}
                                ]
                            }
                        ],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_daily_streamflow(site_no="01646500")

            assert isinstance(result, pd.DataFrame)

    def test_get_daily_streamflow_error(self, usgs_connector):
        """Test error handling in get_daily_streamflow."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_daily_streamflow()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_daily_streamflow_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_daily_streamflow()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetPeakStreamflow:
    """Test get_peak_streamflow method."""

    def test_get_peak_streamflow_no_filters(self, usgs_connector):
        """Test getting peak streamflow data."""
        mock_response = {"text": "Peak streamflow data..."}

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_peak_streamflow()

            assert isinstance(result, pd.DataFrame)

    def test_get_peak_streamflow_error(self, usgs_connector):
        """Test error handling in get_peak_streamflow."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_peak_streamflow()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_peak_streamflow_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_peak_streamflow()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetWaterUseData:
    """Test get_water_use_data method."""

    def test_get_water_use_data_no_filters(self, usgs_connector):
        """Test getting water use data."""
        mock_response = {"state": "CA", "year": 2015, "category": "public", "withdrawal": 1234.5}

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_water_use_data()

            assert isinstance(result, pd.DataFrame)

    def test_get_water_use_data_error(self, usgs_connector):
        """Test error handling in get_water_use_data."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_water_use_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_water_use_data_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_water_use_data()

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorGetStatisticalData:
    """Test get_statistical_data method."""

    def test_get_statistical_data(self, usgs_connector):
        """Test getting statistical data."""
        mock_response = {
            "value": {
                "timeSeries": [
                    {
                        "sourceInfo": {
                            "siteCode": [{"value": "01646500"}],
                        },
                        "values": [{"value": [{"dateTime": "2024-01", "value": "1500"}]}],
                    }
                ]
            }
        }

        with patch.object(usgs_connector, "fetch", return_value=mock_response):
            result = usgs_connector.get_statistical_data(site_no="01646500")

            assert isinstance(result, pd.DataFrame)

    def test_get_statistical_data_error(self, usgs_connector):
        """Test error handling in get_statistical_data."""
        with patch.object(usgs_connector, "fetch", side_effect=Exception("API error")):
            result = usgs_connector.get_statistical_data(site_no="01646500")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0

    def test_get_statistical_data_empty_response(self, usgs_connector):
        """Test handling of empty response."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_statistical_data(site_no="01646500")

            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestUSGSConnectorClose:
    """Test close method."""

    def test_close(self, usgs_connector):
        """Test closing connection."""
        mock_session = MagicMock()
        usgs_connector.session = mock_session
        usgs_connector.close()
        mock_session.close.assert_called_once()
        assert usgs_connector.session is None


class TestUSGSConnectorTypeContracts:
    """Test type contracts and data validation (Phase 4 Layer 8)."""

    def test_get_streamflow_data_returns_dataframe(self, usgs_connector):
        """Test that get_streamflow_data returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_streamflow_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_water_quality_data_returns_dataframe(self, usgs_connector):
        """Test that get_water_quality_data returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_water_quality_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_groundwater_levels_returns_dataframe(self, usgs_connector):
        """Test that get_groundwater_levels returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_groundwater_levels()
            assert isinstance(result, pd.DataFrame)

    def test_get_site_information_returns_dataframe(self, usgs_connector):
        """Test that get_site_information returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_site_information()
            assert isinstance(result, pd.DataFrame)

    def test_get_earthquakes_returns_dataframe(self, usgs_connector):
        """Test that get_earthquakes returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_earthquakes()
            assert isinstance(result, pd.DataFrame)

    def test_get_daily_streamflow_returns_dataframe(self, usgs_connector):
        """Test that get_daily_streamflow returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_daily_streamflow()
            assert isinstance(result, pd.DataFrame)

    def test_get_peak_streamflow_returns_dataframe(self, usgs_connector):
        """Test that get_peak_streamflow returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_peak_streamflow()
            assert isinstance(result, pd.DataFrame)

    def test_get_water_use_data_returns_dataframe(self, usgs_connector):
        """Test that get_water_use_data returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_water_use_data()
            assert isinstance(result, pd.DataFrame)

    def test_get_statistical_data_returns_dataframe(self, usgs_connector):
        """Test that get_statistical_data returns DataFrame."""
        with patch.object(usgs_connector, "fetch", return_value={}):
            result = usgs_connector.get_statistical_data(site_no="01646500")
            assert isinstance(result, pd.DataFrame)

    def test_constants_defined(self):
        """Test that required constants are defined."""
        assert isinstance(WATER_PARAMETERS, dict)
        assert isinstance(MAGNITUDE_TYPES, dict)
        assert isinstance(SITE_TYPES, dict)
        assert "discharge" in WATER_PARAMETERS
        assert "temperature" in WATER_PARAMETERS
