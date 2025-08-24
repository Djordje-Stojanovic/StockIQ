#!/usr/bin/env python3
"""Test Google (GOOGL) with optimized GPT-5-mini + GPT-5 configuration."""

import asyncio
import os
from datetime import datetime
from src.agents.valuation_agent import ValuationAgent

async def test_googl():
    """Test Google with the optimized configuration."""
    print("=" * 80)
    print("OPTIMIZED TEST: Google (GOOGL) Valuation")
    print("Research: GPT-5-mini (32k, high verbosity, 200k TPM)")
    print("Analysis: GPT-5 (12k, medium verbosity, 30k TPM)")
    print("=" * 80)
    
    agent = ValuationAgent()
    session_id = f"googl_optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ticker = "GOOGL"
    expertise_level = 10  # Executive level
    
    print(f"\nParameters:")
    print(f"  Ticker: {ticker}")
    print(f"  Expertise: {expertise_level} (Executive)")
    print(f"  Session: {session_id}")
    print(f"\nOptimizations applied:")
    print(f"  - Research: GPT-5-mini, 32k tokens, high verbosity")
    print(f"  - Analysis: GPT-5, 12k tokens, medium verbosity")
    print(f"  - Rate limits: 200k TPM for research, 30k TPM for analysis")
    
    print(f"\nStarting workflow...")
    
    try:
        result = await agent.conduct_research(session_id, ticker, expertise_level)
        
        print(f"\n{'='*80}")
        print(f"RESULTS:")
        print(f"  Success: {result.success}")
        print(f"  Time: {result.execution_time_seconds:.1f}s")
        print(f"  Files Created: {len(result.research_files_created)}")
        
        if result.success:
            # Read and show both files
            for file_path in result.research_files_created:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_name = os.path.basename(file_path)
                    print(f"\n{'='*80}")
                    print(f"FILE: {file_name} ({len(content):,} characters)")
                    print(f"{'='*80}")
                    
                    # Show first 4000 chars to see more content
                    if len(content) > 4000:
                        print(content[:4000])
                        print(f"\n... [{len(content)-4000:,} more characters] ...")
                    else:
                        print(content)
                        
                print(f"\n{'='*80}")
                print(f"WORKFLOW SUCCESS!")
                print(f"✅ GPT-5-mini research: {len(result.research_files_created[0] if result.research_files_created else '')} chars")
                print(f"✅ GPT-5 analysis: Complete valuation.md")
                print(f"✅ Total time: {result.execution_time_seconds:.1f}s")
        else:
            print(f"\nFAILED: {result.error_message}")
            
    except Exception as e:
        print(f"\nException: {e}")
    
    print(f"\n{'='*80}")
    print("TEST COMPLETE")

if __name__ == "__main__":
    asyncio.run(test_googl())