.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Economic Data Connectors
========================

Connectors for economic and financial data sources.

FRED Connector
--------------

Federal Reserve Economic Data connector for accessing 800,000+ economic time series.

.. autoclass:: krl_data_connectors.FREDConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import FREDConnector

   # Initialize with API key from environment
   fred = FREDConnector()

   # Get unemployment rate
   unemployment = fred.get_series(
       series_id="UNRATE",
       observation_start="2020-01-01"
   )

   # Search for series
   results = fred.search_series(search_text="GDP")

BLS Connector
-------------

Bureau of Labor Statistics connector for employment, inflation, and wage data.

.. autoclass:: krl_data_connectors.BLSConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import BLSConnector

   # Initialize
   bls = BLSConnector()

   # Get CPI data
   cpi = bls.get_series(
       series_ids=["CUUR0000SA0"],
       start_year=2020,
       end_year=2023
   )

BEA Connector
-------------

Bureau of Economic Analysis connector for GDP, personal income, and international trade data.

.. autoclass:: krl_data_connectors.BEAConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import BEAConnector

   # Initialize
   bea = BEAConnector()

   # Get GDP data
   gdp = bea.get_data(
       dataset_name="NIPA",
       table_name="T10101",
       frequency="Q",
       year="2023"
   )
