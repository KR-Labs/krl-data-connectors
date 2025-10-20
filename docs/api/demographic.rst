.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Demographic Data Connectors
============================

Connectors for Census Bureau demographic and business data.

Census ACS Connector
--------------------

American Community Survey connector for demographic and socioeconomic data.

.. autoclass:: krl_data_connectors.CensusConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import CensusConnector

   # Initialize
   census = CensusConnector()

   # Get population data
   population = census.get_data(
       dataset="acs/acs5",
       year=2022,
       variables=["B01003_001E"],  # Total population
       geography="county:*",
       state="06"  # California
   )

County Business Patterns Connector
-----------------------------------

County Business Patterns connector for establishment and employment statistics.

.. autoclass:: krl_data_connectors.CountyBusinessPatternsConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import CountyBusinessPatternsConnector

   # Initialize
   cbp = CountyBusinessPatternsConnector()

   # Get county business data
   businesses = cbp.get_county_data(
       year=2021,
       state="CA",
       county="037",  # Los Angeles
       naics_code="54"  # Professional services
   )

LEHD Connector
--------------

Longitudinal Employer-Household Dynamics connector for job flow and worker characteristics.

.. autoclass:: krl_data_connectors.LEHDConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import LEHDConnector

   # Initialize
   lehd = LEHDConnector()

   # Get origin-destination employment statistics
   od_data = lehd.get_od_data(
       state="ca",
       year=2020,
       job_type="JT00"  # All jobs
   )
