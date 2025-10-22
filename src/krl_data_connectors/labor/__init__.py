# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Labor Data Connectors.

Connectors for labor and employment data from various government agencies.
"""

from .osha_connector import OSHAConnector

__all__ = ["OSHAConnector"]
