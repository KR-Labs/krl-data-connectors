.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Health Data Connectors
======================

Connectors for healthcare facility, health outcomes, and medical research data.

HRSA Connector
--------------

Health Resources and Services Administration connector for healthcare facility data.

.. autoclass:: krl_data_connectors.HRSAConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

CDC WONDER Connector
--------------------

Centers for Disease Control and Prevention WONDER database for mortality and disease data.

.. autoclass:: krl_data_connectors.CDCWonderConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

County Health Rankings Connector
---------------------------------

County Health Rankings & Roadmaps connector for county-level health outcomes.

.. autoclass:: krl_data_connectors.CountyHealthRankingsConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

FDA Connector
-------------

Food and Drug Administration connector for drug approvals, recalls, and medical device data.

.. autoclass:: krl_data_connectors.FDAConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

NIH Connector
-------------

National Institutes of Health connector for research projects, grants, and clinical trials.

.. autoclass:: krl_data_connectors.NIHConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

Example Usage
~~~~~~~~~~~~~

.. code-block:: python

   from krl_data_connectors import (
       HRSAConnector,
       CDCWonderConnector,
       CountyHealthRankingsConnector,
       FDAConnector,
       NIHConnector
   )

   # HRSA health centers
   hrsa = HRSAConnector()
   health_centers = hrsa.get_health_centers(
       state="CA",
       service_type="Primary Care"
   )

   # CDC mortality data
   cdc = CDCWonderConnector()
   mortality = cdc.get_mortality_data(
       state="NY",
       year=2024
   )
   
   # County health rankings
   chr = CountyHealthRankingsConnector()
   rankings = chr.get_county_rankings(
       state="TX",
       year=2024
   )
   
   # FDA drug approvals
   fda = FDAConnector()
   approvals = fda.get_drug_approvals(
       year=2024,
       limit=100
   )
   
   # NIH research projects
   nih = NIHConnector()
   projects = nih.get_projects(
       keywords="cancer research",
       fiscal_year=2024
   )
