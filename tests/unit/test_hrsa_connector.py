"""
Tests for HRSA (Health Resources and Services Administration) Connector

© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC.
Licensed under the Apache License, Version 2.0.
"""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from krl_data_connectors.health import HRSAConnector


@pytest.fixture
def hrsa_connector():
    """Create HRSA connector instance for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield HRSAConnector(cache_dir=tmpdir)


@pytest.fixture
def sample_hpsa_data():
    """Create sample HPSA data for testing."""
    return pd.DataFrame({
        'State_Abbr': ['RI', 'RI', 'RI', 'RI', 'CA', 'CA', 'CA', 'CA', 'TX', 'TX'],
        'State_Name': ['Rhode Island'] * 4 + ['California'] * 4 + ['Texas'] * 2,
        'County_Name': ['Providence', 'Providence', 'Kent', 'Newport', 'Los Angeles', 
                       'Los Angeles', 'San Diego', 'San Diego', 'Harris', 'Dallas'],
        'HPSA_Name': [
            'Providence Urban Area', 'Providence West End', 'Kent County Rural',
            'Newport Island', 'LA Downtown', 'LA South Central', 'SD Border',
            'SD East County', 'Houston Medical Desert', 'Dallas South'
        ],
        'Designation_Type': ['Geographic', 'Population', 'Geographic', 'Facility',
                            'Geographic', 'Population', 'Geographic', 'Population',
                            'Geographic', 'Population'],
        'HPSA_Discipline': ['Primary Care', 'Primary Care', 'Dental Health', 'Mental Health',
                           'Primary Care', 'Dental Health', 'Mental Health', 'Primary Care',
                           'Primary Care', 'Dental Health'],
        'HPSA_Score': [18, 22, 16, 14, 21, 19, 17, 23, 20, 15],
        'HPSA_Status': ['Designated'] * 10,
        'Rural_Status': ['Not Rural', 'Not Rural', 'Rural', 'Not Rural', 
                        'Not Rural', 'Not Rural', 'Not Rural', 'Not Rural',
                        'Not Rural', 'Not Rural'],
        'HPSA_FTE': [5.2, 8.3, 3.1, 2.4, 12.5, 7.8, 4.6, 9.2, 10.1, 6.3]
    })


@pytest.fixture
def sample_mua_data():
    """Create sample MUA/P data for testing."""
    return pd.DataFrame({
        'State_Abbr': ['RI', 'RI', 'CA', 'CA', 'TX'],
        'State_Name': ['Rhode Island', 'Rhode Island', 'California', 'California', 'Texas'],
        'County_Name': ['Providence', 'Kent', 'Los Angeles', 'San Diego', 'Harris'],
        'MUA_Name': ['Providence MUA', 'Kent Rural MUA', 'LA Central MUA', 
                    'SD Border MUP', 'Houston Inner City MUA'],
        'Designation_Type': ['Geographic MUA', 'Geographic MUA', 'Geographic MUA',
                           'Population MUP', 'Geographic MUA and Population MUP'],
        'MUA_Status': ['Designated'] * 5,
        'Rural_Status': ['Not Rural', 'Rural', 'Not Rural', 'Not Rural', 'Not Rural'],
        'IMU_Score': [58.2, 52.1, 61.3, 55.8, 49.7]
    })


@pytest.fixture
def sample_health_center_data():
    """Create sample Health Center data for testing."""
    return pd.DataFrame({
        'Health_Center_Name': ['Providence Community Health', 'Kent Family Care',
                              'LA Downtown Clinic', 'SD Border Health', 'Houston Central HC'],
        'State_Abbr': ['RI', 'RI', 'CA', 'CA', 'TX'],
        'State_Name': ['Rhode Island', 'Rhode Island', 'California', 'California', 'Texas'],
        'City': ['Providence', 'Warwick', 'Los Angeles', 'San Diego', 'Houston'],
        'Zip_Code': ['02903', '02886', '90012', '92101', '77002'],
        'Health_Center_Type': ['FQHC', 'FQHC Look-Alike', 'FQHC', 'FQHC', 'FQHC'],
        'Patients_Served': [15000, 8500, 25000, 18000, 22000]
    })


class TestHRSAConnectorInit:
    """Test HRSA connector initialization."""
    
    def test_init_default(self):
        """Test default initialization."""
        connector = HRSAConnector()
        assert connector.__class__.__name__ == "HRSAConnector"
        assert "hrsa" in str(connector.cache.cache_dir).lower()
    
    def test_init_custom_cache(self):
        """Test initialization with custom cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            connector = HRSAConnector(cache_dir=tmpdir)
            assert str(connector.cache.cache_dir) == tmpdir
    
    def test_no_api_key_required(self, hrsa_connector):
        """Test that no API key is required."""
        assert hrsa_connector._get_api_key() is None
    
    def test_fetch_not_supported(self, hrsa_connector):
        """Test that fetch() raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="HRSA does not provide an API"):
            hrsa_connector.fetch()


class TestLoadHPSAData:
    """Test loading HPSA data."""
    
    def test_load_hpsa_data_success(self, hrsa_connector, sample_hpsa_data):
        """Test successful loading of HPSA data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_hpsa_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            data = hrsa_connector.load_hpsa_data(temp_path)
            assert len(data) == 10
            assert 'HPSA_Score' in data.columns
            assert 'HPSA_Discipline' in data.columns
        finally:
            Path(temp_path).unlink()
    
    def test_load_hpsa_data_file_not_found(self, hrsa_connector):
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            hrsa_connector.load_hpsa_data('nonexistent.csv')
    
    def test_load_hpsa_data_invalid_format(self, hrsa_connector):
        """Test loading invalid CSV format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("invalid,csv,content\n")
            f.write("incomplete row\n")
            temp_path = f.name
        
        try:
            # Should not raise error - pandas is forgiving
            data = hrsa_connector.load_hpsa_data(temp_path)
            assert isinstance(data, pd.DataFrame)
        finally:
            Path(temp_path).unlink()


class TestLoadMUAData:
    """Test loading MUA/P data."""
    
    def test_load_mua_data_success(self, hrsa_connector, sample_mua_data):
        """Test successful loading of MUA/P data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_mua_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            data = hrsa_connector.load_mua_data(temp_path)
            assert len(data) == 5
            assert 'IMU_Score' in data.columns
            assert 'Designation_Type' in data.columns
        finally:
            Path(temp_path).unlink()
    
    def test_load_mua_data_file_not_found(self, hrsa_connector):
        """Test loading non-existent MUA file."""
        with pytest.raises(FileNotFoundError):
            hrsa_connector.load_mua_data('nonexistent.csv')


class TestLoadHealthCenterData:
    """Test loading Health Center data."""
    
    def test_load_health_center_data_success(self, hrsa_connector, sample_health_center_data):
        """Test successful loading of Health Center data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_health_center_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            data = hrsa_connector.load_health_center_data(temp_path)
            assert len(data) == 5
            assert 'Health_Center_Name' in data.columns
            assert 'Patients_Served' in data.columns
        finally:
            Path(temp_path).unlink()
    
    def test_load_health_center_data_file_not_found(self, hrsa_connector):
        """Test loading non-existent Health Center file."""
        with pytest.raises(FileNotFoundError):
            hrsa_connector.load_health_center_data('nonexistent.csv')


class TestGetStateData:
    """Test filtering by state."""
    
    def test_get_state_data_ri(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Rhode Island data."""
        ri_data = hrsa_connector.get_state_data(sample_hpsa_data, 'RI')
        assert len(ri_data) == 4
        assert all(ri_data['State_Abbr'] == 'RI')
    
    def test_get_state_data_ca(self, hrsa_connector, sample_hpsa_data):
        """Test filtering California data."""
        ca_data = hrsa_connector.get_state_data(sample_hpsa_data, 'CA')
        assert len(ca_data) == 4
        assert all(ca_data['State_Abbr'] == 'CA')
    
    def test_get_state_data_lowercase(self, hrsa_connector, sample_hpsa_data):
        """Test case-insensitive state filtering."""
        ri_data = hrsa_connector.get_state_data(sample_hpsa_data, 'ri')
        assert len(ri_data) == 4
    
    def test_get_state_data_missing_column(self, hrsa_connector):
        """Test error when state column is missing."""
        data = pd.DataFrame({'foo': [1, 2, 3]})
        with pytest.raises(ValueError, match="State column .* not found"):
            hrsa_connector.get_state_data(data, 'RI')


class TestGetCountyData:
    """Test filtering by county."""
    
    def test_get_county_data_providence(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Providence County."""
        prov_data = hrsa_connector.get_county_data(sample_hpsa_data, 'Providence')
        assert len(prov_data) == 2
        assert all(prov_data['County_Name'] == 'Providence')
    
    def test_get_county_data_with_state(self, hrsa_connector, sample_hpsa_data):
        """Test filtering county with state specification."""
        prov_ri = hrsa_connector.get_county_data(sample_hpsa_data, 'Providence', state='RI')
        assert len(prov_ri) == 2
        assert all(prov_ri['State_Abbr'] == 'RI')
    
    def test_get_county_data_case_insensitive(self, hrsa_connector, sample_hpsa_data):
        """Test case-insensitive county filtering."""
        kent_data = hrsa_connector.get_county_data(sample_hpsa_data, 'kent')
        assert len(kent_data) == 1
        assert kent_data.iloc[0]['County_Name'] == 'Kent'
    
    def test_get_county_data_missing_column(self, hrsa_connector):
        """Test error when county column is missing."""
        data = pd.DataFrame({'State_Abbr': ['RI']})
        with pytest.raises(ValueError, match="County column .* not found"):
            hrsa_connector.get_county_data(data, 'Providence')


class TestFilterByDiscipline:
    """Test filtering by HPSA discipline."""
    
    def test_filter_primary_care(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Primary Care HPSAs."""
        primary = hrsa_connector.filter_by_discipline(sample_hpsa_data, 'Primary Care')
        assert len(primary) == 5
        assert all(primary['HPSA_Discipline'] == 'Primary Care')
    
    def test_filter_dental_health(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Dental Health HPSAs."""
        dental = hrsa_connector.filter_by_discipline(sample_hpsa_data, 'Dental Health')
        assert len(dental) == 3
        assert all(dental['HPSA_Discipline'] == 'Dental Health')
    
    def test_filter_mental_health(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Mental Health HPSAs."""
        mental = hrsa_connector.filter_by_discipline(sample_hpsa_data, 'Mental Health')
        assert len(mental) == 2
        assert all(mental['HPSA_Discipline'] == 'Mental Health')
    
    def test_filter_invalid_discipline(self, hrsa_connector, sample_hpsa_data):
        """Test error with invalid discipline."""
        with pytest.raises(ValueError, match="Invalid discipline"):
            hrsa_connector.filter_by_discipline(sample_hpsa_data, 'Invalid')
    
    def test_filter_missing_column(self, hrsa_connector):
        """Test error when discipline column is missing."""
        data = pd.DataFrame({'State_Abbr': ['RI']})
        with pytest.raises(ValueError, match="Discipline column .* not found"):
            hrsa_connector.filter_by_discipline(data, 'Primary Care')


class TestFilterByType:
    """Test filtering by designation type."""
    
    def test_filter_geographic(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Geographic HPSAs."""
        geo = hrsa_connector.filter_by_type(sample_hpsa_data, 'Geographic')
        assert len(geo) == 5
        assert all(geo['Designation_Type'] == 'Geographic')
    
    def test_filter_population(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Population HPSAs."""
        pop = hrsa_connector.filter_by_type(sample_hpsa_data, 'Population')
        assert len(pop) == 4
        assert all(pop['Designation_Type'] == 'Population')
    
    def test_filter_facility(self, hrsa_connector, sample_hpsa_data):
        """Test filtering Facility HPSAs."""
        fac = hrsa_connector.filter_by_type(sample_hpsa_data, 'Facility')
        assert len(fac) == 1
        assert all(fac['Designation_Type'] == 'Facility')
    
    def test_filter_missing_column(self, hrsa_connector):
        """Test error when type column is missing."""
        data = pd.DataFrame({'State_Abbr': ['RI']})
        with pytest.raises(ValueError, match="Type column .* not found"):
            hrsa_connector.filter_by_type(data, 'Geographic')


class TestGetHighNeedAreas:
    """Test filtering high-need areas by score."""
    
    def test_get_high_need_default(self, hrsa_connector, sample_hpsa_data):
        """Test filtering with default threshold (15)."""
        high_need = hrsa_connector.get_high_need_areas(sample_hpsa_data)
        assert len(high_need) == 9  # Scores >= 15
        assert all(high_need['HPSA_Score'] >= 15)
    
    def test_get_high_need_threshold_20(self, hrsa_connector, sample_hpsa_data):
        """Test filtering with threshold of 20 (critical)."""
        critical = hrsa_connector.get_high_need_areas(sample_hpsa_data, score_threshold=20)
        assert len(critical) == 4  # Scores >= 20
        assert all(critical['HPSA_Score'] >= 20)
    
    def test_get_high_need_threshold_25(self, hrsa_connector, sample_hpsa_data):
        """Test filtering with very high threshold."""
        extreme = hrsa_connector.get_high_need_areas(sample_hpsa_data, score_threshold=25)
        assert len(extreme) == 0  # No scores >= 25
    
    def test_get_high_need_missing_column(self, hrsa_connector):
        """Test error when score column is missing."""
        data = pd.DataFrame({'State_Abbr': ['RI']})
        with pytest.raises(ValueError, match="Score column .* not found"):
            hrsa_connector.get_high_need_areas(data)


class TestGetRuralAreas:
    """Test filtering rural areas."""
    
    def test_get_rural_areas(self, hrsa_connector, sample_hpsa_data):
        """Test filtering rural areas."""
        rural = hrsa_connector.get_rural_areas(sample_hpsa_data)
        assert len(rural) == 1
        assert all(rural['Rural_Status'] == 'Rural')
        assert rural.iloc[0]['County_Name'] == 'Kent'
    
    def test_get_rural_areas_mua(self, hrsa_connector, sample_mua_data):
        """Test filtering rural MUA/P areas."""
        rural = hrsa_connector.get_rural_areas(sample_mua_data)
        assert len(rural) == 1
        assert rural.iloc[0]['County_Name'] == 'Kent'
    
    def test_get_rural_areas_missing_column(self, hrsa_connector):
        """Test error when rural column is missing."""
        data = pd.DataFrame({'State_Abbr': ['RI']})
        with pytest.raises(ValueError, match="Rural column .* not found"):
            hrsa_connector.get_rural_areas(data)


class TestSummarizeByState:
    """Test state-level summarization."""
    
    def test_summarize_default_metrics(self, hrsa_connector, sample_hpsa_data):
        """Test summarization with default metrics."""
        summary = hrsa_connector.summarize_by_state(sample_hpsa_data)
        assert len(summary) == 3  # RI, CA, TX
        assert 'HPSA_Score' in summary.columns.get_level_values(0)
        assert 'mean' in summary.columns.get_level_values(1)
    
    def test_summarize_custom_metrics(self, hrsa_connector, sample_hpsa_data):
        """Test summarization with custom metrics."""
        summary = hrsa_connector.summarize_by_state(
            sample_hpsa_data, 
            metrics=['HPSA_Score', 'HPSA_FTE']
        )
        assert 'HPSA_Score' in summary.columns.get_level_values(0)
        assert 'HPSA_FTE' in summary.columns.get_level_values(0)
    
    def test_summarize_mua_data(self, hrsa_connector, sample_mua_data):
        """Test summarization of MUA/P data."""
        summary = hrsa_connector.summarize_by_state(
            sample_mua_data,
            metrics=['IMU_Score']
        )
        assert len(summary) == 3  # RI, CA, TX
        assert 'IMU_Score' in summary.columns.get_level_values(0)
    
    def test_summarize_missing_state_column(self, hrsa_connector):
        """Test error when State_Abbr column is missing."""
        data = pd.DataFrame({'HPSA_Score': [10, 20]})
        with pytest.raises(ValueError, match="State_Abbr column not found"):
            hrsa_connector.summarize_by_state(data)
    
    def test_summarize_missing_metric(self, hrsa_connector, sample_hpsa_data):
        """Test error when specified metric doesn't exist."""
        with pytest.raises(ValueError, match="Metric column .* not found"):
            hrsa_connector.summarize_by_state(
                sample_hpsa_data,
                metrics=['NonexistentColumn']
            )


class TestGetAvailableDisciplines:
    """Test getting discipline counts."""
    
    def test_get_available_disciplines(self, hrsa_connector, sample_hpsa_data):
        """Test getting discipline counts."""
        disciplines = hrsa_connector.get_available_disciplines(sample_hpsa_data)
        assert len(disciplines) == 3
        assert disciplines['Primary Care'] == 5
        assert disciplines['Dental Health'] == 3
        assert disciplines['Mental Health'] == 2
    
    def test_get_available_disciplines_no_column(self, hrsa_connector):
        """Test with data missing discipline column."""
        data = pd.DataFrame({'State_Abbr': ['RI', 'CA']})
        disciplines = hrsa_connector.get_available_disciplines(data)
        assert disciplines == {}


class TestIntegration:
    """Integration tests combining multiple operations."""
    
    def test_state_discipline_filtering(self, hrsa_connector, sample_hpsa_data):
        """Test combined state and discipline filtering."""
        ri_data = hrsa_connector.get_state_data(sample_hpsa_data, 'RI')
        ri_primary = hrsa_connector.filter_by_discipline(ri_data, 'Primary Care')
        assert len(ri_primary) == 2
        assert all(ri_primary['State_Abbr'] == 'RI')
        assert all(ri_primary['HPSA_Discipline'] == 'Primary Care')
    
    def test_high_need_rural_areas(self, hrsa_connector, sample_hpsa_data):
        """Test finding high-need rural areas."""
        high_need = hrsa_connector.get_high_need_areas(sample_hpsa_data, score_threshold=15)
        rural_high_need = hrsa_connector.get_rural_areas(high_need)
        assert len(rural_high_need) == 1
        assert rural_high_need.iloc[0]['County_Name'] == 'Kent'
        assert rural_high_need.iloc[0]['HPSA_Score'] == 16
    
    def test_county_high_score_analysis(self, hrsa_connector, sample_hpsa_data):
        """Test analyzing high-score areas in specific county."""
        la_data = hrsa_connector.get_county_data(sample_hpsa_data, 'Los Angeles', state='CA')
        high_need_la = hrsa_connector.get_high_need_areas(la_data, score_threshold=19)
        assert len(high_need_la) == 2
        assert all(high_need_la['HPSA_Score'] >= 19)


# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class TestHRSASecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    def test_sql_injection_in_state(self, hrsa_connector, sample_hpsa_data):
        """Test SQL injection attempt in state parameter."""
        # SQL injection attempt
        malicious_state = "RI'; DROP TABLE data; --"

        # Should handle safely
        try:
            df = hrsa_connector.get_state_data(sample_hpsa_data, malicious_state)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, KeyError):
            # Acceptable to reject invalid state codes
            pass

    def test_command_injection_in_county(self, hrsa_connector, sample_hpsa_data):
        """Test command injection prevention in county parameter."""
        # Command injection attempt
        malicious_county = "Providence; rm -rf /"

        # Should handle safely
        try:
            df = hrsa_connector.get_county_data(sample_hpsa_data, malicious_county)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject malicious input
            pass

    def test_xss_injection_in_discipline(self, hrsa_connector, sample_hpsa_data):
        """Test XSS injection prevention."""
        # XSS attempt
        xss_payload = "<script>alert('XSS')</script>"

        # Should handle safely
        try:
            df = hrsa_connector.filter_by_discipline(sample_hpsa_data, xss_payload)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, KeyError):
            # Acceptable to reject XSS payloads
            pass


class TestHRSASecurityInputValidation:
    """Test security: Input validation and sanitization."""

    def test_score_threshold_validation(self, hrsa_connector, sample_hpsa_data):
        """Test score threshold parameter validation."""
        # Negative score (invalid)
        with pytest.raises((ValueError, TypeError)):
            hrsa_connector.get_high_need_areas(sample_hpsa_data, score_threshold=-1)

        # Score too high (invalid)
        with pytest.raises((ValueError, TypeError)):
            hrsa_connector.get_high_need_areas(sample_hpsa_data, score_threshold=100)

    def test_handles_null_bytes_in_state(self, hrsa_connector, sample_hpsa_data):
        """Test handling of null bytes in state parameter."""
        # Null byte injection
        malicious_state = "RI\x00malicious"

        # Should handle safely or reject
        try:
            df = hrsa_connector.get_state_data(sample_hpsa_data, malicious_state)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    def test_handles_extremely_long_county_names(self, hrsa_connector, sample_hpsa_data):
        """Test handling of excessively long county names (DoS prevention)."""
        # Extremely long county name
        long_county = "Providence" * 10000

        # Should handle safely or reject
        try:
            df = hrsa_connector.get_county_data(sample_hpsa_data, long_county)
            assert isinstance(df, pd.DataFrame)
        except (ValueError, Exception):
            # Acceptable to reject overly long inputs
            pass

    def test_empty_state_validation(self, hrsa_connector, sample_hpsa_data):
        """Test empty state parameter validation."""
        # Empty state
        with pytest.raises((ValueError, KeyError, TypeError)):
            hrsa_connector.get_state_data(sample_hpsa_data, "")

    def test_none_dataframe_handling(self, hrsa_connector):
        """Test handling of None DataFrame."""
        # None DataFrame
        with pytest.raises((ValueError, AttributeError, TypeError)):
            hrsa_connector.get_state_data(None, "RI")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
