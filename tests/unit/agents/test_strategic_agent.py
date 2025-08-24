"""Unit tests for StrategicAgent with 2-step workflow."""

import os
from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

from src.agents.strategic_agent import StrategicAgent
from src.models.collaboration import AgentResult


class TestStrategicAgent:
    """Test suite for StrategicAgent implementation."""

    @pytest.fixture
    def agent(self):
        """Create StrategicAgent instance for testing."""
        # Set mock API key to avoid initialization error
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            return StrategicAgent()

    @pytest.fixture
    def mock_research_response(self):
        """Mock research phase response."""
        return """# AAPL Strategic Research

## Competitive Positioning
- Market Share: 20.1% in global smartphone market [Source: Counterpoint Research, Q2 2025]
- Premium segment dominance: 60%+ market share >$800 price point [Source: IDC, 2025]

## Industry Dynamics
- Global smartphone market: -2.1% YoY decline [Source: Gartner, Q2 2025]
- Services growth: 8.2% YoY, now $74B annually [Source: AAPL Q3 2025 earnings]

## Competitive Moats
- iOS ecosystem lock-in: 1.46B active users [Source: AAPL investor update]
- App Store network effects: 34M developers [Source: WWDC 2025]
- Brand loyalty: 92% customer satisfaction [Source: ACSI 2025]

## Strategic Risks
- EU Digital Markets Act compliance costs [Source: AAPL 10-K 2025, Risk Factors]
- China regulatory pressure affecting 19% of revenue [Source: AAPL geographic revenue]
- Services revenue concentration risk [Source: SEC filing analysis]

## Management Assessment
- Tim Cook tenure: Strong execution on Services strategy [Source: Seeking Alpha analysis]
- Capital allocation: $76.6B in buybacks (LTM) [Source: AAPL cash flow statement]
- R&D investment: 6.1% of revenue vs 2.8% industry average [Source: Bloomberg analysis]
"""

    @pytest.fixture
    def mock_strategic_response(self):
        """Mock strategic analysis response."""
        return """# AAPL Strategic Analysis

## Executive Summary
- **Strategic Position**: STRONG
- **Competitive Moat**: WIDE
- **Strategic Risk Level**: MODERATE
- **Management Quality**: EXCELLENT
- **Investment Implication**: Strategic moats support premium valuation

## Competitive Moat Analysis
### Network Effects & Switching Costs
- iOS ecosystem creates high switching costs (~$2,500 average device/service investment)
- App Store network effects strengthen with 34M developers
- iMessage and FaceTime create social switching barriers

**Moat Assessment**: Wide moat with strengthening network effects

## Strategic Risk Evaluation
### Regulatory & Political Risks
- EU Digital Markets Act: Estimated $2-5B annual compliance costs
- China regulatory risks affecting 19% of revenue base

### Technology Disruption Threats
- AI integration race with Google, Microsoft
- AR/VR market positioning vs Meta

**Overall Risk Assessment**: Moderate risk with manageable regulatory exposure

## Investment Implications
### Strategic Factor Impact on Valuation
- Ecosystem moats justify 15%+ premium to tech peers
- Services growth (8%+ annually) supports multiple expansion
- Regulatory headwinds create 5-10% valuation discount

### Strategic Monitoring Points
- Services revenue growth sustainability
- China market regulatory developments
- AI/AR competitive positioning progress
"""

    @pytest.fixture
    def mock_valuation_context(self):
        """Mock valuation context from previous agent."""
        return {
            "summary": """Owner-Returns Valuation Complete for AAPL:
✅ Current FCF Yield: 3.5%
✅ Target IRR: 12.8%
✅ Investment Recommendation: HOLD
✅ Trading above fair value at current levels""",
            "agent_name": "valuation_agent",
            "confidence_score": 0.8,
        }

    @pytest.mark.asyncio
    async def test_conduct_research_success(
        self, agent, mock_research_response, mock_strategic_response, mock_valuation_context
    ):
        """Test successful 2-step strategic research workflow."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        with patch.object(agent.openai_client, "respond_with_web_search") as mock_research, patch.object(
            agent.openai_client, "create_completion"
        ) as mock_analysis, patch.object(agent, "_write_research_files") as mock_write:

            # Setup mocks
            mock_research.return_value = mock_research_response
            mock_analysis.return_value = mock_strategic_response
            mock_write.return_value = [
                f"research_database/sessions/{session_id}/{ticker}/strategic/temp_competition.md",
                f"research_database/sessions/{session_id}/{ticker}/strategic/strategic_analysis.md",
            ]

            # Execute test
            result = await agent.conduct_research(session_id, ticker, expertise_level, mock_valuation_context)

            # Verify result
            assert isinstance(result, AgentResult)
            assert result.success is True
            assert result.agent_name == "strategic_agent"
            assert len(result.research_files_created) == 2
            assert ticker in result.summary
            assert result.confidence_score == 0.8

            # Verify method calls
            mock_research.assert_called_once()
            mock_analysis.assert_called_once()
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_research_phase(self, agent):
        """Test research phase with GPT-5 web search."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        mock_response = "Mock competitive data with [Source: Industry Report]"

        with patch.object(agent.openai_client, "respond_with_web_search") as mock_web_search:
            mock_web_search.return_value = mock_response

            result = await agent._run_research_phase(session_id, ticker, expertise_level)

            assert result == mock_response
            mock_web_search.assert_called_once()

            # Verify correct parameters passed
            call_args = mock_web_search.call_args
            messages = call_args[1]["messages"]
            assert any(ticker in str(msg) for msg in messages)
            assert call_args[1]["reasoning_effort"] == "low"
            assert call_args[1]["max_output_tokens"] == 64000

    @pytest.mark.asyncio
    async def test_run_analysis_phase(self, agent, mock_research_response, mock_valuation_context):
        """Test strategic analysis phase with GPT-5."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        mock_analysis = "# AAPL Strategic Analysis\nMoat: Wide"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.return_value = mock_analysis

            result = await agent._run_analysis_phase(
                session_id, ticker, expertise_level, mock_research_response, mock_valuation_context
            )

            assert result == mock_analysis
            mock_completion.assert_called_once()

            # Verify research data and valuation context are included
            call_args = mock_completion.call_args
            messages = call_args[1]["messages"]
            prompt_content = str(messages)
            assert ticker in prompt_content
            assert "competitive" in prompt_content.lower()
            assert "VALUATION CONTEXT" in prompt_content

            # Verify GPT-5 parameters
            assert call_args[1]["max_tokens"] == 16000
            assert call_args[1]["use_complex_model"] is True

    @pytest.mark.asyncio
    async def test_run_analysis_phase_no_valuation_context(self, agent, mock_research_response):
        """Test strategic analysis phase without valuation context."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        mock_analysis = "# AAPL Strategic Analysis\nMoat: Wide"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.return_value = mock_analysis

            result = await agent._run_analysis_phase(
                session_id, ticker, expertise_level, mock_research_response, None
            )

            assert result == mock_analysis
            mock_completion.assert_called_once()

            # Verify handles missing valuation context gracefully
            call_args = mock_completion.call_args
            messages = call_args[1]["messages"]
            prompt_content = str(messages)
            assert "No valuation context provided" in prompt_content

    @pytest.mark.asyncio
    async def test_write_research_files(self, agent):
        """Test strategic research file writing to database."""
        session_id = "test_session_123"
        ticker = "AAPL"
        temp_md = "Competitive research data"
        strategic_md = "Strategic analysis"

        with patch("builtins.open", mock_open()) as mock_file, patch("os.makedirs") as mock_makedirs:

            result = await agent._write_research_files(session_id, ticker, temp_md, strategic_md)

            # Verify file paths
            assert len(result) == 2
            assert "temp_competition.md" in result[0]
            assert "strategic_analysis.md" in result[1]
            assert session_id in result[0]
            assert ticker in result[0]
            assert "strategic" in result[0]

            # Verify files were written
            assert mock_file.call_count == 2
            mock_makedirs.assert_called()

    def test_get_expertise_depth_config(self, agent):
        """Test expertise level mapping."""
        # Test different expertise levels
        config_1 = agent._get_expertise_depth_config(1)
        assert config_1["depth_name"] == "Foundational"

        config_5 = agent._get_expertise_depth_config(5)
        assert config_5["depth_name"] == "Intermediate"

        config_10 = agent._get_expertise_depth_config(10)
        assert config_10["depth_name"] == "Executive"

    def test_get_strategic_framework(self, agent):
        """Test strategic analysis framework."""
        framework = agent._get_strategic_framework()

        # Verify key strategic frameworks are present
        assert "Competitive Moat Analysis" in framework
        assert "Porter's Five Forces" in framework
        assert "Network Effects" in framework
        assert "Switching Costs" in framework
        assert "Strategic Risk Assessment" in framework
        assert "Management Quality" in framework

    @pytest.mark.asyncio
    async def test_error_handling_research_phase(self, agent):
        """Test error handling in research phase."""
        session_id = "test_session_123"
        ticker = "INVALID"
        expertise_level = 5

        with patch.object(agent.openai_client, "respond_with_web_search") as mock_web_search:
            mock_web_search.side_effect = Exception("API Error")

            result = await agent._run_research_phase(session_id, ticker, expertise_level)

            # Should return error message, not crash
            assert "Strategic Research Failed" in result
            assert ticker in result
            assert "API Error" in result

    @pytest.mark.asyncio
    async def test_error_handling_analysis_phase(self, agent):
        """Test error handling in strategic analysis phase."""
        session_id = "test_session_123"
        ticker = "INVALID"
        expertise_level = 5
        temp_md = "Some research data"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.side_effect = Exception("Analysis Error")

            result = await agent._run_analysis_phase(session_id, ticker, expertise_level, temp_md)

            # Should return error message, not crash
            assert "Strategic Analysis Failed" in result
            assert ticker in result
            assert "Analysis Error" in result

    @pytest.mark.asyncio
    async def test_conduct_research_with_error(self, agent):
        """Test conduct_research method error handling."""
        session_id = "test_session_123"
        ticker = "INVALID"
        expertise_level = 5

        with patch.object(agent, "_run_research_phase") as mock_research:
            mock_research.side_effect = Exception("Research failed")

            result = await agent.conduct_research(session_id, ticker, expertise_level)

            assert isinstance(result, AgentResult)
            assert result.success is False
            assert result.agent_name == "strategic_agent"
            assert result.error_message == "Research failed"
            assert len(result.research_files_created) == 0
            assert result.confidence_score == 0.0

    def test_create_execution_summary(self, agent):
        """Test execution summary creation."""
        ticker = "AAPL"
        execution_time = 3.2
        research_chars = 2000
        strategic_chars = 2500

        summary = agent._create_execution_summary(ticker, execution_time, research_chars, strategic_chars)

        assert ticker in summary
        assert "3.2 seconds" in summary
        assert "2,000 characters" in summary
        assert "2,500 characters" in summary
        assert "Strategic Analysis" in summary
        assert "GPT-5" in summary
        assert "Porter's Five Forces" in summary

    def test_create_error_result(self, agent):
        """Test error result creation."""
        from datetime import UTC
        session_id = "test_session_123"
        ticker = "INVALID"
        error_message = "Test error"
        start_time = datetime.now(UTC)

        result = agent._create_error_result(session_id, ticker, error_message, start_time)

        assert isinstance(result, AgentResult)
        assert result.success is False
        assert result.agent_name == "strategic_agent"
        assert result.error_message == error_message
        assert ticker in result.summary
        assert result.confidence_score == 0.0

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_name == "strategic_agent"
        assert hasattr(agent, "openai_client")
        assert hasattr(agent, "research_db")
