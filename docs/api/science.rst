Science & Research Data Connectors
===================================

This module provides connectors for scientific research data, geological surveys, and research funding.

USGS Connector
--------------

.. automodule:: krl_data_connectors.science.usgs_connector
   :members:
   :undoc-members:
   :show-inheritance:

U.S. Geological Survey data including earthquake data, water resources, and land use information.

NSF Connector
-------------

.. automodule:: krl_data_connectors.science.nsf_connector
   :members:
   :undoc-members:
   :show-inheritance:

National Science Foundation research awards, grants, and funding data.

**Example Usage:**

.. code-block:: python

    from krl_data_connectors import USGSConnector, NSFConnector
    
    # USGS earthquake data
    usgs = USGSConnector()
    earthquakes = usgs.get_earthquakes(
        min_magnitude=4.0,
        start_time="2024-01-01",
        end_time="2024-12-31"
    )
    
    # NSF research awards
    nsf = NSFConnector()
    awards = nsf.get_awards(
        keyword="machine learning",
        directorate="Computer and Information Science",
        year=2024
    )
