.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Base Classes and Utilities
===========================

Core base classes and utility functions used across all connectors.

BaseConnector
-------------

Abstract base class that all connectors inherit from, providing common functionality
for API key management, caching, logging, and error handling.

.. autoclass:: krl_data_connectors.BaseConnector
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__

Key Features
~~~~~~~~~~~~

- **API Key Management**: Automatic resolution from multiple sources (constructor, environment, config files)
- **Smart Caching**: File-based caching with configurable TTL
- **Structured Logging**: Consistent logging across all operations
- **Error Handling**: Graceful handling of API errors with retries
- **Type Safety**: Full type hints for all methods

Configuration
~~~~~~~~~~~~~

All connectors support configuration through:

1. Constructor parameters
2. Environment variables
3. Configuration files (.env, config files)

Example:

.. code-block:: python

   from krl_data_connectors import FREDConnector

   # Method 1: Constructor
   fred = FREDConnector(api_key="your_key")

   # Method 2: Environment variable
   # export FRED_API_KEY="your_key"
   fred = FREDConnector()

   # Method 3: Config file
   # Create .env file with FRED_API_KEY=your_key
   fred = FREDConnector()

Caching
~~~~~~~

All connectors implement intelligent caching:

- Automatically caches API responses
- Configurable cache directory
- Respects TTL (time-to-live)
- Cache key based on request parameters

.. code-block:: python

   from krl_data_connectors import FREDConnector

   # Default cache directory: ./.krl_cache
   fred = FREDConnector()

   # Custom cache directory
   fred = FREDConnector(cache_dir="/path/to/cache")

   # First call: fetches from API
   data1 = fred.get_series("UNRATE")

   # Second call: returns from cache (fast!)
   data2 = fred.get_series("UNRATE")

Logging
~~~~~~~

All connectors use structured logging:

.. code-block:: python

   import logging
   from krl_data_connectors import FREDConnector

   # Enable debug logging
   logging.basicConfig(level=logging.DEBUG)

   fred = FREDConnector()
   data = fred.get_series("UNRATE")
   # Logs: API request, cache hits/misses, errors, etc.

Error Handling
~~~~~~~~~~~~~~

Connectors implement robust error handling:

- Network errors with retries
- API rate limiting
- Invalid parameters
- Missing API keys
- Data validation errors

.. code-block:: python

   from krl_data_connectors import FREDConnector
   from krl_data_connectors.exceptions import APIError

   fred = FREDConnector()

   try:
       data = fred.get_series("INVALID_SERIES")
   except APIError as e:
       print(f"API error: {e}")
       # Handle error appropriately
