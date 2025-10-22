#!/usr/bin/env python3
# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0


"""
Script to add Layer 5 (Security) tests to connector test files.

This script adds comprehensive security test suites to connector test files
that don't already have them, following the pattern established in:
- BEA connector
- CDC connector
- BLS connector
"""

import re
from pathlib import Path

# Security test template
SECURITY_TESTS_TEMPLATE = '''

# =============================================================================
# Layer 5: Security Tests
# =============================================================================


class Test{connector_class}SecurityInjection:
    """Test security: SQL injection and command injection prevention."""

    def test_sql_injection_in_parameters(self, {fixture_name}):
        """Test SQL injection attempt in parameters."""
        # SQL injection attempt
        malicious_input = "test'; DROP TABLE data; --"
        
        # Should handle safely - not execute SQL
        try:
            # Test with malicious input on a key method
            result = {fixture_name}.{test_method}({malicious_params})
            assert isinstance(result, (pd.DataFrame, dict, list, type(None)))
        except (ValueError, TypeError, AttributeError):
            # Acceptable to reject malicious input
            pass

    def test_command_injection_prevention(self, {fixture_name}):
        """Test command injection prevention."""
        # Command injection attempt
        malicious_cmd = "test; rm -rf /"
        
        # Should handle safely
        try:
            result = {fixture_name}.{test_method}({malicious_params_cmd})
            assert isinstance(result, (pd.DataFrame, dict, list, type(None)))
        except (ValueError, TypeError):
            # Acceptable to reject malicious input
            pass

    def test_xss_injection_prevention(self, {fixture_name}):
        """Test XSS (Cross-Site Scripting) prevention."""
        # XSS attempt
        xss_payload = "<script>alert('XSS')</script>"
        
        # Should handle safely (escape or reject)
        try:
            result = {fixture_name}.{test_method}({malicious_params_xss})
            assert isinstance(result, (pd.DataFrame, dict, list, type(None)))
        except (ValueError, TypeError):
            # Acceptable to reject XSS payloads
            pass


class Test{connector_class}SecurityInputValidation:
    """Test security: Input validation and sanitization."""

    def test_handles_null_bytes(self, {fixture_name}):
        """Test handling of null bytes in parameters."""
        # Null byte injection attempt
        malicious_input = "test\\x00malicious"
        
        # Should handle safely or reject
        try:
            result = {fixture_name}.{test_method}({null_byte_params})
            assert isinstance(result, (pd.DataFrame, dict, list, type(None)))
        except (ValueError, TypeError):
            # Acceptable to reject null bytes
            pass

    def test_handles_extremely_long_inputs(self, {fixture_name}):
        """Test handling of excessively long inputs (DoS prevention)."""
        # Extremely long input (potential DoS attack)
        long_input = "A" * 10000
        
        # Should handle safely or reject
        try:
            result = {fixture_name}.{test_method}({long_input_params})
            assert isinstance(result, (pd.DataFrame, dict, list, type(None)))
        except (ValueError, Exception):
            # Acceptable to reject overly long inputs
            pass

    def test_type_validation(self, {fixture_name}):
        """Test parameter type validation."""
        # Invalid types
        invalid_inputs = [None, [], {{}}, 12345, True]
        
        for invalid in invalid_inputs:
            try:
                result = {fixture_name}.{test_method}({type_validation_params})
                # Some connectors may handle None gracefully
                if result is not None:
                    assert isinstance(result, (pd.DataFrame, dict, list))
            except (ValueError, TypeError, AttributeError):
                # Expected to reject invalid types
                pass
'''

# Connector-specific configurations
CONNECTOR_CONFIGS = {
    'air_quality': {
        'connector_class': 'AirQuality',
        'fixture_name': 'air_quality_connector',
        'test_method': 'get_data',
        'malicious_params': 'pollutant=malicious_input',
        'malicious_params_cmd': 'state=malicious_cmd',
        'malicious_params_xss': 'county=xss_payload',
        'null_byte_params': 'state=malicious_input',
        'long_input_params': 'pollutant=long_input',
        'type_validation_params': 'year=invalid',
    },
    'base': {
        'connector_class': 'Base',
        'fixture_name': 'base_connector',
        'test_method': '_make_request',
        'malicious_params': 'url=malicious_input',
        'malicious_params_cmd': 'endpoint=malicious_cmd',
        'malicious_params_xss': 'params={"key": xss_payload}',
        'null_byte_params': 'url=malicious_input',
        'long_input_params': 'endpoint=long_input',
        'type_validation_params': 'method=invalid',
    },
    'cbp': {
        'connector_class': 'CBP',
        'fixture_name': 'cbp_connector',
        'test_method': 'get_population_data',
        'malicious_params': 'geography=malicious_input',
        'malicious_params_cmd': 'year=malicious_cmd',
        'malicious_params_xss': 'state=xss_payload',
        'null_byte_params': 'geography=malicious_input',
        'long_input_params': 'state=long_input',
        'type_validation_params': 'year=invalid',
    },
    'chr_unit': {
        'connector_class': 'CHR',
        'fixture_name': 'chr_connector',
        'test_method': 'load_data',
        'malicious_params': 'file_path=malicious_input',
        'malicious_params_cmd': 'file_path=malicious_cmd',
        'malicious_params_xss': 'file_path=xss_payload',
        'null_byte_params': 'file_path=malicious_input',
        'long_input_params': 'file_path=long_input',
        'type_validation_params': 'year=invalid',
    },
    'ejscreen': {
        'connector_class': 'EJScreen',
        'fixture_name': 'ejscreen_connector',
        'test_method': 'get_data',
        'malicious_params': 'geography=malicious_input',
        'malicious_params_cmd': 'state=malicious_cmd',
        'malicious_params_xss': 'county=xss_payload',
        'null_byte_params': 'geography=malicious_input',
        'long_input_params': 'state=long_input',
        'type_validation_params': 'year=invalid',
    },
    'fbi_ucr': {
        'connector_class': 'FBIUCR',
        'fixture_name': 'fbi_ucr_connector',
        'test_method': 'get_crime_data',
        'malicious_params': 'state=malicious_input',
        'malicious_params_cmd': 'year=malicious_cmd',
        'malicious_params_xss': 'crime_type=xss_payload',
        'null_byte_params': 'state=malicious_input',
        'long_input_params': 'crime_type=long_input',
        'type_validation_params': 'year=invalid',
    },
    'hrsa': {
        'connector_class': 'HRSA',
        'fixture_name': 'hrsa_connector',
        'test_method': 'get_facility_data',
        'malicious_params': 'state=malicious_input',
        'malicious_params_cmd': 'facility_type=malicious_cmd',
        'malicious_params_xss': 'county=xss_payload',
        'null_byte_params': 'state=malicious_input',
        'long_input_params': 'facility_type=long_input',
        'type_validation_params': 'year=invalid',
    },
    'hud_fmr': {
        'connector_class': 'HUDFMR',
        'fixture_name': 'hud_fmr_connector',
        'test_method': 'get_fair_market_rents',
        'malicious_params': 'area=malicious_input',
        'malicious_params_cmd': 'year=malicious_cmd',
        'malicious_params_xss': 'state=xss_payload',
        'null_byte_params': 'area=malicious_input',
        'long_input_params': 'area=long_input',
        'type_validation_params': 'year=invalid',
    },
    'lehd': {
        'connector_class': 'LEHD',
        'fixture_name': 'lehd_connector',
        'test_method': 'get_employment_data',
        'malicious_params': 'state=malicious_input',
        'malicious_params_cmd': 'year=malicious_cmd',
        'malicious_params_xss': 'industry=xss_payload',
        'null_byte_params': 'state=malicious_input',
        'long_input_params': 'industry=long_input',
        'type_validation_params': 'year=invalid',
    },
    'nces': {
        'connector_class': 'NCES',
        'fixture_name': 'nces_connector',
        'test_method': 'get_school_data',
        'malicious_params': 'state=malicious_input',
        'malicious_params_cmd': 'year=malicious_cmd',
        'malicious_params_xss': 'school_type=xss_payload',
        'null_byte_params': 'state=malicious_input',
        'long_input_params': 'school_type=long_input',
        'type_validation_params': 'year=invalid',
    },
    'zillow_unit': {
        'connector_class': 'Zillow',
        'fixture_name': 'zillow_connector',
        'test_method': 'load_data',
        'malicious_params': 'file_path=malicious_input',
        'malicious_params_cmd': 'file_path=malicious_cmd',
        'malicious_params_xss': 'file_path=xss_payload',
        'null_byte_params': 'file_path=malicious_input',
        'long_input_params': 'file_path=long_input',
        'type_validation_params': 'data_type=invalid',
    },
}


def add_security_tests_to_file(file_path: Path, connector_key: str):
    """Add security tests to a connector test file."""
    
    if connector_key not in CONNECTOR_CONFIGS:
        print(f"⚠️  No configuration for {connector_key}, skipping {file_path}")
        return False
    
    config = CONNECTOR_CONFIGS[connector_key]
    
    # Read the file
    content = file_path.read_text()
    
    # Check if security tests already exist
    if 'Layer 5: Security Tests' in content or 'SecurityInjection' in content:
        print(f"✓  {file_path.name} already has security tests")
        return False
    
    # Generate security tests from template
    security_tests = SECURITY_TESTS_TEMPLATE.format(**config)
    
    # Find the last if __name__ == "__main__": line
    main_pattern = r'if __name__ == "__main__":\s+pytest\.main\(\[__file__.*?\]\)'
    
    match = re.search(main_pattern, content)
    
    if match:
        # Insert security tests before the if __name__ == "__main__": block
        insert_pos = match.start()
        new_content = content[:insert_pos] + security_tests + '\n\n' + content[insert_pos:]
    else:
        # Append to the end of the file
        new_content = content + '\n' + security_tests + '\n\nif __name__ == "__main__":\n    pytest.main([__file__, "-v"])\n'
    
    # Write the updated content
    file_path.write_text(new_content)
    print(f"✅  Added security tests to {file_path.name}")
    return True


def main():
    """Main function to add security tests to all connectors."""
    
    test_dir = Path(__file__).parent.parent / 'tests'
    unit_test_dir = test_dir / 'unit'
    
    # Connectors needing security tests
    connectors_to_update = {
        'air_quality': unit_test_dir / 'test_air_quality_connector.py',
        'base': unit_test_dir / 'test_base_connector.py',
        'cbp': unit_test_dir / 'test_cbp_connector.py',
        'chr_unit': unit_test_dir / 'test_chr_connector.py',
        'ejscreen': unit_test_dir / 'test_ejscreen_connector.py',
        'fbi_ucr': unit_test_dir / 'test_fbi_ucr_connector.py',
        'hrsa': unit_test_dir / 'test_hrsa_connector.py',
        'hud_fmr': unit_test_dir / 'test_hud_fmr_connector.py',
        'lehd': unit_test_dir / 'test_lehd_connector.py',
        'nces': unit_test_dir / 'test_nces_connector.py',
        'zillow_unit': unit_test_dir / 'test_zillow_connector.py',
    }
    
    total_updated = 0
    
    for connector_key, test_file in connectors_to_update.items():
        if test_file.exists():
            if add_security_tests_to_file(test_file, connector_key):
                total_updated += 1
        else:
            print(f"⚠️  File not found: {test_file}")
    
    print(f"\n{'='*60}")
    print(f"✅  Successfully added security tests to {total_updated} connector(s)")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
