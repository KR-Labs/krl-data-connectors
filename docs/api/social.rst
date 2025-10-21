Social Services Data Connectors
================================

This module provides connectors for social security, child welfare, and family assistance programs.

Social Security Administration Connector
-----------------------------------------

.. automodule:: krl_data_connectors.social.ssa_connector
   :members:
   :undoc-members:
   :show-inheritance:

Social Security Administration data including benefits data and retirement statistics.

ACF Connector
-------------

.. automodule:: krl_data_connectors.social.acf_connector
   :members:
   :undoc-members:
   :show-inheritance:

Administration for Children and Families data including child welfare and family assistance programs.

**Example Usage:**

.. code-block:: python

    from krl_data_connectors import SSAConnector, ACFConnector
    
    # Social Security benefits
    ssa = SSAConnector()
    benefits = ssa.get_benefits_data(
        state="CA",
        year=2024,
        benefit_type="retirement"
    )
    
    # Child welfare programs
    acf = ACFConnector()
    programs = acf.get_child_welfare_data(
        state="NY",
        year=2024,
        program="foster_care"
    )
