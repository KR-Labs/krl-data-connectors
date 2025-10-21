.. Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

KRL Data Connectors Documentation
==================================

Welcome to the **KRL Data Connectors** documentation!

Production-ready data connectors for socioeconomic and policy data infrastructure.

Overview
--------

KRL Data Connectors provide standardized, robust interfaces for accessing a broad spectrum 
of socioeconomic, demographic, health, and environmental datasets. Designed for institutional 
workflows, these connectors ensure reproducibility, scalability, and operational reliability.

Features
--------

- **14 Production-Ready Connectors**: Census, FRED, BLS, BEA, EPA, HRSA, HUD, FBI, NCES, Zillow, and more
- **Unified API**: Consistent interface across all data sources
- **Smart Caching**: Minimize API calls with intelligent file-based caching
- **Type-Safe**: Full type hints and validation throughout
- **Production-Ready**: Robust error handling, structured logging, retry logic
- **10-Layer Testing Architecture**: Comprehensive testing using OSS tools (Unit, Integration, E2E, Performance, SAST, DAST, Mutation, Contract, Pen Testing, Continuous Monitoring)
- **Well-Tested**: 408+ tests with 73%+ coverage (target: 90%+)

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
