.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Environmental Data Connectors
==============================

Connectors for environmental quality and justice data.

EPA EJScreen Connector
----------------------

Environmental Protection Agency EJScreen connector for environmental justice screening data.

.. autoclass:: krl_data_connectors.environment.EJScreenConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.environment import EJScreenConnector

   # Initialize
   ejscreen = EJScreenConnector()

   # Get environmental indicators
   env_data = ejscreen.get_indicators(
       geography="blockgroup",
       state="06",
       county="037"
   )

EPA Air Quality Connector
--------------------------

EPA Air Quality System connector for air pollution monitoring data.

.. autoclass:: krl_data_connectors.environment.EPAAirQualityConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.environment import EPAAirQualityConnector

   # Initialize
   aqs = EPAAirQualityConnector()

   # Get PM2.5 data
   pm25_data = aqs.get_monitor_data(
       parameter="PM2.5",
       bdate="20230101",
       edate="20231231",
       state="06",
       county="037"
   )
