"""Integration tests for assessment API endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)


class TestAssessmentAPI:
    """Test assessment API endpoints."""

    def test_start_assessment_valid_ticker(self, client):
        """Test starting assessment with valid ticker."""
        response = client.post("/api/assessment/start", json={"ticker_symbol": "ASML"})

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert data["ticker_symbol"] == "ASML"
        assert data["status"] == "active"
        assert "created_at" in data
        assert data["message"] == "Session initialized for ASML"

    def test_start_assessment_lowercase_ticker(self, client):
        """Test that lowercase ticker is accepted and converted."""
        response = client.post("/api/assessment/start", json={"ticker_symbol": "msft"})

        assert response.status_code == 200
        data = response.json()
        assert data["ticker_symbol"] == "MSFT"

    def test_start_assessment_invalid_ticker_numbers(self, client):
        """Test validation rejects ticker with numbers."""
        response = client.post("/api/assessment/start", json={"ticker_symbol": "ABC123"})

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "only letters" in data["detail"]

    def test_start_assessment_invalid_ticker_too_long(self, client):
        """Test validation rejects ticker that's too long."""
        response = client.post("/api/assessment/start", json={"ticker_symbol": "VERYLONGTICKER"})

        assert response.status_code == 422  # Pydantic validation error
        data = response.json()
        assert "detail" in data
        # Pydantic returns validation errors in a different format

    def test_start_assessment_invalid_ticker_special_chars(self, client):
        """Test validation rejects ticker with special characters."""
        response = client.post("/api/assessment/start", json={"ticker_symbol": "AB-C"})

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "special characters" in data["detail"]

    def test_start_assessment_missing_ticker(self, client):
        """Test validation when ticker is missing."""
        response = client.post("/api/assessment/start", json={})

        assert response.status_code == 422  # Pydantic validation error

    def test_start_assessment_empty_ticker(self, client):
        """Test validation when ticker is empty string."""
        response = client.post("/api/assessment/start", json={"ticker_symbol": ""})

        assert response.status_code == 422  # Pydantic min_length validation

    def test_get_session(self, client):
        """Test retrieving session information."""
        # First create a session
        create_response = client.post("/api/assessment/start", json={"ticker_symbol": "GOOGL"})

        assert create_response.status_code == 200
        session_id = create_response.json()["session_id"]

        # Now retrieve the session
        get_response = client.get(f"/api/assessment/session/{session_id}")

        assert get_response.status_code == 200
        data = get_response.json()

        assert data["session_id"] == session_id
        assert data["ticker_symbol"] == "GOOGL"
        assert data["status"] == "active"

    def test_get_nonexistent_session(self, client):
        """Test retrieving non-existent session returns 404."""
        response = client.get("/api/assessment/session/nonexistent-id")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_multiple_sessions_isolation(self, client):
        """Test that multiple sessions are properly isolated."""
        # Create first session
        response1 = client.post("/api/assessment/start", json={"ticker_symbol": "AAPL"})
        session1_id = response1.json()["session_id"]

        # Create second session
        response2 = client.post("/api/assessment/start", json={"ticker_symbol": "TSLA"})
        session2_id = response2.json()["session_id"]

        # Verify sessions are different
        assert session1_id != session2_id

        # Verify each session has correct ticker
        session1 = client.get(f"/api/assessment/session/{session1_id}")
        assert session1.json()["ticker_symbol"] == "AAPL"

        session2 = client.get(f"/api/assessment/session/{session2_id}")
        assert session2.json()["ticker_symbol"] == "TSLA"
