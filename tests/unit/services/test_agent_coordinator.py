"""Unit tests for agent coordinator service."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from src.services.agent_coordinator import AgentCoordinator
from src.models.collaboration import AgentHandoff, ResearchStatus


class TestAgentCoordinator:
    """Test suite for AgentCoordinator class."""

    @pytest.fixture
    def coordinator(self):
        """Create an AgentCoordinator instance for testing."""
        return AgentCoordinator(enable_retries=False)  # Disable retries for predictable testing

    @pytest.mark.asyncio
    async def test_start_research_process(self, coordinator):
        """Test starting a research process."""
        session_id = "test-session-123"
        ticker = "AAPL"
        expertise_level = 5

        research_id = await coordinator.start_research_process(session_id, ticker, expertise_level)

        assert research_id == session_id
        assert session_id in coordinator.active_sessions
        
        status = coordinator.active_sessions[session_id]
        assert isinstance(status, ResearchStatus)
        assert status.session_id == session_id
        assert status.ticker == ticker
        assert status.status == "active"
        assert status.current_agent == "valuation_agent"

    @pytest.mark.asyncio
    async def test_get_research_status_existing_session(self, coordinator):
        """Test getting research status for existing session."""
        session_id = "test-session-123"
        ticker = "AAPL"
        
        # Start research process first
        await coordinator.start_research_process(session_id, ticker, 5)
        
        # Get status
        status_info = await coordinator.get_research_status(session_id)
        
        assert status_info["session_id"] == session_id
        assert status_info["ticker"] == ticker
        assert status_info["status"] == "active"
        assert status_info["current_agent"] == "valuation_agent"
        assert "started_at" in status_info

    @pytest.mark.asyncio
    async def test_get_research_status_nonexistent_session(self, coordinator):
        """Test getting research status for non-existent session."""
        session_id = "nonexistent-session"
        
        status_info = await coordinator.get_research_status(session_id)
        
        assert "error" in status_info
        assert status_info["session_id"] == session_id

    @pytest.mark.asyncio
    async def test_handle_agent_failure_critical_agent(self, coordinator):
        """Test handling failure of critical agent."""
        session_id = "test-session-123"
        ticker = "AAPL"
        
        # Start research process
        await coordinator.start_research_process(session_id, ticker, 5)
        
        # Simulate critical agent failure
        error = Exception("Test error")
        success = await coordinator.handle_agent_failure(session_id, "valuation_agent", error)
        
        assert not success  # Critical failure should return False
        status = coordinator.active_sessions[session_id]
        assert status.status == "failed"
        assert "valuation_agent" in status.agents_failed
        assert "Critical agent valuation_agent failed" in status.error_message

    @pytest.mark.asyncio
    async def test_handle_agent_failure_all_agents_critical(self, coordinator):
        """Test handling failure when all agents are critical (PO requirement)."""
        session_id = "test-session-123"
        ticker = "AAPL"
        
        # Start research process
        await coordinator.start_research_process(session_id, ticker, 5)
        
        # Simulate strategic agent failure (now also critical)
        error = Exception("Test error")
        success = await coordinator.handle_agent_failure(session_id, "strategic_agent", error)
        
        assert not success  # All agents are now critical, so should return False
        status = coordinator.active_sessions[session_id]
        assert status.status == "failed"  # Should be failed
        assert "strategic_agent" in status.agents_failed
        assert "Critical agent strategic_agent failed" in status.error_message

    @pytest.mark.asyncio
    async def test_coordinate_agent_handoff_valid_data(self, coordinator):
        """Test successful agent handoff with valid data."""
        session_id = "test-session-123"
        ticker = "AAPL"
        
        # Start research process
        await coordinator.start_research_process(session_id, ticker, 5)
        
        # Create valid handoff data
        handoff_data = {
            "research_files": ["valuation/analysis_v1.md"],
            "context_summary": "Completed valuation analysis with DCF model and peer comparison. Key findings include strong competitive moat and reasonable valuation at current levels.",
            "cross_references": [],
            "confidence_metrics": {"confidence": 0.8, "completeness": 0.9},
            "token_usage": 1500
        }
        
        # Execute handoff
        success = await coordinator.coordinate_agent_handoff(
            session_id, "valuation_agent", "strategic_agent", handoff_data
        )
        
        assert success
        assert session_id in coordinator.session_handoffs
        assert len(coordinator.session_handoffs[session_id]) == 1
        
        handoff = coordinator.session_handoffs[session_id][0]
        assert isinstance(handoff, AgentHandoff)
        assert handoff.source_agent == "valuation_agent"
        assert handoff.target_agent == "strategic_agent"
        
        # Check status update
        status = coordinator.active_sessions[session_id]
        assert "valuation_agent" in status.agents_completed
        assert status.current_agent == "strategic_agent"
        assert status.progress_percentage > 0

    @pytest.mark.asyncio
    async def test_coordinate_agent_handoff_invalid_data(self, coordinator):
        """Test agent handoff with invalid data."""
        session_id = "test-session-123"
        ticker = "AAPL"
        
        # Start research process
        await coordinator.start_research_process(session_id, ticker, 5)
        
        # Create invalid handoff data (missing research files and short summary)
        handoff_data = {
            "research_files": [],  # Empty list
            "context_summary": "Too short",  # Less than 100 characters
            "cross_references": [],
            "confidence_metrics": {"confidence": 0.8},
            "token_usage": 1500
        }
        
        # Execute handoff
        success = await coordinator.coordinate_agent_handoff(
            session_id, "valuation_agent", "strategic_agent", handoff_data
        )
        
        assert not success  # Should fail validation

    def test_get_session_handoffs(self, coordinator):
        """Test getting handoffs for a session."""
        session_id = "test-session-123"
        
        # Initially should be empty
        handoffs = coordinator.get_session_handoffs(session_id)
        assert handoffs == []
        
        # Add a mock handoff
        coordinator.session_handoffs[session_id] = [
            AgentHandoff(
                source_agent="valuation_agent",
                target_agent="strategic_agent",
                research_files=["valuation/analysis_v1.md"],
                context_summary="Test handoff with comprehensive analysis and findings for next agent processing."
            )
        ]
        
        handoffs = coordinator.get_session_handoffs(session_id)
        assert len(handoffs) == 1
        assert handoffs[0]["source_agent"] == "valuation_agent"
        assert handoffs[0]["target_agent"] == "strategic_agent"

    def test_cleanup_session(self, coordinator):
        """Test session cleanup."""
        session_id = "test-session-123"
        
        # Add mock data
        coordinator.active_sessions[session_id] = ResearchStatus(
            session_id=session_id, ticker="AAPL"
        )
        coordinator.session_handoffs[session_id] = []
        
        # Cleanup
        coordinator.cleanup_session(session_id)
        
        # Verify cleanup
        assert session_id not in coordinator.active_sessions
        assert session_id not in coordinator.session_handoffs

    def test_agent_order_sequence(self, coordinator):
        """Test that agents are ordered correctly."""
        expected_order = ["valuation_agent", "strategic_agent", "historian_agent", "synthesis_agent"]
        assert coordinator.agent_order == expected_order

    @pytest.mark.asyncio
    async def test_mock_agent_execution(self, coordinator):
        """Test mock agent execution for framework testing."""
        session_id = "test-session-123"
        ticker = "AAPL"
        expertise_level = 5
        
        result = await coordinator._mock_agent_execution(session_id, "valuation_agent", ticker, expertise_level)
        
        assert result.agent_name == "valuation_agent"
        assert result.success is True
        assert len(result.research_files_created) > 0
        assert result.token_usage > 0
        assert result.confidence_score > 0

    @pytest.mark.asyncio
    async def test_complete_research_workflow_simulation(self, coordinator):
        """Test complete research workflow with mock agents."""
        session_id = "test-session-123"
        ticker = "AAPL"
        expertise_level = 5
        
        # Start research
        await coordinator.start_research_process(session_id, ticker, expertise_level)
        
        # Wait for workflow to complete (with timeout)
        max_wait = 10  # Maximum 10 seconds
        wait_time = 0
        
        while wait_time < max_wait:
            await asyncio.sleep(1)
            wait_time += 1
            status_info = await coordinator.get_research_status(session_id)
            
            if status_info["status"] == "completed":
                break
        
        # Check final status
        status_info = await coordinator.get_research_status(session_id)
        
        # Should be completed
        assert status_info["status"] == "completed"
        assert status_info["progress_percentage"] == 100.0
        assert len(status_info["agents_completed"]) == 3  # All agents except synthesis (which is marked as completed in the status)

    @pytest.mark.asyncio
    async def test_concurrent_sessions(self, coordinator):
        """Test handling multiple concurrent research sessions."""
        sessions = [
            ("session-1", "AAPL", 5),
            ("session-2", "GOOGL", 7),
            ("session-3", "MSFT", 3)
        ]
        
        # Start all sessions
        for session_id, ticker, expertise in sessions:
            await coordinator.start_research_process(session_id, ticker, expertise)
        
        # Verify all sessions are tracked
        for session_id, ticker, _ in sessions:
            assert session_id in coordinator.active_sessions
            status = coordinator.active_sessions[session_id]
            assert status.ticker == ticker

    def test_agent_handoff_validation_integrity(self):
        """Test AgentHandoff validation logic."""
        # Valid handoff
        valid_handoff = AgentHandoff(
            source_agent="valuation_agent",
            target_agent="strategic_agent",
            research_files=["valuation/analysis_v1.md"],
            context_summary="This is a comprehensive analysis with detailed findings and recommendations for the strategic agent to build upon in their analysis."
        )
        assert valid_handoff.validate_handoff_integrity() is True
        
        # Invalid handoff - no research files
        invalid_handoff_no_files = AgentHandoff(
            source_agent="valuation_agent",
            target_agent="strategic_agent",
            research_files=[],
            context_summary="This is a comprehensive analysis with detailed findings and recommendations for the strategic agent to build upon in their analysis."
        )
        assert invalid_handoff_no_files.validate_handoff_integrity() is False
        
        # Invalid handoff - short summary
        invalid_handoff_short_summary = AgentHandoff(
            source_agent="valuation_agent",
            target_agent="strategic_agent",
            research_files=["valuation/analysis_v1.md"],
            context_summary="Too short"
        )
        assert invalid_handoff_short_summary.validate_handoff_integrity() is False
        
        # Invalid handoff - same agent
        invalid_handoff_same_agent = AgentHandoff(
            source_agent="valuation_agent",
            target_agent="valuation_agent",
            research_files=["valuation/analysis_v1.md"],
            context_summary="This is a comprehensive analysis with detailed findings and recommendations."
        )
        assert invalid_handoff_same_agent.validate_handoff_integrity() is False