"""Assessment Agent for dynamically generating contextual investment questions."""

import logging

from ..models.assessment import AssessmentQuestion, AssessmentResponse, AssessmentResult
from ..utils.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class AssessmentAgent:
    """
    Assessment Agent that generates contextual questions and evaluates expertise.

    This agent uses GPT-5 for complex tasks (question generation and holistic evaluation)
    and adapts questions specifically to the chosen ticker symbol.
    """

    def __init__(self):
        """Initialize the Assessment Agent with OpenAI client."""
        self.client = OpenAIClient()
        self.categories = [
            "general_investing",
            "ticker_specific",
            "sector_expertise",
            "analytical_sophistication",
        ]

    def generate_contextual_assessment_questions(self, ticker: str) -> list[AssessmentQuestion]:
        """
        Generate 20 contextual questions tailored to specific ticker.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "ASML")

        Returns:
            List of 20 AssessmentQuestion objects with progressive difficulty

        Raises:
            Exception: If question generation fails
        """
        try:
            logger.info(f"Generating contextual assessment questions for ticker: {ticker}")

            # Define the JSON schema for structured response
            questions_schema = {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer", "minimum": 1, "maximum": 20},
                                "difficulty_level": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 10,
                                },
                                "category": {
                                    "type": "string",
                                    "enum": [
                                        "general_investing",
                                        "ticker_specific",
                                        "sector_expertise",
                                        "analytical_sophistication",
                                    ],
                                },
                                "question": {"type": "string", "maxLength": 800},
                                "options": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 4,
                                    "maxItems": 4,
                                },
                                "correct_answer_index": {
                                    "type": "integer",
                                    "minimum": 0,
                                    "maximum": 3,
                                },
                                "weight": {"type": "number", "minimum": 1.0, "maximum": 2.0},
                            },
                            "required": [
                                "id",
                                "difficulty_level",
                                "category",
                                "question",
                                "options",
                                "correct_answer_index",
                                "weight",
                            ],
                            "additionalProperties": False,
                        },
                        "minItems": 20,
                        "maxItems": 20,
                    }
                },
                "required": ["questions"],
                "additionalProperties": False,
            }

            # Create the assessment prompt
            messages = [
                {"role": "system", "content": self._get_question_generation_prompt()},
                {
                    "role": "user",
                    "content": f"""Generate exactly 20 contextual assessment questions for ticker symbol: {ticker}

CRITICAL REQUIREMENTS:
1. Generate exactly 20 questions (questions 1-20)
2. Use exactly 5 questions per category: general_investing, ticker_specific, sector_expertise, analytical_sophistication
3. Progressive difficulty: 2 questions each for levels 1-10 (Level 1 = complete novice, Level 10 = top-tier analyst)
4. Questions must be contextually relevant to {ticker} and its industry/sector
5. Each question must have exactly 4 multiple choice options
6. Assign appropriate weights: Level 1-3 = 1.0, Level 4-7 = 1.5, Level 8-10 = 2.0

Please generate the questions now.""",
                },
            ]

            # Generate questions using GPT-5 (complex model)
            # Note: GPT-5 only supports default temperature (1.0)
            logger.info(f"Sending question generation request to OpenAI for {ticker}")
            logger.debug(f"Question generation messages: {messages}")

            response_data = self.client.create_structured_completion(
                messages=messages,
                response_schema=questions_schema,
                use_complex_model=True,  # Use GPT-5 for intelligent question generation
                temperature=None,  # Use default temperature for GPT-5 compatibility
            )

            logger.debug(f"Raw OpenAI response: {response_data}")

            # Check if all correct answers are in position 0 (debugging)
            if "questions" in response_data:
                answer_positions = [
                    q.get("correct_answer_index", 0) for q in response_data["questions"]
                ]
                logger.warning(f"Correct answer positions: {answer_positions}")
                if all(pos == 0 for pos in answer_positions):
                    logger.error(
                        "AI GENERATED ALL CORRECT ANSWERS IN POSITION 0 - RANDOMIZATION FAILED!"
                    )

            # Convert to AssessmentQuestion objects and force randomize correct answers
            import random

            questions = []
            for q_data in response_data["questions"]:
                # Force randomize correct answer position if AI didn't do it
                original_correct_index = q_data["correct_answer_index"]
                options = q_data["options"].copy()

                # Generate a random position for the correct answer
                new_correct_index = random.randint(0, 3)

                # If position changed, swap the options
                if new_correct_index != original_correct_index:
                    # Swap correct answer to new position
                    correct_option = options[original_correct_index]
                    options[original_correct_index] = options[new_correct_index]
                    options[new_correct_index] = correct_option
                    logger.info(
                        f"Q{q_data['id']}: Moved correct answer from position {original_correct_index} to {new_correct_index}"
                    )

                question = AssessmentQuestion(
                    id=q_data["id"],
                    difficulty_level=q_data["difficulty_level"],
                    category=q_data["category"],
                    question=q_data["question"],
                    options=options,  # Use potentially shuffled options
                    correct_answer_index=new_correct_index,  # Use new position
                    ticker_context=ticker,
                    weight=q_data["weight"],
                )
                questions.append(question)

            logger.info(f"Successfully generated {len(questions)} questions for {ticker}")
            return questions

        except Exception as e:
            logger.error(f"Failed to generate assessment questions for {ticker}: {str(e)}")
            raise

    def evaluate_user_expertise(
        self, questions: list[AssessmentQuestion], responses: list[AssessmentResponse], ticker: str
    ) -> AssessmentResult:
        """
        Evaluate user expertise using AI holistic assessment.

        Args:
            questions: List of assessment questions that were asked
            responses: List of user responses to evaluate
            ticker: Ticker symbol for context

        Returns:
            AssessmentResult with expertise level (1-10) and explanation

        Raises:
            Exception: If evaluation fails
        """
        try:
            logger.info(f"Evaluating user expertise for ticker: {ticker}")

            # Calculate basic scores by category and overall percentage
            score_breakdown = self._calculate_category_scores(questions, responses)
            percentage_score = self._calculate_score_percentage(questions, responses)
            suggested_level = self._map_percentage_to_expertise_level(percentage_score)

            # Create evaluation context for AI assessment
            evaluation_context = self._create_evaluation_context(
                questions, responses, score_breakdown, ticker, percentage_score, suggested_level
            )

            # Define schema for AI evaluation response
            evaluation_schema = {
                "type": "object",
                "properties": {
                    "expertise_level": {"type": "integer", "minimum": 1, "maximum": 10},
                    "explanation": {"type": "string", "minLength": 100, "maxLength": 1000},
                    "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                },
                "required": [
                    "expertise_level",
                    "explanation",
                    "confidence_score",
                ],
                "additionalProperties": False,
            }

            messages = [
                {"role": "system", "content": self._get_expertise_evaluation_prompt()},
                {"role": "user", "content": evaluation_context},
            ]

            # Use GPT-5 for holistic expertise evaluation
            # Note: GPT-5 only supports default temperature (1.0)
            evaluation_data = self.client.create_structured_completion(
                messages=messages,
                response_schema=evaluation_schema,
                use_complex_model=True,  # Use GPT-5 for intelligent evaluation
                temperature=None,  # Use default temperature for GPT-5 compatibility
            )

            # Map expertise level to appropriate report complexity
            complexity = self._determine_report_complexity(evaluation_data["expertise_level"])

            result = AssessmentResult(
                session_id="",  # Will be set by calling code
                expertise_level=evaluation_data["expertise_level"],
                report_complexity=complexity,
                explanation=evaluation_data["explanation"],
                ticker_context=ticker,
                score_breakdown=score_breakdown,
            )

            logger.info(f"Evaluated expertise level: {result.expertise_level}/10 for {ticker}")
            return result

        except Exception as e:
            logger.error(f"Failed to evaluate expertise for {ticker}: {str(e)}")
            raise

    def _calculate_category_scores(
        self, questions: list[AssessmentQuestion], responses: list[AssessmentResponse]
    ) -> dict:
        """Calculate scores by category for breakdown analysis."""
        category_scores = dict.fromkeys(self.categories, 0.0)

        response_dict = {r.question_id: r for r in responses}

        for question in questions:
            response = response_dict.get(question.id)
            if response:
                # Award points based on correctness and weight
                if response.selected_option == response.correct_option:
                    points = question.weight
                else:
                    points = response.partial_credit * question.weight

                category_scores[question.category] += points

        return category_scores

    def _calculate_max_possible_score(self, questions: list[AssessmentQuestion]) -> float:
        """Calculate the maximum possible score from all questions."""
        return sum(q.weight for q in questions)

    def _create_evaluation_context(
        self,
        questions: list[AssessmentQuestion],
        responses: list[AssessmentResponse],
        score_breakdown: dict,
        ticker: str,
        percentage_score: float,
        suggested_level: int,
    ) -> str:
        """Create detailed context for AI evaluation."""
        response_dict = {r.question_id: r for r in responses}

        context_parts = [
            f"ASSESSMENT EVALUATION FOR TICKER: {ticker}",
            f"Total Questions: {len(questions)}",
            f"Total Responses: {len(responses)}",
            f"Overall Score: {percentage_score:.1f}%",
            f"Baseline-Adjusted Suggested Level: {suggested_level}/10",
            "",
            "ADJUSTED SCORING SCALE (ACCOUNTING FOR 25% RANDOM GUESSING):",
            "- Level 1: 0-27% (Random guessing or below)",
            "- Level 2: 28-35% (Slightly above random)",
            "- Level 3: 36-43% (Basic knowledge)",
            "- Level 4: 44-51% (Developing understanding)",
            "- Level 5: 52-59% (Intermediate knowledge)",
            "- Level 6: 60-67% (Good understanding)",
            "- Level 7: 68-75% (Advanced knowledge)",
            "- Level 8: 76-83% (Sophisticated analysis)",
            "- Level 9: 84-91% (Expert level)",
            "- Level 10: 92-100% (Top-tier analyst)",
            "",
            "SCORE BREAKDOWN BY CATEGORY:",
        ]

        for category, score in score_breakdown.items():
            context_parts.append(f"- {category}: {score:.2f} points")

        context_parts.extend(
            [
                "",
                "DETAILED RESPONSE ANALYSIS:",
            ]
        )

        for question in questions:
            response = response_dict.get(question.id)
            if response:
                correct = "✓" if response.selected_option == response.correct_option else "✗"
                context_parts.append(
                    f"Q{question.id} (Level {question.difficulty_level}, {question.category}): {correct} "
                    f"Weight: {question.weight}, Time: {response.time_taken:.1f}s"
                )

        return "\n".join(context_parts)

    def _determine_report_complexity(self, expertise_level: int) -> str:
        """
        Map expertise level to appropriate report complexity.

        Args:
            expertise_level: User expertise level (1-10)

        Returns:
            Report complexity type for appropriate report length
        """
        if expertise_level <= 2:
            return "foundational"  # 250-300 pages
        elif expertise_level <= 4:
            return "educational"  # 150-200 pages
        elif expertise_level <= 6:
            return "intermediate"  # 80-100 pages
        elif expertise_level <= 8:
            return "advanced"  # 50-60 pages
        else:  # 9-10
            return "executive"  # 10-20 pages

    def get_report_complexity_info(self, complexity: str) -> dict:
        """
        Get detailed information about report complexity levels.

        Args:
            complexity: Report complexity type

        Returns:
            Dictionary with page count and description
        """
        complexity_mapping = {
            "foundational": {
                "page_range": "250-300",
                "description": "Comprehensive educational reports with maximum detail and fundamentals",
                "target_audience": "Complete novices needing extensive education",
            },
            "educational": {
                "page_range": "150-200",
                "description": "Detailed explanatory reports with examples and context",
                "target_audience": "Basic understanding users requiring detailed explanations",
            },
            "intermediate": {
                "page_range": "80-100",
                "description": "Balanced analysis with moderate complexity and context",
                "target_audience": "Intermediate knowledge users comfortable with some advanced concepts",
            },
            "advanced": {
                "page_range": "50-60",
                "description": "Sophisticated analysis reports with minimal educational content",
                "target_audience": "Advanced users appreciating sophisticated analysis",
            },
            "executive": {
                "page_range": "10-20",
                "description": "Expert-level executive summaries with advanced insights",
                "target_audience": "Expert-level users preferring concise summaries",
            },
        }
        return complexity_mapping.get(complexity, {})

    def _calculate_score_percentage(
        self, questions: list[AssessmentQuestion], responses: list[AssessmentResponse]
    ) -> float:
        """
        Calculate the percentage score from weighted responses.

        Args:
            questions: List of assessment questions
            responses: List of user responses

        Returns:
            Percentage score (0-100)
        """
        total_possible_points = sum(q.weight for q in questions)
        earned_points = 0.0

        response_dict = {r.question_id: r for r in responses}

        for question in questions:
            response = response_dict.get(question.id)
            if response:
                if response.selected_option == response.correct_option:
                    earned_points += question.weight
                else:
                    earned_points += response.partial_credit * question.weight

        return (earned_points / total_possible_points) * 100.0 if total_possible_points > 0 else 0.0

    def _map_percentage_to_expertise_level(self, percentage: float) -> int:
        """
        Map percentage score to expertise level using adjusted scale.

        20-100% range (80% total) divided into 10 levels = 8% per level
        Level N starts at: 20% + ((N-1) × 8%)

        Args:
            percentage: Score percentage (0-100)

        Returns:
            Expertise level (1-10)
        """
        if percentage < 28:  # 0-27%
            return 1
        elif percentage < 36:  # 28-35%
            return 2
        elif percentage < 44:  # 36-43%
            return 3
        elif percentage < 52:  # 44-51%
            return 4
        elif percentage < 60:  # 52-59%
            return 5
        elif percentage < 68:  # 60-67%
            return 6
        elif percentage < 76:  # 68-75%
            return 7
        elif percentage < 84:  # 76-83%
            return 8
        elif percentage < 92:  # 84-91%
            return 9
        else:  # 92-100%
            return 10

    def _get_question_generation_prompt(self) -> str:
        """Get the system prompt for question generation."""
        return """You are an expert investment assessment specialist tasked with generating contextual, progressive assessment questions for individual stock tickers.

CORE RESPONSIBILITIES:
1. Generate exactly 20 questions tailored to the specific ticker and its industry context
2. Create progressive difficulty from Level 1 (complete novice) to Level 10 (top-tier analyst)
3. Ensure questions are contextually relevant to the specific company/ticker
4. Distribute questions evenly across 4 categories (5 questions each)

DIFFICULTY PROGRESSION GUIDELINES:
- Level 1-2: Basic market concepts, awareness of company existence
- Level 3-4: Understanding of business model, basic financial metrics
- Level 5-6: Industry knowledge, competitive positioning
- Level 7-8: Advanced valuation concepts, detailed company analysis
- Level 9-10: Expert-level insights, sophisticated analytical frameworks

CATEGORIES (5 questions each):
1. general_investing: Broad market knowledge, investment principles
2. ticker_specific: Company-specific knowledge, history, products
3. sector_expertise: Industry dynamics, competitive landscape
4. analytical_sophistication: Valuation methods, financial analysis techniques

QUESTION QUALITY STANDARDS:
- Each question must have exactly 4 plausible multiple choice options
- Options should include one clearly correct answer and three reasonable distractors
- Questions should be clear, unambiguous, and professionally worded
- Avoid trick questions; focus on knowledge assessment
- Weight assignment: Levels 1-3 = 1.0, Levels 4-7 = 1.5, Levels 8-10 = 2.0
CRITICAL: RANDOMIZE CORRECT ANSWER POSITIONS
- DO NOT put all correct answers in position 0 (first choice)
- Randomly distribute correct answers across positions 0, 1, 2, and 3
- Make sure incorrect options are plausible but clearly wrong to experts
- Vary the correct_answer_index to prevent pattern recognition

Generate questions that effectively differentiate between novice and expert knowledge levels while remaining contextually relevant to the specific ticker."""

    def _get_expertise_evaluation_prompt(self) -> str:
        """Get the system prompt for holistic expertise evaluation."""
        return """You are an expert investment assessment evaluator specializing in holistic analysis of investor expertise based on contextual assessment performance.

EVALUATION MISSION:
Analyze assessment performance to determine expertise level (1-10) and appropriate report complexity, providing clear explanations for your assessment.

EXPERTISE LEVEL SCALE (ADJUSTED FOR RANDOM GUESSING):
- Level 1: 0-27% - Random guessing or below (needs maximum educational content)
- Level 2: 28-35% - Slightly above random (basic awareness, comprehensive education needed)
- Level 3: 36-43% - Basic knowledge (fundamental understanding, detailed explanations needed)
- Level 4: 44-51% - Developing understanding (good basics, requires explanatory content)
- Level 5: 52-59% - Intermediate knowledge (solid foundation, moderate complexity acceptable)
- Level 6: 60-67% - Good understanding (comfortable with complexity, balanced analysis)
- Level 7: 68-75% - Advanced knowledge (sophisticated concepts, minimal education needed)
- Level 8: 76-83% - Sophisticated analysis (expert-level concepts, advanced reports)
- Level 9: 84-91% - Expert level (top-tier knowledge, executive summaries preferred)
- Level 10: 92-100% - Top-tier analyst (comprehensive expertise, concise expert content)

REPORT COMPLEXITY MAPPING:
- Levels 1-2: "foundational" (250-300 page comprehensive educational reports)
- Levels 3-4: "educational" (150-200 page detailed explanatory reports)
- Levels 5-6: "intermediate" (80-100 page balanced analysis with context)
- Levels 7-8: "advanced" (50-60 page sophisticated analysis reports)
- Levels 9-10: "executive" (10-20 page expert-level executive summaries)

SCORING METHODOLOGY (CRITICAL):
- Random guessing baseline: 25% expected accuracy on multiple choice
- Effective scoring range: 20-100% (80% range) mapped across 10 expertise levels
- Each level represents 8% increment: Level N = 20% + ((N-1) × 8%)
- Score calculation: (Correct answers × weights) / Total possible points × 100%

HOLISTIC EVALUATION FACTORS:
1. Adjusted score percentage accounting for random guessing baseline
2. Performance on higher difficulty questions (levels 7-10) weighted more heavily
3. Consistency across different knowledge areas (pattern analysis)
4. Time taken per question (confidence and knowledge depth indicators)
5. Category-specific performance distribution

EVALUATION PRINCIPLES:
- Account for 25% random guessing baseline in all assessments
- Use compressed 20-100% scale for true knowledge differentiation
- Weight advanced questions (levels 8-10) significantly higher
- Look for knowledge patterns that distinguish real understanding from guessing
- Be precise with level assignments using the 8% increment scale
- Provide clear explanations referencing the adjusted scoring methodology

Your evaluation should be thorough, fair, and provide valuable insights into the user's investment knowledge level."""
