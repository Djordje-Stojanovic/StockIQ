"""Unit tests for base agent implementation."""

import shutil
import tempfile
from unittest.mock import patch

import pytest

from src.agents.base_agent import BaseAgent
from src.services.research_database import ResearchDatabase


class MockAgent(BaseAgent):
    """Mock implementation of BaseAgent for testing."""

    async def conduct_research(self, session_id, ticker, expertise_level, context=None):
        """Mock research method."""
        return {
            "agent_name": self.agent_name,
            "success": True,
            "summary": f"Mock research completed for {ticker}",
            "files_created": ["test_file.md"]
        }


class TestBaseAgent:
    """Test suite for BaseAgent class."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary research database."""
        temp_dir = tempfile.mkdtemp()
        db = ResearchDatabase(base_path=temp_dir)
        yield db
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_agent(self, temp_db):
        """Create mock agent with temporary database."""
        with patch('src.agents.base_agent.get_research_database', return_value=temp_db):
            agent = MockAgent("test_agent")
            yield agent

    def test_agent_initialization(self, mock_agent):
        """Test agent initialization."""
        assert mock_agent.agent_name == "test_agent"
        assert mock_agent.research_db is not None
        assert mock_agent.logger is not None

    def test_read_research_context_empty(self, mock_agent, temp_db):
        """Test reading context when no previous research exists."""
        session_id = "test-session-123"
        ticker = "AAPL"

        # Create session directory
        temp_db.create_session_directory(session_id, ticker)

        context = mock_agent.read_research_context(session_id, ticker)

        assert context["session_id"] == session_id
        assert context["ticker"] == ticker
        assert context["requesting_agent"] == "test"  # From agent type mapping
        assert context["previous_research"] == {}

    def test_read_research_context_with_data(self, mock_agent, temp_db):
        """Test reading context with existing research data."""
        session_id = "test-session-123"
        ticker = "AAPL"

        # Create session and add some research
        temp_db.create_session_directory(session_id, ticker)
        temp_db.write_research_file(
            session_id, ticker, "valuation", "dcf.md", "DCF analysis content"
        )

        # Mock agent as strategic to get valuation context
        with patch.object(mock_agent, '_get_agent_type', return_value='strategic'):
            context = mock_agent.read_research_context(session_id, ticker)

        assert "valuation" in context["previous_research"]
        assert len(context["previous_research"]["valuation"]) == 1

    def test_write_research_file(self, mock_agent, temp_db):
        """Test writing a research file."""
        session_id = "test-session-123"
        ticker = "AAPL"
        filename = "test_analysis.md"
        content = "# Test Analysis\n\nThis is a test analysis."

        # Create session directory
        temp_db.create_session_directory(session_id, ticker)

        relative_path = mock_agent.write_research_file(
            session_id, ticker, filename, content,
            metadata={"priority": "high"}
        )

        assert relative_path.endswith(filename)

        # Verify file was written correctly
        file_data = temp_db.read_research_file(session_id, ticker, relative_path)
        assert file_data["content"] == content
        assert file_data["metadata"]["author"] == "test_agent"
        assert file_data["metadata"]["priority"] == "high"

    def test_add_cross_reference(self, mock_agent, temp_db):
        """Test adding cross-references between files."""
        session_id = "test-session-123"
        ticker = "AAPL"

        temp_db.create_session_directory(session_id, ticker)

        mock_agent.add_cross_reference(
            session_id, ticker,
            "test/source.md",
            "test/target.md",
            "References financial data"
        )

        # Verify cross-reference was added
        cross_refs = temp_db._read_cross_references(session_id, ticker)
        assert len(cross_refs["references"]) == 1
        ref = cross_refs["references"][0]
        assert ref["source"] == "test/source.md"
        assert ref["target"] == "test/target.md"

    def test_format_handoff_data(self, mock_agent):
        """Test formatting data for agent handoff."""
        session_id = "test-session-123"
        ticker = "AAPL"
        research_files = ["test/analysis.md"]
        summary = "Completed test analysis with key findings."

        handoff_data = mock_agent.format_handoff_data(
            session_id, ticker, research_files, summary,
            confidence_metrics={"confidence": 0.8, "completeness": 0.9},
            token_usage=1500
        )

        assert handoff_data["research_files"] == research_files
        assert handoff_data["context_summary"] == summary
        assert handoff_data["confidence_metrics"]["confidence"] == 0.8
        assert handoff_data["token_usage"] == 1500
        assert "cross_references" in handoff_data

    def test_format_handoff_data_defaults(self, mock_agent):
        """Test formatting handoff data with default values."""
        handoff_data = mock_agent.format_handoff_data(
            "session-123", "AAPL", ["file.md"], "Summary"
        )

        assert handoff_data["confidence_metrics"]["confidence"] == 0.5
        assert handoff_data["token_usage"] == 0
        assert handoff_data["cross_references"] == []

    def test_get_agent_type_mapping(self, mock_agent):
        """Test agent type mapping from agent names."""
        test_cases = [
            ("valuation_agent", "valuation"),
            ("strategic_agent", "strategic"),
            ("historian_agent", "historical"),
            ("synthesis_agent", "synthesis"),
            ("custom_agent", "custom")
        ]

        for agent_name, expected_type in test_cases:
            mock_agent.agent_name = agent_name
            agent_type = mock_agent._get_agent_type()
            assert agent_type == expected_type

    def test_validate_research_context(self, mock_agent):
        """Test research context validation."""
        # Valid context
        valid_context = {
            "session_id": "test-session-123",
            "ticker": "AAPL",
            "requesting_agent": "test_agent",
            "previous_research": {}
        }
        assert mock_agent.validate_research_context(valid_context) is True

        # Invalid context - missing keys
        invalid_context = {
            "session_id": "test-session-123",
            "ticker": "AAPL"
            # Missing requesting_agent
        }
        assert mock_agent.validate_research_context(invalid_context) is False

    def test_get_expertise_adjusted_depth(self, mock_agent):
        """Test expertise level to research depth mapping."""
        test_cases = [
            (1, "foundational"),
            (2, "foundational"),
            (3, "educational"),
            (4, "educational"),
            (5, "intermediate"),
            (6, "intermediate"),
            (7, "advanced"),
            (8, "advanced"),
            (9, "executive"),
            (10, "executive")
        ]

        for expertise_level, expected_depth in test_cases:
            depth = mock_agent.get_expertise_adjusted_depth(expertise_level)
            assert depth == expected_depth

    def test_log_research_start(self, mock_agent):
        """Test research start logging."""
        with patch.object(mock_agent.logger, 'info') as mock_log:
            mock_agent.log_research_start("session-123", "AAPL", 5)

            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            assert "Starting test_agent research" in call_args
            assert "AAPL" in call_args
            assert "Session: session-123" in call_args
            assert "Expertise: 5" in call_args
            assert "Depth: intermediate" in call_args

    def test_log_research_complete(self, mock_agent):
        """Test research completion logging."""
        files_created = ["analysis.md", "summary.md"]

        with patch.object(mock_agent.logger, 'info') as mock_log:
            mock_agent.log_research_complete("session-123", "AAPL", files_created)

            mock_log.assert_called_once()
            call_args = mock_log.call_args[0][0]
            assert "Completed test_agent research" in call_args
            assert "AAPL" in call_args
            assert "Session: session-123" in call_args
            assert "Files: 2" in call_args

    def test_write_research_file_error_handling(self, mock_agent):
        """Test error handling in write_research_file."""
        # Mock database to raise exception
        with patch.object(mock_agent.research_db, 'write_research_file', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as exc_info:
                mock_agent.write_research_file("session-123", "AAPL", "test.md", "content")

            assert "Test error" in str(exc_info.value)

    def test_add_cross_reference_error_handling(self, mock_agent):
        """Test error handling in add_cross_reference."""
        with patch.object(mock_agent.research_db, 'add_cross_reference', side_effect=Exception("Test error")):
            with patch.object(mock_agent.logger, 'error') as mock_log:
                # Should not raise exception, just log error
                mock_agent.add_cross_reference("session-123", "AAPL", "source.md", "target.md", "relationship")

                mock_log.assert_called_once()
                assert "Error adding cross-reference" in mock_log.call_args[0][0]

    def test_read_research_context_error_handling(self, mock_agent):
        """Test error handling in read_research_context."""
        with patch.object(mock_agent.research_db, 'get_agent_context', side_effect=Exception("Test error")):
            context = mock_agent.read_research_context("session-123", "AAPL")

            assert "error" in context
            assert context["error"] == "Test error"
            assert context["previous_research"] == {}

    @pytest.mark.asyncio
    async def test_conduct_research_abstract_method(self, mock_agent):
        """Test that the mock agent implements conduct_research."""
        result = await mock_agent.conduct_research("session-123", "AAPL", 5)

        assert result["agent_name"] == "test_agent"
        assert result["success"] is True
        assert "AAPL" in result["summary"]
