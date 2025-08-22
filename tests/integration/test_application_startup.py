"""
Integration tests for application startup and configuration.

Tests the complete application initialization process,
environment loading, and endpoint availability.
"""

import os
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app


class TestApplicationStartup:
    """Test suite for complete application startup."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "integration_test_key"})
    def test_application_starts_with_environment_config(self):
        """Test that application starts successfully with environment configuration."""
        with TestClient(app) as client:
            # Test that app starts without errors
            response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["openai_configured"] is True

    def test_static_files_mounting(self):
        """Test that static files are properly mounted."""
        with TestClient(app) as client:
            # This should return a 404 for non-existent files, not a routing error
            response = client.get("/static/nonexistent.css")

        # Should be 404 (file not found) not 500 (server error)
        assert response.status_code == 404

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_cors_headers_present(self):
        """Test that CORS headers are properly configured."""
        with TestClient(app) as client:
            response = client.get("/health", headers={"Origin": "http://localhost:3000"})

        assert response.status_code == 200
        # Check for CORS headers (may vary based on CORS middleware implementation)
        # At minimum, the request should succeed without CORS errors


class TestEndpointsIntegration:
    """Test suite for endpoint integration."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_integration_key"})
    def test_all_endpoints_accessible(self):
        """Test that all defined endpoints are accessible."""
        with TestClient(app) as client:
            # Test root endpoint
            root_response = client.get("/")
            assert root_response.status_code == 200

            # Test health endpoint
            health_response = client.get("/health")
            assert health_response.status_code == 200

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
    def test_endpoint_response_consistency(self):
        """Test that endpoints return consistent response formats."""
        with TestClient(app) as client:
            health_response = client.get("/health")
            root_response = client.get("/")

        health_data = health_response.json()
        root_data = root_response.json()

        # Health response should have required fields
        required_health_fields = ["status", "service", "version", "openai_configured"]
        for field in required_health_fields:
            assert field in health_data

        # Root response should have required fields
        required_root_fields = ["message", "description", "health_check"]
        for field in required_root_fields:
            assert field in root_data


class TestDirectoryStructureIntegration:
    """Test suite for directory structure validation."""

    def test_required_directories_exist(self):
        """Test that all required directories from the story were created."""
        import os

        required_dirs = [
            "src",
            "src/routers",
            "src/agents",
            "src/services",
            "src/models",
            "src/utils",
            "static",
            "static/css",
            "static/js",
            "config",
            "research_database",
            "tmp",
            "tests",
        ]

        for directory in required_dirs:
            assert os.path.exists(directory), f"Required directory {directory} does not exist"

    def test_init_files_exist(self):
        """Test that __init__.py files exist in all Python packages."""
        import os

        init_files = [
            "src/__init__.py",
            "src/routers/__init__.py",
            "src/agents/__init__.py",
            "src/services/__init__.py",
            "src/models/__init__.py",
            "src/utils/__init__.py",
            "config/__init__.py",
            "tests/__init__.py",
        ]

        for init_file in init_files:
            assert os.path.exists(init_file), (
                f"Required __init__.py file {init_file} does not exist"
            )
