"""Unit tests for assessment models."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from src.models.assessment import AssessmentQuestion, AssessmentResponse, UserSession


class TestUserSessionModel:
    """Test UserSession model validation."""

    def test_valid_session_creation(self):
        """Test creating a valid UserSession."""
        session = UserSession(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            ticker_symbol="ASML",
            research_database_path="research_database/sessions/test/ASML",
        )

        assert session.ticker_symbol == "ASML"
        assert session.status == "active"
        assert session.user_expertise_level is None
        assert len(session.assessment_responses) == 0

    def test_ticker_validation(self):
        """Test ticker symbol validation in model."""
        with pytest.raises(ValidationError) as exc_info:
            UserSession(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                ticker_symbol="ABC123",  # Invalid ticker
                research_database_path="test/path",
            )

        assert "ticker_symbol" in str(exc_info.value)

    def test_expertise_level_bounds(self):
        """Test expertise level validation bounds."""
        session_data = {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticker_symbol": "ASML",
            "research_database_path": "test/path",
        }

        # Valid expertise levels
        for level in [1, 5, 10]:
            session = UserSession(**session_data, user_expertise_level=level)
            assert session.user_expertise_level == level

        # Invalid expertise levels
        for level in [0, 11, -1]:
            with pytest.raises(ValidationError):
                UserSession(**session_data, user_expertise_level=level)

    def test_report_complexity_validation(self):
        """Test report complexity enum validation."""
        session_data = {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticker_symbol": "ASML",
            "research_database_path": "test/path",
        }

        # Valid complexities
        for complexity in ["comprehensive", "executive"]:
            session = UserSession(**session_data, report_complexity=complexity)
            assert session.report_complexity == complexity

        # Invalid complexity
        with pytest.raises(ValidationError):
            UserSession(**session_data, report_complexity="simple")

    def test_status_validation(self):
        """Test session status enum validation."""
        session_data = {
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "ticker_symbol": "ASML",
            "research_database_path": "test/path",
        }

        # Valid statuses
        for status in ["active", "research", "generation", "complete", "error"]:
            session = UserSession(**session_data, status=status)
            assert session.status == status

        # Invalid status
        with pytest.raises(ValidationError):
            UserSession(**session_data, status="invalid")

    def test_whitespace_stripping(self):
        """Test that whitespace is stripped from ticker."""
        session = UserSession(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            ticker_symbol="  ASML  ",
            research_database_path="test/path",
        )

        assert session.ticker_symbol == "ASML"


class TestAssessmentQuestion:
    """Test AssessmentQuestion model."""

    def test_valid_question_creation(self):
        """Test creating a valid assessment question."""
        question = AssessmentQuestion(
            question_id="q1",
            question_text="What is your investment experience?",
            options=["< 1 year", "1-3 years", "3-5 years", "> 5 years"],
            category="experience",
        )

        assert question.question_id == "q1"
        assert len(question.options) == 4
        assert question.weight == 1.0

    def test_weight_validation(self):
        """Test weight bounds validation."""
        question_data = {
            "question_id": "q1",
            "question_text": "Test question",
            "options": ["A", "B"],
            "category": "test",
        }

        # Valid weights
        for weight in [0, 1, 5, 10]:
            question = AssessmentQuestion(**question_data, weight=weight)
            assert question.weight == weight

        # Invalid weights
        for weight in [-1, 11]:
            with pytest.raises(ValidationError):
                AssessmentQuestion(**question_data, weight=weight)


class TestAssessmentResponse:
    """Test AssessmentResponse model."""

    def test_valid_response_creation(self):
        """Test creating a valid assessment response."""
        response = AssessmentResponse(question_id="q1", answer="1-3 years")

        assert response.question_id == "q1"
        assert response.answer == "1-3 years"
        assert isinstance(response.timestamp, datetime)
