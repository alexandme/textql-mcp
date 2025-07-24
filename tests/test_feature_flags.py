"""Tests for the feature flag management system."""

import os
import pytest
from unittest.mock import patch, MagicMock
from textql_mcp.core.feature_flags import (
    FeatureFlagManager,
    FeatureFlag,
    feature_flag_required,
    check_feature_flag,
)


class TestFeatureFlagManager:
    """Test cases for FeatureFlagManager."""

    def test_default_flags(self):
        """Test that default flags are loaded correctly."""
        manager = FeatureFlagManager()

        # Core features should be enabled by default
        assert manager.is_enabled(FeatureFlag.ENABLE_QUERY_GRAPH) is True
        assert manager.is_enabled(FeatureFlag.ENABLE_SCHEMA_FETCH) is True

        # Admin and experimental features should be disabled by default
        assert manager.is_enabled(FeatureFlag.ENABLE_ADMIN_ENDPOINTS) is False
        assert manager.is_enabled(FeatureFlag.ENABLE_EXPERIMENTAL_FEATURES) is False

    def test_load_from_config(self):
        """Test loading feature flags from configuration."""
        config = {
            "feature_flags": {
                "enable_query_graph": False,
                "enable_admin_endpoints": True,
                "unknown_flag": True,  # Should be ignored with warning
            }
        }

        manager = FeatureFlagManager(config)

        assert manager.is_enabled(FeatureFlag.ENABLE_QUERY_GRAPH) is False
        assert manager.is_enabled(FeatureFlag.ENABLE_ADMIN_ENDPOINTS) is True
        # Default value should remain for unspecified flags
        assert manager.is_enabled(FeatureFlag.ENABLE_SCHEMA_FETCH) is True

    def test_load_from_env(self):
        """Test loading feature flags from environment variables."""
        with patch.dict(
            os.environ,
            {
                "TEXTQL_FF_ENABLE_QUERY_GRAPH": "false",
                "TEXTQL_FF_ENABLE_ADMIN_ENDPOINTS": "true",
                "TEXTQL_FF_ENABLE_EXPERIMENTAL_FEATURES": "1",
            },
        ):
            manager = FeatureFlagManager()

            assert manager.is_enabled(FeatureFlag.ENABLE_QUERY_GRAPH) is False
            assert manager.is_enabled(FeatureFlag.ENABLE_ADMIN_ENDPOINTS) is True
            assert manager.is_enabled(FeatureFlag.ENABLE_EXPERIMENTAL_FEATURES) is True

    def test_env_overrides_config(self):
        """Test that environment variables override config file settings."""
        config = {
            "feature_flags": {
                "enable_query_graph": True,
            }
        }

        with patch.dict(
            os.environ,
            {
                "TEXTQL_FF_ENABLE_QUERY_GRAPH": "false",
            },
        ):
            manager = FeatureFlagManager(config)

            # Environment should override config
            assert manager.is_enabled(FeatureFlag.ENABLE_QUERY_GRAPH) is False

    def test_set_flag_runtime_updates_disabled(self):
        """Test that runtime updates fail when disabled."""
        manager = FeatureFlagManager()

        # Runtime updates are disabled by default
        result = manager.set_flag(FeatureFlag.ENABLE_QUERY_GRAPH, False)
        assert result is False
        # Flag should remain unchanged
        assert manager.is_enabled(FeatureFlag.ENABLE_QUERY_GRAPH) is True

    def test_set_flag_runtime_updates_enabled(self):
        """Test runtime flag updates when enabled."""
        config = {
            "feature_flags": {
                "enable_flag_runtime_updates": True,
            }
        }
        manager = FeatureFlagManager(config)

        # Should be able to update flags
        result = manager.set_flag(FeatureFlag.ENABLE_QUERY_GRAPH, False)
        assert result is True
        assert manager.is_enabled(FeatureFlag.ENABLE_QUERY_GRAPH) is False

        # Test with string input
        result = manager.set_flag("enable_query_graph", True)
        assert result is True
        assert manager.is_enabled("enable_query_graph") is True

    def test_get_all_flags(self):
        """Test getting all flag states."""
        manager = FeatureFlagManager()
        flags = manager.get_all_flags()

        assert isinstance(flags, dict)
        assert len(flags) == len(FeatureFlag)
        assert all(isinstance(v, bool) for v in flags.values())

    def test_get_enabled_features(self):
        """Test getting only enabled features."""
        config = {
            "feature_flags": {
                "enable_query_graph": True,
                "enable_schema_fetch": True,
                "enable_admin_endpoints": False,
            }
        }
        manager = FeatureFlagManager(config)

        enabled = manager.get_enabled_features()
        assert "enable_query_graph" in enabled
        assert "enable_schema_fetch" in enabled
        assert "enable_admin_endpoints" not in enabled


class TestFeatureFlagDecorator:
    """Test cases for the feature flag decorator."""

    def test_sync_function_flag_enabled(self):
        """Test decorator on sync function with flag enabled."""
        # Create mock context with feature flags
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_query_graph": True}}
        )

        @feature_flag_required(FeatureFlag.ENABLE_QUERY_GRAPH)
        def test_function(ctx):
            return {"result": "success"}

        result = test_function(ctx=ctx)
        assert result == {"result": "success"}

    def test_sync_function_flag_disabled(self):
        """Test decorator on sync function with flag disabled."""
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_query_graph": False}}
        )

        @feature_flag_required(FeatureFlag.ENABLE_QUERY_GRAPH)
        def test_function(ctx):
            return {"result": "success"}

        result = test_function(ctx=ctx)
        assert result["error"] == "Feature 'enable_query_graph' is not enabled"
        assert result["feature_required"] == "enable_query_graph"
        assert result["enabled"] is False

    @pytest.mark.asyncio
    async def test_async_function_flag_enabled(self):
        """Test decorator on async function with flag enabled."""
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_query_graph": True}}
        )

        @feature_flag_required(FeatureFlag.ENABLE_QUERY_GRAPH)
        async def test_function(ctx):
            return {"result": "success"}

        result = await test_function(ctx=ctx)
        assert result == {"result": "success"}

    @pytest.mark.asyncio
    async def test_async_function_flag_disabled(self):
        """Test decorator on async function with flag disabled."""
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_query_graph": False}}
        )

        @feature_flag_required(FeatureFlag.ENABLE_QUERY_GRAPH)
        async def test_function(ctx):
            return {"result": "success"}

        result = await test_function(ctx=ctx)
        assert result["error"] == "Feature 'enable_query_graph' is not enabled"

    def test_custom_error_message(self):
        """Test decorator with custom error message."""
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_admin_endpoints": False}}
        )

        @feature_flag_required(
            FeatureFlag.ENABLE_ADMIN_ENDPOINTS, "Admin access required"
        )
        def test_function(ctx):
            return {"result": "success"}

        result = test_function(ctx=ctx)
        assert result["error"] == "Admin access required"

    def test_context_as_positional_arg(self):
        """Test decorator when context is passed as positional argument."""
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_query_graph": True}}
        )

        @feature_flag_required(FeatureFlag.ENABLE_QUERY_GRAPH)
        def test_function(context, data):
            return {"data": data}

        result = test_function(ctx, "test_data")
        assert result == {"data": "test_data"}


class TestCheckFeatureFlag:
    """Test cases for the check_feature_flag utility."""

    def test_check_feature_flag_enabled(self):
        """Test checking an enabled feature flag."""
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_query_graph": True}}
        )

        assert check_feature_flag(ctx, FeatureFlag.ENABLE_QUERY_GRAPH) is True

    def test_check_feature_flag_disabled(self):
        """Test checking a disabled feature flag."""
        ctx = MagicMock()
        ctx.lifespan_ctx.feature_flags = FeatureFlagManager(
            {"feature_flags": {"enable_query_graph": False}}
        )

        assert check_feature_flag(ctx, FeatureFlag.ENABLE_QUERY_GRAPH) is False

    def test_check_feature_flag_no_context(self):
        """Test checking feature flag with invalid context."""
        ctx = MagicMock()
        # No lifespan_ctx attribute
        del ctx.lifespan_ctx

        assert check_feature_flag(ctx, FeatureFlag.ENABLE_QUERY_GRAPH) is False
