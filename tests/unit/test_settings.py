"""
Unit tests for the settings configuration module.

Tests Pydantic settings, environment variable loading,
and configuration validation.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from config.settings import Settings, get_settings


class TestSettingsModel:
    """Test suite for Settings Pydantic model."""

    @patch.dict(os.environ, {}, clear=True)
    def test_settings_requires_openai_api_key(self):
        """Test that Settings requires OpenAI API key."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(_env_file=None)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == "openai_api_key" for error in errors)

    def test_settings_with_valid_openai_key(self):
        """Test Settings creation with valid OpenAI API key."""
        settings = Settings(openai_api_key="test_key_12345")

        assert settings.openai_api_key == "test_key_12345"
        assert settings.app_name == "StockIQ"
        assert settings.app_version == "1.0.0"
        assert settings.host == "127.0.0.1"
        assert settings.port == 8000
        assert settings.debug is True

    def test_settings_default_values(self):
        """Test that default values are properly set."""
        settings = Settings(openai_api_key="test_key")

        assert settings.research_db_path == "research_database"
        assert settings.tmp_path == "tmp"
        assert settings.max_tokens_per_request == 4000
        assert settings.agent_temperature == 0.7
        assert settings.reload is True

    def test_settings_custom_values(self):
        """Test Settings with custom values."""
        settings = Settings(
            openai_api_key="test_key",
            app_name="CustomStockIQ",
            port=9000,
            debug=False,
            max_tokens_per_request=2000,
        )

        assert settings.app_name == "CustomStockIQ"
        assert settings.port == 9000
        assert settings.debug is False
        assert settings.max_tokens_per_request == 2000


class TestSettingsEnvironmentLoading:
    """Test suite for environment variable loading."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env_test_key", "PORT": "8080"})
    def test_settings_loads_from_environment(self):
        """Test that settings load from environment variables."""
        settings = Settings()

        assert settings.openai_api_key == "env_test_key"
        assert settings.port == 8080

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env_key", "DEBUG": "false"})
    def test_boolean_environment_variables(self):
        """Test that boolean environment variables are properly parsed."""
        settings = Settings()

        assert settings.debug is False

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env_key", "AGENT_TEMPERATURE": "0.5"})
    def test_float_environment_variables(self):
        """Test that float environment variables are properly parsed."""
        settings = Settings()

        assert settings.agent_temperature == 0.5


class TestGetSettingsFunction:
    """Test suite for get_settings function."""

    @patch("config.settings.Settings")
    def test_get_settings_returns_settings_instance(self, mock_settings_class):
        """Test that get_settings returns a Settings instance."""
        mock_instance = MagicMock()
        mock_settings_class.return_value = mock_instance

        # Clear any cached result
        get_settings.cache_clear()

        result = get_settings()

        assert result == mock_instance
        mock_settings_class.assert_called_once()

    @patch("config.settings.Settings")
    def test_get_settings_caches_result(self, mock_settings_class):
        """Test that get_settings caches the result using lru_cache."""
        mock_instance = MagicMock()
        mock_settings_class.return_value = mock_instance

        # Clear any cached result
        get_settings.cache_clear()

        # Call twice
        result1 = get_settings()
        result2 = get_settings()

        # Should return same instance
        assert result1 == result2
        # Should only create Settings once due to caching
        mock_settings_class.assert_called_once()
