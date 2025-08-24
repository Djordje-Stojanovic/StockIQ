#!/usr/bin/env python3
"""Real AI integration test for Assessment Agent - QA Critical Test."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agents.assessment_agent import AssessmentAgent
from src.models.assessment import AssessmentResponse


async def test_real_ai_assessment():
    """Test real AI question generation and evaluation."""
    print("CRITICAL QA TEST: Testing Real AI Assessment Components")
    print("=" * 60)

    try:
        # Initialize agent
        agent = AssessmentAgent()
        ticker = "AAPL"

        print(f"Testing question generation for {ticker}...")

        # Test 1: Real question generation
        questions = agent.generate_contextual_assessment_questions(ticker)

        print(f"[SUCCESS] Generated {len(questions)} questions successfully!")
        print(
            f"Sample question (Level {questions[0].difficulty_level}): {questions[0].question[:100]}..."
        )

        # Verify question quality
        categories = {q.category for q in questions}
        difficulty_levels = {q.difficulty_level for q in questions}

        print(f"Categories covered: {len(categories)} ({', '.join(categories)})")
        print(f"Difficulty levels: {min(difficulty_levels)}-{max(difficulty_levels)}")

        # Test 2: Create sample responses (mix of correct/incorrect)
        responses = []
        for i, question in enumerate(questions[:5]):  # Test first 5 questions
            # Simulate mix of correct (60%) and incorrect (40%) responses
            selected = (
                question.correct_answer_index
                if i % 5 < 3
                else (question.correct_answer_index + 1) % 4
            )

            response = AssessmentResponse(
                question_id=question.id,
                selected_option=selected,
                correct_option=question.correct_answer_index,
                time_taken=15.0 + (i * 2.0),
                partial_credit=0.0,
            )
            responses.append(response)

        print(f"Created {len(responses)} sample responses (60% correct)")

        # Test 3: Real expertise evaluation
        print("Testing AI expertise evaluation...")
        result = agent.evaluate_user_expertise(questions, responses, ticker)

        print("[SUCCESS] Expertise evaluation completed!")
        print(f"Expertise Level: {result.expertise_level}/10")
        print(f"Report Complexity: {result.report_complexity}")
        print(f"AI Explanation: {result.explanation[:200]}...")

        # Test 4: Validate result structure
        assert 1 <= result.expertise_level <= 10, (
            f"Invalid expertise level: {result.expertise_level}"
        )
        assert result.report_complexity in ["comprehensive", "executive"], (
            f"Invalid complexity: {result.report_complexity}"
        )
        assert len(result.explanation) >= 100, "Explanation too short"
        assert result.ticker_context == ticker, "Ticker context mismatch"

        print("\n[SUCCESS] ALL AI TESTS PASSED - REAL AI FUNCTIONALITY CONFIRMED!")
        return True

    except Exception as e:
        print(f"\n[FAILED] AI TEST FAILED: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Load environment
    from dotenv import load_dotenv

    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        print("[ERROR] OPENAI_API_KEY not found in environment")
        sys.exit(1)

    success = asyncio.run(test_real_ai_assessment())
    sys.exit(0 if success else 1)
