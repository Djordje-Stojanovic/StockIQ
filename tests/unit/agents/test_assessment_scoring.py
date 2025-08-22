"""Unit tests for Assessment Agent scoring algorithms."""

import pytest

from src.agents.assessment_agent import AssessmentAgent
from src.models.assessment import AssessmentQuestion, AssessmentResponse


class TestAssessmentScoring:
    """Test suite for Assessment Agent scoring algorithms."""

    @pytest.fixture
    def assessment_agent(self):
        """Create an AssessmentAgent instance for testing."""
        return AssessmentAgent()

    @pytest.fixture
    def varied_difficulty_questions(self):
        """Questions with varied difficulty levels for scoring tests."""
        return [
            # Level 1-3 questions (weight 1.0)
            AssessmentQuestion(
                id=1,
                difficulty_level=1,
                category="general_investing",
                question="Basic Q1",
                options=["A", "B", "C", "D"],
                correct_answer_index=0,
                ticker_context="TEST",
                weight=1.0,
            ),
            AssessmentQuestion(
                id=2,
                difficulty_level=3,
                category="ticker_specific",
                question="Basic Q2",
                options=["A", "B", "C", "D"],
                correct_answer_index=1,
                ticker_context="TEST",
                weight=1.0,
            ),
            # Level 4-7 questions (weight 1.5)
            AssessmentQuestion(
                id=3,
                difficulty_level=5,
                category="sector_expertise",
                question="Intermediate Q1",
                options=["A", "B", "C", "D"],
                correct_answer_index=2,
                ticker_context="TEST",
                weight=1.5,
            ),
            AssessmentQuestion(
                id=4,
                difficulty_level=7,
                category="analytical_sophistication",
                question="Intermediate Q2",
                options=["A", "B", "C", "D"],
                correct_answer_index=3,
                ticker_context="TEST",
                weight=1.5,
            ),
            # Level 8-10 questions (weight 2.0)
            AssessmentQuestion(
                id=5,
                difficulty_level=8,
                category="general_investing",
                question="Advanced Q1",
                options=["A", "B", "C", "D"],
                correct_answer_index=0,
                ticker_context="TEST",
                weight=2.0,
            ),
            AssessmentQuestion(
                id=6,
                difficulty_level=10,
                category="ticker_specific",
                question="Expert Q1",
                options=["A", "B", "C", "D"],
                correct_answer_index=1,
                ticker_context="TEST",
                weight=2.0,
            ),
        ]

    def test_perfect_score_calculation(self, assessment_agent, varied_difficulty_questions):
        """Test scoring with all correct answers."""
        responses = [
            AssessmentResponse(question_id=1, selected_option=0, correct_option=0, time_taken=10.0),
            AssessmentResponse(question_id=2, selected_option=1, correct_option=1, time_taken=15.0),
            AssessmentResponse(question_id=3, selected_option=2, correct_option=2, time_taken=20.0),
            AssessmentResponse(question_id=4, selected_option=3, correct_option=3, time_taken=25.0),
            AssessmentResponse(question_id=5, selected_option=0, correct_option=0, time_taken=30.0),
            AssessmentResponse(question_id=6, selected_option=1, correct_option=1, time_taken=35.0),
        ]

        scores = assessment_agent._calculate_category_scores(varied_difficulty_questions, responses)
        max_score = assessment_agent._calculate_max_possible_score(varied_difficulty_questions)

        # Perfect score should equal max possible
        total_score = sum(scores.values())
        expected_max = 1.0 + 1.0 + 1.5 + 1.5 + 2.0 + 2.0  # Sum of all weights
        assert max_score == expected_max
        assert total_score == expected_max

        # Category breakdown verification
        assert scores["general_investing"] == 3.0  # 1.0 + 2.0
        assert scores["ticker_specific"] == 3.0  # 1.0 + 2.0
        assert scores["sector_expertise"] == 1.5  # 1.5
        assert scores["analytical_sophistication"] == 1.5  # 1.5

    def test_zero_score_calculation(self, assessment_agent, varied_difficulty_questions):
        """Test scoring with all incorrect answers."""
        responses = [
            AssessmentResponse(question_id=1, selected_option=1, correct_option=0, time_taken=10.0),
            AssessmentResponse(question_id=2, selected_option=0, correct_option=1, time_taken=15.0),
            AssessmentResponse(question_id=3, selected_option=0, correct_option=2, time_taken=20.0),
            AssessmentResponse(question_id=4, selected_option=0, correct_option=3, time_taken=25.0),
            AssessmentResponse(question_id=5, selected_option=1, correct_option=0, time_taken=30.0),
            AssessmentResponse(question_id=6, selected_option=0, correct_option=1, time_taken=35.0),
        ]

        scores = assessment_agent._calculate_category_scores(varied_difficulty_questions, responses)

        # All scores should be zero
        assert all(score == 0.0 for score in scores.values())

    def test_mixed_score_calculation(self, assessment_agent, varied_difficulty_questions):
        """Test scoring with mixed correct/incorrect answers."""
        responses = [
            AssessmentResponse(
                question_id=1, selected_option=0, correct_option=0, time_taken=10.0
            ),  # Correct
            AssessmentResponse(
                question_id=2, selected_option=0, correct_option=1, time_taken=15.0
            ),  # Incorrect
            AssessmentResponse(
                question_id=3, selected_option=2, correct_option=2, time_taken=20.0
            ),  # Correct
            AssessmentResponse(
                question_id=4, selected_option=0, correct_option=3, time_taken=25.0
            ),  # Incorrect
            AssessmentResponse(
                question_id=5, selected_option=0, correct_option=0, time_taken=30.0
            ),  # Correct
            AssessmentResponse(
                question_id=6, selected_option=0, correct_option=1, time_taken=35.0
            ),  # Incorrect
        ]

        scores = assessment_agent._calculate_category_scores(varied_difficulty_questions, responses)

        # Expected scores: Q1(1.0) + Q3(1.5) + Q5(2.0) = 4.5 total
        assert scores["general_investing"] == 3.0  # Q1(1.0) + Q5(2.0)
        assert scores["ticker_specific"] == 0.0  # Q2 incorrect, Q6 incorrect
        assert scores["sector_expertise"] == 1.5  # Q3(1.5)
        assert scores["analytical_sophistication"] == 0.0  # Q4 incorrect

    def test_partial_credit_scoring(self, assessment_agent):
        """Test scoring with partial credit awards."""
        questions = [
            AssessmentQuestion(
                id=1,
                difficulty_level=5,
                category="general_investing",
                question="Test Q1",
                options=["A", "B", "C", "D"],
                correct_answer_index=0,
                ticker_context="TEST",
                weight=2.0,
            ),
            AssessmentQuestion(
                id=2,
                difficulty_level=8,
                category="ticker_specific",
                question="Test Q2",
                options=["A", "B", "C", "D"],
                correct_answer_index=1,
                ticker_context="TEST",
                weight=1.5,
            ),
        ]

        responses = [
            AssessmentResponse(
                question_id=1,
                selected_option=1,
                correct_option=0,
                time_taken=20.0,
                partial_credit=0.5,  # 50% partial credit
            ),
            AssessmentResponse(
                question_id=2,
                selected_option=0,
                correct_option=1,
                time_taken=30.0,
                partial_credit=0.25,  # 25% partial credit
            ),
        ]

        scores = assessment_agent._calculate_category_scores(questions, responses)

        # Expected: Q1: 0.5 * 2.0 = 1.0, Q2: 0.25 * 1.5 = 0.375
        assert scores["general_investing"] == 1.0
        assert scores["ticker_specific"] == 0.375

    def test_weight_distribution_correctness(self, assessment_agent):
        """Test that weight assignment follows expected patterns."""
        # Test weight calculation logic implicitly through question creation
        questions = []

        # Create questions with different difficulty levels
        for level in range(1, 11):
            expected_weight = 1.0 if level <= 3 else 1.5 if level <= 7 else 2.0

            question = AssessmentQuestion(
                id=level,
                difficulty_level=level,
                category="general_investing",
                question=f"Level {level} question",
                options=["A", "B", "C", "D"],
                correct_answer_index=0,
                ticker_context="TEST",
                weight=expected_weight,
            )
            questions.append(question)

        # Verify max score calculation works with proper weights
        max_score = assessment_agent._calculate_max_possible_score(questions)

        # Expected: 3 questions * 1.0 + 4 questions * 1.5 + 3 questions * 2.0
        expected_max = (3 * 1.0) + (4 * 1.5) + (3 * 2.0)
        assert max_score == expected_max

    def test_category_distribution_scoring(self, assessment_agent):
        """Test scoring across all category types."""
        questions = [
            AssessmentQuestion(
                id=1,
                difficulty_level=5,
                category="general_investing",
                question="General Q",
                options=["A", "B", "C", "D"],
                correct_answer_index=0,
                ticker_context="TEST",
                weight=1.5,
            ),
            AssessmentQuestion(
                id=2,
                difficulty_level=5,
                category="ticker_specific",
                question="Ticker Q",
                options=["A", "B", "C", "D"],
                correct_answer_index=1,
                ticker_context="TEST",
                weight=1.5,
            ),
            AssessmentQuestion(
                id=3,
                difficulty_level=5,
                category="sector_expertise",
                question="Sector Q",
                options=["A", "B", "C", "D"],
                correct_answer_index=2,
                ticker_context="TEST",
                weight=1.5,
            ),
            AssessmentQuestion(
                id=4,
                difficulty_level=5,
                category="analytical_sophistication",
                question="Analysis Q",
                options=["A", "B", "C", "D"],
                correct_answer_index=3,
                ticker_context="TEST",
                weight=1.5,
            ),
        ]

        # All correct responses
        responses = [
            AssessmentResponse(question_id=1, selected_option=0, correct_option=0, time_taken=20.0),
            AssessmentResponse(question_id=2, selected_option=1, correct_option=1, time_taken=20.0),
            AssessmentResponse(question_id=3, selected_option=2, correct_option=2, time_taken=20.0),
            AssessmentResponse(question_id=4, selected_option=3, correct_option=3, time_taken=20.0),
        ]

        scores = assessment_agent._calculate_category_scores(questions, responses)

        # Each category should have equal score
        for category in assessment_agent.categories:
            assert scores[category] == 1.5

    def test_edge_case_empty_responses(self, assessment_agent, varied_difficulty_questions):
        """Test scoring with no responses provided."""
        scores = assessment_agent._calculate_category_scores(varied_difficulty_questions, [])

        # All scores should be zero
        assert all(score == 0.0 for score in scores.values())

    def test_edge_case_mismatched_responses(self, assessment_agent, varied_difficulty_questions):
        """Test scoring with response IDs that don't match questions."""
        responses = [
            AssessmentResponse(
                question_id=19, selected_option=0, correct_option=0, time_taken=10.0
            ),
            AssessmentResponse(
                question_id=20, selected_option=1, correct_option=1, time_taken=15.0
            ),
        ]

        scores = assessment_agent._calculate_category_scores(varied_difficulty_questions, responses)

        # All scores should be zero since no responses match questions
        assert all(score == 0.0 for score in scores.values())

    def test_scoring_consistency(self, assessment_agent):
        """Test that scoring is consistent across multiple calculations."""
        questions = [
            AssessmentQuestion(
                id=1,
                difficulty_level=5,
                category="general_investing",
                question="Consistency test",
                options=["A", "B", "C", "D"],
                correct_answer_index=1,
                ticker_context="TEST",
                weight=1.5,
            )
        ]

        responses = [
            AssessmentResponse(question_id=1, selected_option=1, correct_option=1, time_taken=25.0)
        ]

        # Calculate scores multiple times
        scores1 = assessment_agent._calculate_category_scores(questions, responses)
        scores2 = assessment_agent._calculate_category_scores(questions, responses)
        scores3 = assessment_agent._calculate_category_scores(questions, responses)

        # All calculations should yield identical results
        assert scores1 == scores2 == scores3
        assert scores1["general_investing"] == 1.5
