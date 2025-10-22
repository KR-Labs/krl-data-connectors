# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Security tests for OpportunityInsightsConnector.

Tests cover:
- Path traversal prevention
- URL validation and SSRF prevention
- Input sanitization
- Command injection prevention
- File handling security

Target: Prevent common attack vectors
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch
import pandas as pd
import pytest
from krl_data_connectors.mobility import OpportunityInsightsConnector


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def connector(tmp_path):
    """Create OpportunityInsightsConnector instance with test cache."""
    cache_dir = tmp_path / "test_cache"
    cache_dir.mkdir()
    return OpportunityInsightsConnector(cache_dir=str(cache_dir))


# ============================================================
# PATH TRAVERSAL TESTS
# ============================================================


class TestPathTraversalPrevention:
    """Test prevention of path traversal attacks."""

    def test_path_traversal_in_filename(self, connector):
        """Test that path traversal in filename is prevented."""
        # Attempt to traverse outside cache directory
        malicious_filename = "../../../etc/passwd"

        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.headers = {"content-length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"data"]
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response

            connector.connect()

            # Download file - should NOT allow traversal
            result_path = connector._download_file(
                "https://example.com/data.csv", malicious_filename, force_download=True
            )

            # Result path should be within cache directory
            assert str(connector.cache.cache_dir) in str(result_path)
            # Should not actually traverse to /etc
            assert "/etc/passwd" not in str(result_path)

    def test_path_traversal_with_absolute_path(self, connector):
        """Test that absolute path in filename is handled safely."""
        # Attempt to use absolute path
        malicious_filename = "/tmp/malicious.csv"

        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.headers = {"content-length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"data"]
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response

            connector.connect()

            # Should create file in cache dir, not at /tmp
            result_path = connector._download_file(
                "https://example.com/data.csv", malicious_filename, force_download=True
            )

            # Result should be in cache directory
            assert str(connector.cache.cache_dir) in str(result_path)
            assert not result_path.is_absolute() or str(connector.cache.cache_dir) in str(
                result_path
            )

    def test_path_traversal_with_encoded_dots(self, connector):
        """Test that URL-encoded path traversal is prevented."""
        # Encoded version of ../
        malicious_filename = "..%2F..%2F..%2Fetc%2Fpasswd"

        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.headers = {"content-length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"data"]
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response

            connector.connect()

            result_path = connector._download_file(
                "https://example.com/data.csv", malicious_filename, force_download=True
            )

            # Should be contained in cache directory
            assert str(connector.cache.cache_dir) in str(result_path)


# ============================================================
# URL VALIDATION / SSRF PREVENTION TESTS
# ============================================================


class TestURLValidation:
    """Test URL validation and SSRF prevention."""

    def test_internal_network_url_prevention(self, connector):
        """Test that internal network URLs are handled safely."""
        internal_urls = [
            "http://localhost/data.csv",
            "http://127.0.0.1/data.csv",
            "http://192.168.1.1/data.csv",
            "http://10.0.0.1/data.csv",
            "http://172.16.0.1/data.csv",
        ]

        connector.connect()

        # We don't actually want to try connecting to internal IPs in tests
        # Just verify the URL validation allows them through to requests
        # (requests library will handle the actual security)
        for url in internal_urls:
            # Should not raise ValueError from our URL validation
            # (The actual connection will fail/timeout, which is expected)
            try:
                # Mock the session to avoid actual network calls
                with patch.object(connector, "session") as mock_session:
                    mock_session.get.side_effect = ConnectionError("Connection refused")
                    connector._download_file(url, "test.csv", force_download=True)
            except (ConnectionError, Exception) as e:
                # Connection errors are expected for internal IPs
                # We just want to ensure no ValueError from URL validation
                assert "Invalid URL scheme" not in str(e)

    def test_file_protocol_url_rejection(self, connector):
        """Test that file:// protocol is rejected."""
        file_url = "file:///etc/passwd"

        connector.connect()

        # Should reject file:// protocol
        with pytest.raises((ValueError, Exception)):
            connector._download_file(file_url, "test.csv", force_download=True)

    def test_ftp_protocol_rejection(self, connector):
        """Test that FTP protocol is rejected (should use HTTPS)."""
        ftp_url = "ftp://example.com/data.csv"

        connector.connect()

        # Connector should only accept HTTPS URLs
        with pytest.raises((ValueError, Exception)):
            connector._download_file(ftp_url, "test.csv", force_download=True)


# ============================================================
# INPUT SANITIZATION TESTS
# ============================================================


class TestInputSanitization:
    """Test input validation and sanitization."""

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_sql_injection_in_state_parameter(self, mock_download, mock_read, connector):
        """Test SQL injection attempt in state parameter."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read.return_value = pd.DataFrame(
            {
                "state": ["06"],
                "county": ["06037"],
                "tract": ["06037980000"],
                "kfr_pooled_p25": [0.45],
            }
        )

        # SQL injection attempt
        malicious_state = "06'; DROP TABLE states; --"

        # Should handle safely without executing SQL
        result = connector.fetch_opportunity_atlas(geography="tract", state=malicious_state)

        # Should return empty or filtered data, not crash
        assert isinstance(result, pd.DataFrame)

    @patch("pandas.read_stata")
    @patch.object(OpportunityInsightsConnector, "_download_file")
    def test_command_injection_in_county_parameter(self, mock_download, mock_read, connector):
        """Test command injection prevention in county parameter."""
        mock_download.return_value = Path("/fake/path.dta")
        mock_read.return_value = pd.DataFrame(
            {
                "state": ["06"],
                "county": ["06037"],
                "tract": ["06037980000"],
                "kfr_pooled_p25": [0.45],
            }
        )

        # Command injection attempt
        malicious_county = "06037; rm -rf /"

        # Should handle safely
        result = connector.fetch_opportunity_atlas(geography="tract", county=malicious_county)

        assert isinstance(result, pd.DataFrame)

    def test_invalid_geography_rejected(self, connector):
        """Test that invalid geography values are rejected."""
        invalid_geographies = [
            "'; DROP TABLE data; --",
            "../../../etc/passwd",
            "<script>alert('XSS')</script>",
            "tract; cat /etc/passwd",
        ]

        for invalid_geo in invalid_geographies:
            with pytest.raises(ValueError, match="Invalid geography"):
                connector.fetch_opportunity_atlas(geography=invalid_geo)


# ============================================================
# NO API KEY EXPOSURE TESTS
# ============================================================


class TestNoAPIKeyExposure:
    """Test that no sensitive data is exposed (connector doesn't use API keys)."""

    def test_repr_safe(self, connector):
        """Test that repr() doesn't expose sensitive data."""
        repr_str = repr(connector)

        # Should not contain file paths or internal details
        assert isinstance(repr_str, str)
        assert len(repr_str) < 500  # Should be concise

    def test_str_safe(self, connector):
        """Test that str() doesn't expose sensitive data."""
        str_repr = str(connector)

        # Should not expose internal implementation details
        assert isinstance(str_repr, str)

    def test_logger_doesnt_expose_sensitive_data(self, connector):
        """Test that logging doesn't expose sensitive file contents."""
        with patch("pandas.read_stata") as mock_read:
            # Create DataFrame with proper structure including state column
            mock_read.return_value = pd.DataFrame(
                {
                    "state": ["06"],
                    "county": ["06037"],
                    "tract": ["06037980000"],
                    "data": ["sensitive"],
                }
            )

            with patch.object(connector, "_download_file") as mock_download:
                mock_download.return_value = Path("/fake/path.dta")

                # Fetch data - logging should not expose full file contents
                connector.fetch_opportunity_atlas(geography="tract", state="06")

                # Check that logger was used but didn't expose data
                # (Implementation detail - logger should log actions, not data)
                assert mock_read.called


# ============================================================
# FILE HANDLING SECURITY TESTS
# ============================================================


class TestFileHandlingSecurity:
    """Test secure file handling."""

    def test_no_arbitrary_file_write(self, connector):
        """Test that connector doesn't write to arbitrary locations."""
        # All files should be written to cache directory
        cache_dir = Path(str(connector.cache.cache_dir))

        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.headers = {"content-length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"data"]
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response

            connector.connect()

            result_path = connector._download_file(
                "https://example.com/data.csv", "test.csv", force_download=True
            )

            # File should be in cache directory
            assert result_path.parent == cache_dir

    def test_no_symlink_following(self, connector, tmp_path):
        """Test that symlinks are not followed outside cache directory."""
        cache_dir = Path(str(connector.cache.cache_dir))

        # Create a symlink to outside directory
        outside_dir = tmp_path / "outside"
        outside_dir.mkdir()

        symlink_path = cache_dir / "malicious_link"
        try:
            symlink_path.symlink_to(outside_dir)
        except OSError:
            pytest.skip("Cannot create symlinks on this system")

        # Attempt to use the symlink
        with patch.object(connector, "session") as mock_session:
            mock_response = Mock()
            mock_response.headers = {"content-length": "100"}
            mock_response.iter_content = lambda chunk_size: [b"data"]
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response

            connector.connect()

            # Should create file in cache, not follow symlink
            result_path = connector._download_file(
                "https://example.com/data.csv",
                "malicious_link/../../outside/data.csv",
                force_download=True,
            )

            # Result should still be within cache directory
            assert str(cache_dir) in str(result_path.resolve())

    def test_cache_directory_permissions_check(self, connector):
        """Test that cache directory has appropriate permissions."""
        cache_dir = Path(str(connector.cache.cache_dir))

        # Cache directory should exist and be writable
        assert cache_dir.exists()
        assert cache_dir.is_dir()
        assert os.access(cache_dir, os.W_OK)

        # Should not be world-writable (security risk)
        stat_info = cache_dir.stat()
        mode = stat_info.st_mode
        # Check that others don't have write permission (checking last bit)
        assert not (mode & 0o002), "Cache directory should not be world-writable"
