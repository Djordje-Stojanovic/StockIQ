"""
Unit tests for the main FastAPI application module.

Tests the FastAPI application creation, health check endpoint,
and basic application configuration.
"""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.main import app, create_app


class TestFastAPIApplication:
    """Test suite for FastAPI application functionality."""

    def test_create_app_returns_fastapi_instance(self):
        """Test that create_app returns a FastAPI instance."""
        with patch('src.main.get_settings') as mock_settings:
            mock_settings.return_value = MagicMock(openai_api_key="test_key")
            test_app = create_app()
            assert test_app.title == "StockIQ"
            assert test_app.description == "Collaborative multi-agent stock analysis platform"
            assert test_app.version == "1.0.0"

    def test_app_instance_exists(self):
        """Test that app instance is created."""
        assert app is not None
        assert app.title == "StockIQ"


class TestHealthCheckEndpoint:
    """Test suite for health check endpoint."""

    @patch('src.main.get_settings')
    def test_health_check_returns_healthy_status(self, mock_settings):
        """Test health check endpoint returns healthy status."""
        mock_settings.return_value = MagicMock(openai_api_key="test_key")

        with TestClient(app) as client:
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "StockIQ"
        assert data["version"] == "1.0.0"
        assert data["openai_configured"] is True

    @patch('src.main.get_settings')
    def test_health_check_without_openai_key(self, mock_settings):
        """Test health check when OpenAI key is not configured."""
        mock_settings.return_value = MagicMock(openai_api_key="")

        with TestClient(app) as client:
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["openai_configured"] is False


class TestRootEndpoint:
    """Test suite for root endpoint."""

    @patch('src.main.get_settings')
    def test_root_endpoint_returns_welcome_message(self, mock_settings):
        """Test root endpoint returns welcome information."""
        mock_settings.return_value = MagicMock(openai_api_key="test_key")

        with TestClient(app) as client:
            response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to StockIQ"
        assert data["description"] == "Collaborative multi-agent stock analysis platform"
        assert data["health_check"] == "/health"


class TestMiddlewareConfiguration:
    """Test suite for middleware configuration."""

    @patch('src.main.get_settings')
    def test_cors_middleware_configured(self, mock_settings):
        """Test that CORS middleware allows expected origins."""
        mock_settings.return_value = MagicMock(openai_api_key="test_key")

        with TestClient(app) as client:
            response = client.options(
                "/health",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                }
            )

        # CORS should allow the request
        assert response.status_code in [200, 204]
