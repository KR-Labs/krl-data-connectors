"""Tests for County Health Rankings Connector"""
import pytest
import pandas as pd
from unittest.mock import patch
from krl_data_connectors.health import CountyHealthRankingsConnector

@pytest.fixture
def chr_connector():
    with patch.dict('os.environ', {'CHR_API_KEY': 'test_key'}):
        return CountyHealthRankingsConnector()

@pytest.fixture
def sample_chr_data():
    return pd.DataFrame({
        'state': ['RI', 'RI', 'RI', 'CA', 'CA'],
        'county': ['Providence', 'Kent', 'Washington', 'Los Angeles', 'San Diego'],
        'fips': ['44007', '44003', '44009', '06037', '06073'],
        'health_outcomes_rank': [2, 1, 3, 45, 30],
        'health_factors_rank': [1, 2, 3, 40, 28],
        'premature_death': [250, 220, 270, 450, 380],
        'adult_obesity': [28.0, 26.5, 29.0, 32.5, 30.2],
        'uninsured': [4.5, 4.0, 4.8, 8.5, 7.2],
        'year': [2025] * 5
    })

def test_initialization(chr_connector):
    assert chr_connector is not None
    assert hasattr(chr_connector, 'connect')

def test_load_rankings_data(chr_connector, sample_chr_data, tmp_path):
    test_file = tmp_path / "chr_data.csv"
    sample_chr_data.to_csv(test_file, index=False)
    data = chr_connector.load_rankings_data(test_file)
    assert not data.empty
    assert 'health_outcomes_rank' in data.columns

def test_get_state_data(chr_connector, sample_chr_data):
    state_data = chr_connector.get_state_data(sample_chr_data, 'RI')
    assert not state_data.empty
    assert all(state_data['state'] == 'RI')
    assert len(state_data) == 3

def test_get_county_data(chr_connector, sample_chr_data):
    county_data = chr_connector.get_county_data(sample_chr_data, 'Providence', state='RI')
    assert not county_data.empty
    assert county_data['county'].iloc[0] == 'Providence'
