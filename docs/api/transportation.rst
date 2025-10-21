Transportation Data Connectors
===============================

This module provides connectors for aviation and transportation data.

FAA Connector
-------------

.. automodule:: krl_data_connectors.transportation.faa_connector
   :members:
   :undoc-members:
   :show-inheritance:

Federal Aviation Administration data including airport information, flight delays, and aircraft registry.

**Key Features:**

- Airport facility data
- Flight delay statistics
- Aircraft registration database
- Airmen certification data
- Airport operations and traffic
- Aviation safety incidents
- Runway and taxiway information

**Example Usage:**

.. code-block:: python

    from krl_data_connectors import FAAConnector
    
    # Initialize connector
    faa = FAAConnector()
    
    # Get airport information
    airports = faa.get_airports(
        state="CA",
        airport_type="large_hub"
    )
    
    # Get flight delay statistics
    delays = faa.get_delays(
        airport="LAX",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    
    # Get aircraft registrations
    aircraft = faa.get_aircraft(
        manufacturer="Boeing",
        model="737"
    )
