# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Science data connectors."""

from .usgs_connector import USGSConnector
from .nsf_connector import NSFConnector
from .uspto_connector import USPTOConnector

__all__ = ['USGSConnector', 'NSFConnector', 'USPTOConnector']