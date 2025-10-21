Financial Data Connectors
=========================

This module provides connectors for financial market data, banking statistics, and treasury data.

SEC Connector
-------------

.. automodule:: krl_data_connectors.financial.sec_connector
   :members:
   :undoc-members:
   :show-inheritance:

Securities and Exchange Commission data including company filings, insider trading, and financial statements.

Treasury Connector
------------------

.. automodule:: krl_data_connectors.financial.treasury_connector
   :members:
   :undoc-members:
   :show-inheritance:

U.S. Department of Treasury data including treasury rates, fiscal data, and debt statistics.

FDIC Connector
--------------

.. automodule:: krl_data_connectors.financial.fdic_connector
   :members:
   :undoc-members:
   :show-inheritance:

Federal Deposit Insurance Corporation data including bank financial data and failed bank lists.

**Example Usage:**

.. code-block:: python

    from krl_data_connectors import SECConnector, TreasuryConnector, FDICConnector
    
    # SEC filings
    sec = SECConnector()
    filings = sec.get_company_filings(cik="0000789019", form_type="10-K")
    
    # Treasury rates
    treasury = TreasuryConnector()
    rates = treasury.get_treasury_rates(security_type="Note", maturity="10-Year")
    
    # Bank data
    fdic = FDICConnector()
    banks = fdic.get_institutions(state="NY", active=True)
