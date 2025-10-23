.. Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

KRL Data Connectors Documentation
==================================

Welcome to the **KRL Data Connectors** documentation!

Production-ready data connectors for socioeconomic and policy data infrastructure.

Overview
--------

KRL Data Connectors provide standardized, robust interfaces for accessing a broad spectrum 
of socioeconomic, demographic, health, and environmental datasets. Built on 73 source modules 
spanning 14 domains, the library delivers 52 production-ready connector implementations validated 
by 2,098 automated tests. Designed for institutional workflows, these connectors ensure 
reproducibility, scalability, and operational reliability.

Features
--------

- **52 Production-Ready Connector Implementations**: Census, FRED, BLS, BEA, EPA, HRSA, HUD, FBI, NCES, Zillow, and more across 14 domains
- **Unified API**: Consistent interface across all 52 data sources built on standardized BaseConnector foundation
- **Smart Caching**: Minimize API calls with intelligent file-based caching with configurable TTL
- **Type-Safe**: Full type hints with mypy strict mode and pydantic validation throughout all 73 modules
- **Production-Ready**: Robust error handling, structured logging, retry logic, and rate limit management
- **10-Layer Testing Architecture**: Comprehensive testing using open-source tools (Unit, Integration, E2E, Performance, SAST, DAST, Mutation, Contract, Pen Testing, Continuous Monitoring)
- **Extensively Tested**: 2,098 automated tests with 78%+ sustained coverage (target: 90%+)
- **Comprehensive Documentation**: 16 quickstart Jupyter notebooks with end-to-end examples

Installation
------------

Install via pip:

.. code-block:: bash

   pip install krl-data-connectors

Quick Start
-----------

Example usage with FRED connector:

.. code-block:: python

   from krl_data_connectors import FREDConnector

   # Initialize connector (API key from environment)
   fred = FREDConnector()

   # Fetch unemployment rate time series
   unemployment = fred.get_series(
       series_id="UNRATE",
       observation_start="2020-01-01",
       observation_end="2023-12-31"
   )

   print(unemployment.head())

For more examples and detailed documentation, visit the 
`GitHub repository <https://github.com/KR-Labs/krl-data-connectors>`_.

Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: Documentation

   installation
   quickstart
   testing
   api/index

Installation
------------

See :doc:`installation` for detailed installation instructions.

Quick Start
-----------

See :doc:`quickstart` for getting started guides.

Testing Guide
-------------

See :doc:`testing` for comprehensive testing documentation, including the 10-layer testing architecture.

API Reference
-------------

Complete API documentation for all connectors: :doc:`api/index`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

License
=======

This project is licensed under the Apache License 2.0.

Copyright © 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
