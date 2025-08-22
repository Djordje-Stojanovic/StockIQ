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

    def test_get_assessment_questions_success(self, client):
        """Test getting assessment questions for valid session."""
        # First create a session
        create_response = client.post("/api/assessment/start", json={"ticker_symbol": "AAPL"})
        session_id = create_response.json()["session_id"]

        # Get assessment questions
        response = client.get(f"/api/assessment/questions?session_id={session_id}")

        assert response.status_code == 200
        data = response.json()

        assert "questions" in data
        assert len(data["questions"]) == 20

        # Verify question structure
        question = data["questions"][0]
        assert "id" in question
        assert "difficulty_level" in question
        assert "category" in question
        assert "question" in question
        assert "options" in question
        assert len(question["options"]) == 4
        assert "ticker_context" in question
        assert question["ticker_context"] == "AAPL"

    def test_get_assessment_questions_invalid_session(self, client):
        """Test getting questions for invalid session."""
        response = client.get("/api/assessment/questions?session_id=invalid-session-id")

        assert response.status_code == 400  # API returns 400 for invalid session format

    def test_submit_assessment_success(self, client):
        """Test submitting assessment responses successfully."""
        # Create session and get questions
        create_response = client.post("/api/assessment/start", json={"ticker_symbol": "AAPL"})
        session_id = create_response.json()["session_id"]

        questions_response = client.get(f"/api/assessment/questions?session_id={session_id}")
        questions = questions_response.json()["questions"]

        # Create sample responses
        responses = []
        for i, question in enumerate(questions):
            responses.append(
                {
                    "question_id": question["id"],
                    "selected_option": 0,  # Always select first option
                    "correct_option": question["correct_answer_index"],
                    "time_taken": 15.0 + i * 2.0,  # Varying time
                }
            )

        # Submit responses
        submit_data = {"session_id": session_id, "responses": responses}

        response = client.post("/api/assessment/submit", json=submit_data)

        assert response.status_code == 200
        data = response.json()

        assert "expertise_level" in data
        assert 1 <= data["expertise_level"] <= 10
        assert "report_complexity" in data
        assert data["report_complexity"] in ["comprehensive", "executive"]
        assert "explanation" in data
        assert "ticker_context" in data
        assert data["ticker_context"] == "AAPL"

    def test_submit_assessment_invalid_session(self, client):
        """Test submitting responses for invalid session."""
        submit_data = {
            "session_id": "invalid-session-id",
            "responses": [
                {"question_id": 1, "selected_option": 0, "correct_option": 0, "time_taken": 15.0}
            ],
        }

        response = client.post("/api/assessment/submit", json=submit_data)
        assert response.status_code == 404

    def test_submit_assessment_incomplete_responses(self, client):
        """Test submitting incomplete responses."""
        # Create session
        create_response = client.post("/api/assessment/start", json={"ticker_symbol": "AAPL"})
        session_id = create_response.json()["session_id"]

        # Submit only partial responses (less than 20)
        submit_data = {
            "session_id": session_id,
            "responses": [
                {"question_id": 1, "selected_option": 0, "correct_option": 0, "time_taken": 15.0}
            ],
        }

        response = client.post("/api/assessment/submit", json=submit_data)
        assert response.status_code == 400

    def test_complete_assessment_workflow(self, client):
        """Test complete assessment workflow from start to finish."""
        # 1. Start assessment
        start_response = client.post("/api/assessment/start", json={"ticker_symbol": "MSFT"})
        assert start_response.status_code == 200
        session_id = start_response.json()["session_id"]

        # 2. Get questions
        questions_response = client.get(f"/api/assessment/questions?session_id={session_id}")
        assert questions_response.status_code == 200
        questions = questions_response.json()["questions"]
        assert len(questions) == 20

        # 3. Submit responses
        responses = []
        for question in questions:
            responses.append(
                {
                    "question_id": question["id"],
                    "selected_option": question["correct_answer_index"],  # All correct
                    "correct_option": question["correct_answer_index"],
                    "time_taken": 20.0,
                }
            )

        submit_response = client.post(
            "/api/assessment/submit", json={"session_id": session_id, "responses": responses}
        )
        assert submit_response.status_code == 200

        # 4. Verify session updated with assessment result
        final_session = client.get(f"/api/assessment/session/{session_id}")
        assert final_session.status_code == 200
        session_data = final_session.json()

        # Should have assessment responses and result
        assert "assessment_responses" in session_data
        assert len(session_data["assessment_responses"]) == 20
