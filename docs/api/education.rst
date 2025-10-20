.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Education Data Connectors
==========================

Connectors for educational institution and outcome data.

NCES Connector
--------------

National Center for Education Statistics connector for K-12 and higher education data.

.. autoclass:: krl_data_connectors.education.NCESConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors.education import NCESConnector

   # Initialize
   nces = NCESConnector()

   # Get school directory information
   schools = nces.get_schools(
       state="CA",
       level="Elementary",
       year=2022
   )

   # Get college scorecard data
   colleges = nces.get_college_scorecard(
       state="CA",
       fields=["school.name", "latest.student.size"]
   )
