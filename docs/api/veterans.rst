Veterans Services Data Connectors
==================================

This module provides connectors for Department of Veterans Affairs data.

VA Connector
------------

.. automodule:: krl_data_connectors.veterans.va_connector
   :members:
   :undoc-members:
   :show-inheritance:

Department of Veterans Affairs data including VA facilities, benefits, healthcare, and disability ratings.

**Key Features:**

- VA facilities and medical centers
- Veterans benefits data (compensation, pension, education)
- Disability rating statistics
- Claims processing and status
- Healthcare utilization and enrollment
- Veteran population statistics
- Suicide prevention programs
- Performance metrics and quality indicators
- VA expenditure tracking

**Example Usage:**

.. code-block:: python

    from krl_data_connectors import VAConnector
    
    # Initialize connector
    va = VAConnector()
    
    # Get VA medical centers in California
    facilities = va.get_facilities(
        state="CA",
        facility_type="medical_center"
    )
    
    # Get disability ratings data
    disability = va.get_disability_ratings(
        state="TX",
        year=2024
    )
    
    # Get healthcare enrollment
    enrollment = va.get_enrollment_data(
        state="FL",
        year=2024,
        priority_group="1"
    )
