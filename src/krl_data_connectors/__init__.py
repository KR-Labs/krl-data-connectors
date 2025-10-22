# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""
KRL Data Connectors - Production-ready data connectors for 51 major data sources.

This package provides unified interfaces for accessing data from major government,
research, and public data providers including FRED, Census Bureau, BLS, World Bank,
OECD, NIH, NSF, USPTO, CDC BRFSS, and 42 other authoritative sources.

Complete coverage across domains:
- Economic & Financial Data (10 connectors) - NEW Gap Analysis (Week 10)
- Demographic & Labor Data (3 connectors)
- Health & Wellbeing Data (7 connectors) - NEW Gap Analysis (Week 12) ✨ FINAL
- Environmental & Climate Data (5 connectors)
- Education Data (3 connectors)
- Housing & Urban Data (2 connectors)
- Housing Equity & Displacement (1 connector) - NEW Gap Analysis
- Agricultural Data (2 connectors)
- Crime & Justice Data (3 connectors)
- Energy Data (1 connector)
- Science & Research Data (3 connectors) - NEW Gap Analysis (Week 11)
- Transportation & Commuting Data (2 connectors)
- Labor Safety Data (1 connector)
- Social Services & Nonprofit Data (3 connectors)
- Veterans Services Data (1 connector)
- Financial Regulation & Inclusion Data (4 connectors)
- Technology & Digital Access (1 connector) - NEW Gap Analysis
- Political & Civic Engagement (2 connectors) - NEW Gap Analysis (Week 9)
"""

from .__version__ import __author__, __license__, __version__
from .agricultural import USDAFoodAtlasConnector, USDANASSConnector
from .base_connector import BaseConnector
from .bea_connector import BEAConnector
from .bls_connector import BLSConnector
from .cbp_connector import CountyBusinessPatternsConnector
from .census_connector import CensusConnector
from .crime import BureauOfJusticeConnector, FBIUCRConnector, VictimsOfCrimeConnector
from .mobility import OpportunityInsightsConnector
from .economic import CensusBDSConnector, OECDConnector, WorldBankConnector
from .education import CollegeScorecardConnector, IPEDSConnector, NCESConnector
from .energy import EIAConnector
from .environment import (
    EJScreenConnector,
    EPAAirQualityConnector,
    NOAAClimateConnector,
    SuperfundConnector,
    WaterQualityConnector,
)
from .financial import FDICConnector, HMDAConnector, SECConnector, TreasuryConnector
from .fred_connector import FREDConnector
from .health import (
    BRFSSConnector,
    CDCWonderConnector,
    CountyHealthRankingsConnector,
    FDAConnector,
    HRSAConnector,
    NIHConnector,
    SAMHSAConnector,
)
from .housing import HUDFMRConnector, ZillowConnector, EvictionLabConnector
from .labor import OSHAConnector
from .lehd_connector import LEHDConnector
from .political import FECConnector, MITElectionLabConnector
from .science import NSFConnector, USGSConnector, USPTOConnector
from .social import ACFConnector, IRS990Connector, SSAConnector
from .technology import FCCBroadbandConnector
from .transportation import FAAConnector, NHTSConnector
from .utils.config import find_config_file, load_api_key_from_config
from .veterans import VAConnector

__all__ = [
    # Base
    "BaseConnector",
    # Mobility & Social Capital (1) - NEW Phase 4
    "OpportunityInsightsConnector",
    # Economic & Financial (10) - NEW Gap Analysis (Week 10)
    "FREDConnector",
    "BLSConnector",
    "BEAConnector",
    "CensusBDSConnector",  # NEW Gap Analysis (Week 10)
    "OECDConnector",
    "WorldBankConnector",
    "SECConnector",
    "TreasuryConnector",
    "FDICConnector",
    "HMDAConnector",  # NEW Gap Analysis (Week 6)
    # Demographic & Labor (3)
    "CensusConnector",
    "CountyBusinessPatternsConnector",
    "LEHDConnector",
    # Health (7) - NEW Gap Analysis (Week 12) ✨ FINAL
    "HRSAConnector",
    "CDCWonderConnector",
    "CountyHealthRankingsConnector",
    "FDAConnector",
    "NIHConnector",
    "SAMHSAConnector",  # NEW Gap Analysis (Week 7)
    "BRFSSConnector",  # NEW Gap Analysis (Week 12) ✨ FINAL STRATEGIC IMPLEMENTATION
    # Environmental (5)
    "EJScreenConnector",
    "EPAAirQualityConnector",
    "SuperfundConnector",
    "WaterQualityConnector",
    "NOAAClimateConnector",
    # Education (3)
    "NCESConnector",
    "CollegeScorecardConnector",
    "IPEDSConnector",
    # Housing (2)
    "HUDFMRConnector",
    "ZillowConnector",
    # Housing Equity (1) - NEW Gap Analysis
    "EvictionLabConnector",
    # Agricultural (2)
    "USDAFoodAtlasConnector",
    "USDANASSConnector",
    # Crime & Justice (3)
    "FBIUCRConnector",
    "BureauOfJusticeConnector",
    "VictimsOfCrimeConnector",
    # Energy (1)
    "EIAConnector",
    # Science (3) - NEW Gap Analysis (Week 11)
    "USGSConnector",
    "NSFConnector",
    "USPTOConnector",  # NEW Gap Analysis (Week 11)
    # Transportation & Commuting (2)
    "FAAConnector",
    "NHTSConnector",  # NEW Gap Analysis
    # Labor Safety (1)
    "OSHAConnector",
    # Social Services & Nonprofit Data (3)
    "SSAConnector",
    "ACFConnector",
    "IRS990Connector",  # NEW Gap Analysis (Week 8)
    # Veterans (1)
    "VAConnector",
    # Technology & Digital Access (1) - NEW Gap Analysis
    "FCCBroadbandConnector",
    # Political & Civic Engagement (2) - NEW Gap Analysis (Week 9)
    "FECConnector",  # NEW Gap Analysis (Week 9)
    "MITElectionLabConnector",
    # Utilities
    "find_config_file",
    "load_api_key_from_config",
]
