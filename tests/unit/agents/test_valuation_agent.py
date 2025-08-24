"""Unit tests for new GPT-5 ValuationAgent with 2-step workflow."""

import os
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

import pytest

from src.agents.valuation_agent import ValuationAgent
from src.models.collaboration import AgentResult


class TestNewValuationAgent:
    """Test suite for new GPT-5 ValuationAgent implementation."""

    @pytest.fixture
    def agent(self):
        """Create ValuationAgent instance for testing."""
        # Set mock API key to avoid initialization error
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            return ValuationAgent()

    @pytest.fixture
    def mock_research_response(self):
        """Mock research phase response."""
        return """# AAPL Financial Research

## Current Stock Price
- Price: $175.30 [Source: NASDAQ, 2025-08-24 16:00]
- Market Cap: $2.7T [Source: NASDAQ, 2025-08-24]

## Latest Financial Data
- Revenue (LTM): $394.3B [Source: AAPL 10-K 2024, p.23]
- Free Cash Flow: $101.9B [Source: AAPL 10-K 2024, Cash Flow Statement]
- FCF per Share: $6.15 [Source: FactSet calculation, diluted shares: 16.56B]
- Net Cash: $70.1B [Source: AAPL 10-Q Q3 2024, Balance Sheet]

## Share Changes
- Diluted Shares Outstanding: 16.56B [Source: AAPL 10-Q Q3 2024]
- Share Buybacks (LTM): $76.6B [Source: AAPL Cash Flow Statement]
- Net Dilution Rate: -2.8% annually [Source: Historical share count analysis]
"""

    @pytest.fixture
    def mock_valuation_response(self):
        """Mock valuation phase response."""
        return """# AAPL Owner-Returns Valuation Analysis

## Executive Summary
- Current Price: $175.30 [Source: research data]
- FCF/Share (LTM): $6.15 [Source: research data]
- Current FCF Yield: 3.5%
- **Investment Recommendation: HOLD**
- **Target IRR: 12.8%**

## IRR Decomposition Analysis
- **Starting Yield**: 3.5% (FCF/share ÷ Price)
- **FCF Growth (10yr)**: 8.5% CAGR with fade assumptions
- **Multiple Reversion**: 1.2% (conservative terminal assumptions)
- **Dilution Impact**: -2.8% (net share buybacks)
- **Total Expected IRR**: 12.8%

## Price Ladder Framework
- **Buffett Floor**: $135 (10× pre-tax earnings approximation)
- **10% IRR Target**: $162 (fair value for quality business)
- **15% IRR Target**: $123 (attractive entry point)
- **Current Assessment**: Trading above fair value
"""

    @pytest.mark.asyncio
    async def test_conduct_research_success(self, agent, mock_research_response, mock_valuation_response):
        """Test successful 2-step research workflow."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        with patch.object(agent.openai_client, 'respond_with_web_search') as mock_research, \
             patch.object(agent.openai_client, 'create_completion') as mock_valuation, \
             patch.object(agent, '_write_research_files') as mock_write:
            
            # Setup mocks
            mock_research.return_value = mock_research_response
            mock_valuation.return_value = mock_valuation_response
            mock_write.return_value = [
                f"research_database/sessions/{session_id}/{ticker}/valuation/temp.md",
                f"research_database/sessions/{session_id}/{ticker}/valuation/valuation.md"
            ]

            # Execute test
            result = await agent.conduct_research(session_id, ticker, expertise_level)

            # Verify result
            assert isinstance(result, AgentResult)
            assert result.success is True
            assert result.agent_name == "valuation_agent"
            assert len(result.research_files_created) == 2
            assert ticker in result.summary
            assert result.confidence_score == 0.8

            # Verify method calls
            mock_research.assert_called_once()
            mock_valuation.assert_called_once()
            mock_write.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_research_phase(self, agent):
        """Test research phase with GPT-5 web search."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        mock_response = "Mock financial data with [Source: AAPL 10-K]"

        with patch.object(agent.openai_client, 'respond_with_web_search') as mock_web_search:
            mock_web_search.return_value = mock_response

            result = await agent._run_research_phase(session_id, ticker, expertise_level)

            assert result == mock_response
            mock_web_search.assert_called_once()
            
            # Verify correct parameters passed
            call_args = mock_web_search.call_args
            messages = call_args[1]['messages']
            assert any(ticker in str(msg) for msg in messages)
            assert call_args[1]['reasoning_effort'] == "low"
            assert call_args[1]['max_output_tokens'] == 32000

    @pytest.mark.asyncio
    async def test_run_valuation_phase(self, agent, mock_research_response):
        """Test valuation phase with GPT-5 analysis."""
        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        mock_valuation = "# AAPL Valuation Analysis\nIRR: 12.5%"

        with patch.object(agent.openai_client, 'create_completion') as mock_completion:
            mock_completion.return_value = mock_valuation

            result = await agent._run_valuation_phase(session_id, ticker, expertise_level, mock_research_response)

            assert result == mock_valuation
            mock_completion.assert_called_once()
            
            # Verify research data is included in prompt
            call_args = mock_completion.call_args
            messages = call_args[1]['messages']
            prompt_content = str(messages)
            assert ticker in prompt_content
            assert "research" in prompt_content.lower()

    @pytest.mark.asyncio
    async def test_write_research_files(self, agent):
        """Test research file writing to database."""
        session_id = "test_session_123"
        ticker = "AAPL"
        temp_md = "Research data"
        valuation_md = "Valuation analysis"

        with patch('builtins.open', mock_open()) as mock_file, \
             patch('os.makedirs') as mock_makedirs:
            
            result = await agent._write_research_files(session_id, ticker, temp_md, valuation_md)

            # Verify file paths
            assert len(result) == 2
            assert "temp.md" in result[0]
            assert "valuation.md" in result[1]
            assert session_id in result[0]
            assert ticker in result[0]

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

    def test_get_owner_returns_formulas(self, agent):
        """Test Owner-Returns formulas are included."""
        formulas = agent._get_owner_returns_formulas()
        
        # Verify key formulas are present
        assert "Starting Yield" in formulas
        assert "FCF Growth" in formulas
        assert "Multiple Reversion" in formulas
        assert "Dilution Impact" in formulas
        assert "Price Ladder" in formulas
        assert "Buffett Floor" in formulas

    @pytest.mark.asyncio
    async def test_error_handling_research_phase(self, agent):
        """Test error handling in research phase."""
        session_id = "test_session_123"
        ticker = "INVALID"
        expertise_level = 5

        with patch.object(agent.openai_client, 'respond_with_web_search') as mock_web_search:
            mock_web_search.side_effect = Exception("API Error")

            result = await agent._run_research_phase(session_id, ticker, expertise_level)

            # Should return error message, not crash
            assert "Research Failed" in result
            assert ticker in result
            assert "API Error" in result

    @pytest.mark.asyncio
    async def test_error_handling_valuation_phase(self, agent):
        """Test error handling in valuation phase."""
        session_id = "test_session_123"
        ticker = "INVALID"
        expertise_level = 5
        temp_md = "Some research data"

        with patch.object(agent.openai_client, 'create_completion') as mock_completion:
            mock_completion.side_effect = Exception("Analysis Error")

            result = await agent._run_valuation_phase(session_id, ticker, expertise_level, temp_md)

            # Should return error message, not crash
            assert "Valuation Analysis Failed" in result
            assert ticker in result
            assert "Analysis Error" in result

    @pytest.mark.asyncio
    async def test_conduct_owner_returns_research_compatibility(self, agent, mock_research_response, mock_valuation_response):
        """Test backward compatibility method."""
        ticker = "AAPL"
        expertise_level = 5

        with patch.object(agent, '_run_research_phase') as mock_research, \
             patch.object(agent, '_run_valuation_phase') as mock_valuation, \
             patch.object(agent, '_extract_citations_from_response') as mock_citations:
            
            mock_research.return_value = mock_research_response
            mock_valuation.return_value = mock_valuation_response
            mock_citations.return_value = ["Source: AAPL 10-K", "Source: NASDAQ"]

            result = await agent.conduct_owner_returns_research(ticker, expertise_level)

            # Verify backward compatibility structure
            assert result["ticker"] == ticker
            assert result["analysis"] == mock_valuation_response
            assert result["temp_research"] == mock_research_response
            assert result["final_valuation"] == mock_valuation_response
            assert result["workflow"] == "2-step: research → valuation"
            assert result["model_used"] == "gpt-5"
            assert len(result["citations"]) == 2

    def test_extract_citations_from_response(self, agent):
        """Test citation extraction."""
        content = """
        Some analysis with [Source: AAPL 10-K 2024] and more data from [Source: NASDAQ, 2025-08-24].
        Additional info from [Source: FactSet Database].
        """
        
        citations = agent._extract_citations_from_response(content)
        
        assert len(citations) == 3
        assert "AAPL 10-K 2024" in citations
        assert "NASDAQ, 2025-08-24" in citations
        assert "FactSet Database" in citations

    def test_log_research_start(self, agent, caplog):
        """Test research start logging."""
        import logging
        caplog.set_level(logging.INFO)

        session_id = "test_session_123"
        ticker = "AAPL"
        expertise_level = 5

        agent.log_research_start(session_id, ticker, expertise_level)

        # Verify key log content (account for Unicode emojis)
        log_text = caplog.text
        assert "Owner-Returns valuation for AAPL" in log_text
        assert session_id in log_text
        assert "Intermediate" in log_text  # expertise level 5
        assert "GPT-5" in log_text

    def test_create_execution_summary(self, agent):
        """Test execution summary creation."""
        ticker = "AAPL"
        execution_time = 2.5
        research_chars = 1500
        valuation_chars = 2200

        summary = agent._create_execution_summary(ticker, execution_time, research_chars, valuation_chars)

        assert ticker in summary
        assert "2.5 seconds" in summary
        assert "1,500 characters" in summary
        assert "2,200 characters" in summary
        assert "Owner-Returns" in summary
        assert "GPT-5" in summary