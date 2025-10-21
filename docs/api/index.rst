.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

API Reference
=============

This section contains the complete API reference for all KRL Data Connectors.

.. toctree::
   :maxdepth: 2
   :caption: Connector Categories

   economic
   financial
   demographic
   housing
   health
   environment
   education
   crime
   agricultural
   energy
   science
   social
   veterans
   labor
   transportation
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
- :doc:`economic` - FRED, BLS, BEA, OECD, World Bank connectors

Financial Data
~~~~~~~~~~~~~~
- :doc:`financial` - SEC, Treasury, FDIC connectors

Demographic Data
~~~~~~~~~~~~~~~~
- :doc:`demographic` - Census ACS, CBP, LEHD connectors

Housing Data
~~~~~~~~~~~~
- :doc:`housing` - HUD, Zillow connectors

Health Data
~~~~~~~~~~~
- :doc:`health` - HRSA, CDC WONDER, County Health Rankings, FDA, NIH connectors

Environmental Data
~~~~~~~~~~~~~~~~~~
- :doc:`environment` - EPA EJScreen, Air Quality, Superfund, Water Quality, NOAA Climate connectors

Education Data
~~~~~~~~~~~~~~
- :doc:`education` - NCES, College Scorecard, IPEDS connectors

Crime & Justice Data
~~~~~~~~~~~~~~~~~~~~
- :doc:`crime` - FBI UCR, Bureau of Justice, Victims of Crime connectors

Agricultural Data
~~~~~~~~~~~~~~~~~
- :doc:`agricultural` - USDA Food Atlas, USDA NASS connectors

Energy Data
~~~~~~~~~~~
- :doc:`energy` - EIA connector

Science & Research Data
~~~~~~~~~~~~~~~~~~~~~~~
- :doc:`science` - USGS, NSF connectors

Social Services Data
~~~~~~~~~~~~~~~~~~~~
- :doc:`social` - Social Security Administration, ACF connectors

Veterans Services Data
~~~~~~~~~~~~~~~~~~~~~~
- :doc:`veterans` - Department of Veterans Affairs connector

Labor Safety Data
~~~~~~~~~~~~~~~~~
- :doc:`labor` - OSHA connector

Transportation Data
~~~~~~~~~~~~~~~~~~~
- :doc:`transportation` - FAA connector

Base Classes
~~~~~~~~~~~~
- :doc:`base` - Core base connector class and utilities
