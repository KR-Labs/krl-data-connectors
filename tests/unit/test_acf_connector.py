# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""Tests for ACF Connector."""

import pytest
import pandas as pd
from unittest.mock import MagicMock, patch

from krl_data_connectors.social.acf_connector import (
    ACFConnector,
    PROGRAM_TYPES,
    DATA_CATEGORIES,
    WELFARE_INDICATORS,
)


@pytest.fixture
def acf_connector():
    """Create ACF connector instance for testing."""
    connector = ACFConnector()
    connector.session = MagicMock()
    return connector


class TestACFConnectorInit:
    """Test ACF connector initialization."""
    
    def test_init_default(self):
        """Test initialization with default parameters."""
        connector = ACFConnector()
        assert connector.api_url == "https://www.acf.hhs.gov/api"
        assert connector._acf_api_key is None
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        connector = ACFConnector(api_key='test-key')
        assert connector._acf_api_key == 'test-key'
    
    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        connector = ACFConnector(timeout=60)
        assert connector.timeout == 60


class TestACFConnectorConnection:
    """Test ACF connector connection methods."""
    
    def test_connect_success(self, acf_connector):
        """Test successful connection."""
        acf_connector.session = None
        with patch.object(acf_connector, '_init_session', return_value=MagicMock()):
            acf_connector.connect()
            assert acf_connector.session is not None


class TestACFConnectorGetTANFData:
    """Test get_tanf_data method."""
    
    def test_get_tanf_data_no_filters(self, acf_connector):
        """Test getting TANF data without filters."""
        mock_response = [{
            'state': 'CA',
            'families': 500000,
            'recipients': 1200000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_tanf_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
            assert 'families' in result.columns
    
    def test_get_tanf_data_with_state(self, acf_connector):
        """Test getting TANF data by state."""
        mock_response = [{
            'state': 'TX',
            'families': 400000,
            'recipients': 950000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_tanf_data(state='TX')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_tanf_data_with_year(self, acf_connector):
        """Test getting TANF data by year."""
        mock_response = [{
            'state': 'CA',
            'families': 480000,
            'recipients': 1150000,
            'year': 2023
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_tanf_data(year=2023)
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_tanf_data_with_category(self, acf_connector):
        """Test getting TANF data by category."""
        mock_response = [{
            'state': 'CA',
            'category': 'caseload',
            'families': 500000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_tanf_data(category='caseload')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_tanf_data_with_year_and_quarter(self, acf_connector):
        """Test getting TANF data with year and fiscal quarter."""
        mock_response = [{
            'state': 'CA',
            'families': 125000,
            'year': 2024,
            'fiscal_quarter': 2
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_tanf_data(year=2024, fiscal_quarter=2)
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_tanf_data_dict_response(self, acf_connector):
        """Test handling dict response with data key."""
        mock_response = {
            'data': [{
                'state': 'CA',
                'families': 500000,
                'year': 2024
            }]
        }
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_tanf_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_tanf_data_error(self, acf_connector):
        """Test error handling in get_tanf_data."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_tanf_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_tanf_data_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_tanf_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetHeadStartData:
    """Test get_head_start_data method."""
    
    def test_get_head_start_data_no_filters(self, acf_connector):
        """Test getting Head Start data without filters."""
        mock_response = [{
            'state': 'CA',
            'enrollment': 100000,
            'programs': 500,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_head_start_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_head_start_data_with_program_type(self, acf_connector):
        """Test getting Head Start data by program type."""
        mock_response = [{
            'state': 'CA',
            'program_type': 'early_head_start',
            'enrollment': 25000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_head_start_data(program_type='early_head_start')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_head_start_data_with_state_and_year(self, acf_connector):
        """Test getting Head Start data with state and year."""
        mock_response = [{
            'state': 'NY',
            'enrollment': 80000,
            'year': 2023
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_head_start_data(state='NY', year=2023)
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_head_start_data_error(self, acf_connector):
        """Test error handling in get_head_start_data."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_head_start_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_head_start_data_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_head_start_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetChildSupportData:
    """Test get_child_support_data method."""
    
    def test_get_child_support_data_no_filters(self, acf_connector):
        """Test getting child support data without filters."""
        mock_response = [{
            'state': 'CA',
            'collections': 5000000000,
            'cases': 1000000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_child_support_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_child_support_data_with_metric(self, acf_connector):
        """Test getting child support data by metric."""
        mock_response = [{
            'state': 'CA',
            'metric': 'collections',
            'value': 5000000000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_child_support_data(metric='collections')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_child_support_data_error(self, acf_connector):
        """Test error handling in get_child_support_data."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_child_support_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_child_support_data_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_child_support_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetFosterCareData:
    """Test get_foster_care_data method."""
    
    def test_get_foster_care_data_no_filters(self, acf_connector):
        """Test getting foster care data without filters."""
        mock_response = [{
            'state': 'CA',
            'in_care': 60000,
            'entries': 15000,
            'exits': 14000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_foster_care_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_foster_care_data_with_data_type(self, acf_connector):
        """Test getting foster care data by data type."""
        mock_response = [{
            'state': 'CA',
            'data_type': 'entries',
            'count': 15000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_foster_care_data(data_type='entries')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_foster_care_data_error(self, acf_connector):
        """Test error handling in get_foster_care_data."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_foster_care_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_foster_care_data_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_foster_care_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetChildWelfareData:
    """Test get_child_welfare_data method."""
    
    def test_get_child_welfare_data_no_filters(self, acf_connector):
        """Test getting child welfare data without filters."""
        mock_response = [{
            'state': 'CA',
            'investigations': 100000,
            'maltreatment_cases': 50000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_child_welfare_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_child_welfare_data_with_indicator(self, acf_connector):
        """Test getting child welfare data by indicator."""
        mock_response = [{
            'state': 'CA',
            'indicator': 'maltreatment',
            'count': 50000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_child_welfare_data(indicator='maltreatment')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_child_welfare_data_error(self, acf_connector):
        """Test error handling in get_child_welfare_data."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_child_welfare_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_child_welfare_data_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_child_welfare_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetAdoptionData:
    """Test get_adoption_data method."""
    
    def test_get_adoption_data_no_filters(self, acf_connector):
        """Test getting adoption data without filters."""
        mock_response = [{
            'state': 'CA',
            'adoptions': 5000,
            'waiting_children': 10000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_adoption_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_adoption_data_with_adoption_type(self, acf_connector):
        """Test getting adoption data by adoption type."""
        mock_response = [{
            'state': 'CA',
            'adoption_type': 'foster',
            'adoptions': 4000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_adoption_data(adoption_type='foster')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_adoption_data_error(self, acf_connector):
        """Test error handling in get_adoption_data."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_adoption_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_adoption_data_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_adoption_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetCCDFData:
    """Test get_ccdf_data method."""
    
    def test_get_ccdf_data_no_filters(self, acf_connector):
        """Test getting CCDF data without filters."""
        mock_response = [{
            'state': 'CA',
            'children_served': 500000,
            'expenditures': 2000000000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_ccdf_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_ccdf_data_with_data_category(self, acf_connector):
        """Test getting CCDF data by data category."""
        mock_response = [{
            'state': 'CA',
            'data_category': 'enrollment',
            'count': 500000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_ccdf_data(data_category='enrollment')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_ccdf_data_error(self, acf_connector):
        """Test error handling in get_ccdf_data."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_ccdf_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_ccdf_data_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_ccdf_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetStateSummary:
    """Test get_state_summary method."""
    
    def test_get_state_summary(self, acf_connector):
        """Test getting state summary data."""
        mock_response = [{
            'state': 'CA',
            'total_programs': 10,
            'total_beneficiaries': 2000000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_state_summary(state='CA')
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_state_summary_with_year(self, acf_connector):
        """Test getting state summary with year filter."""
        mock_response = [{
            'state': 'TX',
            'total_programs': 8,
            'total_beneficiaries': 1500000,
            'year': 2023
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_state_summary(state='TX', year=2023)
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_state_summary_error(self, acf_connector):
        """Test error handling in get_state_summary."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_state_summary(state='CA')
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_state_summary_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_state_summary(state='CA')
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetNationalStatistics:
    """Test get_national_statistics method."""
    
    def test_get_national_statistics_no_filters(self, acf_connector):
        """Test getting national statistics without filters."""
        mock_response = [{
            'total_beneficiaries': 20000000,
            'total_expenditures': 50000000000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_national_statistics()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_national_statistics_with_program(self, acf_connector):
        """Test getting national statistics by program."""
        mock_response = [{
            'program': 'tanf',
            'total_beneficiaries': 2000000,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_national_statistics(program='tanf')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_national_statistics_error(self, acf_connector):
        """Test error handling in get_national_statistics."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_national_statistics()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_national_statistics_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_national_statistics()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorGetProgramOutcomes:
    """Test get_program_outcomes method."""
    
    def test_get_program_outcomes(self, acf_connector):
        """Test getting program outcomes."""
        mock_response = [{
            'program': 'tanf',
            'state': 'CA',
            'employment_rate': 0.65,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_program_outcomes(program='tanf')
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_get_program_outcomes_with_state(self, acf_connector):
        """Test getting program outcomes with state filter."""
        mock_response = [{
            'program': 'head_start',
            'state': 'NY',
            'school_readiness': 0.85,
            'year': 2024
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_program_outcomes(program='head_start', state='NY')
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_program_outcomes_with_year(self, acf_connector):
        """Test getting program outcomes with year filter."""
        mock_response = [{
            'program': 'foster_care',
            'permanency_rate': 0.75,
            'year': 2023
        }]
        
        with patch.object(acf_connector, 'fetch', return_value=mock_response):
            result = acf_connector.get_program_outcomes(program='foster_care', year=2023)
            
            assert isinstance(result, pd.DataFrame)
    
    def test_get_program_outcomes_error(self, acf_connector):
        """Test error handling in get_program_outcomes."""
        with patch.object(acf_connector, 'fetch', side_effect=Exception('API error')):
            result = acf_connector.get_program_outcomes(program='tanf')
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0
    
    def test_get_program_outcomes_empty_response(self, acf_connector):
        """Test handling of empty response."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_program_outcomes(program='tanf')
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 0


class TestACFConnectorClose:
    """Test close method."""
    
    def test_close(self, acf_connector):
        """Test closing connection."""
        mock_session = MagicMock()
        acf_connector.session = mock_session
        acf_connector.close()
        mock_session.close.assert_called_once()
        assert acf_connector.session is None


class TestACFConnectorTypeContracts:
    """Test type contracts and data validation (Phase 4 Layer 8)."""
    
    def test_get_tanf_data_returns_dataframe(self, acf_connector):
        """Test that get_tanf_data returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_tanf_data()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_head_start_data_returns_dataframe(self, acf_connector):
        """Test that get_head_start_data returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_head_start_data()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_child_support_data_returns_dataframe(self, acf_connector):
        """Test that get_child_support_data returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_child_support_data()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_foster_care_data_returns_dataframe(self, acf_connector):
        """Test that get_foster_care_data returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_foster_care_data()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_child_welfare_data_returns_dataframe(self, acf_connector):
        """Test that get_child_welfare_data returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_child_welfare_data()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_adoption_data_returns_dataframe(self, acf_connector):
        """Test that get_adoption_data returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_adoption_data()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_ccdf_data_returns_dataframe(self, acf_connector):
        """Test that get_ccdf_data returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_ccdf_data()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_state_summary_returns_dataframe(self, acf_connector):
        """Test that get_state_summary returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_state_summary(state='CA')
            assert isinstance(result, pd.DataFrame)
    
    def test_get_national_statistics_returns_dataframe(self, acf_connector):
        """Test that get_national_statistics returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_national_statistics()
            assert isinstance(result, pd.DataFrame)
    
    def test_get_program_outcomes_returns_dataframe(self, acf_connector):
        """Test that get_program_outcomes returns DataFrame."""
        with patch.object(acf_connector, 'fetch', return_value={}):
            result = acf_connector.get_program_outcomes(program='tanf')
            assert isinstance(result, pd.DataFrame)
    
    def test_constants_defined(self):
        """Test that required constants are defined."""
        assert isinstance(PROGRAM_TYPES, dict)
        assert isinstance(DATA_CATEGORIES, dict)
        assert isinstance(WELFARE_INDICATORS, dict)
        assert 'tanf' in PROGRAM_TYPES
        assert 'caseload' in DATA_CATEGORIES
        assert 'maltreatment' in WELFARE_INDICATORS
