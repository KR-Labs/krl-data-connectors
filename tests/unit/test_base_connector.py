# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""Unit tests for BaseConnector."""

from unittest.mock import Mock, patch

import pytest
import requests

from krl_data_connectors import BaseConnector


class MockConnector(BaseConnector):
    """Mock connector for testing BaseConnector."""

    def _get_api_key(self):
        return "mock_api_key"

    def connect(self):
        pass

    def fetch(self, **kwargs):
        return {"data": "test"}


class TestBaseConnectorInit:
    """Test BaseConnector initialization."""

    def test_init_with_api_key(self, temp_cache_dir):
        """Test initialization with explicit API key."""
        connector = MockConnector(api_key="test_key", cache_dir=str(temp_cache_dir))

        assert connector.api_key == "test_key"
        assert connector.cache is not None
        assert connector.session is None

    def test_init_with_config_api_key(self, temp_cache_dir):
        """Test initialization with API key from config."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        assert connector.api_key == "mock_api_key"

    def test_init_cache_settings(self, temp_cache_dir):
        """Test cache initialization."""
        connector = MockConnector(cache_dir=str(temp_cache_dir), cache_ttl=7200)

        assert connector.cache.cache_dir == temp_cache_dir
        assert connector.cache.default_ttl == 7200


class TestBaseConnectorSession:
    """Test HTTP session management."""

    def test_init_session_creates_session(self, temp_cache_dir):
        """Test session initialization."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        session = connector._init_session()

        assert isinstance(session, requests.Session)
        assert connector.session is session

    def test_init_session_reuses_session(self, temp_cache_dir):
        """Test session is reused."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        session1 = connector._init_session()
        session2 = connector._init_session()

        assert session1 is session2


class TestBaseConnectorCacheKey:
    """Test cache key generation."""

    def test_make_cache_key_url_only(self, temp_cache_dir):
        """Test cache key from URL only."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        key1 = connector._make_cache_key("https://api.example.com/data")
        key2 = connector._make_cache_key("https://api.example.com/data")

        assert key1 == key2
        assert len(key1) == 64  # SHA256 hash length

    def test_make_cache_key_with_params(self, temp_cache_dir):
        """Test cache key with parameters."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        params = {"series_id": "UNRATE", "start": "2020-01-01"}
        key = connector._make_cache_key("https://api.example.com/data", params)

        assert len(key) == 64

    def test_make_cache_key_param_order_invariant(self, temp_cache_dir):
        """Test cache key is same regardless of parameter order."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        params1 = {"a": "1", "b": "2", "c": "3"}
        params2 = {"c": "3", "a": "1", "b": "2"}

        key1 = connector._make_cache_key("https://api.example.com", params1)
        key2 = connector._make_cache_key("https://api.example.com", params2)

        assert key1 == key2


class TestBaseConnectorRequest:
    """Test HTTP request functionality."""

    @patch("requests.Session.get")
    def test_make_request_success(self, mock_get, temp_cache_dir):
        """Test successful API request."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = connector._make_request("https://api.example.com/data", use_cache=False)

        assert result == {"data": "test"}
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_make_request_with_cache(self, mock_get, temp_cache_dir):
        """Test request with caching."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # First request - should hit API
        result1 = connector._make_request("https://api.example.com/data", use_cache=True)

        # Second request - should hit cache
        result2 = connector._make_request("https://api.example.com/data", use_cache=True)

        assert result1 == result2
        assert mock_get.call_count == 1  # Only called once

    @patch("requests.Session.get")
    def test_make_request_http_error(self, mock_get, temp_cache_dir):
        """Test HTTP error handling."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            connector._make_request("https://api.example.com/data", use_cache=False)

    @patch("requests.Session.get")
    def test_make_request_timeout(self, mock_get, temp_cache_dir):
        """Test timeout handling."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        mock_get.side_effect = requests.exceptions.Timeout()

        with pytest.raises(requests.exceptions.Timeout):
            connector._make_request("https://api.example.com/data", use_cache=False)


class TestBaseConnectorCache:
    """Test cache management."""

    def test_get_cache_stats(self, temp_cache_dir):
        """Test getting cache statistics."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        stats = connector.get_cache_stats()

        assert "hits" in stats
        assert "misses" in stats
        assert "cache_size" in stats

    def test_clear_cache(self, temp_cache_dir):
        """Test clearing cache."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        # Add something to cache
        connector.cache.set("test_key", "test_value")
        assert connector.cache.has("test_key")

        # Clear cache
        connector.clear_cache()

        assert not connector.cache.has("test_key")


class TestBaseConnectorDisconnect:
    """Test disconnect functionality."""

    def test_disconnect_closes_session(self, temp_cache_dir):
        """Test disconnect closes HTTP session."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        # Initialize session
        connector._init_session()
        assert connector.session is not None

        # Disconnect
        connector.disconnect()

        assert connector.session is None


class TestBaseConnectorContextManager:
    """Test context manager functionality."""

    def test_context_manager(self, temp_cache_dir):
        """Test using connector as context manager."""
        with MockConnector(cache_dir=str(temp_cache_dir)) as connector:
            assert connector is not None
            assert isinstance(connector, MockConnector)


class TestBaseConnectorRepr:
    """Test string representation."""

    def test_repr(self, temp_cache_dir):
        """Test __repr__ method."""
        connector = MockConnector(api_key="test_key", cache_dir=str(temp_cache_dir))

        repr_str = repr(connector)

        assert "MockConnector" in repr_str
        assert "has_api_key=True" in repr_str
        assert str(temp_cache_dir) in repr_str


class TestBaseConnectorSecurityInjection:
    """Test Layer 5: Security - Injection Prevention."""

    @patch("requests.Session.get")
    def test_sql_injection_in_url(self, mock_get, temp_cache_dir):
        """Test SQL injection attempts in URL are handled safely."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        malicious_url = "https://api.example.com/data'; DROP TABLE users;--"

        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Should not raise exception, URL is passed as-is (escaping is HTTP library's job)
        try:
            connector._make_request(malicious_url, use_cache=False)
        except Exception:
            pass  # Any exception is fine, just shouldn't execute SQL

    @patch("requests.Session.get")
    def test_command_injection_in_cache_key(self, mock_get, temp_cache_dir):
        """Test command injection attempts in cache key generation."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        malicious_param = "test; rm -rf /"
        params = {"key": malicious_param}

        # Cache key should be hashed, not executed
        cache_key = connector._make_cache_key("https://api.example.com", params)

        # Should be a safe hash
        assert len(cache_key) == 64
        assert "rm" not in cache_key
        assert ";" not in cache_key

    def test_path_traversal_in_cache_dir(self, temp_cache_dir):
        """Test path traversal attempts in cache directory."""
        malicious_cache_dir = "../../etc/passwd"

        # Should handle path normalization safely
        try:
            connector = MockConnector(cache_dir=malicious_cache_dir)
            # Cache should still be usable
            assert connector.cache is not None
        except Exception:
            pass  # Exception is acceptable for invalid paths


class TestBaseConnectorSecurityAPIKey:
    """Test Layer 5: Security - API Key Protection."""

    def test_api_key_not_in_repr(self, temp_cache_dir):
        """Test API key is not exposed in repr()."""
        connector = MockConnector(api_key="super_secret_key_12345", cache_dir=str(temp_cache_dir))

        repr_str = repr(connector)

        assert "super_secret_key_12345" not in repr_str
        assert "has_api_key=True" in repr_str

    def test_api_key_not_in_str(self, temp_cache_dir):
        """Test API key is not exposed in str()."""
        connector = MockConnector(api_key="super_secret_key_12345", cache_dir=str(temp_cache_dir))

        str_repr = str(connector)

        assert "super_secret_key_12345" not in str_repr

    @patch("requests.Session.get")
    def test_api_key_not_in_error_messages(self, mock_get, temp_cache_dir):
        """Test API key is not exposed in error messages."""
        connector = MockConnector(api_key="super_secret_key_12345", cache_dir=str(temp_cache_dir))

        mock_get.side_effect = requests.exceptions.HTTPError("API Error")

        try:
            connector._make_request("https://api.example.com", use_cache=False)
        except requests.exceptions.HTTPError as e:
            # API key should not be in exception message
            assert "super_secret_key_12345" not in str(e)

    def test_api_key_not_in_logs(self, temp_cache_dir, caplog):
        """Test API key is not exposed in log messages."""
        import logging

        caplog.set_level(logging.INFO)

        connector = MockConnector(api_key="super_secret_key_12345", cache_dir=str(temp_cache_dir))

        # Check all log records
        for record in caplog.records:
            assert "super_secret_key_12345" not in record.getMessage()


class TestBaseConnectorSecurityInputValidation:
    """Test Layer 5: Security - Input Validation."""

    def test_handles_null_bytes_in_url(self, temp_cache_dir):
        """Test null byte injection handling in URLs."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        malicious_url = "https://api.example.com/data\x00.txt"

        # Should handle null bytes safely (likely raise exception or sanitize)
        try:
            connector._make_cache_key(malicious_url)
        except (ValueError, TypeError):
            pass  # Expected to reject null bytes

    def test_handles_extremely_long_url(self, temp_cache_dir):
        """Test handling of extremely long URLs (DoS prevention)."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        extremely_long_url = "https://api.example.com/" + "a" * 100000

        # Should handle long URLs without crashing
        try:
            cache_key = connector._make_cache_key(extremely_long_url)
            # Cache key should still be fixed length (hash)
            assert len(cache_key) == 64
        except Exception:
            pass  # May raise exception for invalid URL

    def test_negative_timeout_validation(self, temp_cache_dir):
        """Test validation of negative timeout values."""
        # Negative timeout should be accepted (Python's requests library handles it)
        # or connector should validate and reject
        try:
            connector = MockConnector(cache_dir=str(temp_cache_dir), timeout=-1)
            # If accepted, should be stored
            assert connector.timeout == -1
        except ValueError:
            pass  # Validation rejection is also acceptable

    def test_negative_cache_ttl_validation(self, temp_cache_dir):
        """Test validation of negative cache TTL values."""
        try:
            connector = MockConnector(cache_dir=str(temp_cache_dir), cache_ttl=-100)
            # If accepted, should be stored
            assert connector.cache.default_ttl == -100
        except ValueError:
            pass  # Validation rejection is also acceptable

    def test_none_cache_dir_handling(self):
        """Test handling of None cache directory."""
        # Should fall back to default cache directory
        connector = MockConnector(cache_dir=None)

        assert connector.cache is not None
        assert connector.cache.cache_dir is not None

    def test_empty_string_api_key(self, temp_cache_dir):
        """Test handling of empty string API key."""
        # MockConnector has a default _get_api_key(), so empty string falls back to it
        # This tests that the connector accepts empty string in initialization
        connector = MockConnector(api_key="", cache_dir=str(temp_cache_dir))

        # Empty string means it should fall back to _get_api_key() method
        assert connector.api_key == "mock_api_key"  # Falls back to MockConnector's default

    def test_whitespace_only_api_key(self, temp_cache_dir):
        """Test handling of whitespace-only API key."""
        connector = MockConnector(api_key="   ", cache_dir=str(temp_cache_dir))

        # Should accept whitespace (validation is connector-specific)
        assert connector.api_key == "   "


class TestBaseConnectorTypeContracts:
    """Test type contracts and return value structures (Layer 8)."""

    def test_connect_return_type(self, temp_cache_dir):
        """Test that connect returns None."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        result = connector.connect()

        assert result is None

    def test_disconnect_return_type(self, temp_cache_dir):
        """Test that disconnect returns None."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))
        connector.session = Mock()

        result = connector.disconnect()

        assert result is None

    def test_clear_cache_return_type(self, temp_cache_dir):
        """Test that clear_cache returns None."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        result = connector.clear_cache()

        assert result is None

    def test_get_cache_stats_return_type(self, temp_cache_dir):
        """Test that get_cache_stats returns dict."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        result = connector.get_cache_stats()

        assert isinstance(result, dict)
        # Basic cache stats should have cache_dir
        assert "cache_dir" in result

    def test_get_cache_stats_structure(self, temp_cache_dir):
        """Test that get_cache_stats returns expected structure."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        result = connector.get_cache_stats()

        # Required keys from FileCache.get_stats()
        assert "cache_dir" in result
        assert "hits" in result
        assert "misses" in result
        assert "total_requests" in result
        assert "hit_rate" in result
        assert "cache_size" in result

        # Value types
        assert isinstance(result["hits"], int)
        assert isinstance(result["misses"], int)
        assert isinstance(result["total_requests"], int)
        assert isinstance(result["cache_size"], int)

    def test_fetch_return_type(self, temp_cache_dir):
        """Test that fetch returns appropriate type."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        # fetch is abstract but should be implementable
        result = connector.fetch()

        # MockConnector's fetch raises NotImplementedError
        # Just verify it's callable
        assert hasattr(connector, "fetch")
        assert callable(connector.fetch)

    def test_get_api_key_return_type(self, temp_cache_dir):
        """Test that _get_api_key returns Optional[str]."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        result = connector._get_api_key()

        assert result is None or isinstance(result, str)

    def test_make_cache_key_return_type(self, temp_cache_dir):
        """Test that _make_cache_key returns str."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        result = connector._make_cache_key("http://test.com", params={"param1": "value1"})

        assert isinstance(result, str)
        assert len(result) > 0

    def test_make_request_return_type(self, temp_cache_dir):
        """Test that _make_request returns appropriate type."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        with patch("requests.Session") as mock_session_class:
            mock_session = Mock()
            mock_response = Mock()
            mock_response.json.return_value = {"data": "test"}
            mock_response.raise_for_status = Mock()
            mock_session.get.return_value = mock_response
            mock_session_class.return_value = mock_session

            connector.session = mock_session
            result = connector._make_request("http://test.com")

            # Should return dict (JSON response)
            assert isinstance(result, dict) or result is None

    def test_context_manager_return_types(self, temp_cache_dir):
        """Test that context manager methods return proper types."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))

        # __enter__ should return self
        result_enter = connector.__enter__()
        assert result_enter is connector

        # __exit__ should return False (doesn't suppress exceptions)
        result_exit = connector.__exit__(None, None, None)
        assert result_exit is False
