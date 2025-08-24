"""End-to-end tests for Valuation Agent with real GPT-5 API calls."""

import os
import pytest
from datetime import datetime
from unittest.mock import patch

from src.agents.valuation_agent import ValuationAgent


class TestValuationWorkflow:
    """End-to-end tests with real API calls."""

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), 
        reason="Real API key required for end-to-end testing"
    )
    @pytest.mark.asyncio
    async def test_real_valuation_workflow_mco(self):
        """Test the exact workflow: User -> GPT-5 web search -> temp.md -> GPT-5 analysis -> valuation.md"""
        agent = ValuationAgent()
        session_id = f"test_e2e_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ticker = "MCO"  # Moody's as requested
        expertise_level = 10  # Executive level as requested
        
        print(f"\nTesting workflow: {ticker} at expertise level {expertise_level}")
        
        # Execute the real workflow
        result = await agent.conduct_research(session_id, ticker, expertise_level)
        
        # Show results regardless of pass/fail
        print(f"\nResults:")
        print(f"   Success: {result.success}")
        print(f"   Files: {result.research_files_created}")
        print(f"   Time: {result.execution_time_seconds:.1f}s")
        
        if result.success:
            # Show actual file contents
            temp_file = f"research_database/sessions/{session_id}/{ticker}/valuation/temp.md"
            val_file = f"research_database/sessions/{session_id}/{ticker}/valuation/valuation.md"
            
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    temp_content = f.read()
                print(f"\ntemp.md ({len(temp_content):,} chars):")
                print("=" * 60)
                print(temp_content[:2000] + ("..." if len(temp_content) > 2000 else ""))
                
            if os.path.exists(val_file):
                with open(val_file, 'r', encoding='utf-8') as f:
                    val_content = f.read()
                print(f"\nvaluation.md ({len(val_content):,} chars):")
                print("=" * 60)
                print(val_content[:2000] + ("..." if len(val_content) > 2000 else ""))
                
            # Basic validation
            assert result.success is True
            assert len(result.research_files_created) == 2
            
        else:
            print(f"\nError: {result.error_message}")
            # Don't fail the test on rate limits - just show what happened
            if "rate limit" not in str(result.error_message).lower():
                assert False, f"Non-rate-limit error: {result.error_message}"

    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), 
        reason="Real API key required for end-to-end testing"
    )
    @pytest.mark.asyncio
    async def test_error_handling_invalid_ticker(self):
        """Test error handling with invalid ticker."""
        agent = ValuationAgent()
        session_id = f"test_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ticker = "INVALID_TICKER_123"
        expertise_level = 5
        
        result = await agent.conduct_research(session_id, ticker, expertise_level)
        
        # Should still return a result (GPT-5 might handle gracefully)
        assert result.agent_name == "valuation_agent"
        # Success depends on how GPT-5 handles invalid tickers
        print(f"\n📊 Error handling test for {ticker}: Success={result.success}")
        if not result.success:
            print(f"Error: {result.error_message}")