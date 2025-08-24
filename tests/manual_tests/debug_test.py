#!/usr/bin/env python3
"""Quick debug test to see response structure."""

import logging
import asyncio
from src.agents.valuation_agent import ValuationAgent

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def debug_test():
    """Quick test to see what response structure we get."""
    agent = ValuationAgent()
    
    # Try a simple research call
    try:
        print("Testing GPT-5 web search...")
        temp_md = await agent._run_research_phase("debug", "AAPL", 5)
        print(f"Result: {len(temp_md)} chars")
        print(f"Content: {temp_md[:500]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_test())