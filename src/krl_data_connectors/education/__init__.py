# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL Data Connectors - Education Domain

Education-related data connectors.
"""

from krl_data_connectors.education.college_scorecard_connector import CollegeScorecardConnector
from krl_data_connectors.education.ipeds_connector import IPEDSConnector
from krl_data_connectors.education.nces_connector import NCESConnector

__all__ = ["CollegeScorecardConnector", "IPEDSConnector", "NCESConnector"]
