.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Crime Data Connectors
=====================

Connectors for crime statistics, criminal justice data, and victim services.

FBI UCR Connector
-----------------

FBI Uniform Crime Reporting connector for crime statistics data.

.. autoclass:: krl_data_connectors.crime.FBIUCRConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Bureau of Justice Connector
---------------------------

Bureau of Justice Statistics connector for criminal justice data.

.. autoclass:: krl_data_connectors.crime.BureauOfJusticeConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Victims of Crime Connector
--------------------------

Office for Victims of Crime connector for crime victimization data.

.. autoclass:: krl_data_connectors.crime.VictimsOfCrimeConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.crime import (
       FBIUCRConnector,
       BureauOfJusticeConnector,
       VictimsOfCrimeConnector
   )

   # FBI crime statistics
   fbi = FBIUCRConnector()
   crime_data = fbi.get_agency_data(
       ori="CA0190000",  # San Francisco PD
       offense="violent-crime",
       since=2020,
       until=2023
   )

   # Bureau of Justice statistics
   bjs = BureauOfJusticeConnector()
   justice_stats = bjs.get_corrections_data(
       year=2024,
       facility_type="prison"
   )
   
   # Victims of crime data
   ovc = VictimsOfCrimeConnector()
   victim_data = ovc.get_victimization_data(
       state="NY",
       year=2024,
       crime_type="violent"
   )
