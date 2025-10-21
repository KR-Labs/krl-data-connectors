"""
KRL Data Connectors - Education Domain

Education-related data connectors.
"""

from krl_data_connectors.education.college_scorecard_connector import CollegeScorecardConnector
from krl_data_connectors.education.nces_connector import NCESConnector

__all__ = ['CollegeScorecardConnector', 'NCESConnector']
