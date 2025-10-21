Energy Data Connectors
======================

This module provides connectors for energy production, consumption, and pricing data.

EIA Connector
-------------

.. automodule:: krl_data_connectors.energy.eia_connector
   :members:
   :undoc-members:
   :show-inheritance:

The EIAConnector provides access to the Energy Information Administration API,
delivering comprehensive data on energy production, consumption, prices, and forecasts.

**Key Features:**

- Energy production data by source (coal, natural gas, renewables, nuclear)
- Energy consumption statistics by sector (residential, commercial, industrial)
- Electricity generation and pricing data
- Natural gas storage and pipeline data
- Petroleum production and refining statistics
- Renewable energy capacity and generation
- State-level and national energy data
- Historical time series and forecasts

**Data Sources:**

- Energy Information Administration (EIA) Open Data API
- Real-time and historical energy statistics
- Monthly, quarterly, and annual data frequencies

**Example Usage:**

.. code-block:: python

    from krl_data_connectors import EIAConnector
    
    # Initialize connector
    eia = EIAConnector(api_key="your_eia_api_key")
    
    # Get electricity generation by source
    generation = eia.get_electricity_generation(
        state="CA",
        source="solar",
        frequency="monthly",
        start_date="2023-01-01"
    )
    
    print(f"Retrieved {len(generation)} records")
