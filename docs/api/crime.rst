.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Crime Data Connectors
=====================

Connectors for crime statistics and public safety data.

FBI UCR Connector
-----------------

FBI Uniform Crime Reporting connector for crime statistics data.

.. autoclass:: krl_data_connectors.crime.FBIUCRConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.crime import FBIUCRConnector

   # Initialize
   fbi = FBIUCRConnector()

   # Get agency crime data
   crime_data = fbi.get_agency_data(
       ori="CA0190000",  # San Francisco PD
       offense="violent-crime",
       since=2020,
       until=2023
   )

   # Get state-level estimates
   state_estimates = fbi.get_state_estimates(
       state="CA",
       variable="violent-crime"
   )
