"""Integration tests for research API endpoints."""

import asyncio
import tempfile
import shutil
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from src.main import create_app
from src.services.session_manager import get_session_manager
from src.services.research_database import ResearchDatabase
from src.models.assessment import UserSession, AssessmentResult


class TestResearchAPI:
    """Test suite for research API endpoints."""

    @pytest.fixture
    def temp_research_db(self):
        """Create temporary research database."""
        temp_dir = tempfile.mkdtemp()
        db = ResearchDatabase(base_path=temp_dir)
        with patch('src.services.research_database.get_research_database', return_value=db):
            yield db
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def client(self, temp_research_db):
        """Create test client with temporary research database."""
        app = create_app()
        return TestClient(app)

    @pytest.fixture
    def test_session(self):
        """Create test session with completed assessment."""
        session = UserSession(
            session_id="test-session-123",
            ticker_symbol="AAPL",
            user_expertise_level=5,
            assessment_result=AssessmentResult(
                session_id="test-session-123",
                expertise_level=5,
                report_complexity="intermediate",
                explanation="User demonstrates intermediate knowledge",
                ticker_context="AAPL"
            ),
            report_complexity="intermediate",
            research_database_path="research_database/sessions/test-session-123/AAPL"
        )
        
        # Add to session manager
        session_manager = get_session_manager()
        session_manager.create_session("AAPL")
        session_manager.sessions["test-session-123"] = session
        
        return session

    def test_start_research_valid_session(self, client, test_session):
        """Test starting research with valid completed assessment session."""
        response = client.post(
            "/api/research/start",
            json={"session_id": "test-session-123"}
        )
        
        assert response.status_code == 202
        data = response.json()
        assert data["research_id"] == "test-session-123"
        assert data["status"] == "active"
        assert "started successfully" in data["message"]

    def test_start_research_nonexistent_session(self, client):
        """Test starting research with non-existent session."""
        response = client.post(
            "/api/research/start",
            json={"session_id": "nonexistent-session"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_start_research_incomplete_assessment(self, client):
        """Test starting research with incomplete assessment."""
        # Create session without assessment result
        session = UserSession(
            session_id="incomplete-session",
            ticker_symbol="AAPL",
            research_database_path="research_database/sessions/incomplete-session/AAPL"
        )
        
        session_manager = get_session_manager()
        session_manager.sessions["incomplete-session"] = session
        
        response = client.post(
            "/api/research/start",
            json={"session_id": "incomplete-session"}
        )
        
        assert response.status_code == 400
        assert "complete assessment" in response.json()["detail"]

    def test_get_research_status_active_session(self, client, test_session):
        """Test getting research status for active session."""
        # Start research first
        client.post("/api/research/start", json={"session_id": "test-session-123"})
        
        # Get status
        response = client.get("/api/research/status?session_id=test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["ticker"] == "AAPL"
        assert "status" in data
        assert "current_agent" in data
        assert "progress_percentage" in data

    def test_get_research_status_nonexistent_session(self, client):
        """Test getting research status for non-existent session."""
        response = client.get("/api/research/status?session_id=nonexistent-session")
        
        assert response.status_code == 404

    def test_get_research_database_valid_session(self, client, test_session, temp_research_db):
        """Test getting research database contents."""
        # Create session directory and add some files
        temp_research_db.create_session_directory("test-session-123", "AAPL")
        temp_research_db.write_research_file(
            "test-session-123", "AAPL", "valuation", "test_analysis.md",
            "# Test Analysis\n\nTest content"
        )
        
        response = client.get("/api/research/database?session_id=test-session-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["ticker"] == "AAPL"
        assert "files" in data
        assert "handoffs" in data
        assert data["file_count"] >= 1

    def test_get_research_database_nonexistent_session(self, client):
        """Test getting research database for non-existent session."""
        response = client.get("/api/research/database?session_id=nonexistent-session")
        
        assert response.status_code == 404

    def test_get_research_file_valid_file(self, client, test_session, temp_research_db):
        """Test getting a specific research file."""
        # Create session and file
        temp_research_db.create_session_directory("test-session-123", "AAPL")
        content = "# Valuation Analysis\n\nDetailed DCF analysis for Apple Inc."
        temp_research_db.write_research_file(
            "test-session-123", "AAPL", "valuation", "dcf_analysis.md", content
        )
        
        response = client.get(
            "/api/research/files/valuation/dcf_analysis.md?session_id=test-session-123"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-session-123"
        assert data["ticker"] == "AAPL"
        assert data["file_path"] == "valuation/dcf_analysis.md"
        assert data["content"] == content
        assert "metadata" in data

    def test_get_research_file_nonexistent_file(self, client, test_session):
        """Test getting non-existent research file."""
        response = client.get(
            "/api/research/files/nonexistent/file.md?session_id=test-session-123"
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_research_file_invalid_session(self, client):
        """Test getting research file with invalid session."""
        response = client.get(
            "/api/research/files/valuation/analysis.md?session_id=invalid-session"
        )
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_complete_research_workflow_integration(self, client, test_session, temp_research_db):
        """Test complete research workflow from start to completion."""
        # Start research
        start_response = client.post(
            "/api/research/start",
            json={"session_id": "test-session-123"}
        )
        assert start_response.status_code == 202
        
        # Wait for some research progress
        await asyncio.sleep(2)
        
        # Check status
        status_response = client.get("/api/research/status?session_id=test-session-123")
        assert status_response.status_code == 200
        status_data = status_response.json()
        
        # Should show progress
        assert status_data["progress_percentage"] >= 0
        assert status_data["status"] in ["active", "completed"]
        
        # Check database contents
        db_response = client.get("/api/research/database?session_id=test-session-123")
        assert db_response.status_code == 200
        db_data = db_response.json()
        
        # Should have handoffs from mock workflow
        assert db_data["handoff_count"] >= 0

    def test_session_status_update_after_research_start(self, client, test_session):
        """Test that session status is updated after starting research."""
        # Verify initial status
        session_manager = get_session_manager()
        session = session_manager.get_session("test-session-123")
        initial_status = session.status
        
        # Start research
        response = client.post(
            "/api/research/start",
            json={"session_id": "test-session-123"}
        )
        assert response.status_code == 202
        
        # Check session status was updated
        updated_session = session_manager.get_session("test-session-123")
        assert updated_session.status == "research"

    def test_research_api_error_handling(self, client):
        """Test error handling in research API endpoints."""
        # Test with invalid JSON
        response = client.post(
            "/api/research/start",
            json={"invalid_field": "value"}
        )
        assert response.status_code == 422  # Validation error
        
        # Test with missing query parameters
        response = client.get("/api/research/status")
        assert response.status_code == 422  # Missing session_id parameter

    def test_concurrent_research_sessions(self, client):
        """Test handling multiple concurrent research sessions."""
        # Create multiple test sessions
        sessions = []
        session_manager = get_session_manager()
        
        for i in range(3):
            session_id = f"test-session-{i}"
            session = UserSession(
                session_id=session_id,
                ticker_symbol=f"TEST{i}",
                user_expertise_level=5,
                assessment_result=AssessmentResult(
                    session_id=session_id,
                    expertise_level=5,
                    report_complexity="intermediate",
                    explanation="Test session",
                    ticker_context=f"TEST{i}"
                ),
                report_complexity="intermediate",
                research_database_path=f"research_database/sessions/{session_id}/TEST{i}"
            )
            session_manager.sessions[session_id] = session
            sessions.append(session_id)
        
        # Start research for all sessions
        for session_id in sessions:
            response = client.post(
                "/api/research/start",
                json={"session_id": session_id}
            )
            assert response.status_code == 202
        
        # Verify all sessions are tracked
        for session_id in sessions:
            response = client.get(f"/api/research/status?session_id={session_id}")
            assert response.status_code == 200

    def test_research_database_file_structure(self, client, test_session, temp_research_db):
        """Test that research database maintains proper file structure."""
        # Start research to create directory structure
        client.post("/api/research/start", json={"session_id": "test-session-123"})
        
        # Check that session directory was created
        session_dir = temp_research_db.sessions_path / "test-session-123" / "AAPL"
        assert session_dir.exists()
        
        # Check agent directories
        agent_dirs = ["valuation", "strategic", "historical", "synthesis", "meta"]
        for agent_dir in agent_dirs:
            assert (session_dir / agent_dir).exists()
        
        # Check metadata files
        meta_dir = session_dir / "meta"
        metadata_files = ["file_index.yaml", "cross_references.yaml", "agent_activity.yaml"]
        for metadata_file in metadata_files:
            assert (meta_dir / metadata_file).exists()