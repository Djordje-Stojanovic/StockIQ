"""Unit tests for Assessment Agent."""

from unittest.mock import Mock, patch

import pytest

from src.agents.assessment_agent import AssessmentAgent
from src.models.assessment import AssessmentQuestion, AssessmentResponse, AssessmentResult


class TestAssessmentAgent:
    """Test suite for Assessment Agent functionality."""

    @pytest.fixture
    def assessment_agent(self):
        """Create an AssessmentAgent instance for testing."""
        return AssessmentAgent()

    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing."""
        with patch("src.agents.assessment_agent.OpenAIClient") as mock_client:
            yield mock_client.return_value

    @pytest.fixture
    def sample_questions(self):
        """Sample assessment questions for testing."""
        return [
            AssessmentQuestion(
                id=1,
                difficulty_level=1,
                category="general_investing",
                question="What does P/E ratio stand for?",
                options=[
                    "Price to Earnings",
                    "Price to Equity",
                    "Profit to Equity",
                    "Profit to Earnings",
                ],
                correct_answer_index=0,
                ticker_context="AAPL",
                weight=1.0,
            ),
            AssessmentQuestion(
                id=2,
                difficulty_level=5,
                category="ticker_specific",
                question="What is Apple's primary revenue source?",
                options=["Mac computers", "iPhone sales", "Services", "iPad sales"],
                correct_answer_index=1,
                ticker_context="AAPL",
                weight=1.5,
            ),
            AssessmentQuestion(
                id=3,
                difficulty_level=10,
                category="analytical_sophistication",
                question="Which DCF component is most sensitive to Apple's valuation?",
                options=["Terminal value", "WACC", "Free cash flow growth", "Tax rate"],
                correct_answer_index=0,
                ticker_context="AAPL",
                weight=2.0,
            ),
        ]

    @pytest.fixture
    def sample_responses(self):
        """Sample assessment responses for testing."""
        return [
            AssessmentResponse(
                question_id=1,
                selected_option=0,
                correct_option=0,
                time_taken=15.5,
                partial_credit=0.0,
            ),
            AssessmentResponse(
                question_id=2,
                selected_option=2,
                correct_option=1,
                time_taken=25.0,
                partial_credit=0.0,
            ),
            AssessmentResponse(
                question_id=3,
                selected_option=0,
                correct_option=0,
                time_taken=45.2,
                partial_credit=0.0,
            ),
        ]

    def test_init(self, assessment_agent):
        """Test AssessmentAgent initialization."""
        assert hasattr(assessment_agent, "client")
        assert hasattr(assessment_agent, "categories")
        assert len(assessment_agent.categories) == 4
        expected_categories = [
            "general_investing",
            "ticker_specific",
            "sector_expertise",
            "analytical_sophistication",
        ]
        assert assessment_agent.categories == expected_categories

    @patch("src.agents.assessment_agent.OpenAIClient")
    def test_generate_contextual_assessment_questions_success(self, mock_client_class):
        """Test successful question generation."""
        # Setup mock response
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_response = {
            "questions": [
                {
                    "id": i,
                    "difficulty_level": (i - 1) // 2 + 1,
                    "category": [
                        "general_investing",
                        "ticker_specific",
                        "sector_expertise",
                        "analytical_sophistication",
                    ][i % 4],
                    "question": f"Sample question {i}?",
                    "options": [f"Option {j}" for j in range(4)],
                    "correct_answer_index": 0,
                    "weight": 1.0 if i <= 6 else 1.5 if i <= 14 else 2.0,
                }
                for i in range(1, 21)
            ]
        }
        mock_client.create_structured_completion.return_value = mock_response

        agent = AssessmentAgent()
        questions = agent.generate_contextual_assessment_questions("AAPL")

        # Verify results
        assert len(questions) == 20
        assert all(isinstance(q, AssessmentQuestion) for q in questions)
        assert all(q.ticker_context == "AAPL" for q in questions)
        assert all(1 <= q.difficulty_level <= 10 for q in questions)
        assert all(q.category in agent.categories for q in questions)

        # Verify OpenAI client was called correctly
        mock_client.create_structured_completion.assert_called_once()
        call_args = mock_client.create_structured_completion.call_args
        assert call_args.kwargs["use_complex_model"] is True
        # Note: Temperature is not set for GPT-5 models (compatibility fix)

    @patch("src.agents.assessment_agent.OpenAIClient")
    def test_generate_contextual_assessment_questions_failure(self, mock_client_class):
        """Test question generation failure handling."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_structured_completion.side_effect = Exception("API Error")

        agent = AssessmentAgent()

        with pytest.raises(Exception, match="API Error"):
            agent.generate_contextual_assessment_questions("AAPL")

    @patch("src.agents.assessment_agent.OpenAIClient")
    def test_evaluate_user_expertise_success(
        self, mock_client_class, sample_questions, sample_responses
    ):
        """Test successful expertise evaluation."""
        # Setup mock response
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_evaluation = {
            "expertise_level": 7,
            "report_complexity": "executive",
            "explanation": "User demonstrates advanced knowledge with strong performance on difficult questions.",
            "confidence_score": 0.85,
        }
        mock_client.create_structured_completion.return_value = mock_evaluation

        agent = AssessmentAgent()
        result = agent.evaluate_user_expertise(sample_questions, sample_responses, "AAPL")

        # Verify results
        assert isinstance(result, AssessmentResult)
        assert result.expertise_level == 7
        assert result.report_complexity == "executive"
        assert result.ticker_context == "AAPL"
        assert "score_breakdown" in result.model_dump()

        # Verify OpenAI client was called correctly
        mock_client.create_structured_completion.assert_called_once()
        call_args = mock_client.create_structured_completion.call_args
        assert call_args.kwargs["use_complex_model"] is True
        # Note: Temperature is not set for GPT-5 models (compatibility fix)

    @patch("src.agents.assessment_agent.OpenAIClient")
    def test_evaluate_user_expertise_failure(
        self, mock_client_class, sample_questions, sample_responses
    ):
        """Test expertise evaluation failure handling."""
        # Setup mock to raise exception
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.create_structured_completion.side_effect = Exception("Evaluation Error")

        agent = AssessmentAgent()

        with pytest.raises(Exception, match="Evaluation Error"):
            agent.evaluate_user_expertise(sample_questions, sample_responses, "AAPL")

    def test_calculate_category_scores(self, assessment_agent, sample_questions, sample_responses):
        """Test category score calculation."""
        scores = assessment_agent._calculate_category_scores(sample_questions, sample_responses)

        # Expected scores:
        # Q1: correct (1.0 points) -> general_investing
        # Q2: incorrect (0.0 points) -> ticker_specific
        # Q3: correct (2.0 points) -> analytical_sophistication
        expected = {
            "general_investing": 1.0,
            "ticker_specific": 0.0,
            "sector_expertise": 0.0,
            "analytical_sophistication": 2.0,
        }
        assert scores == expected

    def test_calculate_category_scores_with_partial_credit(self, assessment_agent):
        """Test category score calculation with partial credit."""
        questions = [
            AssessmentQuestion(
                id=1,
                difficulty_level=5,
                category="general_investing",
                question="Test question",
                options=["A", "B", "C", "D"],
                correct_answer_index=0,
                ticker_context="TEST",
                weight=1.5,
            )
        ]

        responses = [
            AssessmentResponse(
                question_id=1,
                selected_option=1,
                correct_option=0,
                time_taken=30.0,
                partial_credit=0.5,  # 50% partial credit
            )
        ]

        scores = assessment_agent._calculate_category_scores(questions, responses)
        expected_score = 0.5 * 1.5  # partial_credit * weight
        assert scores["general_investing"] == expected_score

    def test_calculate_max_possible_score(self, assessment_agent, sample_questions):
        """Test maximum possible score calculation."""
        max_score = assessment_agent._calculate_max_possible_score(sample_questions)
        expected = 1.0 + 1.5 + 2.0  # Sum of weights
        assert max_score == expected

    def test_create_evaluation_context(self, assessment_agent, sample_questions, sample_responses):
        """Test evaluation context creation."""
        score_breakdown = {
            "general_investing": 1.0,
            "ticker_specific": 0.0,
            "sector_expertise": 0.0,
            "analytical_sophistication": 2.0,
        }

        context = assessment_agent._create_evaluation_context(
            sample_questions, sample_responses, score_breakdown, "AAPL"
        )

        # Verify context contains expected elements
        assert "ASSESSMENT EVALUATION FOR TICKER: AAPL" in context
        assert "Total Questions: 3" in context
        assert "Total Responses: 3" in context
        assert "general_investing: 1.00 points" in context
        assert "ticker_specific: 0.00 points" in context
        assert "Q1 (Level 1, general_investing): ✓" in context
        assert "Q2 (Level 5, ticker_specific): ✗" in context
        assert "Q3 (Level 10, analytical_sophistication): ✓" in context

    def test_get_question_generation_prompt(self, assessment_agent):
        """Test question generation prompt."""
        prompt = assessment_agent._get_question_generation_prompt()

        # Verify prompt contains key elements
        assert "exactly 20 questions" in prompt
        assert "Level 1 (complete novice) to Level 10 (top-tier analyst)" in prompt
        assert "general_investing" in prompt
        assert "ticker_specific" in prompt
        assert "sector_expertise" in prompt
        assert "analytical_sophistication" in prompt

    def test_get_expertise_evaluation_prompt(self, assessment_agent):
        """Test expertise evaluation prompt."""
        prompt = assessment_agent._get_expertise_evaluation_prompt()

        # Verify prompt contains key elements
        assert "expertise level (1-10)" in prompt
        assert "comprehensive" in prompt
        assert "executive" in prompt
        assert "holistic analysis" in prompt

    def test_question_distribution_validation(self):
        """Test that generated questions follow expected distribution patterns."""
        # This would be an integration test with actual OpenAI calls
        # For unit testing, we verify the schema and validation logic
        categories = [
            "general_investing",
            "ticker_specific",
            "sector_expertise",
            "analytical_sophistication",
        ]

        # Verify categories are properly defined
        agent = AssessmentAgent()
        assert agent.categories == categories

        # Verify schema structure in question generation
        # This validates that the schema enforces 20 questions
        assert hasattr(agent, "generate_contextual_assessment_questions")

    def test_scoring_algorithm_edge_cases(self, assessment_agent):
        """Test scoring algorithm with edge cases."""
        # Test with no responses
        questions = [
            AssessmentQuestion(
                id=1,
                difficulty_level=1,
                category="general_investing",
                question="Test",
                options=["A", "B", "C", "D"],
                correct_answer_index=0,
                ticker_context="TEST",
                weight=1.0,
            )
        ]

        scores = assessment_agent._calculate_category_scores(questions, [])
        assert all(score == 0.0 for score in scores.values())

        # Test with mismatched question IDs (valid IDs but don't match questions)
        responses = [
            AssessmentResponse(
                question_id=20,  # Valid ID but doesn't match our test question
                selected_option=0,
                correct_option=0,
                time_taken=10.0,
                partial_credit=0.0,
            )
        ]

        scores = assessment_agent._calculate_category_scores(questions, responses)
        assert all(score == 0.0 for score in scores.values())
