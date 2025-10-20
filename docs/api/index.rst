.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

API Reference
=============

This section contains the complete API reference for all KRL Data Connectors.

.. toctree::
   :maxdepth: 2
   :caption: Connector Categories

   economic
   demographic
   housing
   health
   environment
   education
   crime
   base

Overview
--------

All connectors inherit from a common ``BaseConnector`` class, providing a consistent
interface across different data sources. Each connector implements data-source-specific
methods while maintaining standardized patterns for:

- API key management
- Caching
- Error handling
- Logging
- Type hints

Quick Navigation
----------------

Economic Data
~~~~~~~~~~~~~
- :doc:`economic` - FRED, BLS, BEA connectors

Demographic Data
~~~~~~~~~~~~~~~~
- :doc:`demographic` - Census ACS, CBP, LEHD connectors

Housing Data
~~~~~~~~~~~~
- :doc:`housing` - HUD, Zillow connectors

Health Data
~~~~~~~~~~~
- :doc:`health` - HRSA connector

Environmental Data
~~~~~~~~~~~~~~~~~~
- :doc:`environment` - EPA EJScreen, Air Quality connectors

Education Data
~~~~~~~~~~~~~~
- :doc:`education` - NCES connector

Crime Data
~~~~~~~~~~
- :doc:`crime` - FBI UCR connector

Base Classes
~~~~~~~~~~~~
- :doc:`base` - Core base connector class and utilities
