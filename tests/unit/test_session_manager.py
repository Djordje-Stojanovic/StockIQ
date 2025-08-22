"""Unit tests for session manager service."""

from datetime import datetime

from src.services.session_manager import SessionManager


class TestSessionManager:
    """Test SessionManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = SessionManager()

    def test_create_session(self):
        """Test session creation."""
        ticker = "ASML"
        session = self.manager.create_session(ticker)

        assert session["ticker_symbol"] == ticker
        assert session["status"] == "active"
        assert "session_id" in session
        assert session["user_expertise_level"] is None
        assert len(session["assessment_responses"]) == 0
        assert isinstance(session["created_at"], datetime)

    def test_create_session_uppercase_conversion(self):
        """Test that ticker is converted to uppercase."""
        session = self.manager.create_session("asml")
        assert session["ticker_symbol"] == "ASML"

    def test_get_session(self):
        """Test retrieving a session."""
        session = self.manager.create_session("MSFT")
        session_id = session["session_id"]

        retrieved = self.manager.get_session(session_id)
        assert retrieved is not None
        assert retrieved["session_id"] == session_id
        assert retrieved["ticker_symbol"] == "MSFT"

    def test_get_nonexistent_session(self):
        """Test retrieving non-existent session returns None."""
        result = self.manager.get_session("nonexistent-id")
        assert result is None

    def test_update_session(self):
        """Test updating session data."""
        session = self.manager.create_session("COST")
        session_id = session["session_id"]

        updates = {
            "user_expertise_level": 7,
            "report_complexity": "comprehensive",
            "status": "research",
        }

        updated = self.manager.update_session(session_id, updates)

        assert updated is not None
        assert updated["user_expertise_level"] == 7
        assert updated["report_complexity"] == "comprehensive"
        assert updated["status"] == "research"
        assert updated["updated_at"] > session["created_at"]

    def test_update_nonexistent_session(self):
        """Test updating non-existent session returns None."""
        result = self.manager.update_session("nonexistent-id", {"status": "error"})
        assert result is None

    def test_delete_session(self):
        """Test deleting a session."""
        session = self.manager.create_session("GOOGL")
        session_id = session["session_id"]

        # Verify session exists
        assert self.manager.get_session(session_id) is not None

        # Delete session
        result = self.manager.delete_session(session_id)
        assert result is True

        # Verify session is gone
        assert self.manager.get_session(session_id) is None

    def test_delete_nonexistent_session(self):
        """Test deleting non-existent session returns False."""
        result = self.manager.delete_session("nonexistent-id")
        assert result is False

    def test_get_active_sessions(self):
        """Test retrieving active sessions."""
        # Create multiple sessions
        session1 = self.manager.create_session("AAPL")
        session2 = self.manager.create_session("TSLA")
        session3 = self.manager.create_session("NVDA")

        # Update one to non-active status
        self.manager.update_session(session2["session_id"], {"status": "complete"})

        active = self.manager.get_active_sessions()

        assert len(active) == 2
        assert session1["session_id"] in active
        assert session2["session_id"] not in active
        assert session3["session_id"] in active

    def test_research_database_path(self):
        """Test that research database path is properly formatted."""
        session = self.manager.create_session("META")

        expected_path = f"research_database/sessions/{session['session_id']}/META"
        assert session["research_database_path"] == expected_path
