# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

# Copyright (c) 2025 KR-Labs Foundation. All rights reserved.
# Licensed under Apache License 2.0 (see LICENSE file for details)

"""Unit tests for BaseConnector."""

from unittest.mock import MagicMock, Mock, patch

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
        connector = MockConnector(
            api_key="test_key",
            cache_dir=str(temp_cache_dir)
        )
        
        assert connector.api_key == "test_key"
        assert connector.cache is not None
        assert connector.session is None
    
    def test_init_with_config_api_key(self, temp_cache_dir):
        """Test initialization with API key from config."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))
        
        assert connector.api_key == "mock_api_key"
    
    def test_init_cache_settings(self, temp_cache_dir):
        """Test cache initialization."""
        connector = MockConnector(
            cache_dir=str(temp_cache_dir),
            cache_ttl=7200
        )
        
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
    
    @patch('requests.Session.get')
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
    
    @patch('requests.Session.get')
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
    
    @patch('requests.Session.get')
    def test_make_request_http_error(self, mock_get, temp_cache_dir):
        """Test HTTP error handling."""
        connector = MockConnector(cache_dir=str(temp_cache_dir))
        
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.exceptions.HTTPError):
            connector._make_request("https://api.example.com/data", use_cache=False)
    
    @patch('requests.Session.get')
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
        connector = MockConnector(
            api_key="test_key",
            cache_dir=str(temp_cache_dir)
        )
        
        repr_str = repr(connector)
        
        assert "MockConnector" in repr_str
        assert "has_api_key=True" in repr_str
        assert str(temp_cache_dir) in repr_str
