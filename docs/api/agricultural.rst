.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Agricultural Data Connectors
=============================

Connectors for agricultural and food environment data.

USDA Food Environment Atlas Connector
--------------------------------------

USDA Economic Research Service Food Environment Atlas connector for food access,
food insecurity, and local food systems data.

.. autoclass:: krl_data_connectors.agricultural.USDAFoodAtlasConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.agricultural import USDAFoodAtlasConnector

   # Initialize
   connector = USDAFoodAtlasConnector()

   # Get food access data for California counties
   access_data = connector.get_county_data(
       category="access",
       state_fips="06"
   )

   # Get specific indicators
   indicators = connector.get_indicators(
       indicators=["PCT_LACCESS_POP15", "GROCERY14", "FOODINSEC_15_17"],
       state_fips="06"
   )

   # Get data for specific county (Los Angeles)
   la_data = connector.get_county_data(county_fips="06037")

   # List available categories
   categories = connector.list_categories()
   for code, description in categories.items():
       print(f"{code}: {description}")

Data Categories
~~~~~~~~~~~~~~~

The Food Environment Atlas provides data across 8 categories:

- **access**: Food access and store availability
- **assistance**: Food assistance programs (SNAP, WIC, school meals)
- **insecurity**: Food insecurity rates
- **prices**: Food prices and taxes
- **health**: Health and physical activity indicators
- **local**: Local food systems (farmers markets, CSAs, food hubs)
- **restaurants**: Restaurant availability and expenditures
- **socioeconomic**: Socioeconomic characteristics

Common Indicators
~~~~~~~~~~~~~~~~~

**Food Access:**
- ``PCT_LACCESS_POP15`` - % population with low access to stores
- ``PCT_LACCESS_CHILD15`` - % children with low access
- ``PCT_LACCESS_SENIORS15`` - % seniors with low access
- ``GROCERY14`` - Grocery stores per 1,000 population
- ``SUPERC14`` - Supercenters per 1,000 population
- ``CONVS14`` - Convenience stores per 1,000 population

**Food Insecurity:**
- ``FOODINSEC_15_17`` - Food insecurity rate (2015-2017)
- ``VLFOODSEC_15_17`` - Very low food security rate
- ``CH_FOODINSEC_12_14_15_17`` - Change in food insecurity

**Food Assistance:**
- ``PCT_SNAP16`` - % stores authorized for SNAP
- ``SNAP_PART_RATE16`` - SNAP participation rate
- ``PCT_NSLP15`` - % students eligible for free/reduced lunch
- ``PCT_SBP15`` - % students eligible for free/reduced breakfast

**Health:**
- ``PCT_DIABETES_ADULTS13`` - % adults with diabetes
- ``PCT_OBESE_ADULTS13`` - % obese adults
- ``RECFAC14`` - Recreation facilities per 1,000 population

**Local Food:**
- ``FMRKT16`` - Farmers markets per 1,000 population
- ``CSA07`` - Community Supported Agriculture farms
- ``FOODHUB16`` - Food hubs

**Restaurants:**
- ``FFR14`` - Fast food restaurants per 1,000 population
- ``FSR14`` - Full-service restaurants per 1,000 population
- ``PCT_FFRSALES12`` - % food sales from fast food
