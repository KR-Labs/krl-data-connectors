.. Copyright (c) 2025 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
.. SPDX-License-Identifier: Apache-2.0

Installation
============

This guide covers installation of KRL Data Connectors and its dependencies.

Requirements
------------

- Python 3.9 or higher
- pip (Python package manager)

Basic Installation
------------------

Install from PyPI using pip:

.. code-block:: bash

   pip install krl-data-connectors

This installs the core package with all 52 production-ready connector implementations across 14 domains.

Verify Installation
-------------------

.. code-block:: python

   import krl_data_connectors
   print(krl_data_connectors.__version__)

Development Installation
------------------------

For development work, clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/KR-Labs/krl-data-connectors.git
   cd krl-data-connectors
   pip install -e ".[dev]"

This installs the package with development dependencies including:

- pytest (testing framework)
- black (code formatting)
- isort (import sorting)
- mypy (type checking)
- flake8 (linting)

Dependencies
------------

Core dependencies installed automatically:

- **pandas** (>=1.5.0) - Data manipulation
- **requests** (>=2.28.0) - HTTP requests
- **numpy** (>=1.23.0) - Numerical operations
- **krl-core** (>=0.1.1) - Core KRL utilities

Optional Dependencies
---------------------

Documentation
~~~~~~~~~~~~~

To build documentation locally:

.. code-block:: bash

   pip install krl-data-connectors[docs]

Testing
~~~~~~~

To run the test suite:

.. code-block:: bash

   pip install krl-data-connectors[test]

All Development Tools
~~~~~~~~~~~~~~~~~~~~~

Install everything for development:

.. code-block:: bash

   pip install krl-data-connectors[dev]

Virtual Environments
--------------------

We recommend using virtual environments:

Using venv
~~~~~~~~~~

.. code-block:: bash

   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
   pip install krl-data-connectors

Using conda
~~~~~~~~~~~

.. code-block:: bash

   conda create -n krl-env python=3.11
   conda activate krl-env
   pip install krl-data-connectors

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade krl-data-connectors

Troubleshooting
---------------

Import Errors
~~~~~~~~~~~~~

If you encounter import errors, ensure you're in the correct environment:

.. code-block:: bash

   python -c "import sys; print(sys.executable)"
   pip list | grep krl-data-connectors

Dependency Conflicts
~~~~~~~~~~~~~~~~~~~~

If you have dependency conflicts, try creating a fresh virtual environment:

.. code-block:: bash

   python -m venv fresh-env
   source fresh-env/bin/activate
   pip install krl-data-connectors

Next Steps
----------

After installation, see the :doc:`quickstart` guide to begin using the connectors.

For API keys and configuration, see :doc:`../API_KEY_SETUP` in the main repository.
