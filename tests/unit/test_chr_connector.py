"""
Tests for County Health Rankings & Roadmaps Connector

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC.
Licensed under the Apache License, Version 2.0.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from krl_data_connectors.health import CountyHealthRankingsConnector


@pytest.fixture
def chr_connector():
    """Create CHR connector instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield CountyHealthRankingsConnector(cache_dir=tmpdir)


@pytest.fixture
def sample_chr_data():
    """Create sample County Health Rankings data for testing."""
    return pd.DataFrame({
        'State': ['RI', 'RI', 'RI', 'RI', 'RI', 'CA', 'CA', 'CA', 'CA', 'TX', 'TX', 'TX'],
        'County': ['Providence', 'Kent', 'Washington', 'Newport', 'Bristol',
                  'Los Angeles', 'San Diego', 'Orange', 'San Francisco',
                  'Harris', 'Dallas', 'Bexar'],
        'FIPS': ['44007', '44003', '44009', '44005', '44001',
                '06037', '06073', '06059', '06075',
                '48201', '48113', '48029'],
        'Health_Outcomes_Rank': [2, 1, 3, 4, 5, 45, 30, 25, 10, 50, 40, 35],
        'Health_Factors_Rank': [1, 2, 3, 4, 5, 40, 28, 20, 8, 48, 38, 32],
        'Length_of_Life_Rank': [2, 1, 3, 4, 5, 48, 32, 28, 12, 52, 42, 38],
        'Quality_of_Life_Rank': [1, 2, 3, 4, 5, 42, 28, 22, 8, 48, 38, 32],
        'Health_Behaviors_Rank': [2, 1, 3, 4, 5, 38, 25, 18, 5, 45, 35, 28],
        'Clinical_Care_Rank': [1, 2, 3, 4, 5, 42, 30, 20, 10, 50, 40, 35],
        'Social_Economic_Rank': [2, 1, 3, 4, 5, 45, 32, 25, 8, 52, 42, 38],
        'Physical_Environment_Rank': [1, 2, 3, 4, 5, 40, 28, 20, 5, 48, 38, 32],
        'Premature_Death': [250, 220, 270, 290, 310, 450, 380, 340, 280, 480, 420, 400],
        'Poor_Physical_Health_Days': [3.2, 3.0, 3.5, 3.8, 4.0, 4.8, 4.2, 3.9, 3.3, 5.2, 4.6, 4.4],
        'Poor_Mental_Health_Days': [3.5, 3.2, 3.8, 4.0, 4.2, 4.9, 4.5, 4.2, 3.6, 5.4, 4.8, 4.6],
        'Low_Birthweight': [6.5, 6.2, 6.8, 7.0, 7.2, 7.8, 7.2, 6.9, 6.4, 8.2, 7.6, 7.4],
        'Adult_Smoking': [15.0, 14.5, 15.5, 16.0, 16.5, 12.5, 11.8, 11.2, 10.5, 18.5, 17.2, 16.8],
        'Adult_Obesity': [28.0, 27.5, 28.5, 29.0, 29.5, 25.5, 24.8, 24.2, 22.5, 32.5, 31.2, 30.8],
        'Physical_Inactivity': [22.0, 21.5, 22.5, 23.0, 23.5, 18.5, 17.8, 17.2, 15.5, 26.5, 25.2, 24.8],
        'Excessive_Drinking': [18.5, 18.0, 19.0, 19.5, 20.0, 16.5, 15.8, 15.2, 14.5, 20.5, 19.2, 18.8],
        'Uninsured': [4.5, 4.2, 4.8, 5.0, 5.2, 8.5, 7.8, 7.2, 5.5, 18.5, 16.2, 15.8],
        'Primary_Care_Physicians': [1250, 890, 450, 380, 320, 8500, 6800, 5500, 4200, 7200, 5800, 4800],
        'Preventable_Hosp_Stays': [3200, 3100, 3400, 3600, 3800, 5200, 4800, 4400, 3500, 5800, 5200, 4900],
        'High_School_Graduation': [88.5, 89.2, 87.8, 87.0, 86.5, 82.5, 84.2, 85.8, 90.5, 78.5, 80.2, 81.8],
        'Some_College': [68.5, 69.2, 67.8, 67.0, 66.5, 62.5, 64.2, 65.8, 72.5, 58.5, 60.2, 61.8],
        'Unemployment': [4.5, 4.2, 4.8, 5.0, 5.2, 8.5, 7.2, 6.5, 4.2, 10.5, 9.2, 8.8],
        'Children_in_Poverty': [18.5, 17.8, 19.2, 19.8, 20.5, 28.5, 25.2, 22.8, 16.5, 32.5, 29.2, 27.8],
        'Income_Inequality': [4.2, 4.0, 4.5, 4.8, 5.0, 5.8, 5.2, 4.9, 4.5, 6.5, 5.9, 5.6],
        'Air_Pollution': [8.2, 8.0, 8.5, 8.8, 9.0, 12.5, 11.2, 10.8, 9.5, 11.8, 11.2, 10.8],
        'Severe_Housing_Problems': [12.5, 12.0, 13.0, 13.5, 14.0, 22.5, 20.2, 18.8, 15.5, 24.5, 22.2, 21.8],
        'Year': [2025] * 12
    })


@pytest.fixture
def sample_trend_data():
    """Create sample multi-year trend data for testing."""
    years = [2020, 2021, 2022, 2023, 2024, 2025]
    counties = ['Providence', 'Kent', 'Washington']
    
    data = []
    for year in years:
        for i, county in enumerate(counties):
            data.append({
                'State': 'RI',
                'County': county,
                'Year': year,
                'Health_Outcomes_Rank': i + 1 + (year - 2020) * 0.1,
                'Premature_Death': 250 + i * 20 + (year - 2020) * 5,
                'Adult_Obesity': 28.0 + i * 0.5 + (year - 2020) * 0.3,
                'Uninsured': 4.5 + i * 0.3 + (year - 2020) * (-0.2)
            })
    
    return pd.DataFrame(data)


# =======================
# Initialization Tests
# =======================

def test_chr_connector_initialization(chr_connector):
    """Test CHR connector initialization."""
    assert chr_connector is not None
    assert hasattr(chr_connector, 'load_rankings_data')
    assert hasattr(chr_connector, 'load_trends_data')


def test_chr_connector_with_custom_cache_dir():
    """Test CHR connector with custom cache directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        connector = CountyHealthRankingsConnector(cache_dir=tmpdir)
        assert connector is not None
        assert Path(tmpdir).exists()


# =======================
# Data Loading Tests
# =======================

def test_load_rankings_data(chr_connector, sample_chr_data, tmp_path):
    """Test loading rankings data from CSV."""
    csv_file = tmp_path / "chr_data.csv"
    sample_chr_data.to_csv(csv_file, index=False)
    
    data = chr_connector.load_rankings_data(str(csv_file))
    assert data is not None
    assert len(data) == len(sample_chr_data)
    assert 'Health_Outcomes_Rank' in data.columns


def test_load_trends_data(chr_connector, sample_trend_data, tmp_path):
    """Test loading trend data from CSV."""
    csv_file = tmp_path / "chr_trends.csv"
    sample_trend_data.to_csv(csv_file, index=False)
    
    data = chr_connector.load_trends_data(str(csv_file))
    assert data is not None
    assert len(data) == len(sample_trend_data)
    assert 'Year' in data.columns


def test_load_data_with_invalid_file(chr_connector):
    """Test loading data with invalid file path."""
    with pytest.raises((FileNotFoundError, ValueError)):
        chr_connector.load_rankings_data('nonexistent_file.csv')


# =======================
# State Filtering Tests
# =======================

def test_get_state_data(chr_connector, sample_chr_data):
    """Test filtering data by state."""
    ri_data = chr_connector.get_state_data(sample_chr_data, 'RI')
    assert len(ri_data) == 5
    assert all(ri_data['State'] == 'RI')


def test_get_state_data_multiple_states(chr_connector, sample_chr_data):
    """Test filtering data by multiple states."""
    states = ['RI', 'CA']
    data = chr_connector.get_state_data(sample_chr_data, states)
    assert len(data) == 9
    assert set(data['State'].unique()) == set(states)


def test_get_state_data_case_insensitive(chr_connector, sample_chr_data):
    """Test state filtering is case-insensitive."""
    ri_data_upper = chr_connector.get_state_data(sample_chr_data, 'RI')
    ri_data_lower = chr_connector.get_state_data(sample_chr_data, 'ri')
    assert len(ri_data_upper) == len(ri_data_lower)


# =======================
# Ranking Retrieval Tests
# =======================

def test_get_health_outcomes(chr_connector, sample_chr_data):
    """Test retrieving health outcomes rankings."""
    outcomes = chr_connector.get_health_outcomes(sample_chr_data)
    assert 'Health_Outcomes_Rank' in outcomes.columns
    assert 'Premature_Death' in outcomes.columns
    assert 'Poor_Physical_Health_Days' in outcomes.columns


def test_get_health_factors(chr_connector, sample_chr_data):
    """Test retrieving health factors rankings."""
    factors = chr_connector.get_health_factors(sample_chr_data)
    assert 'Health_Factors_Rank' in factors.columns
    assert 'Health_Behaviors_Rank' in factors.columns
    assert 'Clinical_Care_Rank' in factors.columns


def test_get_specific_measure(chr_connector, sample_chr_data):
    """Test retrieving specific health measure."""
    obesity = chr_connector.get_measure(sample_chr_data, 'Adult_Obesity')
    assert 'Adult_Obesity' in obesity.columns
    assert len(obesity) == len(sample_chr_data)


def test_get_multiple_measures(chr_connector, sample_chr_data):
    """Test retrieving multiple health measures."""
    measures = ['Adult_Smoking', 'Adult_Obesity', 'Physical_Inactivity']
    data = chr_connector.get_measures(sample_chr_data, measures)
    for measure in measures:
        assert measure in data.columns


# =======================
# Performance Analysis Tests
# =======================

def test_get_top_performers(chr_connector, sample_chr_data):
    """Test identifying top performing counties."""
    top5 = chr_connector.get_top_performers(sample_chr_data, n=5)
    assert len(top5) <= 5
    ranks = top5['Health_Outcomes_Rank'].tolist()
    assert ranks == sorted(ranks)  # Should be in ascending order


def test_get_poor_performers(chr_connector, sample_chr_data):
    """Test identifying poor performing counties."""
    poor = chr_connector.get_poor_performers(sample_chr_data, percentile=75)
    assert len(poor) > 0
    # All ranks should be in the bottom 25% (higher ranks = worse performance)
    threshold = sample_chr_data['Health_Outcomes_Rank'].quantile(0.75)
    assert all(poor['Health_Outcomes_Rank'] >= threshold)


def test_compare_counties(chr_connector, sample_chr_data):
    """Test comparing specific counties."""
    counties = ['Providence', 'Kent', 'Washington']
    comparison = chr_connector.compare_counties(sample_chr_data, counties)
    assert len(comparison) == 3
    assert set(comparison['County']) == set(counties)


# =======================
# Trend Analysis Tests
# =======================

def test_get_county_trends(chr_connector, sample_trend_data):
    """Test retrieving trends for specific county."""
    trends = chr_connector.get_county_trends(sample_trend_data, 'Providence')
    assert len(trends) == 6  # 6 years
    assert all(trends['County'] == 'Providence')
    assert 'Year' in trends.columns


def test_calculate_trend(chr_connector, sample_trend_data):
    """Test calculating trend direction and magnitude."""
    providence_trends = sample_trend_data[sample_trend_data['County'] == 'Providence']
    trend = chr_connector.calculate_trend(providence_trends, 'Adult_Obesity')
    
    assert 'trend_direction' in trend
    assert 'trend_magnitude' in trend
    assert trend['trend_direction'] in ['increasing', 'decreasing', 'stable']


def test_identify_improving_counties(chr_connector, sample_trend_data):
    """Test identifying counties with improving health outcomes."""
    improving = chr_connector.identify_improving_counties(sample_trend_data, 'Premature_Death')
    assert isinstance(improving, list)
    assert len(improving) <= 3  # Max 3 counties in sample


def test_identify_declining_counties(chr_connector, sample_trend_data):
    """Test identifying counties with declining health outcomes."""
    declining = chr_connector.identify_declining_counties(sample_trend_data, 'Uninsured')
    assert isinstance(declining, list)


# =======================
# Statistical Tests
# =======================

def test_calculate_state_average(chr_connector, sample_chr_data):
    """Test calculating state average for a measure."""
    ri_data = sample_chr_data[sample_chr_data['State'] == 'RI']
    avg = chr_connector.calculate_state_average(ri_data, 'Adult_Obesity')
    assert isinstance(avg, (int, float))
    assert avg > 0


def test_calculate_percentile(chr_connector, sample_chr_data):
    """Test calculating percentile ranking for county."""
    percentile = chr_connector.calculate_percentile(
        sample_chr_data, 'Providence', 'Adult_Obesity'
    )
    assert 0 <= percentile <= 100


def test_identify_outliers(chr_connector, sample_chr_data):
    """Test identifying outlier counties for a measure."""
    outliers = chr_connector.identify_outliers(sample_chr_data, 'Premature_Death')
    assert isinstance(outliers, pd.DataFrame)
    assert len(outliers) <= len(sample_chr_data)


# =======================
# Ranking Category Tests
# =======================

def test_get_length_of_life_rankings(chr_connector, sample_chr_data):
    """Test retrieving length of life rankings."""
    rankings = chr_connector.get_length_of_life_rankings(sample_chr_data)
    assert 'Length_of_Life_Rank' in rankings.columns
    assert 'Premature_Death' in rankings.columns


def test_get_quality_of_life_rankings(chr_connector, sample_chr_data):
    """Test retrieving quality of life rankings."""
    rankings = chr_connector.get_quality_of_life_rankings(sample_chr_data)
    assert 'Quality_of_Life_Rank' in rankings.columns
    assert 'Poor_Physical_Health_Days' in rankings.columns
    assert 'Poor_Mental_Health_Days' in rankings.columns


def test_get_health_behaviors_rankings(chr_connector, sample_chr_data):
    """Test retrieving health behaviors rankings."""
    rankings = chr_connector.get_health_behaviors_rankings(sample_chr_data)
    assert 'Health_Behaviors_Rank' in rankings.columns
    assert 'Adult_Smoking' in rankings.columns
    assert 'Adult_Obesity' in rankings.columns


def test_get_clinical_care_rankings(chr_connector, sample_chr_data):
    """Test retrieving clinical care rankings."""
    rankings = chr_connector.get_clinical_care_rankings(sample_chr_data)
    assert 'Clinical_Care_Rank' in rankings.columns
    assert 'Uninsured' in rankings.columns
    assert 'Primary_Care_Physicians' in rankings.columns


def test_get_social_economic_rankings(chr_connector, sample_chr_data):
    """Test retrieving social & economic factors rankings."""
    rankings = chr_connector.get_social_economic_rankings(sample_chr_data)
    assert 'Social_Economic_Rank' in rankings.columns
    assert 'High_School_Graduation' in rankings.columns
    assert 'Unemployment' in rankings.columns


def test_get_physical_environment_rankings(chr_connector, sample_chr_data):
    """Test retrieving physical environment rankings."""
    rankings = chr_connector.get_physical_environment_rankings(sample_chr_data)
    assert 'Physical_Environment_Rank' in rankings.columns
    assert 'Air_Pollution' in rankings.columns
    assert 'Severe_Housing_Problems' in rankings.columns


# =======================
# Validation Tests
# =======================

def test_validate_data_structure(chr_connector, sample_chr_data):
    """Test validating CHR data structure."""
    is_valid = chr_connector.validate_data_structure(sample_chr_data)
    assert is_valid is True


def test_validate_data_structure_missing_columns(chr_connector):
    """Test validation fails with missing required columns."""
    incomplete_data = pd.DataFrame({
        'State': ['RI'],
        'County': ['Providence']
    })
    is_valid = chr_connector.validate_data_structure(incomplete_data)
    assert is_valid is False


def test_validate_ranking_values(chr_connector, sample_chr_data):
    """Test validating ranking values are within expected range."""
    is_valid = chr_connector.validate_ranking_values(sample_chr_data)
    assert is_valid is True


# =======================
# Export Tests
# =======================

def test_export_to_csv(chr_connector, sample_chr_data, tmp_path):
    """Test exporting data to CSV."""
    output_file = tmp_path / "chr_export.csv"
    chr_connector.export_to_csv(sample_chr_data, str(output_file))
    assert output_file.exists()
    
    # Verify can reload
    reloaded = pd.read_csv(output_file)
    assert len(reloaded) == len(sample_chr_data)


def test_generate_summary_report(chr_connector, sample_chr_data, tmp_path):
    """Test generating summary report for state."""
    report_file = tmp_path / "ri_summary.txt"
    chr_connector.generate_summary_report(
        sample_chr_data[sample_chr_data['State'] == 'RI'],
        str(report_file)
    )
    assert report_file.exists()
    assert report_file.stat().st_size > 0


# =======================
# Edge Cases
# =======================

def test_empty_dataframe(chr_connector):
    """Test handling empty dataframe."""
    empty_df = pd.DataFrame()
    result = chr_connector.get_state_data(empty_df, 'RI')
    assert len(result) == 0


def test_single_county(chr_connector):
    """Test analysis with single county."""
    single_county = pd.DataFrame({
        'State': ['RI'],
        'County': ['Providence'],
        'Health_Outcomes_Rank': [1],
        'Health_Factors_Rank': [1]
    })
    result = chr_connector.get_top_performers(single_county, n=1)
    assert len(result) == 1


def test_missing_values_handling(chr_connector, sample_chr_data):
    """Test handling of missing values in data."""
    data_with_na = sample_chr_data.copy()
    data_with_na.loc[0, 'Adult_Obesity'] = None
    
    result = chr_connector.calculate_state_average(data_with_na, 'Adult_Obesity')
    assert result is not None  # Should handle NaN gracefully
