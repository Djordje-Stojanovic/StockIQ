#!/usr/bin/env python3
"""Final test - Moody's valuation with fixed implementation."""

import asyncio
import os
from datetime import datetime
from src.agents.valuation_agent import ValuationAgent

async def test_moody():
    """Test Moody's with the fixed implementation."""
    print("=" * 60)
    print("FINAL TEST: Moody's (MCO) Valuation")
    print("Workflow: User -> GPT-5 web search -> temp.md -> GPT-5 analysis -> valuation.md")
    print("=" * 60)
    
    agent = ValuationAgent()
    session_id = f"mco_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ticker = "MCO"
    expertise_level = 10  # Executive level as requested
    
    print(f"\nParameters:")
    print(f"  Ticker: {ticker}")
    print(f"  Expertise: {expertise_level} (Executive)")
    print(f"  Session: {session_id}")
    print(f"\nKey fixes applied:")
    print(f"  - SDK upgraded to 1.101.0")
    print(f"  - Using 8000 tokens (was 1800)")
    print(f"  - Reasoning effort: low (was minimal)")
    print(f"  - Typed content blocks for tools")
    print(f"  - Proper retry logic")
    
    print(f"\nExecuting workflow...")
    
    try:
        result = await agent.conduct_research(session_id, ticker, expertise_level)
        
        print(f"\n{'='*60}")
        print(f"RESULTS:")
        print(f"  Success: {result.success}")
        print(f"  Time: {result.execution_time_seconds:.1f}s")
        print(f"  Files: {len(result.research_files_created)}")
        
        if result.success:
            # Read and show the actual files
            for file_path in result.research_files_created:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_name = os.path.basename(file_path)
                    print(f"\n{'='*60}")
                    print(f"FILE: {file_name} ({len(content):,} characters)")
                    print(f"{'='*60}")
                    
                    # Show first 3000 chars of each file
                    if len(content) > 3000:
                        print(content[:3000])
                        print(f"\n... [{len(content)-3000:,} more characters] ...")
                    else:
                        print(content)
        else:
            print(f"\nError: {result.error_message}")
            
    except Exception as e:
        print(f"\nException: {e}")
    
    print(f"\n{'='*60}")
    print("TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_moody())