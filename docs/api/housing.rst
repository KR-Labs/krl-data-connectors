.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Housing Data Connectors
========================

Connectors for housing market and rental data.

HUD Fair Market Rent Connector
-------------------------------

HUD connector for Fair Market Rent (FMR) data by metropolitan area.

.. autoclass:: krl_data_connectors.housing.HUDFMRConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.housing import HUDFMRConnector

   # Initialize
   hud = HUDFMRConnector()

   # Get Fair Market Rents
   fmr_data = hud.get_fmr_data(
       year=2024,
       entity_id="METRO41860M41860"  # San Francisco
   )

Zillow Connector
----------------

Zillow Research Data connector for housing market indicators and trends.

.. autoclass:: krl_data_connectors.housing.ZillowConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.housing import ZillowConnector

   # Initialize
   zillow = ZillowConnector()

   # Get home values (ZHVI)
   home_values = zillow.get_zhvi(
       geography="Metro",
       metric="MedianValue_1Bedroom"
   )

   # Get rental index (ZRI)
   rental_index = zillow.get_zri(
       geography="Zip",
       metric="MedianRentalPrice_AllHomes"
   )
