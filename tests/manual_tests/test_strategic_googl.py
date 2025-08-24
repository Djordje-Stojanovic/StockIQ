"""Manual test for StrategicAgent with real GOOGL data."""

import asyncio
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_strategic_agent_googl():
    """Test StrategicAgent with real GOOGL ticker."""
    # Import here to avoid path issues
    import sys
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from src.agents.strategic_agent import StrategicAgent
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("OPENAI_API_KEY not set. Please set your OpenAI API key.")
        return
    
    print("Starting Strategic Agent manual test with GOOGL")
    print("=" * 60)
    
    # Initialize agent
    agent = StrategicAgent()
    
    # Test parameters
    session_id = f"manual_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ticker = "GOOGL"
    expertise_level = 5  # Intermediate level
    
    # Mock valuation context (simulating previous valuation agent results)
    valuation_context = {
        "summary": """Owner-Returns Valuation Complete for GOOGL:
✅ Current FCF Yield: 4.2%
✅ Target IRR: 14.5%
✅ Investment Recommendation: BUY
✅ Trading below fair value with strong FCF generation
✅ Conservative assumptions support 14%+ annual returns""",
        "agent_name": "valuation_agent",
        "confidence_score": 0.85
    }
    
    try:
        print(f"Running strategic analysis for {ticker}")
        print(f"Session ID: {session_id}")
        print(f"Expertise Level: {expertise_level}")
        print(f"Valuation Context: Present")
        print()
        
        # Execute full research workflow
        start_time = datetime.now()
        result = await agent.conduct_research(
            session_id=session_id,
            ticker=ticker,
            expertise_level=expertise_level,
            context=valuation_context
        )
        execution_time = (datetime.now() - start_time).total_seconds()
        
        print("=" * 60)
        print("STRATEGIC ANALYSIS RESULTS")
        print("=" * 60)
        
        if result.success:
            print("Strategic analysis completed successfully!")
            print(f"Total execution time: {execution_time:.1f} seconds")
            print(f"Confidence score: {result.confidence_score}")
            print(f"Files created: {len(result.research_files_created)}")
            
            print("\nFiles created:")
            for file_path in result.research_files_created:
                print(f"  - {file_path}")
            
            print(f"\nSummary:")
            print("-" * 40)
            print(result.summary)
            
            # Try to read and display portions of the created files
            print("\n" + "=" * 60)
            print("SAMPLE FILE CONTENT")
            print("=" * 60)
            
            for file_path in result.research_files_created:
                if os.path.exists(file_path):
                    print(f"\nContent from {os.path.basename(file_path)}:")
                    print("-" * 50)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Display first 500 characters
                        if len(content) > 500:
                            print(content[:500] + "\n... [truncated]")
                        else:
                            print(content)
                    
                    print(f"\nFile stats: {len(content)} characters")
                else:
                    print(f"File not found: {file_path}")
            
        else:
            print("Strategic analysis failed!")
            print(f"Error: {result.error_message}")
            print(f"Execution time: {execution_time:.1f} seconds")
        
    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Strategic Agent manual test completed")
    print("=" * 60)

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("src/agents/strategic_agent.py"):
        print("Please run this test from the StockIQ root directory")
        print("   cd to the directory containing src/ and run:")
        print("   py tests/manual_tests/test_strategic_googl.py")
        exit(1)
    
    asyncio.run(test_strategic_agent_googl())