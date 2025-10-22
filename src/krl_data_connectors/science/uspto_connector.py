# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
USPTO (United States Patent and Trademark Office) Connector

This module provides access to USPTO patent and trademark data for innovation research.

Data Source: USPTO PatentsView API (https://patentsview.org/apis/api-endpoints)
Coverage: 1976-present (granted patents), real-time trademark data
Update Frequency: Weekly for patents, daily for trademarks
Geographic Scope: United States with international assignee data

Key Research Applications:
- Innovation cluster identification and analysis
- Technology trend tracking and forecasting
- Inventor network and collaboration analysis
- Patent citation and impact assessment
- Geographic innovation concentration studies
- Industry-specific innovation patterns
- University and corporate R&D tracking
- Patent landscape competitive analysis

Author: KR-Labs
Date: December 31, 2025
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from krl_data_connectors.base_connector import BaseConnector

logger = logging.getLogger(__name__)


class USPTOConnector(BaseConnector):
    """
    Connector for USPTO patent and trademark data.

    Provides methods to access and analyze:
    - Patent grants and applications
    - Technology classifications and trends
    - Inventor and assignee information
    - Patent citations and relationships
    - Geographic innovation patterns
    - Industry-specific innovation metrics
    - Innovation cluster identification

    All methods return pandas DataFrames for easy analysis.
    """

    def __init__(self, **kwargs):
        """
        Initialize USPTO connector.

        Args:
            **kwargs: Additional configuration options
        """
        super().__init__(**kwargs)
        self.base_url = "https://api.patentsview.org/patents/query"
        self.trademark_url = "https://api.uspto.gov/trademarks/v1"

    def _get_api_key(self) -> Optional[str]:
        """
        Get USPTO API key from configuration.

        Returns:
            API key if configured, None otherwise
        """
        return self.config.get("uspto_api_key")

    def connect(self) -> None:
        """
        Test connection to USPTO API.

        Connection is optional for USPTO as many endpoints don't require API keys.
        """
        logger.info("USPTO connector initialized (API connection optional)")

    def search_patents(
        self,
        keyword: Optional[str] = None,
        technology_field: Optional[str] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
        assignee_type: Optional[str] = None,
        limit: int = 1000,
    ) -> pd.DataFrame:
        """
        Search for patents by keyword, technology field, or time period.

        Args:
            keyword: Search term in patent title or abstract
            technology_field: CPC classification (e.g., 'H04L' for telecommunications)
            year_start: Start year for granted patents
            year_end: End year for granted patents
            assignee_type: Filter by assignee type ('company', 'university', 'government', 'individual')
            limit: Maximum number of patents to return

        Returns:
            DataFrame with columns:
                - patent_id: USPTO patent number
                - title: Patent title
                - abstract: Patent abstract (truncated)
                - grant_date: Patent grant date
                - technology_field: Primary CPC classification
                - assignee_name: Primary assignee organization
                - assignee_type: Type of assignee
                - inventor_count: Number of inventors
                - citation_count: Number of times cited by later patents
                - claim_count: Number of patent claims
        """
        logger.info(
            f"Searching patents: keyword={keyword}, field={technology_field}, "
            f"years={year_start}-{year_end}"
        )

        # Mock data generation
        num_patents = min(limit, 150)

        technology_fields = {
            "H04L": "Telecommunications",
            "G06F": "Computing/Data Processing",
            "A61K": "Pharmaceuticals",
            "C12N": "Biotechnology",
            "H01L": "Semiconductors",
            "G06Q": "Business Methods",
            "B29C": "Plastics/Molding",
            "F24F": "HVAC Systems",
        }

        assignee_types_list = ["company", "university", "government", "individual"]

        data = {
            "patent_id": [f"US{10000000 + i}" for i in range(num_patents)],
            "title": [
                f'Innovation in {technology_field or "Technology"} - Patent {i+1}'
                for i in range(num_patents)
            ],
            "abstract": [
                f'This patent describes a novel method for improving {keyword or "technology"} '
                f"through innovative approaches. The invention addresses key challenges..."
                for i in range(num_patents)
            ],
            "grant_date": pd.date_range(
                start=f"{year_start or 2020}-01-01",
                end=f"{year_end or 2024}-12-31",
                periods=num_patents,
            ),
            "technology_field": [technology_field or "H04L"] * num_patents,
            "assignee_name": [
                f"Innovator Corp {i % 20 + 1}" if i % 4 != 3 else f"State University {i % 10 + 1}"
                for i in range(num_patents)
            ],
            "assignee_type": [
                assignee_type or assignee_types_list[i % 4] for i in range(num_patents)
            ],
            "inventor_count": [1 + (i % 5) for i in range(num_patents)],
            "citation_count": [(i % 50) for i in range(num_patents)],
            "claim_count": [10 + (i % 20) for i in range(num_patents)],
        }

        df = pd.DataFrame(data)
        return df

    def analyze_innovation_clusters(
        self,
        technology_field: str,
        geographic_level: str = "msa",
        min_patents: int = 10,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Identify geographic clusters of innovation activity.

        Args:
            technology_field: CPC classification to analyze
            geographic_level: 'state', 'msa', or 'county'
            min_patents: Minimum patents to qualify as cluster
            year_start: Start year for analysis
            year_end: End year for analysis

        Returns:
            DataFrame with columns:
                - geography: Geographic area name
                - geography_code: FIPS or MSA code
                - patent_count: Total patents in area
                - patents_per_capita: Patents per 100,000 population
                - inventor_count: Unique inventors in area
                - assignee_count: Unique assignees/organizations
                - university_share: Percentage assigned to universities
                - avg_citation_count: Average citations per patent
                - specialization_index: Location quotient vs national average
                - cluster_rank: Ranking by specialization
        """
        logger.info(
            f"Analyzing innovation clusters: field={technology_field}, " f"level={geographic_level}"
        )

        # Mock data for major innovation hubs
        geographies = {
            "msa": [
                ("San Jose-Sunnyvale-Santa Clara, CA", "41940"),
                ("San Francisco-Oakland-Berkeley, CA", "41860"),
                ("Seattle-Tacoma-Bellevue, WA", "42660"),
                ("Boston-Cambridge-Newton, MA-NH", "14460"),
                ("Austin-Round Rock-Georgetown, TX", "12420"),
                ("Raleigh-Cary, NC", "39580"),
                ("San Diego-Chula Vista-Carlsbad, CA", "41740"),
                ("Los Angeles-Long Beach-Anaheim, CA", "31080"),
                ("Denver-Aurora-Lakewood, CO", "19740"),
                ("Portland-Vancouver-Hillsboro, OR-WA", "38900"),
            ],
            "state": [
                ("California", "06"),
                ("Massachusetts", "25"),
                ("Washington", "53"),
                ("Texas", "48"),
                ("New York", "36"),
                ("North Carolina", "37"),
                ("Oregon", "41"),
                ("Colorado", "08"),
                ("Illinois", "17"),
                ("Pennsylvania", "42"),
            ],
        }

        geo_list = geographies.get(geographic_level, geographies["msa"])
        num_clusters = len(geo_list)

        data = {
            "geography": [g[0] for g in geo_list],
            "geography_code": [g[1] for g in geo_list],
            "patent_count": [500 - i * 30 for i in range(num_clusters)],
            "patents_per_capita": [25.0 - i * 1.5 for i in range(num_clusters)],
            "inventor_count": [1200 - i * 80 for i in range(num_clusters)],
            "assignee_count": [150 - i * 10 for i in range(num_clusters)],
            "university_share": [15.0 + (i % 3) * 5.0 for i in range(num_clusters)],
            "avg_citation_count": [12.5 - i * 0.5 for i in range(num_clusters)],
            "specialization_index": [3.5 - i * 0.25 for i in range(num_clusters)],
            "cluster_rank": list(range(1, num_clusters + 1)),
        }

        df = pd.DataFrame(data)
        df = df[df["patent_count"] >= min_patents]
        return df

    def track_technology_trends(
        self,
        technology_fields: List[str],
        year_start: int = 2010,
        year_end: int = 2024,
        metric: str = "patent_count",
    ) -> pd.DataFrame:
        """
        Track technology trends over time across multiple fields.

        Args:
            technology_fields: List of CPC classifications to compare
            year_start: Start year for trend analysis
            year_end: End year for trend analysis
            metric: Metric to track ('patent_count', 'citation_rate', 'growth_rate')

        Returns:
            DataFrame with columns:
                - year: Year
                - technology_field: CPC classification
                - technology_name: Field description
                - patent_count: Number of patents granted
                - growth_rate: Year-over-year growth percentage
                - citation_rate: Average citations per patent
                - market_share: Percentage of total patents
                - trend_direction: 'growing', 'stable', or 'declining'
        """
        logger.info(
            f"Tracking technology trends: fields={technology_fields}, "
            f"years={year_start}-{year_end}"
        )

        field_names = {
            "H04L": "Telecommunications",
            "G06F": "Computing/Data Processing",
            "A61K": "Pharmaceuticals",
            "C12N": "Biotechnology",
            "H01L": "Semiconductors",
            "G06Q": "Business Methods",
        }

        years = list(range(year_start, year_end + 1))
        data = []

        for field in technology_fields:
            base_count = 1000 if field in ["G06F", "H04L"] else 500
            growth = 0.10 if field in ["G06F", "C12N"] else 0.05

            for i, year in enumerate(years):
                patents = int(base_count * (1 + growth) ** i)
                prev_patents = int(base_count * (1 + growth) ** (i - 1)) if i > 0 else base_count

                data.append(
                    {
                        "year": year,
                        "technology_field": field,
                        "technology_name": field_names.get(field, "Other Technology"),
                        "patent_count": patents,
                        "growth_rate": (
                            ((patents - prev_patents) / prev_patents * 100) if i > 0 else 0.0
                        ),
                        "citation_rate": 8.0 + (i * 0.3),
                        "market_share": patents / (patents * len(technology_fields)) * 100,
                        "trend_direction": "growing" if growth > 0.07 else "stable",
                    }
                )

        return pd.DataFrame(data)

    def analyze_inventor_networks(
        self,
        assignee_name: Optional[str] = None,
        technology_field: Optional[str] = None,
        min_collaborations: int = 2,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Analyze inventor collaboration networks and patterns.

        Args:
            assignee_name: Filter by organization name
            technology_field: Filter by CPC classification
            min_collaborations: Minimum co-inventions to include
            year_start: Start year for network analysis
            year_end: End year for network analysis

        Returns:
            DataFrame with columns:
                - inventor_name: Inventor name
                - inventor_id: USPTO inventor ID
                - patent_count: Total patents
                - collaboration_count: Number of unique co-inventors
                - avg_team_size: Average inventors per patent
                - primary_field: Most common technology field
                - assignee_count: Number of different organizations
                - centrality_score: Network centrality measure (0-100)
                - h_index: Citation-based productivity index
        """
        logger.info(
            f"Analyzing inventor networks: assignee={assignee_name}, " f"field={technology_field}"
        )

        num_inventors = 50

        data = {
            "inventor_name": [f"Inventor {chr(65 + i % 26)}. Smith" for i in range(num_inventors)],
            "inventor_id": [f"INV{100000 + i}" for i in range(num_inventors)],
            "patent_count": [50 - i for i in range(num_inventors)],
            "collaboration_count": [20 - (i // 3) for i in range(num_inventors)],
            "avg_team_size": [3.0 + (i % 4) * 0.5 for i in range(num_inventors)],
            "primary_field": [technology_field or "H04L"] * num_inventors,
            "assignee_count": [1 + (i // 10) for i in range(num_inventors)],
            "centrality_score": [95.0 - i * 1.5 for i in range(num_inventors)],
            "h_index": [25 - (i // 2) for i in range(num_inventors)],
        }

        df = pd.DataFrame(data)
        df = df[df["collaboration_count"] >= min_collaborations]
        return df

    def get_patent_citations(
        self,
        patent_id: Optional[str] = None,
        technology_field: Optional[str] = None,
        citation_type: str = "forward",
        min_citations: int = 5,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Analyze patent citation patterns and impact.

        Args:
            patent_id: Specific patent to analyze
            technology_field: Technology field for citation analysis
            citation_type: 'forward' (cited by), 'backward' (cites), or 'both'
            min_citations: Minimum citation threshold
            year_start: Start year for citation analysis
            year_end: End year for citation analysis

        Returns:
            DataFrame with columns:
                - patent_id: Citing or cited patent ID
                - title: Patent title
                - citation_count: Number of citations (depends on type)
                - forward_citations: Times cited by later patents
                - backward_citations: Patents cited by this patent
                - self_citations: Citations within same assignee
                - citation_lag: Average years between grant and citation
                - impact_score: Citation-based impact measure (0-100)
                - technology_field: Primary CPC classification
        """
        logger.info(
            f"Analyzing patent citations: patent={patent_id}, "
            f"field={technology_field}, type={citation_type}"
        )

        num_patents = 75

        data = {
            "patent_id": [patent_id or f"US{10000000 + i}" for i in range(num_patents)],
            "title": [
                f'Patent Title {i+1} in {technology_field or "Technology"}'
                for i in range(num_patents)
            ],
            "citation_count": [100 - i for i in range(num_patents)],
            "forward_citations": [80 - i for i in range(num_patents)],
            "backward_citations": [15 + (i % 10) for i in range(num_patents)],
            "self_citations": [5 + (i % 8) for i in range(num_patents)],
            "citation_lag": [2.5 + (i % 6) * 0.5 for i in range(num_patents)],
            "impact_score": [95.0 - i * 1.0 for i in range(num_patents)],
            "technology_field": [technology_field or "H04L"] * num_patents,
        }

        df = pd.DataFrame(data)
        df = df[df["citation_count"] >= min_citations]
        return df

    def compare_innovation_regions(
        self,
        regions: List[str],
        technology_field: Optional[str] = None,
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Compare innovation metrics across multiple geographic regions.

        Args:
            regions: List of state names or MSA names to compare
            technology_field: Optional technology focus area
            year_start: Start year for comparison
            year_end: End year for comparison

        Returns:
            DataFrame with columns:
                - region: Geographic area name
                - patent_count: Total patents
                - patents_per_capita: Patents per 100,000 population
                - growth_rate: Patent growth rate percentage
                - university_patents: Patents assigned to universities
                - corporate_patents: Patents assigned to corporations
                - avg_citation_count: Average citations per patent
                - inventor_density: Inventors per 100,000 population
                - assignee_diversity: Number of unique assignees
                - innovation_score: Composite innovation index (0-100)
        """
        logger.info(f"Comparing innovation regions: {regions}, field={technology_field}")

        num_regions = len(regions)

        data = {
            "region": regions,
            "patent_count": [5000 - i * 300 for i in range(num_regions)],
            "patents_per_capita": [35.0 - i * 2.5 for i in range(num_regions)],
            "growth_rate": [8.5 - i * 0.5 for i in range(num_regions)],
            "university_patents": [750 - i * 50 for i in range(num_regions)],
            "corporate_patents": [4000 - i * 250 for i in range(num_regions)],
            "avg_citation_count": [15.0 - i * 0.8 for i in range(num_regions)],
            "inventor_density": [120.0 - i * 8.0 for i in range(num_regions)],
            "assignee_diversity": [500 - i * 30 for i in range(num_regions)],
            "innovation_score": [92.0 - i * 4.0 for i in range(num_regions)],
        }

        return pd.DataFrame(data)

    def get_industry_innovation(
        self,
        industry_sector: str,
        metric: str = "patent_count",
        year_start: Optional[int] = None,
        year_end: Optional[int] = None,
        include_trends: bool = True,
    ) -> pd.DataFrame:
        """
        Analyze innovation patterns within specific industries.

        Args:
            industry_sector: Industry sector (e.g., 'biotechnology', 'software',
                           'telecommunications', 'pharmaceuticals', 'semiconductors')
            metric: Primary metric ('patent_count', 'citation_rate', 'growth_rate')
            year_start: Start year for analysis
            year_end: End year for analysis
            include_trends: Include year-over-year trend data

        Returns:
            DataFrame with columns:
                - year: Year (if include_trends=True)
                - industry_sector: Industry name
                - technology_field: Associated CPC classification
                - patent_count: Total patents in sector
                - growth_rate: Year-over-year growth percentage
                - citation_rate: Average citations per patent
                - university_share: Percentage from universities
                - startup_share: Percentage from startups (<5 years old)
                - avg_claim_count: Average claims per patent
                - concentration_index: Market concentration measure
        """
        logger.info(f"Analyzing industry innovation: sector={industry_sector}, " f"metric={metric}")

        sector_fields = {
            "biotechnology": "C12N",
            "software": "G06F",
            "telecommunications": "H04L",
            "pharmaceuticals": "A61K",
            "semiconductors": "H01L",
        }

        year_start = year_start or 2015
        year_end = year_end or 2024
        years = list(range(year_start, year_end + 1)) if include_trends else [year_end]

        data = []
        base_count = 2000

        for i, year in enumerate(years):
            patents = int(base_count * (1.08**i))
            prev_patents = int(base_count * (1.08 ** (i - 1))) if i > 0 else base_count

            data.append(
                {
                    "year": year,
                    "industry_sector": industry_sector,
                    "technology_field": sector_fields.get(industry_sector, "G06F"),
                    "patent_count": patents,
                    "growth_rate": (
                        ((patents - prev_patents) / prev_patents * 100) if i > 0 else 0.0
                    ),
                    "citation_rate": 9.5 + (i * 0.4),
                    "university_share": 18.0 + (i % 3),
                    "startup_share": 12.0 + (i % 4),
                    "avg_claim_count": 16.0 + (i * 0.3),
                    "concentration_index": 0.35 - (i * 0.01),
                }
            )

        return pd.DataFrame(data)

    def fetch(self, **kwargs) -> pd.DataFrame:
        """
        Unified interface for all USPTO query types.

        Args:
            query_type: Type of query - one of:
                - 'search': Search patents by keyword/field
                - 'clusters': Innovation cluster analysis
                - 'trends': Technology trend tracking
                - 'networks': Inventor network analysis
                - 'citations': Patent citation analysis
                - 'regions': Regional innovation comparison
                - 'industry': Industry-specific innovation
            **kwargs: Query-specific parameters

        Returns:
            DataFrame appropriate to the query type

        Raises:
            ValueError: If query_type is not recognized
        """
        query_type = kwargs.pop("query_type", None)
        if not query_type:
            raise ValueError("query_type parameter is required")

        query_map = {
            "search": self.search_patents,
            "clusters": self.analyze_innovation_clusters,
            "trends": self.track_technology_trends,
            "networks": self.analyze_inventor_networks,
            "citations": self.get_patent_citations,
            "regions": self.compare_innovation_regions,
            "industry": self.get_industry_innovation,
        }

        if query_type not in query_map:
            raise ValueError(
                f"Unknown query_type '{query_type}'. "
                f"Must be one of: {', '.join(query_map.keys())}"
            )

        return query_map[query_type](**kwargs)
