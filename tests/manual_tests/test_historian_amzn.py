"""Manual test for HistorianAgent with Amazon (AMZN)."""

import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.agents.historian_agent import HistorianAgent


async def test_historian_agent_amzn():
    """Test HistorianAgent with real Amazon data."""
    print("\n" + "=" * 80)
    print("MANUAL TEST: Company Historian Agent - Amazon (AMZN)")
    print("=" * 80)

    # Initialize agent
    print("\n1. Initializing HistorianAgent...")
    agent = HistorianAgent()
    print("   [OK] Agent initialized")

    # Test parameters
    session_id = f"manual_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ticker = "AMZN"
    expertise_level = 5  # Intermediate level

    # Mock context from previous agents (simulating valuation and strategic agents)
    context = {
        "valuation": {
            "summary": """Amazon Valuation Analysis:
[OK] Current FCF Yield: 2.8%
[OK] Owner-Returns IRR: 14.2%
[OK] AWS operating margins: 35%
[OK] Retail margins improving: 3.5% -> 5.2%
[OK] Fair Value: $185 (current: $170)
[OK] Investment Recommendation: BUY
[OK] Strong cash flow generation from AWS offsetting retail investments"""
        },
        "strategic": {
            "summary": """Amazon Strategic Analysis:
[OK] Competitive Moat: WIDE (AWS dominance, Prime ecosystem)
[OK] Market Position: DOMINANT (40% US e-commerce, 33% cloud)
[OK] Strategic Risks: MODERATE (regulatory, competition from MSFT/GOOGL in cloud)
[OK] Management Quality: EXCELLENT (Jassy proving capable successor)
[OK] Growth Opportunities: AI services, healthcare, logistics-as-a-service"""
        }
    }

    print(f"\n2. Starting historical research for {ticker}")
    print(f"   Session ID: {session_id}")
    print(f"   Expertise Level: {expertise_level} (Intermediate)")
    print("   Context: Valuation + Strategic data provided")

    try:
        # Execute research
        print("\n3. Executing 2-step research workflow...")
        print("   Step 1: GPT-5 web search for historical data...")
        result = await agent.conduct_research(
            session_id=session_id,
            ticker=ticker,
            expertise_level=expertise_level,
            context=context
        )

        # Display results
        print("\n4. Research Results:")
        print(f"   Success: {result.success}")
        print(f"   Agent: {result.agent_name}")
        print(f"   Execution Time: {result.execution_time_seconds:.1f} seconds")
        print(f"   Confidence Score: {result.confidence_score}")

        if result.success:
            print(f"\n5. Files Created ({len(result.research_files_created)}):")
            for file in result.research_files_created:
                print(f"   - {file}")
                # Check if file exists and show size
                if os.path.exists(file):
                    size = os.path.getsize(file)
                    print(f"     Size: {size:,} bytes")

            print("\n6. Summary:")
            print(result.summary)

            # Read and display snippets of the generated files
            print("\n7. File Content Samples:")
            for file in result.research_files_created:
                if os.path.exists(file):
                    print(f"\n   --- {os.path.basename(file)} (first 500 chars) ---")
                    with open(file, encoding='utf-8') as f:
                        content = f.read()
                        print(f"   {content[:500]}...")
                        print(f"   [Total length: {len(content):,} characters]")

            # Display key historical insights
            if "company_history.md" in result.research_files_created[1]:
                history_file = result.research_files_created[1]
                with open(history_file, encoding='utf-8') as f:
                    content = f.read()

                    print("\n8. Key Historical Insights Found:")

                    # Check for key sections
                    sections_to_check = [
                        "Executive Summary",
                        "Founding & Early Years",
                        "Leadership Evolution",
                        "Crisis Management",
                        "Strategic Decision",
                        "Predictive Historical Patterns"
                    ]

                    for section in sections_to_check:
                        if section in content:
                            print(f"   [OK] {section} section present")

                    # Check for specific Amazon milestones
                    amazon_milestones = [
                        "1994",  # Founded
                        "1997",  # IPO
                        "Bezos",  # Founder
                        "AWS",   # Cloud launch
                        "Prime",  # Prime membership
                        "Jassy",  # Current CEO
                        "COVID",  # Pandemic response
                        "Whole Foods",  # Major acquisition
                    ]

                    print("\n   Amazon-specific content found:")
                    for milestone in amazon_milestones:
                        if milestone in content:
                            print(f"   [OK] {milestone} mentioned")

        else:
            print(f"\n   ERROR: {result.error_message}")

    except Exception as e:
        print(f"\n   ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)


if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("src/agents/historian_agent.py"):
        print("Please run this test from the StockIQ root directory")
        print("   cd to the directory containing src/ and run:")
        print("   py tests/manual_tests/test_historian_amzn.py")
        exit(1)

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key before running this test")
        exit(1)

    # Run the test
    asyncio.run(test_historian_agent_amzn())
