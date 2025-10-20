.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Health Data Connectors
======================

Connectors for healthcare facility and health outcome data.

HRSA Connector
--------------

Health Resources and Services Administration connector for healthcare facility data.

.. autoclass:: krl_data_connectors.HRSAConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import HRSAConnector

   # Initialize
   hrsa = HRSAConnector()

   # Get health center data
   health_centers = hrsa.get_health_centers(
       state="CA",
       service_type="Primary Care"
   )

   # Get medically underserved areas
   mua_data = hrsa.get_underserved_areas(
       designation_type="MUA"  # Medically Underserved Area
   )
