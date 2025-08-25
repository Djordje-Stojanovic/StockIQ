"""Unit tests for HistorianAgent with 2-step workflow."""

import os
from datetime import datetime
from unittest.mock import mock_open, patch

import pytest

from src.agents.historian_agent import HistorianAgent
from src.models.collaboration import AgentResult


class TestHistorianAgent:
    """Test suite for HistorianAgent implementation."""

    @pytest.fixture
    def agent(self):
        """Create HistorianAgent instance for testing."""
        # Set mock API key to avoid initialization error
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            return HistorianAgent()

    @pytest.fixture
    def mock_research_response(self):
        """Mock research phase response."""
        return """# AAPL Historical Research

## Founding Story
- Founded April 1, 1976 by Steve Jobs, Steve Wozniak, Ronald Wayne [Source: Apple History Archive, 2025]
- Original vision: Personal computers for everyone [Source: Isaacson Biography, 2011]
- Incorporated January 3, 1977 [Source: SEC Historical Records]

## Major Milestones Timeline
- 1980: IPO at $22/share, $1.3B valuation [Source: NASDAQ Historical Data]
- 1985: Steve Jobs leaves Apple after boardroom coup [Source: WSJ Archives, 1985]
- 1997: Steve Jobs returns, company near bankruptcy [Source: Fortune, 1997]
- 2001: iPod launch revolutionizes music industry [Source: Apple Press Release, Oct 2001]
- 2007: iPhone launch transforms mobile computing [Source: MacWorld Keynote, Jan 2007]
- 2010: iPad creates tablet category [Source: Apple Event, Jan 2010]
- 2011: Tim Cook becomes CEO after Jobs' passing [Source: Apple Board Statement, Aug 2011]
- 2018: Becomes first $1T market cap company [Source: Bloomberg, Aug 2018]
- 2020: First $2T market cap during pandemic [Source: Reuters, Aug 2020]
- 2023: Vision Pro AR headset announced [Source: WWDC 2023]

## Leadership Evolution
- Steve Jobs (1976-1985, 1997-2011): Visionary founder, product genius [Source: Multiple biographies]
- John Sculley (1983-1993): Former Pepsi exec, marketing focus [Source: Sculley memoir]
- Michael Spindler (1993-1996): Brief tenure, licensing attempts [Source: Business Week archives]
- Gil Amelio (1996-1997): Failed turnaround CEO [Source: Apple Confidential book]
- Tim Cook (2011-present): Operations expert, Services expansion [Source: Current 10-K]

## Crisis Management
- 1996-1997: Near bankruptcy, 90 days from insolvency [Source: Michael Dell quote, 1997]
- 2008 Financial Crisis: Stock fell 58% but maintained R&D spending [Source: 2009 10-K]
- 2011-2012: Post-Jobs succession uncertainty handled smoothly [Source: Analyst reports]
- 2016: FBI encryption battle, defended privacy [Source: Cook Congressional testimony]
- 2020 COVID: Supply chain mastery, record profits [Source: 2020 earnings calls]

## Strategic Decisions
- 1997: Killed Newton, focused on core products [Source: Jobs' first all-hands]
- 2001: Opened Apple Stores despite skepticism [Source: Retail Week analysis]
- 2005: Intel transition from PowerPC [Source: WWDC 2005 keynote]
- 2014: Apple Watch enters wearables [Source: September Event 2014]
- 2020: Apple Silicon M1 chip transition [Source: WWDC 2020]
- 2023: $110B in buybacks, largest in history [Source: Q1 2023 earnings]

## Financial Journey
- 1980 IPO: $1.3B valuation [Source: IPO Prospectus]
- 1997: $2B market cap at Jobs' return [Source: Yahoo Finance historical]
- 2018: First $1T company [Source: CNBC, Aug 2018]
- 2020: First $2T company [Source: WSJ, Aug 2020]
- 2022: Peaked at $3T intraday [Source: Bloomberg, Jan 2022]
- 2025: $3.2T current market cap [Source: Current market data]
"""

    @pytest.fixture
    def mock_history_response(self):
        """Mock historical analysis response."""
        return """# AAPL Company History & Evolution

## Executive Summary
- **Company Age**: 49 years since founding (1976-2025)
- **Leadership Stability**: HIGH (only 2 CEOs in 28 years)
- **Crisis Management Track Record**: STRONG
- **Strategic Consistency**: HIGH
- **Historical Growth Pattern**: Exponential with platform shifts

## Founding & Early Years
### The Origin Story
Apple Computer Company founded April 1, 1976 in Los Altos garage by Steve Jobs (21), Steve Wozniak (25), and Ronald Wayne. Wayne sold his 10% stake for $800 after 12 days [Source: Apple History Archive, 2025].

### Initial Vision & Mission
"A computer for the rest of us" - democratizing personal computing when computers were room-sized mainframes [Source: Original Apple mission statement].

### Early Challenges & Pivots
- Apple I: 200 units hand-built, sold for $666.66 [Source: Wozniak autobiography]
- Apple II (1977): First mass-produced personal computer with color graphics
- Survived near-bankruptcy in 1997 through Microsoft investment and Jobs' return

## Leadership Evolution
### CEO Succession History
- Jobs Era 1 (1976-1985): Visionary founder, forced out after Sculley conflict
- Sculley/Spindler/Amelio Era (1985-1997): Lost focus, near bankruptcy
- Jobs Era 2 (1997-2011): Greatest corporate turnaround in history
- Cook Era (2011-present): Operational excellence, Services expansion

**Leadership Assessment**: Exceptional stability under Cook with smooth succession planning. Deep bench of internal talent.

## Crisis Management Track Record
### Financial Crisis Response (2008)
- Stock fell 58% but maintained R&D investment at 3% of revenue
- Launched App Store during downturn, creating new ecosystem [Source: 2009 10-K]

### COVID-19 Response (2020)
- First major company to close retail stores globally
- Supply chain resilience: Only company to grow PC shipments in 2020
- Record Mac and iPad sales from work-from-home demand [Source: 2020 earnings]

**Crisis Management Rating**: STRONG - Consistently uses crises as opportunities for strategic advances

## Strategic Decision Analysis
### Successful Strategic Moves
- iPod/iTunes (2001): Created digital music industry, $10B revenue at peak
- iPhone (2007): Redefined mobile computing, now 50% of revenue
- App Store (2008): Platform economics, 30% commission on $100B+ GMV
- Apple Silicon (2020): Vertical integration delivering 2x performance/watt

### Strategic Mistakes & Recoveries
- Newton PDA (1993): Too early, killed by Jobs in 1997
- MobileMe (2008): Cloud service failure, led to iCloud success
- Maps (2012): Premature Google Maps replacement, now vastly improved

**Strategic Consistency Score**: HIGH - Maintains focus on premium integrated experiences

## Predictive Historical Patterns
### Recurring Strategic Themes
- Enter markets late with superior execution (MP3 players, smartphones, tablets, watches)
- Vertical integration when technology matures (chips, displays, modems)
- Platform transitions every 10-15 years (Mac→iPod→iPhone→?)

### Management Playbook Analysis
- Crisis response: Increase R&D, never chase market share
- Capital allocation: Massive buybacks when undervalued
- Product strategy: Say no to 1000 things, focus on few done perfectly

### Future Performance Indicators
- History suggests next platform shift due 2025-2030 (AR/VR or automotive)
- Services growth follows hardware install base with 2-3 year lag
- Margin expansion through vertical integration pattern continuing

## Key Historical Lessons
1. **Leadership Matters**: Jobs' return saved company; Cook's operations extended dominance
2. **Crisis Resilience**: Every crisis used to strengthen competitive position
3. **Platform Power**: Success comes from creating platforms, not just products
4. **Vertical Integration**: Control of full stack creates sustainable advantages
5. **Capital Discipline**: Best capital allocation in tech history (15% annual TSR since 1997)
6. **Innovation Timing**: Enter markets when technology ready, not first-mover
7. **Cultural Consistency**: Design-first, user-experience focus unchanged since 1976

## Data Sources & Citations
[All sources cited inline throughout document]
"""

    @pytest.fixture
    def mock_context(self):
        """Mock context from previous agents."""
        return {
            "valuation": {
                "summary": """Owner-Returns Valuation Complete for AAPL:
✅ Current FCF Yield: 3.5%
✅ Target IRR: 12.8%
✅ Investment Recommendation: HOLD""",
            },
            "strategic": {
                "summary": """Strategic Analysis Complete for AAPL:
✅ Competitive Moat: WIDE
✅ Strategic Position: STRONG
✅ Management Quality: EXCELLENT""",
            },
        }

    @pytest.mark.asyncio
    async def test_conduct_research_success(
        self, agent, mock_research_response, mock_history_response, mock_context
    ):
        """Test successful 2-step historical research workflow."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        with patch.object(agent.openai_client, "respond_with_web_search") as mock_research, patch.object(
            agent.openai_client, "create_completion"
        ) as mock_analysis, patch.object(agent, "_write_research_files") as mock_write:

            # Setup mocks
            mock_research.return_value = mock_research_response
            mock_analysis.return_value = mock_history_response
            mock_write.return_value = [
                f"research_database/sessions/{session_id}/{ticker}/historical/temp_history.md",
                f"research_database/sessions/{session_id}/{ticker}/historical/company_history.md",
            ]

            # Execute test
            result = await agent.conduct_research(session_id, ticker, expertise_level, mock_context)

            # Verify result
            assert isinstance(result, AgentResult)
            assert result.success is True
            assert result.agent_name == "historian_agent"
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

        mock_response = "Mock historical data with [Source: Company Archives]"

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
    async def test_run_analysis_phase(self, agent, mock_research_response, mock_context):
        """Test historical analysis phase with GPT-5."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        mock_analysis = "# AAPL Company History\nFounded: 1976"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.return_value = mock_analysis

            result = await agent._run_analysis_phase(
                session_id, ticker, expertise_level, mock_research_response, mock_context
            )

            assert result == mock_analysis
            mock_completion.assert_called_once()

            # Verify research data and context are included
            call_args = mock_completion.call_args
            messages = call_args[1]["messages"]
            prompt_content = str(messages)
            assert ticker in prompt_content
            assert "historical" in prompt_content.lower()
            assert "VALUATION CONTEXT" in prompt_content
            assert "STRATEGIC CONTEXT" in prompt_content

            # Verify GPT-5 parameters
            assert call_args[1]["max_tokens"] == 16000
            assert call_args[1]["use_complex_model"] is True

    @pytest.mark.asyncio
    async def test_run_analysis_phase_no_context(self, agent, mock_research_response):
        """Test historical analysis phase without previous agent context."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        mock_analysis = "# AAPL Company History\nFounded: 1976"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.return_value = mock_analysis

            result = await agent._run_analysis_phase(
                session_id, ticker, expertise_level, mock_research_response, None
            )

            assert result == mock_analysis
            mock_completion.assert_called_once()

            # Verify handles missing context gracefully
            call_args = mock_completion.call_args
            messages = call_args[1]["messages"]
            prompt_content = str(messages)
            assert "No previous agent context provided" in prompt_content

    @pytest.mark.asyncio
    async def test_write_research_files(self, agent):
        """Test historical research file writing to database."""
        session_id = "test_session_123"
        ticker = "AAPL"
        temp_md = "Historical research data"
        history_md = "Company history analysis"

        with patch("builtins.open", mock_open()) as mock_file, patch("os.makedirs") as mock_makedirs:

            result = await agent._write_research_files(session_id, ticker, temp_md, history_md)

            # Verify file paths
            assert len(result) == 2
            assert "temp_history.md" in result[0]
            assert "company_history.md" in result[1]
            assert session_id in result[0]
            assert ticker in result[0]
            assert "historical" in result[0]

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
            assert "Historical Research Failed" in result
            assert ticker in result
            assert "API Error" in result

    @pytest.mark.asyncio
    async def test_error_handling_analysis_phase(self, agent):
        """Test error handling in historical analysis phase."""
        session_id = "test_session_123"
        ticker = "INVALID"
        expertise_level = 5
        temp_md = "Some research data"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.side_effect = Exception("Analysis Error")

            result = await agent._run_analysis_phase(session_id, ticker, expertise_level, temp_md)

            # Should return error message, not crash
            assert "Historical Analysis Failed" in result
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
            assert result.agent_name == "historian_agent"
            assert result.error_message == "Research failed"
            assert len(result.research_files_created) == 0
            assert result.confidence_score == 0.0

    def test_create_execution_summary(self, agent):
        """Test execution summary creation."""
        ticker = "AAPL"
        execution_time = 4.5
        research_chars = 3000
        history_chars = 3500

        summary = agent._create_execution_summary(ticker, execution_time, research_chars, history_chars)

        assert ticker in summary
        assert "4.5 seconds" in summary
        assert "3,000 characters" in summary
        assert "3,500 characters" in summary
        assert "Historical Analysis" in summary
        assert "GPT-5" in summary
        assert "founding to present" in summary

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
        assert result.agent_name == "historian_agent"
        assert result.error_message == error_message
        assert ticker in result.summary
        assert result.confidence_score == 0.0

    def test_agent_initialization(self, agent):
        """Test agent initialization."""
        assert agent.agent_name == "historian_agent"
        assert hasattr(agent, "openai_client")
        assert hasattr(agent, "research_db")

    @pytest.mark.asyncio
    async def test_context_formatting_both_agents(self, agent, mock_research_response):
        """Test context formatting when both valuation and strategic agents provide context."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        context = {
            "valuation": {"summary": "Valuation summary here"},
            "strategic": {"summary": "Strategic summary here"},
        }

        mock_analysis = "# Complete History"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.return_value = mock_analysis

            await agent._run_analysis_phase(
                session_id, ticker, expertise_level, mock_research_response, context
            )

            # Verify both contexts are included
            call_args = mock_completion.call_args
            messages = call_args[1]["messages"]
            prompt_content = str(messages)
            assert "VALUATION CONTEXT" in prompt_content
            assert "Valuation summary here" in prompt_content
            assert "STRATEGIC CONTEXT" in prompt_content
            assert "Strategic summary here" in prompt_content

    @pytest.mark.asyncio
    async def test_context_formatting_partial(self, agent, mock_research_response):
        """Test context formatting with only valuation context."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        context = {
            "valuation": {"summary": "Valuation summary only"},
        }

        mock_analysis = "# Partial Context History"

        with patch.object(agent.openai_client, "create_completion") as mock_completion:
            mock_completion.return_value = mock_analysis

            await agent._run_analysis_phase(
                session_id, ticker, expertise_level, mock_research_response, context
            )

            # Verify only valuation context is included
            call_args = mock_completion.call_args
            messages = call_args[1]["messages"]
            prompt_content = str(messages)
            assert "VALUATION CONTEXT" in prompt_content
            assert "Valuation summary only" in prompt_content
            assert "STRATEGIC CONTEXT" not in prompt_content
