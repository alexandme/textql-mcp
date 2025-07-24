"""Feature flag management system for textql-mcp.

This module provides a flexible feature flag system that allows enabling/disabling
features at runtime without requiring server restarts. Features can be controlled
via configuration files or environment variables.
"""

import os
import functools
from typing import Dict, Any, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class FeatureFlag(str, Enum):
    """Enumeration of available feature flags."""

    # Core functionality flags
    ENABLE_QUERY_GRAPH = "enable_query_graph"
    ENABLE_SCHEMA_FETCH = "enable_schema_fetch"
    ENABLE_NATURAL_LANGUAGE = "enable_natural_language"

    # Admin and management flags
    ENABLE_ADMIN_ENDPOINTS = "enable_admin_endpoints"
    ENABLE_FLAG_RUNTIME_UPDATES = "enable_flag_runtime_updates"

    # Security and access control flags
    ENABLE_AUTH_CHECKS = "enable_auth_checks"
    ENABLE_RATE_LIMITING = "enable_rate_limiting"

    # Experimental features
    ENABLE_EXPERIMENTAL_FEATURES = "enable_experimental_features"


class FeatureFlagManager:
    """Manages feature flags for the application.

    Feature flags can be loaded from:
    1. Configuration files (TOML/YAML)
    2. Environment variables (prefixed with TEXTQL_FF_)
    3. Runtime updates (if enabled)

    Environment variables take precedence over config files.
    """

    ENV_PREFIX = "TEXTQL_FF_"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the feature flag manager.

        Args:
            config: Optional configuration dictionary containing feature flags
        """
        self.flags: Dict[str, bool] = {}
        self._load_defaults()

        if config:
            self._load_from_config(config)

        self._load_from_env()
        self._log_flag_status()

    def _load_defaults(self):
        """Load default feature flag values."""
        # Default to enabling core features, disabling admin/experimental
        self.flags = {
            FeatureFlag.ENABLE_QUERY_GRAPH.value: True,
            FeatureFlag.ENABLE_SCHEMA_FETCH.value: True,
            FeatureFlag.ENABLE_NATURAL_LANGUAGE.value: False,
            FeatureFlag.ENABLE_ADMIN_ENDPOINTS.value: False,
            FeatureFlag.ENABLE_FLAG_RUNTIME_UPDATES.value: False,
            FeatureFlag.ENABLE_AUTH_CHECKS.value: False,
            FeatureFlag.ENABLE_RATE_LIMITING.value: False,
            FeatureFlag.ENABLE_EXPERIMENTAL_FEATURES.value: False,
        }

    def _load_from_config(self, config: Dict[str, Any]):
        """Load feature flags from configuration dictionary.

        Args:
            config: Configuration dictionary, expects 'feature_flags' section
        """
        feature_flags = config.get("feature_flags", {})
        for flag, value in feature_flags.items():
            if flag in [f.value for f in FeatureFlag]:
                self.flags[flag] = bool(value)
                logger.debug(f"Loaded feature flag from config: {flag}={value}")
            else:
                logger.warning(f"Unknown feature flag in config: {flag}")

    def _load_from_env(self):
        """Load feature flags from environment variables.

        Environment variables should be prefixed with TEXTQL_FF_ and use
        uppercase flag names. For example:
        - TEXTQL_FF_ENABLE_QUERY_GRAPH=true
        - TEXTQL_FF_ENABLE_ADMIN_ENDPOINTS=false
        """
        for flag in FeatureFlag:
            env_var = f"{self.ENV_PREFIX}{flag.value.upper()}"
            if env_var in os.environ:
                value = os.environ[env_var].lower() in ("true", "1", "yes", "on")
                self.flags[flag.value] = value
                logger.debug(f"Loaded feature flag from env: {flag.value}={value}")

    def _log_flag_status(self):
        """Log the current status of all feature flags."""
        logger.info("Feature flag status:")
        for flag, enabled in self.flags.items():
            status = "ENABLED" if enabled else "DISABLED"
            logger.info(f"  {flag}: {status}")

    def is_enabled(self, flag: str) -> bool:
        """Check if a feature flag is enabled.

        Args:
            flag: The feature flag name (use FeatureFlag enum values)

        Returns:
            True if the feature is enabled, False otherwise
        """
        # Handle both string and enum inputs
        if hasattr(flag, "value"):
            flag = flag.value

        return self.flags.get(flag, False)

    def set_flag(self, flag: str, enabled: bool) -> bool:
        """Set a feature flag at runtime.

        Args:
            flag: The feature flag name
            enabled: Whether to enable or disable the flag

        Returns:
            True if the flag was set successfully, False otherwise
        """
        if not self.is_enabled(FeatureFlag.ENABLE_FLAG_RUNTIME_UPDATES):
            logger.warning("Runtime flag updates are disabled")
            return False

        if hasattr(flag, "value"):
            flag = flag.value

        if flag not in [f.value for f in FeatureFlag]:
            logger.error(f"Unknown feature flag: {flag}")
            return False

        old_value = self.flags.get(flag, False)
        self.flags[flag] = enabled
        logger.info(f"Feature flag '{flag}' changed from {old_value} to {enabled}")
        return True

    def get_all_flags(self) -> Dict[str, bool]:
        """Get the current state of all feature flags.

        Returns:
            Dictionary mapping flag names to their enabled status
        """
        return self.flags.copy()

    def get_enabled_features(self) -> list[str]:
        """Get a list of all enabled features.

        Returns:
            List of enabled feature flag names
        """
        return [flag for flag, enabled in self.flags.items() if enabled]


def feature_flag_required(flag: FeatureFlag, error_message: Optional[str] = None):
    """Decorator to protect functions/tools with feature flags.

    This decorator checks if a feature flag is enabled before allowing
    the decorated function to execute. If the flag is disabled, it returns
    an error response.

    Args:
        flag: The feature flag that must be enabled
        error_message: Optional custom error message

    Example:
        @feature_flag_required(FeatureFlag.ENABLE_QUERY_GRAPH)
        async def query_graph(ctx, gql_query: str):
            # Tool implementation
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Try to get context from kwargs or args
            ctx = kwargs.get("ctx")
            if ctx is None and args:
                # Check if first arg might be context
                ctx = args[0] if hasattr(args[0], "lifespan_ctx") else None

            if ctx and hasattr(ctx, "lifespan_ctx"):
                feature_flags = getattr(ctx.lifespan_ctx, "feature_flags", None)
                if feature_flags and not feature_flags.is_enabled(flag):
                    default_msg = f"Feature '{flag.value}' is not enabled"
                    return {
                        "error": error_message or default_msg,
                        "feature_required": flag.value,
                        "enabled": False,
                    }
            else:
                logger.warning(f"Could not access feature flags in {func.__name__}")

            # Call the original function
            return await func(*args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar logic for synchronous functions
            ctx = kwargs.get("ctx")
            if ctx is None and args:
                ctx = args[0] if hasattr(args[0], "lifespan_ctx") else None

            if ctx and hasattr(ctx, "lifespan_ctx"):
                feature_flags = getattr(ctx.lifespan_ctx, "feature_flags", None)
                if feature_flags and not feature_flags.is_enabled(flag):
                    default_msg = f"Feature '{flag.value}' is not enabled"
                    return {
                        "error": error_message or default_msg,
                        "feature_required": flag.value,
                        "enabled": False,
                    }
            else:
                logger.warning(f"Could not access feature flags in {func.__name__}")

            return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def check_feature_flag(ctx: Any, flag: FeatureFlag) -> bool:
    """Utility function to check if a feature flag is enabled.

    Args:
        ctx: The context object containing feature flags
        flag: The feature flag to check

    Returns:
        True if enabled, False otherwise
    """
    if hasattr(ctx, "lifespan_ctx"):
        feature_flags = getattr(ctx.lifespan_ctx, "feature_flags", None)
        if feature_flags:
            return feature_flags.is_enabled(flag)
    return False
