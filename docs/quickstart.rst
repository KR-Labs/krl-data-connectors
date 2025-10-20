.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Quick Start Guide
=================

Get started with KRL Data Connectors in minutes.

Your First Data Fetch
---------------------

Let's fetch economic data from FRED:

.. code-block:: python

   from krl_data_connectors import FREDConnector

   # Initialize (API key from environment: FRED_API_KEY)
   fred = FREDConnector()

   # Fetch unemployment rate
   unemployment = fred.get_series(series_id="UNRATE")
   print(unemployment.head())

That's it! You've just fetched real economic data.

Setting Up API Keys
-------------------

Most connectors require API keys. Set them as environment variables:

.. code-block:: bash

   # Linux/Mac
   export FRED_API_KEY="your_key_here"
   export CENSUS_API_KEY="your_key_here"
   export BLS_API_KEY="your_key_here"

   # Windows (PowerShell)
   $env:FRED_API_KEY="your_key_here"

Or use a `.env` file:

.. code-block:: text

   # .env
   FRED_API_KEY=your_key_here
   CENSUS_API_KEY=your_key_here
   BLS_API_KEY=your_key_here

Common Usage Patterns
---------------------

Economic Data
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import FREDConnector, BLSConnector

   # FRED: Get GDP data
   fred = FREDConnector()
   gdp = fred.get_series("GDP", observation_start="2020-01-01")

   # BLS: Get CPI data
   bls = BLSConnector()
   cpi = bls.get_series(["CUUR0000SA0"], start_year=2020, end_year=2023)

Demographic Data
~~~~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import CensusConnector

   # Get population by county
   census = CensusConnector()
   population = census.get_data(
       dataset="acs/acs5",
       year=2022,
       variables=["B01003_001E"],
       geography="county:*",
       state="06"  # California
   )

Housing Data
~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.housing import HUDFMRConnector, ZillowConnector

   # HUD: Fair Market Rents
   hud = HUDFMRConnector()
   fmr = hud.get_fmr_data(year=2024, entity_id="METRO41860M41860")

   # Zillow: Home value index
   zillow = ZillowConnector()
   zhvi = zillow.get_zhvi(geography="Metro", metric="MedianValue_1Bedroom")

Environmental Data
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.environment import EJScreenConnector

   # EPA: Environmental justice indicators
   ejscreen = EJScreenConnector()
   env_data = ejscreen.get_indicators(
       geography="blockgroup",
       state="06",
       county="037"
   )

Working with Results
--------------------

All connectors return pandas DataFrames:

.. code-block:: python

   from krl_data_connectors import FREDConnector

   fred = FREDConnector()
   data = fred.get_series("UNRATE")

   # Standard pandas operations
   print(data.head())
   print(data.describe())
   print(data.info())

   # Save to CSV
   data.to_csv("unemployment.csv")

   # Plot
   data.plot(title="Unemployment Rate")

Caching
-------

All connectors automatically cache responses:

.. code-block:: python

   from krl_data_connectors import FREDConnector

   fred = FREDConnector()

   # First call: fetches from API
   data1 = fred.get_series("GDP")

   # Second call: returns from cache (instant!)
   data2 = fred.get_series("GDP")

Configure cache location:

.. code-block:: python

   fred = FREDConnector(cache_dir="/path/to/cache")

Error Handling
--------------

Handle errors gracefully:

.. code-block:: python

   from krl_data_connectors import FREDConnector
   from krl_data_connectors.exceptions import APIError

   fred = FREDConnector()

   try:
       data = fred.get_series("INVALID_SERIES_ID")
   except APIError as e:
       print(f"API Error: {e}")
       # Handle appropriately

Logging
-------

Enable logging to debug issues:

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)

   from krl_data_connectors import FREDConnector

   fred = FREDConnector()
   data = fred.get_series("GDP")
   # Logs API calls, cache operations, etc.

Next Steps
----------

- Explore the :doc:`api/index` for detailed connector documentation
- See example notebooks in the `examples/` directory
- Read :doc:`../FAQ` for common questions
- Check :doc:`../TROUBLESHOOTING` for debugging help

Getting Help
------------

- **Documentation**: https://krl-data-connectors.readthedocs.io
- **GitHub Issues**: https://github.com/KR-Labs/krl-data-connectors/issues
- **Examples**: https://github.com/KR-Labs/krl-data-connectors/tree/main/examples
