# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Contract tests for OpportunityInsightsConnector.

These tests verify that the connector adheres to the BaseConnector
interface contract defined in Phase 4 Layer 8 specifications.

Contract Requirements:
- Implements all required abstract methods
- Returns correct types
- Handles errors appropriately
- Follows naming conventions
- Maintains backward compatibility

Tests cover:
- Interface compliance
- Method signatures
- Return types
- Error handling patterns
- BaseConnector contract
"""

import inspect
from typing import Optional
import pandas as pd
import pytest
from krl_data_connectors.base_connector import BaseConnector
from krl_data_connectors.mobility import OpportunityInsightsConnector


# ============================================================
# INTERFACE COMPLIANCE TESTS
# ============================================================


class TestInterfaceCompliance:
    """Test that connector implements required BaseConnector interface."""

    def test_inherits_from_base_connector(self):
        """Test that connector inherits from BaseConnector."""
        assert issubclass(OpportunityInsightsConnector, BaseConnector)

    def test_implements_required_methods(self):
        """Test that all required abstract methods are implemented."""
        required_methods = ["connect", "fetch", "_get_api_key"]

        for method_name in required_methods:
            assert hasattr(OpportunityInsightsConnector, method_name)
            method = getattr(OpportunityInsightsConnector, method_name)
            assert callable(method)

    def test_can_instantiate(self):
        """Test that connector can be instantiated."""
        oi = OpportunityInsightsConnector()
        assert isinstance(oi, OpportunityInsightsConnector)
        assert isinstance(oi, BaseConnector)

    def test_has_required_attributes(self):
        """Test that connector has required attributes after initialization."""
        oi = OpportunityInsightsConnector()

        # Attributes from BaseConnector
        assert hasattr(oi, "cache")
        assert hasattr(oi, "logger")
        assert hasattr(oi, "session")
        assert hasattr(oi, "timeout")
        assert hasattr(oi, "max_retries")

        # Connector-specific attributes
        assert hasattr(oi, "data_version")


# ============================================================
# METHOD SIGNATURE TESTS
# ============================================================


class TestMethodSignatures:
    """Test that method signatures match expected contracts."""

    def test_init_signature(self):
        """Test __init__ method signature."""
        sig = inspect.signature(OpportunityInsightsConnector.__init__)
        params = sig.parameters

        # Should accept these parameters
        assert "self" in params
        assert "cache_dir" in params
        assert "cache_ttl" in params
        assert "timeout" in params
        assert "max_retries" in params
        assert "data_version" in params

        # All except self should have defaults
        for param_name, param in params.items():
            if param_name != "self":
                assert param.default is not inspect.Parameter.empty

    def test_connect_signature(self):
        """Test connect() method signature."""
        sig = inspect.signature(OpportunityInsightsConnector.connect)
        params = sig.parameters

        # Should only take self (no API key needed)
        assert len(params) == 1
        assert "self" in params

        # Return type should be None
        assert sig.return_annotation in [None, inspect.Signature.empty, "None"]

    def test_fetch_signature(self):
        """Test fetch() method signature."""
        sig = inspect.signature(OpportunityInsightsConnector.fetch)
        params = sig.parameters

        # Should take self and kwargs
        assert "self" in params
        assert "kwargs" in params

        # Return type should be DataFrame
        # Note: May not have annotation
        if sig.return_annotation != inspect.Signature.empty:
            assert "DataFrame" in str(sig.return_annotation)

    def test_get_api_key_signature(self):
        """Test _get_api_key() method signature."""
        sig = inspect.signature(OpportunityInsightsConnector._get_api_key)
        params = sig.parameters

        # Should only take self
        assert len(params) == 1
        assert "self" in params

        # Return type should be Optional[str]
        if sig.return_annotation != inspect.Signature.empty:
            assert "Optional" in str(sig.return_annotation) or "str" in str(sig.return_annotation)


# ============================================================
# RETURN TYPE TESTS
# ============================================================


class TestReturnTypes:
    """Test that methods return expected types."""

    def test_init_returns_instance(self):
        """Test that __init__ returns proper instance."""
        oi = OpportunityInsightsConnector()
        assert isinstance(oi, OpportunityInsightsConnector)
        assert isinstance(oi, BaseConnector)

    def test_connect_returns_none(self):
        """Test that connect() returns None."""
        oi = OpportunityInsightsConnector()
        result = oi.connect()
        assert result is None

    def test_get_api_key_returns_optional_string(self):
        """Test that _get_api_key() returns None or string."""
        oi = OpportunityInsightsConnector()
        result = oi._get_api_key()
        assert result is None or isinstance(result, str)

    @pytest.mark.slow
    def test_fetch_returns_dataframe(self):
        """Test that fetch() returns DataFrame."""
        oi = OpportunityInsightsConnector()
        oi.connect()

        result = oi.fetch(data_product="atlas", geography="tract", state="44")

        assert isinstance(result, pd.DataFrame)

    @pytest.mark.slow
    def test_fetch_opportunity_atlas_returns_dataframe(self):
        """Test that fetch_opportunity_atlas() returns DataFrame."""
        oi = OpportunityInsightsConnector()
        result = oi.fetch_opportunity_atlas(geography="tract", state="44")
        assert isinstance(result, pd.DataFrame)


# ============================================================
# ERROR HANDLING TESTS
# ============================================================


class TestErrorHandlingContract:
    """Test that connector handles errors according to contract."""

    def test_invalid_init_params_raises_typeerror(self):
        """Test that invalid initialization parameters raise TypeError."""
        with pytest.raises(TypeError):
            # Pass invalid type for timeout
            OpportunityInsightsConnector(timeout="invalid")

    def test_invalid_geography_raises_valueerror(self):
        """Test that invalid geography raises ValueError."""
        oi = OpportunityInsightsConnector()

        with pytest.raises(ValueError, match="Invalid geography"):
            oi.fetch_opportunity_atlas(geography="invalid_geography")

    def test_fetch_invalid_product_raises_valueerror(self):
        """Test that invalid data product raises ValueError."""
        oi = OpportunityInsightsConnector()

        with pytest.raises(ValueError, match="Unknown data_product"):
            oi.fetch(data_product="nonexistent_product")

    def test_network_errors_propagate(self):
        """Test that network errors propagate appropriately."""
        import requests
        from unittest.mock import patch, Mock

        oi = OpportunityInsightsConnector()
        oi.connect()

        # Mock a network error
        with patch.object(oi.session, "get") as mock_get:
            mock_get.side_effect = requests.ConnectionError("Network error")

            with pytest.raises(requests.ConnectionError):
                oi._download_file("https://example.com/file.dta", "test.dta")


# ============================================================
# BASECONNECTOR CONTRACT TESTS
# ============================================================


class TestBaseConnectorContract:
    """Test compliance with BaseConnector contract."""

    def test_cache_initialized(self):
        """Test that cache is properly initialized."""
        oi = OpportunityInsightsConnector()

        assert oi.cache is not None
        assert hasattr(oi.cache, "cache_dir")
        assert hasattr(oi.cache, "default_ttl")

    def test_logger_initialized(self):
        """Test that logger is properly initialized."""
        oi = OpportunityInsightsConnector()

        assert oi.logger is not None
        assert hasattr(oi.logger, "info")
        assert hasattr(oi.logger, "error")
        assert hasattr(oi.logger, "warning")
        assert hasattr(oi.logger, "debug")

    def test_session_lifecycle(self):
        """Test session initialization lifecycle."""
        oi = OpportunityInsightsConnector()

        # Session should be None initially
        assert oi.session is None

        # After connect, session should be initialized
        oi.connect()
        assert oi.session is not None

        # Session should be requests.Session
        import requests

        assert isinstance(oi.session, requests.Session)

    def test_timeout_configuration(self):
        """Test that timeout is configurable."""
        # Default timeout
        oi1 = OpportunityInsightsConnector()
        assert oi1.timeout == 60

        # Custom timeout
        oi2 = OpportunityInsightsConnector(timeout=120)
        assert oi2.timeout == 120

    def test_max_retries_configuration(self):
        """Test that max_retries is configurable."""
        # Default retries
        oi1 = OpportunityInsightsConnector()
        assert oi1.max_retries == 3

        # Custom retries
        oi2 = OpportunityInsightsConnector(max_retries=5)
        assert oi2.max_retries == 5


# ============================================================
# NAMING CONVENTION TESTS
# ============================================================


class TestNamingConventions:
    """Test that connector follows naming conventions."""

    def test_class_name_follows_convention(self):
        """Test that class name follows CamelCase convention."""
        class_name = OpportunityInsightsConnector.__name__
        assert class_name.endswith("Connector")
        assert class_name[0].isupper()

    def test_public_methods_use_snake_case(self):
        """Test that public methods use snake_case."""
        oi = OpportunityInsightsConnector()
        public_methods = [
            name for name in dir(oi) if not name.startswith("_") and callable(getattr(oi, name))
        ]

        for method_name in public_methods:
            # Should be snake_case (lowercase with underscores)
            assert method_name.islower() or "_" in method_name

    def test_private_methods_start_with_underscore(self):
        """Test that private methods start with underscore."""
        private_methods = [
            "_get_api_key",
            "_download_file",
            "_normalize_column_names",
            "_aggregate_atlas",
            "_init_session",
        ]

        for method_name in private_methods:
            assert hasattr(OpportunityInsightsConnector, method_name)
            assert method_name.startswith("_")

    def test_data_attributes_use_underscore_prefix(self):
        """Test that internal data attributes use underscore prefix."""
        oi = OpportunityInsightsConnector()

        # Internal data should be prefixed with underscore
        assert hasattr(oi, "_atlas_data")
        assert hasattr(oi, "_social_capital_data")


# ============================================================
# BACKWARD COMPATIBILITY TESTS
# ============================================================


class TestBackwardCompatibility:
    """Test that connector maintains backward compatibility."""

    def test_default_parameters_maintained(self):
        """Test that default parameters haven't changed."""
        # Can instantiate with no parameters
        oi = OpportunityInsightsConnector()
        assert oi is not None

        # Default cache directory
        assert oi.cache.cache_dir.endswith(".krl_cache/mobility")

        # Default timeout
        assert oi.timeout == 60

        # Default data version
        assert oi.data_version == "latest"

    def test_fetch_opportunity_atlas_basic_call(self):
        """Test basic fetch_opportunity_atlas call works."""
        oi = OpportunityInsightsConnector()

        # Should work with minimal parameters
        result = oi.fetch_opportunity_atlas(geography="tract", state="44")

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_aggregation_methods_available(self):
        """Test that aggregation methods are available."""
        oi = OpportunityInsightsConnector()

        # Public aggregation methods
        assert hasattr(oi, "aggregate_to_county")
        assert hasattr(oi, "aggregate_to_cz")
        assert hasattr(oi, "aggregate_to_state")

        # All should be callable
        assert callable(oi.aggregate_to_county)
        assert callable(oi.aggregate_to_cz)
        assert callable(oi.aggregate_to_state)


# ============================================================
# DATA CONTRACT TESTS
# ============================================================


class TestDataContract:
    """Test that returned data adheres to expected contracts."""

    @pytest.mark.slow
    def test_dataframe_has_required_columns(self):
        """Test that returned DataFrame has required geographic columns."""
        oi = OpportunityInsightsConnector()
        data = oi.fetch_opportunity_atlas(geography="tract", state="44")

        # Required geographic columns
        assert "tract" in data.columns
        assert "county" in data.columns
        assert "state" in data.columns
        assert "cz" in data.columns

    @pytest.mark.slow
    def test_geographic_codes_are_strings(self):
        """Test that geographic codes are returned as strings."""
        oi = OpportunityInsightsConnector()
        data = oi.fetch_opportunity_atlas(geography="tract", state="44")

        assert data["state"].dtype == "object"  # strings
        assert data["county"].dtype == "object"
        assert data["tract"].dtype == "object"

    @pytest.mark.slow
    def test_metrics_are_numeric(self):
        """Test that metric columns are numeric."""
        oi = OpportunityInsightsConnector()
        data = oi.fetch_opportunity_atlas(geography="tract", state="44", metrics=["kfr_pooled_p25"])

        assert pd.api.types.is_numeric_dtype(data["kfr_pooled_p25"])

    @pytest.mark.slow
    def test_no_duplicate_indices(self):
        """Test that returned DataFrame has no duplicate indices."""
        oi = OpportunityInsightsConnector()
        data = oi.fetch_opportunity_atlas(geography="tract", state="44")

        assert not data.index.has_duplicates


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
