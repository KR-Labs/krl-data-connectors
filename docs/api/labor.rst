Labor Safety Data Connectors
=============================

This module provides connectors for occupational safety and health data.

OSHA Connector
--------------

.. automodule:: krl_data_connectors.labor.osha_connector
   :members:
   :undoc-members:
   :show-inheritance:

Occupational Safety and Health Administration data including workplace inspections, violations, and citations.

**Key Features:**

- Workplace safety inspections
- OSHA violations and citations
- Injury and illness statistics
- Establishment-level safety data
- Industry-specific hazard data
- Enforcement case tracking
- Fatality and catastrophe investigations

**Example Usage:**

.. code-block:: python

    from krl_data_connectors import OSHAConnector
    
    # Initialize connector
    osha = OSHAConnector()
    
    # Get recent inspections
    inspections = osha.get_inspections(
        state="CA",
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    
    # Get violations by industry
    violations = osha.get_violations(
        naics_code="23",  # Construction
        year=2024,
        severity="serious"
    )
